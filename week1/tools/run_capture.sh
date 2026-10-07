#!/usr/bin/env bash
# Reproduce the week 1 capture on a CPU-only Linux box with no Anthropic account:
#   Claude Code  ->  mitmdump (reverse proxy, :58888)  ->  Ollama's Anthropic-compatible /v1/messages (:11434)
# Run from week1/ . Requires: ollama, claude (npm i -g @anthropic-ai/claude-code), mitmproxy (pip install mitmproxy).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CAP="${CAP:-$HERE/../../capture}"   # keep captures OUTSIDE any git repo
mkdir -p "$CAP"; cp "$HERE/dump_bodies.py" "$CAP/"

# 1. Local model server (20k context, q8 KV cache to fit in ~4 GB RAM)
OLLAMA_CONTEXT_LENGTH=20480 OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 \
  nohup ollama serve > "$CAP/ollama_serve.log" 2>&1 &
sleep 3
ollama pull qwen3:4b-instruct-2507-q4_K_M

# 2. Reverse proxy that records every flow + dumps request bodies (no headers) to $CAP/bodies/
(cd "$CAP" && nohup mitmdump --listen-host 127.0.0.1 --listen-port 58888 \
   --mode reverse:http://127.0.0.1:11434 -w session.flows -s dump_bodies.py > mitmdump.log 2>&1 &)

# 3. Project-level settings in the scratch repo point Claude Code at the proxy
#    (scratch-textstats/.claude/settings.json: ANTHROPIC_BASE_URL=http://127.0.0.1:58888, ENABLE_TOOL_SEARCH=true)
source "$HERE/env.sh"
cd "$HERE/../scratch-textstats"
claude -p "The test suite in this repo is failing. Do the following: (1) Make a plan first using your todo list tool. (2) Run the tests with \`python -m pytest -q\` to see the failure. (3) Fix the code so all tests pass. (4) Add a new function \`unique_words(text) -> int\` to textstats/stats.py and a test for it in tests/test_stats.py. (5) Re-run the tests and confirm they all pass." \
  --model qwen3:4b-instruct-2507-q4_K_M --dangerously-skip-permissions --max-turns 30 \
  --verbose --output-format stream-json > "$CAP/claude_session.jsonl"

python "$HERE/analyze_trace.py" "$CAP/bodies"
# 4. Clean up afterwards: delete scratch-textstats/.claude/settings.json and stop mitmdump/ollama.
