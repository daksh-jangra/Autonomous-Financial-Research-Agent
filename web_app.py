"""Minimal local web UI for the Autonomous Financial Research Agent.

A single-page app: type a research question, submit, and see the rendered
report. Built on Python's stdlib http.server (no Flask/FastAPI needed) and
markdown-it-py for Markdown -> HTML.

Usage:
    python web_app.py            # serves http://127.0.0.1:8000
    python web_app.py 8080       # custom port

Note: this is a local development UI for demoing the agent, not a hardened
production server.
"""
import html
import logging
import os
import sys
import urllib.parse
import warnings
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from agent.core import FinancialResearchAgent
from agent.llm_factory import build_llm_from_env, llm_status

try:
    from markdown_it import MarkdownIt
    _md = MarkdownIt("commonmark", {"html": False}).enable("table")

    def render_md(text):
        return _md.render(text)
except Exception:  # fallback: show raw markdown safely
    def render_md(text):
        return "<pre>" + html.escape(text) + "</pre>"

# Single shared agent instance (auto-detects an LLM key, else deterministic).
AGENT = FinancialResearchAgent(llm=build_llm_from_env())

EXAMPLES = [
    "Create a comprehensive profile of Microsoft Corporation",
    "Produce a risk assessment for Tesla Inc.",
    "Compare the cloud divisions of Amazon, Microsoft, and Google",
    "What's happening with the banks?",
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Autonomous Financial Research Agent</title>
<style>
  :root {{ --bg:#0f1419; --card:#1a2029; --fg:#e6e9ef; --muted:#9aa4b2; --accent:#4f9cf9; --border:#2a313c; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; line-height:1.55; }}
  .wrap {{ max-width: 880px; margin: 0 auto; padding: 32px 20px 80px; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 4px; }}
  .sub {{ color: var(--muted); margin: 0 0 24px; font-size: .9rem; }}
  form {{ display:flex; gap:10px; margin-bottom: 14px; }}
  input[type=text] {{ flex:1; padding:13px 15px; border-radius:10px; border:1px solid var(--border);
                      background:var(--card); color:var(--fg); font-size:1rem; }}
  button {{ padding:13px 22px; border:0; border-radius:10px; background:var(--accent); color:#fff;
            font-weight:600; cursor:pointer; font-size:1rem; }}
  button:hover {{ filter:brightness(1.08); }}
  .examples {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:28px; }}
  .examples a {{ font-size:.82rem; color:var(--muted); text-decoration:none; border:1px solid var(--border);
                 padding:5px 10px; border-radius:20px; }}
  .examples a:hover {{ color:var(--fg); border-color:var(--accent); }}
  .report {{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:26px 30px; }}
  .report h1 {{ font-size:1.4rem; }} .report h2 {{ font-size:1.1rem; border-bottom:1px solid var(--border);
                padding-bottom:6px; margin-top:28px; }}
  .report table {{ border-collapse:collapse; width:100%; margin:12px 0; font-size:.9rem; }}
  .report th, .report td {{ border:1px solid var(--border); padding:7px 10px; text-align:left; }}
  .report th {{ background:#222b36; }}
  .report code {{ background:#222b36; padding:2px 6px; border-radius:5px; }}
  .report pre {{ background:#222b36; padding:14px; border-radius:8px; overflow:auto; }}
  .report a {{ color:var(--accent); }}
  .meta {{ color:var(--muted); font-size:.82rem; margin:14px 0 0; }}
  .empty {{ color:var(--muted); }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Autonomous Financial Research Agent</h1>
    <p class="sub">{status}</p>
    <form method="get" action="/">
      <input type="text" name="q" placeholder="Ask a research question, e.g. 'Profile Apple Inc.'"
             value="{query_value}" autofocus>
      <button type="submit">Research</button>
    </form>
    <div class="examples">{examples}</div>
    {body}
  </div>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence per-request logging

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in ("/", ""):
            self.send_response(404)
            self.end_headers()
            return
        params = urllib.parse.parse_qs(parsed.query)
        query = (params.get("q", [""])[0]).strip()

        if query:
            try:
                result = AGENT.run(query)
                report_html = render_md(result.get("report", "_No report._"))
                t = result.get("trace", {})
                meta = (f"intent: {t.get('intent')} &nbsp;|&nbsp; tickers: "
                        f"{', '.join(t.get('tickers') or []) or 'none'} &nbsp;|&nbsp; "
                        f"tool calls: {t.get('iterations')} &nbsp;|&nbsp; degraded: "
                        f"{t.get('degraded_calls')} &nbsp;|&nbsp; {t.get('duration_seconds')}s")
                body = f'<div class="report">{report_html}</div><p class="meta">{meta}</p>'
            except Exception as e:
                body = f'<div class="report"><p class="empty">Error: {html.escape(str(e))}</p></div>'
        else:
            body = ('<div class="report"><p class="empty">Enter a research question above '
                    'to generate a report.</p></div>')

        examples = "".join(
            f'<a href="/?q={urllib.parse.quote(ex)}">{html.escape(ex)}</a>' for ex in EXAMPLES)
        page = PAGE.format(status=html.escape(llm_status()),
                           query_value=html.escape(query),
                           examples=examples, body=body)
        encoded = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"ARA-1 web UI running at  http://127.0.0.1:{port}")
    print(f"Status: {llm_status()}")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
