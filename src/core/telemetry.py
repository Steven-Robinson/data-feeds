import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

BOT_SIGNATURES = (
    "bot", "crawler", "spider", "slurp", "headlesschrome", "phantomjs",
    "ahrefsbot", "semrushbot", "dotbot", "mj12bot", "googlebot", "bingbot",
    "uptime", "pingdom", "statuscake", "feedfetcher", "bluesky", "facebookexternalhit",
    "bytespider", "yandex", "sogou", "duckduckbot"
)

def evaluate_visitor(headers: Dict[str, str], payload: Dict[str, Any], client_ip: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluates whether an incoming telemetry ping is a genuine human or automated bot.
    Returns (is_human, structured_event).
    """
    ua = headers.get("user-agent", headers.get("User-Agent", ""))
    ua_lower = ua.lower()

    is_bot = any(sig in ua_lower for sig in BOT_SIGNATURES)
    is_webdriver = bool(payload.get("wd"))

    date_salt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ip_hash = hashlib.sha256(f"data-feeds-human-{date_salt}:{client_ip}".encode("utf-8")).hexdigest()[:16]

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "uip": ip_hash,
        "sid": str(payload.get("sid", ""))[:32],
        "path": str(payload.get("path", "/"))[:256],
        "ref": str(payload.get("ref", ""))[:256],
        "utm_source": str(payload.get("utm_source", ""))[:64],
        "utm_medium": str(payload.get("utm_medium", ""))[:64],
        "utm_campaign": str(payload.get("utm_campaign", ""))[:64],
        "screen": str(payload.get("screen", ""))[:32],
        "lang": str(payload.get("lang", ""))[:16],
        "ua": ua[:160],
        "is_bot": is_bot or is_webdriver
    }

    is_human = not (is_bot or is_webdriver)
    return is_human, event
