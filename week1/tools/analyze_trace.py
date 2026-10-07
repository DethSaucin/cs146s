"""Summarize captured Claude Code /v1/messages request bodies.

Usage: python analyze_trace.py <bodies_dir>
Reads NNN_POST_v1_messages.req.json files written by dump_bodies.py and prints, per request:
message count, request size, tool inventory (built-in / MCP / deferred), where <system-reminder>
blocks appear, and the tool_use -> tool_result sequence. Never prints headers (no secrets there).
"""
import glob
import json
import os
import re
import sys

DEFERRED_RE = re.compile(r"deferred tools are now available via ToolSearch.*?:\n((?:[A-Za-z0-9_]+\n)+)", re.S)


def blocks(msg):
    c = msg["content"]
    return [{"type": "text", "text": c}] if isinstance(c, str) else c


def text_of(b):
    if b.get("type") == "text":
        return b["text"]
    if b.get("type") == "tool_result":
        c = b.get("content")
        return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []))
    return ""


def main(d):
    files = sorted(glob.glob(os.path.join(d, "*_POST_v1_messages.req.json")))
    prev_tools = None
    for f in files:
        r = json.load(open(f))
        name = os.path.basename(f).split("_")[0]
        tools = [t["name"] for t in r.get("tools", [])]
        mcp = [t for t in tools if t.startswith("mcp__")]
        placeholder = [t["name"] for t in r.get("tools", []) if t.get("defer_loading")]
        builtin = [t for t in tools if t not in mcp and t not in placeholder]
        deferred = []
        for m in r["messages"]:
            for b in blocks(m):
                mm = DEFERRED_RE.search(text_of(b))
                if mm:
                    deferred = mm.group(1).split()
        reminders = []
        for i, m in enumerate(r["messages"]):
            for b in blocks(m):
                n = text_of(b).count("<system-reminder>")
                if n:
                    reminders.append(f"msg[{i}]/{m['role']}/{b['type']}x{n}")
        sys_rem = sum(b.get("text", "").count("<system-reminder>") for b in r.get("system", []))
        print(f"=== request {name}  model={r.get('model')}  bytes={os.path.getsize(f)}  messages={len(r['messages'])}")
        print(f"    tools sent={len(tools)}: built-in={len(builtin)} mcp={len(mcp)} placeholder={len(placeholder)}; "
              f"deferred-by-name={len(deferred)} -> total reachable={len(builtin)+len(mcp)+len(deferred)}")
        if prev_tools is not None and prev_tools != tools:
            print(f"    TOOL SET CHANGED: +{sorted(set(tools)-set(prev_tools))} -{sorted(set(prev_tools)-set(tools))}")
        prev_tools = tools
        print(f"    system blocks={len(r.get('system', []))} (literal '<system-reminder>' mentions inside system text: {sys_rem}); "
              f"role=system messages={[i for i,m in enumerate(r['messages']) if m['role']=='system']}")
        print(f"    <system-reminder> locations: {reminders}")
        cache = [f"system[{i}]" for i, b in enumerate(r.get("system", [])) if b.get("cache_control")]
        cache += [f"msg[{i}]" for i, m in enumerate(r["messages"]) for b in blocks(m) if b.get("cache_control")]
        cache += [f"tool:{t['name']}" for t in r.get("tools", []) if t.get("cache_control")]
        print(f"    cache_control breakpoints: {cache}")
        for i, m in enumerate(r["messages"]):
            for b in blocks(m):
                if b.get("type") == "tool_use":
                    print(f"    msg[{i}] tool_use {b['name']} {json.dumps(b['input'])[:160]}")
                elif b.get("type") == "tool_result":
                    err = " ERROR" if b.get("is_error") else ""
                    print(f"    msg[{i}] tool_result{err}: {text_of(b)[:160]!r}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bodies")
