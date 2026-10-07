# Week 1: The Internals of Coding Agents

Course materials: [syllabus](https://themodernsoftware.dev) (Fall 2026, Week 1) ·
[assignment (upstream)](https://github.com/mihail911/modern-software-dev-assignments/tree/master/week1) ·
[local copy of the assignment text](assignment_upstream.md)

| File | What it is |
|---|---|
| [`week1_summary.md`](week1_summary.md) | **Start here.** Teaching summary: concepts, each assignment part, results, takeaways, experiments |
| [`writeup.md`](writeup.md) | The assignment's `writeup.md` template, fully filled in from my own trace |
| [`tools/`](tools/) | `run_capture.sh` (reproduce the capture), `env.sh`, `dump_bodies.py` (mitmproxy addon, saves bodies, never headers), `analyze_trace.py` (counts tools, reminders, cache breakpoints, tool calls per request) |
| [`trace-analysis/`](trace-analysis/) | Analyzer output for my two runs (derived summaries only, no raw request bodies) |
| [`scratch-textstats/`](scratch-textstats/) | The throwaway repo the agent worked on, final state (`4 passed`), plus [`HISTORY.md`](scratch-textstats/HISTORY.md) with the break, the agent's attempt, and my fix |

**Caveat:** I captured the real Claude Code client (v2.1.292), but the model behind it was a local
`qwen3:4b-instruct-2507` served by Ollama, not Claude. Request structure is Claude Code's. Behavior is the
small model's. Raw captures (`session.flows`, request bodies) stay off GitHub, as the assignment asks.
