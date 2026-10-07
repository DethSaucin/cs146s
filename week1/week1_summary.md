# CS146S Week 1: The Internals of Coding Agents (self-study summary)

*Written for me as a self-learner. Sources: course site <https://themodernsoftware.dev> (Fall 2026
syllabus), assignment <https://github.com/mihail911/modern-software-dev-assignments/tree/master/week1>,
lecture transcript <https://themodernsoftware.dev/materials/9-24-26-transcript.txt>, and the readings below.
My completed assignment is in [`writeup.md`](writeup.md).*

---

## 1. What week 1 is about

Week 1 opens the hood on a coding agent. The claim is that a coding agent is **a model plus a harness**.
You can't see the model (its weights live on someone else's servers), but you *can* see everything the
harness sends it, and most of what makes an agent good or bad lives there.

| Session | Topic |
|---|---|
| Tue 9/22 | Course intro + **build Claude Code in 200 lines** (the bare agent loop) |
| Thu 9/24 | **How state-of-the-art coding agents are designed**: a deep dive into Claude Code's system prompt, tools, CLAUDE.md, plan mode, skills, subagents, hooks, compaction |

Readings: *Building a Coding Agent* (video, <https://youtube.com/watch?v=s7ZzkdvCMDY>), *Lessons from
Building Claude Code* (Thariq, <https://x.com/trq212/status/2027463795355095314>), and *Dive into Claude
Code* (arXiv 2604.14228, <https://arxiv.org/abs/2604.14228>). I read the paper and the 9/24 transcript. I
couldn't watch the video or open the X post from my box, so nothing here comes from those two.

Assignment: **Trace Dissection of a Real Claude Code Session**. Put Claude Code behind a proxy, capture
its real HTTP requests, and annotate the system prompt, the tools, and the behavior.

> FYI: the Fall 2025 version of week 1 was different ("LLM Prompting Playground": prompting techniques
> against a local Ollama model). That's what the current site's "Fall 2025" tab and the repo's old history
> show. I did the current Fall 2026 version.

---

## 2. Key concepts, explained plainly

**The agent loop.** (A community analysis cited in the paper estimates only ~1.6% of Claude Code's code is "AI decision logic"; the rest is infrastructure.) An agent is a `while` loop: send
the conversation to the model. If the model asks for a tool, run it, append the result, and loop. If it
answers in plain text, stop. That's all the 200-line demo is:

```python
# illustrative sketch of the Tue 9/22 idea (not run)
messages = [{"role": "user", "content": task}]
while True:
    resp = llm(system=SYSTEM_PROMPT, tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    calls = [b for b in resp.content if b.type == "tool_use"]
    if not calls:
        break                                   # plain text means done
    results = [{"type": "tool_result", "tool_use_id": c.id, "content": run_tool(c.name, c.input)}
               for c in calls]
    messages.append({"role": "user", "content": results})   # tool results come back as a *user* turn
```

The *Dive into Claude Code* paper says the same about the real product: "The core of the system is a
simple while-loop… Most of the code, however, lives in the systems around this loop": permissions,
context compaction, extensibility, subagents, and session storage.

**The harness is everything around the loop.** That includes the system prompt, tool definitions,
CLAUDE.md/AGENTS.md, plan mode, skills, subagents, hooks, compaction, permissions, and memory. Mihail's
main point: *harness design is one of the hardest and most important problems in agents*, and the current
trend is **simpler harnesses: fewer, more powerful tools and shorter prompts**.

**A tool is part of the prompt.** A tool's name, description, and JSON schema are pasted into *every*
request. Writing a tool means writing prompt text: clear names and descriptions, typed arguments.
Powerful general tools (Bash, SQL) beat 100 narrow ones. Early GitHub MCP servers shipped ~110 tools and
bloated every request.

**The system prompt** is the harness's fixed, behind-the-scenes "blueprint": identity, safety rules,
how to use the harness, memory, environment. You don't write it, but you pay for its tokens and live with
its effects.

**CLAUDE.md / AGENTS.md** is the part *you* control. It's injected as a user-side message, not into the
system prompt, so following it is probabilistic. Keep it short: how to run tests and start the server,
the project layout. Too much over-constrains the agent.

**`<system-reminder>` blocks** are harness-injected notes placed inside the conversation (git status,
policy updates, tool or skill listings). Putting them in the conversation instead of the system prompt
keeps the big prefix stable (cacheable) and puts fresh facts near the end, where the model pays the most
attention.

**Progressive disclosure.** Don't load everything up front. Skills appear as one-line descriptions until
used. With `ENABLE_TOOL_SEARCH`, "deferred" tools appear by *name only* and the model calls `ToolSearch`
to load a schema when it needs one.

**Subagents** are a tool call (`Agent`) that starts a fresh agent with only the prompt you give it. It
explores in its own context and returns a summary. Mostly this is a *context-management* tool.

**Compaction** summarizes old context when the window fills up. The "dumb zone" is the informal name for
the point where too much context makes the model worse.

**Context is the binding constraint.** Almost every harness feature (deferred tools, skills, subagents,
compaction, prompt caching) exists to protect the context window.

---

## 3. The assignment: what each part asked, what I did, and why it works

**My setup (important caveat).** I didn't have an Anthropic login on the box I used, so I ran the **real
Claude Code client (v2.1.292)** but pointed `ANTHROPIC_BASE_URL` at a proxy in front of **Ollama running
`qwen3:4b-instruct-2507` locally**. Ollama speaks Anthropic's `/v1/messages` format. What I captured (the
system prompt, tools, reminders, and message layout) is genuinely Claude Code's. The *decisions and skill*
in the session are a 4B local model's, so behavior is far weaker than real Claude.

### Part I: Capture a session (multi-file, at least one failure, a plan, your own repo)

**What I did:** I wrote a tiny repo, `scratch-textstats` (`tokens.words()` imported by `stats.py`, plus 3
tests), deleted `words()` on purpose, and asked Claude Code to plan, run the tests, fix them, add
`unique_words()` plus a test, and re-run. The proxy is a reverse proxy, so there's no TLS certificate to
deal with:

```bash
mitmdump --listen-host 127.0.0.1 --listen-port 58888 \
         --mode reverse:http://127.0.0.1:11434 -w session.flows -s dump_bodies.py
# scratch-textstats/.claude/settings.json
{"env": {"ANTHROPIC_BASE_URL": "http://127.0.0.1:58888", "ENABLE_TOOL_SEARCH": "true"}}
```

**Why it works:** Claude Code takes its API base URL from settings, so a project-level setting sends only
*this* repo's traffic to the proxy. Reverse mode means plain HTTP to localhost, so you're looking at the
exact JSON body (`system`, `tools`, `messages`) the model receives. A small mitmproxy addon saved request
bodies only (headers are where API keys live).

**Result:** 19 completed requests (plus 4 client timeouts/aborts). It touched 3 files and hit 4 kinds
of failure. A first attempt with `qwen2.5-coder:3b` died after 1 request because the model *printed* a
JSON tool call as text instead of emitting a real `tool_use` block. That's a good reminder that tool
calling is a trained skill.

### Part II: Annotate the system prompt

**Asked:** for each section, what behavior it buys and what failure it defends against: structure,
tone, when not to act, environment, and `<system-reminder>`.

**What I found:** `system` = 3 blocks: billing/version header, identity line (*"You are a Claude agent,
built on Anthropic's Claude Agent SDK."* in headless mode), and a ~5.7 KB main prompt (security policy,
then harness mechanics, then code style, then irreversible-action rules, then memory, environment, and
context management). Session-specific information is **not** in `system`. Git status is a
`<system-reminder>` in the first user message. Cwd/OS/date/model/skills/deferred tools are in a
`role:"system"` message. A `<total_tokens>… left` system note follows every tool result.

Key snippet, a judgment rule instead of a list of banned commands:
```
For actions that are hard to reverse or outward-facing, confirm first unless durably authorized or
explicitly told to proceed without asking; approval in one context doesn't extend to the next.
```
**Why it's designed this way:** a reversibility test generalizes to commands nobody listed, and "doesn't
extend" blocks scope creep. Hard enforcement lives in the permission system, so the prompt is the soft
layer. Keeping `system` free of per-session facts makes the prefix identical across sessions, so it can
be cached.

### Part III: Annotate the tool design

**Asked:** exact counts (built-in, MCP, deferred), plus an interface-design analysis of two different tools.

**What I found:** **12 definitions sent = 11 built-in with full schemas + 1 `DeferredToolPlaceholder`;
10 more deferred by name; 0 MCP; 21 callable.** No change across requests (`ToolSearch` was never
called). Tool schemas were **61% of the first request (27.8 of 45.2 KB)**.

- **Edit**: `file_path`, `old_string`, `new_string`, optional `replace_all`. It uses exact unique string
  replacement, not line numbers or diffs, because line numbers go stale and models garble patches. Scar
  tissue: *"Strip the Read line prefix (line number + tab) before matching"* exists because models pasted
  `cat -n` line numbers into `old_string`. I watched its failure contract:
  `<tool_use_error>No changes to make: old_string and new_string are exactly the same.</tool_use_error>`
- **Agent**: only `description` + `prompt` are required. There's no way to pass the parent's history, so
  subagents start fresh, and only a final report comes back. Scar tissue: *"Never fabricate or predict a
  pending agent's results"*.

**Why it matters:** good tools are small, exact, and **fail loudly with an error the model can act on**,
while the harness tracks state (read-before-edit, "Wasted call — file unchanged since your last Read").

### Part IV: Behavioral analysis (cite evidence, label OBSERVED vs. INFERRED)

- **Error recovery [OBSERVED, model-dependent]:** it fixed the planted `ImportError` in 3 requests, then
  introduced `SyntaxError: unterminated triple-quoted string literal` (opened with `'''`, closed with
  `''`). It rewrote the *identical* file 3 times, saying "I see the issue now" each time. Even after my
  exact hint, it sent no-op Edits. I stopped it and fixed it by hand (also restoring lowercasing and fixing
  its wrong test, which expected 3 unique words in "a a a b b b"). Final: `4 passed`.
- **Planning [OBSERVED]:** this headless build had **no** todo or plan tool. The 4-step plan was plain
  assistant text, prompted by my request. It was emergent, not a tool or a system instruction.
- **Task state / subagents [INFERRED]:** no structured task state, and no subagent was spawned. From the
  definitions: subagents get only `prompt` and return a summary.
- **Context management [OBSERVED]:** append-only history (2 → 59 messages, 45 → 68 KB). `system` and
  `tools` never changed. A **rolling `cache_control` breakpoint** moved to the newest message every turn.
  No compaction (far below the window). On resume, the harness inserted a synthetic *"No response
  requested."* assistant turn to close the interrupted turn.

### Part V: Reflection (short)

Copy: **stable prefix, dynamic tail**, and **loud-failing primitives with harness state tracking**. Change:
defer rarely used heavy tools (Workflow, ScheduleWakeup, and ReportFindings are ~13 KB every turn). What
changed for me: an agent's "I see the issue now" means nothing, so verify with diffs and tests and break
loops early.

---

## 4. Observed results at a glance

| Metric | Value |
|---|---|
| Claude Code version | 2.1.292 (headless `-p`, `bypassPermissions`) |
| Model behind it | `qwen3:4b-instruct-2507-q4_K_M` on CPU via Ollama (not Claude) |
| `/v1/messages` requests | 23 sent, 19 completed (14 first run + 5 after resume) |
| First request size | 45.2 KB (~10.6k tokens): tools 27.8 KB, system 5.8 KB, `messages[1]` 9.1 KB |
| Tools | 11 full + 1 placeholder + 10 deferred = 21 callable, 0 MCP, never changed |
| Failures seen | ImportError (planted) → fixed; SyntaxError (self-made) → **not** fixed by the agent; 2 Edit errors; 1 "Wasted call" |
| Final tests | `4 passed` after my manual fix |
| Speed | First request ~16 min on CPU (3 timeout retries), later turns 1-3 min thanks to prefix caching |

---

## 5. Key takeaways

1. **Agent = loop + harness.** The loop is about 20 lines. The value and difficulty are in the harness:
   what goes into context, which tools exist, and how failures are reported.
2. **Everything is prompt.** Tool descriptions, schemas, CLAUDE.md, MCP servers, and skill listings all
   cost tokens on *every* request. In my trace, tool schemas alone were 61% of the first request.
3. **Context is the scarce resource.** Deferred tools, skills, subagents, compaction, and caching all
   exist to protect it. Treat your own CLAUDE.md and MCP setup the same way.
4. **Stable prefix, dynamic tail.** Put fixed instructions first and changing facts in late messages or
   reminders, so the expensive part is cached. The `<system-reminder>` pattern is how this is done.
5. **Design tools to fail loudly and instructively.** Exact, unique, read-before-write contracts turn
   silent damage into errors the model can fix. Tool descriptions are "scar tissue": each odd sentence
   records a real past failure.
6. **Planning and delegation are often just prompting.** Here, the plan was emergent text and subagents
   are just a tool call with a fresh context. Don't assume there's magic structure underneath.
7. **The model still matters a lot.** The same harness with a 4B model hit a 1-character bug and looped
   forever while claiming progress. The harness can't fix bad judgment, but it can make failures visible.
8. **Steering lesson:** verify claims with diffs and tests, give pinpoint hints, and restart with a fresh
   context instead of piling on instructions when an agent loops.

---

## 6. Experiments to try yourself

1. **Measure the tax.** Re-capture the first request with `ENABLE_TOOL_SEARCH` off, with one MCP server
   added (e.g. a GitHub or Notion MCP), and with a 30-line CLAUDE.md. Run
   `python tools/analyze_trace.py <bodies>` and compare bytes and tool counts. Where does your CLAUDE.md
   land (system vs. a user `<system-reminder>`)?
2. **Swap the brain, keep the harness.** Replay the same broken-repo task with a stronger model (real
   Claude via your own account, or a bigger local model if you have the RAM) and diff the traces. The
   requests should be nearly identical. What changes is the decisions: does it use `Edit` instead of
   rewriting with `Write`? Does it catch the lowercasing regression? Does it try the deferred tools?
3. **Trigger the features I didn't see.** Run interactively (not `-p`) and ask for plan mode, a subagent
   ("use an Explore agent to…"), and a skill. Find where the plan-mode prompt, the subagent's `prompt`,
   and the skill text get injected, and whether new `<system-reminder>`s appear mid-session.
4. **Build the 200-line agent.** Implement the loop above against Ollama's `/v1/messages` with just
   `read_file`, `write_file`, and `bash`, then add Claude Code's Edit contract (unique `old_string`,
   read-before-edit) and see how much it improves a small model's reliability on the same task.
