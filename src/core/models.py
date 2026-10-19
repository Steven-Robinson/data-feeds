from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
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

class FeedItem(BaseModel):
    id: str
    title: str
    link: str
    source: str
    pub_epoch: float
    pub_date_iso: str
    summary: str = ""
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None  # "movie", "tv", "model", "drug", etc.
    stage: Optional[ProductionStage] = None
    image_url: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def age_days(self) -> float:
        return (time.time() - self.pub_epoch) / 86400.0

class DomainConfig(BaseModel):
    domain_id: str
    name: str
    tagline: str
    hosts: List[str]
    theme_primary: str      # e.g. '#D4AF37' (Hollywood Gold)
    theme_accent: str       # e.g. '#E50914' or '#38bdf8'
    theme_bg: str = "#0b0d12"
    feeds: List[Dict[str, Any]] = Field(default_factory=list)
    cache_ttl_seconds: int = 600
    seo_title_template: str = "{name} — Zero-Fluff Live Intelligence Wire"
    seo_desc_template: str = "Real-time, verified updates with zero clickbait. Powered by {name}."
