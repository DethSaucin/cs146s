"""mitmproxy addon: save every request/response body to numbered JSON files (no headers)."""
import itertools, json, os
from mitmproxy import http

_n = itertools.count(1)
OUT = os.path.join(os.path.dirname(__file__), "bodies")
os.makedirs(OUT, exist_ok=True)

def response(flow: http.HTTPFlow) -> None:
    i = next(_n)
    path = flow.request.path.split("?")[0].strip("/").replace("/", "_")
    base = os.path.join(OUT, f"{i:03d}_{flow.request.method}_{path}")
    with open(base + ".req.json", "wb") as f:
        f.write(flow.request.get_content() or b"")
    with open(base + ".resp.txt", "wb") as f:
        f.write(flow.response.get_content() or b"")
