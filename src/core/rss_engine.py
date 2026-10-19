import re
import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import feedparser
import httpx
from src.core.models import FeedItem

logger = logging.getLogger(__name__)

class RSSEngine:
    def __init__(self, user_agent: str = "DataFeedsBot/1.0 (+https://github.com/Steven-Robinson/data-feeds)"):
        self.user_agent = user_agent
        self.client = httpx.Client(
            headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
            timeout=10.0,
            follow_redirects=True
        )

    def clean_html(self, raw_html: str) -> str:
        """Strip HTML tags and unescape entities."""
        if not raw_html:
            return ""
        clean = re.sub(r'<[^>]+>', ' ', raw_html)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def parse_pub_date(self, entry: Any) -> tuple[float, str]:
        """Convert entry published date into (epoch_seconds, iso_string)."""
        pub_epoch = 0.0
        iso_str = ""

        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                pub_epoch = time.mktime(entry.published_parsed)
                dt = datetime.fromtimestamp(pub_epoch, timezone.utc)
                iso_str = dt.isoformat()
                return pub_epoch, iso_str
            except Exception:
                pass

        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                pub_epoch = time.mktime(entry.updated_parsed)
                dt = datetime.fromtimestamp(pub_epoch, timezone.utc)
                iso_str = dt.isoformat()
                return pub_epoch, iso_str
            except Exception:
                pass

        # Fallback to current time
        now = time.time()
        return now, datetime.fromtimestamp(now, timezone.utc).isoformat()

    def extract_image_url(self, entry: Any) -> Optional[str]:
        """Extract featured media/image from RSS enclosures or media tags."""
        # Check media:content or media:thumbnail
        if hasattr(entry, 'media_content') and entry.media_content:
            for m in entry.media_content:
                if 'url' in m and ('image' in m.get('type', '') or m['url'].endswith(('.jpg', '.png', '.webp'))):
                    return m['url']
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url')
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if 'image' in enc.get('type', ''):
                    return enc.get('href')
        return None

    def fetch_feed(
        self,
        url: str,
        source_name: str,
        max_age_days: float = 14.0,
        exclusions: Optional[List[str]] = None,
        inclusions: Optional[List[str]] = None
    ) -> List[FeedItem]:
        """Fetch and parse an RSS feed with deduplication and regex boundary filters."""
        items: List[FeedItem] = []
        try:
            resp = self.client.get(url)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch {url}: HTTP {resp.status_code}")
                return []

            parsed = feedparser.parse(resp.text)
            now = time.time()

            compiled_exclusions = [
                re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                for term in (exclusions or [])
            ]
            compiled_inclusions = [
                re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                for term in (inclusions or [])
            ]

            for entry in parsed.entries:
                title = self.clean_html(getattr(entry, 'title', ''))
                link = getattr(entry, 'link', '')
                if not title or not link:
                    continue

                summary = self.clean_html(getattr(entry, 'summary', '') or getattr(entry, 'description', ''))
                full_text = f"{title} {summary}"

                # Exclusion check
                if any(rgx.search(full_text) for rgx in compiled_exclusions):
                    continue

                # Inclusion check (if defined)
                if compiled_inclusions and not any(rgx.search(full_text) for rgx in compiled_inclusions):
                    continue

                pub_epoch, pub_iso = self.parse_pub_date(entry)
                if max_age_days > 0 and (now - pub_epoch) > (max_age_days * 86400):
                    continue

                # Unique content ID
                item_id = hashlib.sha256(f"{source_name}:{link}".encode('utf-8')).hexdigest()[:16]
                image_url = self.extract_image_url(entry)

                items.append(FeedItem(
                    id=item_id,
                    title=title,
                    link=link,
                    source=source_name,
                    pub_epoch=pub_epoch,
                    pub_date_iso=pub_iso,
                    summary=summary[:400],
                    image_url=image_url
                ))

        except Exception as e:
            logger.error(f"Error parsing feed {url}: {e}")

        return items
