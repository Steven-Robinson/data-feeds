import re
import time
import hashlib
import logging
import html
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.models import FeedItem

logger = logging.getLogger(__name__)

class RSSEngine:
    def __init__(self, user_agent: str = "BacklotWire-Aggregator/1.0 (+https://backlotwire.com)"):
        self.user_agent = user_agent

    def clean_html(self, raw_html: str) -> str:
        """Strip HTML tags and unescape entities."""
        if not raw_html:
            return ""
        clean = html.unescape(raw_html)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def parse_pub_date(self, date_str: str) -> tuple[float, str]:
        """Convert RSS pubDate string into (epoch_seconds, iso_string)."""
        if not date_str:
            now = time.time()
            return now, datetime.fromtimestamp(now, timezone.utc).isoformat()
        try:
            dt = parsedate_to_datetime(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            epoch = dt.timestamp()
            return epoch, dt.isoformat()
        except Exception:
            now = time.time()
            return now, datetime.fromtimestamp(now, timezone.utc).isoformat()

    def extract_image_from_item(self, item: ET.Element) -> Optional[str]:
        """Extract media/enclosure image from XML element."""
        # Check enclosure
        enclosure = item.find('enclosure')
        if enclosure is not None and 'image' in enclosure.attrib.get('type', ''):
            return enclosure.attrib.get('url')

        # Check media:content or media:thumbnail namespaces
        namespaces = {
            'media': 'http://search.yahoo.com/mrss/',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }
        for tag in ['media:content', 'media:thumbnail']:
            el = item.find(tag, namespaces)
            if el is not None and el.attrib.get('url'):
                return el.attrib.get('url')

        # Check inside description or content:encoded for <img src="...">
        desc = item.find('description')
        if desc is not None and desc.text:
            m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc.text)
            if m:
                return m.group(1)

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
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/rss+xml, application/xml, text/xml, */*"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)
            channel = root.find("channel")
            if channel is None:
                channel = root

            now = time.time()
            compiled_exclusions = [
                re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                for term in (exclusions or [])
            ]
            compiled_inclusions = [
                re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                for term in (inclusions or [])
            ]

            for item in channel.findall("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                if title_el is None or link_el is None:
                    continue

                title = self.clean_html(title_el.text or "")
                link = (link_el.text or "").strip()
                if not title or not link:
                    continue

                desc_el = item.find("description")
                summary = self.clean_html(desc_el.text or "") if desc_el is not None else ""
                full_text = f"{title} {summary}"

                # Exclusion check
                if any(rgx.search(full_text) for rgx in compiled_exclusions):
                    continue

                # Inclusion check (if defined)
                if compiled_inclusions and not any(rgx.search(full_text) for rgx in compiled_inclusions):
                    continue

                pub_date_el = item.find("pubDate")
                pub_str = pub_date_el.text if pub_date_el is not None else ""
                pub_epoch, pub_iso = self.parse_pub_date(pub_str)

                if max_age_days > 0 and (now - pub_epoch) > (max_age_days * 86400):
                    continue

                item_id = hashlib.sha256(f"{source_name}:{link}".encode("utf-8")).hexdigest()[:16]
                image_url = self.extract_image_from_item(item)

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
