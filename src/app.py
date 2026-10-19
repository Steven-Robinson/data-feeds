import os
import json
import logging
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any
from src.domains.registry import registry
from src.domains.entertainment.ui import render_backlot_ui
from src.core.telemetry import evaluate_visitor
from src.core.seo import generate_rss_feed, generate_sitemap_xml, generate_llms_txt, submit_indexnow, INDEXNOW_KEY

logger = logging.getLogger(__name__)

ORIGIN_VERIFY_SECRET = os.getenv("ORIGIN_VERIFY_SECRET", "")

def handle_request(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Universal handler compatible with AWS Lambda Function URLs, API Gateway, and local ASGI."""
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}

    # CloudFront origin verification (if configured)
    if ORIGIN_VERIFY_SECRET and headers.get("x-origin-verify") != ORIGIN_VERIFY_SECRET:
        return {
            "statusCode": 403,
            "headers": {"Content-Type": "text/plain; charset=utf-8"},
            "body": "Access Denied: Direct origin access is forbidden. Please visit via official domain."
        }

    # Resolve host from x-forwarded-host (CloudFront) or host header
    host = headers.get("x-forwarded-host") or headers.get("host") or ""
    domain_id = registry.resolve_domain(host)
    service = registry.get_service(domain_id)

    scheme = headers.get("x-forwarded-proto") or "https"
    # Canonical host handling: ignore internal AWS Lambda URL hostnames for SEO/RSS
    if not host or "lambda-url" in host or host.endswith(".on.aws"):
        host_val = "backlotwire.com"
    else:
        host_val = host
    clean_host = host_val.split(":")[0]
    base_url = f"{scheme}://{host_val}"

    raw_path = event.get("rawPath") or event.get("path") or "/"
    clean_path = raw_path.strip("/")
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

    # 4. Static Assets (/assets/...)
    if raw_path.startswith("/assets/"):
        asset_name = os.path.basename(raw_path)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        asset_path = os.path.join(base_dir, "assets", asset_name)
        if os.path.isfile(asset_path):
            import base64
            with open(asset_path, "rb") as f:
                raw_bytes = f.read()
            mime_type = "image/png" if asset_name.endswith(".png") else "image/jpeg"
            return {
                "statusCode": 200,
                "isBase64Encoded": True,
                "headers": {
                    "Content-Type": mime_type,
                    "Cache-Control": "public, max-age=86400, s-maxage=604800",
                },
                "body": base64.b64encode(raw_bytes).decode("ascii")
            }
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "text/plain"},
            "body": "Asset not found"
        }

    # 5. IndexNow Key Verification Route
    if clean_path in (f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY):
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "public, max-age=604800",
                "Access-Control-Allow-Origin": "*"
            },
            "body": INDEXNOW_KEY
        }

    # 6. IndexNow Search Engine Instant Submission API (/api/indexnow)
    if clean_path == "api/indexnow":
        res = submit_indexnow(base_url=base_url, host=clean_host)
        status_code = 200 if res.get("success") else 500
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(res)
        }

    # 7. Public Syndicated RSS 2.0 & Atom Feed (/rss.xml, /feed.xml, /rss, /feed)
    if clean_path in ("rss.xml", "feed.xml", "rss", "feed"):
        items = service.get_radar_items()
        rss_body = generate_rss_feed(items, base_url=base_url)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/rss+xml; charset=utf-8",
                "Cache-Control": "public, max-age=300",
                "Access-Control-Allow-Origin": "*"
            },
            "body": rss_body
        }

    # 8. XML Sitemap (/sitemap.xml)
    if clean_path == "sitemap.xml":
        sitemap_body = generate_sitemap_xml(base_url=base_url)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/xml; charset=utf-8",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            },
            "body": sitemap_body
        }

    # 9. LLMs.txt AI Search Protocol (/llms.txt)
    if clean_path == "llms.txt":
        llms_body = generate_llms_txt(base_url=base_url)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/markdown; charset=utf-8",
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            },
            "body": llms_body
        }

    # 10. Robots.txt
    if clean_path == "robots.txt":
        robots_txt = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\nLLMs-Txt: {base_url}/llms.txt\n"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "public, max-age=86400"
            },
            "body": robots_txt
        }

    # 11. Default: SSR Web Interface
    stage_filter = query_params.get("stage")
    items = service.get_radar_items(stage=stage_filter)
    stage_counts = service.get_stage_breakdown()

    html = render_backlot_ui(
        items=items,
        current_stage=stage_filter,
        stage_counts=stage_counts,
        base_url=base_url
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "public, max-age=60, s-maxage=300"
        },
        "body": html
    }
