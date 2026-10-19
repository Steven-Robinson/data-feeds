import re
from typing import Optional, Tuple
from src.core.models import ProductionStage

# Regex patterns mapped to stages with priorities
STAGE_PATTERNS = [
    (
        ProductionStage.CANCELED,
        re.compile(r'\b(canceled|cancelled|scrapped|shelved|will not return|axed)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.RENEWED,
        re.compile(r'\b(renewed for season|renewed for|gets season \d|picked up for season|season \d renewal)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.GREENLIT,
        re.compile(r'\b(greenlit|greenlights|ordered to series|given series order|straight-to-series|series order|lands series|strikes deal for|lands deal|picked up by)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.FILMING,
        re.compile(r'\b(begins filming|starts filming|begins production|starts production|cameras rolling|currently filming|shooting begins|currently shooting|on set|production begins|production underway)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.POST_PRODUCTION,
        re.compile(r'\b(wraps filming|wraps production|filming concludes|finishes shooting|production wraps|in post-production)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.RELEASE_SCHEDULED,
        re.compile(r'\b(sets release date|premiere date|teaser trailer|official trailer|first look|first-look|release date|hitting theaters|streaming on|to premiere|set for)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.PRE_PRODUCTION,
        re.compile(r'\b(casts|casting|joins cast|to star in|in talks to star|sets director|taps director|hires director|taps|adds to cast|joins)\b', re.IGNORECASE)
    ),
    (
        ProductionStage.WRITING,
        re.compile(r'\b(writers room|penning script|hired to write|script stage|to write and direct|to pen|penned by)\b', re.IGNORECASE)
    ),
]

def classify_stage(title: str, summary: str = "") -> Optional[ProductionStage]:
    """Classifies an entertainment article into a production stage."""
    full_text = f"{title} {summary}"
    for stage, pattern in STAGE_PATTERNS:
        if pattern.search(full_text):
            return stage
    return None

def extract_title_candidate(headline: str) -> Optional[str]:
    """Extracts likely TV/film title from common trade headline syntax."""
    # Matches patterns like: 'Stranger Things' Season 5 Begins Filming...
    quoted = re.findall(r"['\"‘“](.*?)['\"’”]", headline)
    if quoted:
        # Return first reasonable title length
        for q in quoted:
            if 2 <= len(q) <= 60 and not any(kw in q.lower() for kw in ['exclusive', 'update', 'breaking']):
                return q.strip()

    # Matches: FX's Alien Series Sets Cast...
    match = re.search(r"\b([A-Z][A-Za-z0-9\s:]{2,30})\s+(?:Season|Series|Movie|Film|Reboot|Sequel)\b", headline)
    if match:
        return match.group(1).strip()

    return None
