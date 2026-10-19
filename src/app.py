import json
import logging
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any
from src.domains.registry import registry
from src.domains.entertainment.ui import render_backlot_ui
from src.core.telemetry import evaluate_visitor

logger = logging.getLogger(__name__)

def handle_request(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Universal handler compatible with AWS Lambda Function URLs, API Gateway, and local ASGI."""
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    host = headers.get("host", "")
    domain_id = registry.resolve_domain(host)
    service = registry.get_service(domain_id)

    raw_path = event.get("rawPath") or event.get("path") or "/"
    http_method = (event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod") or "GET").upper()

    query_params = event.get("queryStringParameters") or {}

    # 1. Telemetry API endpoint
    if raw_path == "/api/telemetry" and http_method == "POST":
        body_str = event.get("body", "{}")
        try:
            payload = json.loads(body_str) if isinstance(body_str, str) else body_str
        except Exception:
            payload = {}

        client_ip = (
            headers.get("x-forwarded-for", "").split(",")[0].strip() or
            event.get("requestContext", {}).get("http", {}).get("sourceIp", "127.0.0.1")
        )

        is_human, ev = evaluate_visitor(headers, payload, client_ip)
        if is_human:
            logger.info(f"[HUMAN_PAGEVIEW] {json.dumps(ev)}")

        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-cache, no-store"
            },
            "body": ""
        }

    # 2. JSON Feed API
    if raw_path == "/api/feed":
        stage_filter = query_params.get("stage")
        items = service.get_radar_items(stage=stage_filter)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=300"
            },
            "body": json.dumps([it.model_dump() for it in items])
        }

    # 3. Stage breakdown API
    if raw_path == "/api/stages":
        counts = service.get_stage_breakdown()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=300"
            },
            "body": json.dumps(counts)
        }

    # 4. Robots.txt
    if raw_path == "/robots.txt":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": "User-agent: *\nAllow: /\nSitemap: https://backlotwire.com/sitemap.xml\n"
        }

    # 5. Default: SSR Web Interface
    stage_filter = query_params.get("stage")
    items = service.get_radar_items(stage=stage_filter)
    stage_counts = service.get_stage_breakdown()

    html = render_backlot_ui(
        items=items,
        current_stage=stage_filter,
        stage_counts=stage_counts
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "public, max-age=60, s-maxage=300"
        },
        "body": html
    }
