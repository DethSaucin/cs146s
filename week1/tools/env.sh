# Environment for running Claude Code against a LOCAL Ollama model (no Anthropic account).
# "ollama" is a dummy token that Ollama ignores; nothing here is a secret.
export PATH=$HOME/.local/bin:$PATH
export CLAUDE_CONFIG_DIR="${CS146S_CLAUDE_HOME:-/tmp/cs146s-claude-home}"   # isolated config, keeps your real ~/.claude untouched
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export DISABLE_TELEMETRY=1
export ANTHROPIC_DEFAULT_HAIKU_MODEL=qwen3:4b-instruct-2507-q4_K_M
export ANTHROPIC_DEFAULT_SONNET_MODEL=qwen3:4b-instruct-2507-q4_K_M
export ANTHROPIC_DEFAULT_OPUS_MODEL=qwen3:4b-instruct-2507-q4_K_M
export ANTHROPIC_SMALL_FAST_MODEL=qwen3:4b-instruct-2507-q4_K_M
export API_TIMEOUT_MS=1800000   # CPU inference is slow; avoid client timeouts + retries on the first (~10k-token) request
