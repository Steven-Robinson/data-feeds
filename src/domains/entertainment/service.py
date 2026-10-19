import time
import logging
from typing import List, Dict, Any, Optional
from src.core.models import FeedItem, ProductionStage
from src.core.rss_engine import RSSEngine
from src.domains.entertainment.config import ENTERTAINMENT_CONFIG, EXCLUSION_KEYWORDS
from src.domains.entertainment.stage_classifier import classify_stage, extract_title_candidate
from src.domains.entertainment.tmdb import TMDbClient

logger = logging.getLogger(__name__)

class EntertainmentService:
    def __init__(self, tmdb_api_key: Optional[str] = None):
        self.config = ENTERTAINMENT_CONFIG
        self.rss = RSSEngine(user_agent="BacklotWire-Aggregator/1.0 (+https://backlotwire.com)")
        self.tmdb = TMDbClient(api_key=tmdb_api_key)
        self._cached_items: List[FeedItem] = []
        self._last_sync: float = 0.0

    def sync_feeds(self, force: bool = False) -> List[FeedItem]:
        """Fetch all trade feeds, parse production stages, and update cache."""
        now = time.time()
        if not force and self._cached_items and (now - self._last_sync) < self.config.cache_ttl_seconds:
            return self._cached_items

        all_items: List[FeedItem] = []
        seen_titles = set()

        for feed in self.config.feeds:
            feed_items = self.rss.fetch_feed(
                url=feed["url"],
                source_name=feed["name"],
                max_age_days=14.0,
                exclusions=EXCLUSION_KEYWORDS
            )

            for item in feed_items:
                # Deduplicate very similar headlines across Deadline/Variety
                norm_title = "".join(ch for ch in item.title.lower() if ch.isalnum())
                if norm_title in seen_titles:
                    continue
                seen_titles.add(norm_title)

                # Classify production stage
                item.stage = classify_stage(item.title, item.summary)
                item.entity_type = feed.get("type", "entertainment")

                # Try title candidate extraction
                candidate = extract_title_candidate(item.title)
                if candidate:
                    item.entity_name = candidate

                all_items.append(item)

        # Sort chronologically (newest first)
        all_items.sort(key=lambda x: x.pub_epoch, reverse=True)
        self._cached_items = all_items
        self._last_sync = now
        logger.info(f"Synced {len(all_items)} entertainment intelligence items.")
        return all_items

    def get_radar_items(self, stage: Optional[ProductionStage] = None) -> List[FeedItem]:
        """Retrieve items filtered optionally by production stage."""
        items = self.sync_feeds()
        if stage:
            return [it for it in items if it.stage == stage]
        return items

    def get_stage_breakdown(self) -> Dict[str, int]:
        """Count how many items currently occupy each production stage."""
        items = self.sync_feeds()
        counts: Dict[str, int] = {}
        for it in items:
            key = it.stage.value if it.stage else "GENERAL_NEWS"
            counts[key] = counts.get(key, 0) + 1
        return counts
