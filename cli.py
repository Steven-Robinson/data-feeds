import sys
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.domains.registry import registry
from src.app import handle_request

console = Console()

class LocalDevHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def _dispatch(self, method: str):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""

        path_parts = self.path.split("?")
        raw_path = path_parts[0]
        query_str = path_parts[1] if len(path_parts) > 1 else ""

        from urllib.parse import parse_qs
        qs_parsed = {k: v[0] for k, v in parse_qs(query_str).items()}

        event = {
            "rawPath": raw_path,
            "path": raw_path,
            "httpMethod": method,
            "headers": dict(self.headers),
            "queryStringParameters": qs_parsed,
            "body": body
        }

        res = handle_request(event)
        self.send_response(res.get("statusCode", 200))
        for h, v in res.get("headers", {}).items():
            self.send_header(h, v)
        self.end_headers()

        if res.get("isBase64Encoded"):
            import base64
            body_bytes = base64.b64decode(res.get("body", ""))
        else:
            body_bytes = res.get("body", "").encode("utf-8")
        self.wfile.write(body_bytes)

def cmd_sync(args):
    service = registry.get_service("entertainment")
    console.print(Panel("[bold yellow]Backlot Wire[/bold yellow] — Syncing Hollywood Trade Feeds...", expand=False))
    items = service.sync_feeds(force=True)

    table = Table(title=f"Synced {len(items)} Trade Intelligence Items", show_header=True, header_style="bold magenta")
    table.add_column("Stage", style="bold cyan", width=14)
    table.add_column("Source", style="green", width=14)
    table.add_column("Headline", style="white")
    table.add_column("Date", style="dim", width=12)

    for it in items[:15]:
        stage_str = it.stage.value if it.stage else "NEWS"
        table.add_row(
            stage_str,
            it.source,
            it.title[:65] + "..." if len(it.title) > 65 else it.title,
            it.pub_date_iso[:10]
        )
    console.print(table)

def cmd_radar(args):
    service = registry.get_service("entertainment")
    counts = service.get_stage_breakdown()
    table = Table(title="Production Stage Breakdown", show_header=True, header_style="bold yellow")
    table.add_column("Production Stage", style="bold")
    table.add_column("Count", justify="right", style="cyan")

    for stage, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        table.add_row(stage, str(count))
    console.print(table)

def cmd_serve(args):
    port = args.port
    server_address = ('', port)
    httpd = HTTPServer(server_address, LocalDevHandler)
    console.print(Panel(
        f"[bold green]Backlot Wire Local Server Running[/bold green]\n\n"
        f"URL: [bold underline cyan]http://localhost:{port}[/bold underline cyan]\n"
        f"Press Ctrl+C to stop.",
        title="Data Feeds Engine",
        expand=False
    ))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")

def main():
    parser = argparse.ArgumentParser(description="Data Feeds CLI — Multi-Domain Intelligence Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # sync
    p_sync = subparsers.add_parser("sync", help="Fetch and process latest trade feeds")
    p_sync.set_defaults(func=cmd_sync)

    # radar
    p_radar = subparsers.add_parser("radar", help="Display current production stage breakdown")
    p_radar.set_defaults(func=cmd_radar)

    # serve
    p_serve = subparsers.add_parser("serve", help="Run local HTTP server")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
