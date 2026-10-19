"""Backlot Wire & Multi-Domain SEO, RSS Syndication, and IndexNow Suite."""

import html
import json
import logging
import urllib.request
import time
from email.utils import formatdate
from typing import List, Dict, Any, Optional
from src.core.models import FeedItem

logger = logging.getLogger(__name__)

INDEXNOW_KEY = "b4c107e9d84e4912b52e0a77f98cb123"

def escape_xml(s: str) -> str:
    """Escapes XML entities safely."""
    if not s:
        return ""
    return html.escape(s, quote=True).replace("'", "&apos;")


def generate_rss_feed(items: List[FeedItem], base_url: str = "https://backlotwire.com") -> str:
    """Generates a valid RSS 2.0 XML string with media enclosures and stage categories."""
    base_url = base_url.rstrip("/")
    now_rfc822 = formatdate(time.time(), usegmt=True)

    items_xml: List[str] = []
    for it in items[:40]:
        title = escape_xml(it.title)
        link = escape_xml(it.link)
        guid = escape_xml(f"backlotwire:intel:{it.id}")
        source_name = escape_xml(it.source)
        summary = escape_xml(it.summary)
        stage_name = escape_xml(it.stage.value if it.stage else "DEVELOPMENT")

        # RFC 822 pubDate
        pub_date = now_rfc822
        if it.pub_date_iso:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(it.pub_date_iso)
                pub_date = formatdate(dt.timestamp(), usegmt=True)
            except Exception:
                pub_date = now_rfc822

        enclosure_xml = ""
        if it.image_url:
            img_url = escape_xml(it.image_url)
            enclosure_xml = f'<enclosure url="{img_url}" length="0" type="image/jpeg" />'

        items_xml.append(f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid isPermaLink="false">{guid}</guid>
            <pubDate>{pub_date}</pubDate>
            <category>{stage_name}</category>
            <source url="{link}">{source_name}</source>
            <description>{summary}</description>
            {enclosure_xml}
        </item>""")

    items_joined = "\n".join(items_xml)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Backlot Wire — Film &amp; TV Production Radar &amp; Greenlight Feed</title>
    <link>{base_url}</link>
    <description>Verified film and television trade reports tracking greenlights, filming, casting, and release dates with zero fluff.</description>
    <language>en-US</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
    <atom:link href="{base_url}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
        <url>{base_url}/assets/mark.jpg</url>
        <title>Backlot Wire</title>
        <link>{base_url}</link>
    </image>
{items_joined}
  </channel>
</rss>"""


def generate_sitemap_xml(base_url: str = "https://backlotwire.com") -> str:
    """Generates a standard XML sitemap covering canonical hubs and stage filters."""
    base_url = base_url.rstrip("/")
    now_date = time.strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{base_url}/", "changefreq": "hourly", "priority": "1.0"},
        {"loc": f"{base_url}/?stage=GREENLIT", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{base_url}/?stage=FILMING", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{base_url}/?stage=PRE_PRODUCTION", "changefreq": "hourly", "priority": "0.8"},
        {"loc": f"{base_url}/?stage=POST_PRODUCTION", "changefreq": "hourly", "priority": "0.8"},
        {"loc": f"{base_url}/?stage=RELEASE_SCHEDULED", "changefreq": "daily", "priority": "0.8"},
        {"loc": f"{base_url}/?stage=CANCELED", "changefreq": "weekly", "priority": "0.6"},
        {"loc": f"{base_url}/rss.xml", "changefreq": "hourly", "priority": "0.7"},
        {"loc": f"{base_url}/llms.txt", "changefreq": "daily", "priority": "0.5"},
    ]

    xml_entries = []
    for u in urls:
        xml_entries.append(f"""  <url>
    <loc>{escape_xml(u["loc"])}</loc>
    <lastmod>{now_date}</lastmod>
    <changefreq>{u["changefreq"]}</changefreq>
    <priority>{u["priority"]}</priority>
  </url>""")

    joined = "\n".join(xml_entries)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{joined}
</urlset>"""


def generate_llms_txt(base_url: str = "https://backlotwire.com") -> str:
    """Generates an llms.txt document for AI search engines and research crawlers."""
    base_url = base_url.rstrip("/")
    return f"""# Backlot Wire — Film & TV Production Radar & Intelligence Wire

> Backlot Wire ({base_url}) is a zero-fluff entertainment intelligence platform tracking Hollywood features, streaming series, and network orders from greenlight to theatrical release.

## Core Hubs & Canonical Routes

- **Homepage & Main Dispatch Desk (`/`)**: Real-time aggregated trade wire tracking active studio productions across Warner Bros., Universal, Paramount, Disney, Netflix, Sony, Apple, and A24.
- **Greenlit & Orders (`/?stage=GREENLIT`)**: Confirmed script greenlights, series commissions, and franchise renewals.
- **Filming & On-Stage (`/?stage=FILMING`)**: Active principal photography dispatches and soundstage production tracking.
- **Casting & Attachments (`/?stage=PRE_PRODUCTION`)**: Director attachments, showrunners, and leading talent casting announcements.
- **Post-Production (`/?stage=POST_PRODUCTION`)**: Editing, VFX, sound mixing, and festival preview tracking.
- **Release Calendar (`/?stage=RELEASE_SCHEDULED`)**: Official studio theatrical releases, premiere dates, and streaming rollout schedules.
- **Cancellations & Shelved (`/?stage=CANCELED`)**: Studio write-downs, series cancellations, and shelved projects.

## Syndication & Machine-Readable Feeds

- **RSS 2.0 Syndicated Feed**: `{base_url}/rss.xml` (also available via `/feed.xml`, `/rss`, `/feed`)
- **JSON Feed API**: `{base_url}/api/feed` (supports `?stage=` query parameter)
- **Stage Breakdown Counts**: `{base_url}/api/stages`
- **Sitemap**: `{base_url}/sitemap.xml`
- **IndexNow Verification**: `{base_url}/{INDEXNOW_KEY}.txt`

## Editorial Integrity & Aggregation Protocol

- **Curated Trade Sources Only**: Aggregates directly from verified primary Hollywood trade bureaus (*Deadline*, *Variety*, *The Hollywood Reporter*) and validated against the TMDb film index.
- **Zero Clickbait**: Strips out sensationalist editorial speculation, celebrity gossip, and social media fan theories. Focuses strictly on industrial production facts.
- **Privacy Telemetry**: GDPR-salted visitor hashing without third-party tracking cookies or ad pixels.

## Contact & Governance

- Website: {base_url}
- Publisher: Ouroborean Software Ltd (UK Company No. 17501725)
- Support: support@backlotwire.com
"""


def submit_indexnow(base_url: str = "https://backlotwire.com", host: str = "backlotwire.com", urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """Submits URLs to IndexNow search engine protocol (Bing, Yandex, Seznam)."""
    base_url = base_url.rstrip("/")
    try:
        if not urls:
            urls = [
                f"{base_url}/",
                f"{base_url}/?stage=GREENLIT",
                f"{base_url}/?stage=FILMING",
                f"{base_url}/?stage=PRE_PRODUCTION",
                f"{base_url}/?stage=POST_PRODUCTION",
                f"{base_url}/?stage=RELEASE_SCHEDULED",
                f"{base_url}/?stage=CANCELED",
                f"{base_url}/rss.xml",
                f"{base_url}/sitemap.xml",
                f"{base_url}/llms.txt",
            ]

        payload = json.dumps({
            "host": host,
            "key": INDEXNOW_KEY,
            "keyLocation": f"{base_url}/{INDEXNOW_KEY}.txt",
            "urlList": urls
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "BacklotWire-IndexNow/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            resp_code = response.getcode()

        logger.info(f"IndexNow submission succeeded: {len(urls)} URLs to {host}, code {resp_code}")
        return {"success": True, "host": host, "submitted_urls": len(urls), "indexnow_response_code": resp_code}
    except Exception as ex:
        logger.warning(f"IndexNow submission failed: {ex}")
        return {"success": False, "host": host, "error": str(ex)}
