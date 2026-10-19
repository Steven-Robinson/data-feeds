from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import time

class ProductionStage(str, Enum):
    PITCH = "PITCH"                         # Pitched / In Development
    GREENLIT = "GREENLIT"                   # Officially Ordered / Greenlit
    WRITING = "WRITING"                     # Writers Room / Script Stage
    PRE_PRODUCTION = "PRE_PRODUCTION"       # Casting / Location Scouting
    FILMING = "FILMING"                     # Principal Photography
    POST_PRODUCTION = "POST_PRODUCTION"     # Editing / VFX / Reshoots
    RELEASE_SCHEDULED = "RELEASE_SCHEDULED" # Release Date Confirmed / Trailer Dropped
    RELEASED = "RELEASED"                   # Currently In Theaters / Streaming
    RENEWED = "RENEWED"                     # Picked up for next season
    CANCELED = "CANCELED"                   # Canceled / Shelved

@dataclass
class FeedItem:
    id: str
    title: str
    link: str
    source: str
    pub_epoch: float
    pub_date_iso: str
    summary: str = ""
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None  # "movie", "tv", etc.
    stage: Optional[ProductionStage] = None
    image_url: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_days(self) -> float:
        return (time.time() - self.pub_epoch) / 86400.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.stage:
            d["stage"] = self.stage.value
        return d

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()

@dataclass
class DomainConfig:
    domain_id: str
    name: str
    tagline: str
    hosts: List[str]
    theme_primary: str      # e.g. '#D4AF37'
    theme_accent: str       # e.g. '#E50914'
    theme_bg: str = "#090B0E"
    feeds: List[Dict[str, Any]] = field(default_factory=list)
    cache_ttl_seconds: int = 600
    seo_title_template: str = "{name} — Zero-Fluff Live Intelligence Wire"
    seo_desc_template: str = "Real-time, verified updates with zero clickbait. Powered by {name}."
