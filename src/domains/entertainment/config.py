from src.core.models import DomainConfig

ENTERTAINMENT_CONFIG = DomainConfig(
    domain_id="backlotwire",
    name="Backlot Wire",
    tagline="Film & Television Production Radar — Zero-Fluff Industry Intelligence",
    hosts=["backlotwire.com", "www.backlotwire.com", "luna.ouroborean.co.uk", "localhost:8000", "127.0.0.1:8000"],
    theme_primary="#D4AF37",  # Hollywood Cine-Gold
    theme_accent="#E50914",   # Studio Red
    theme_bg="#090B0E",       # Deep Backlot Charcoal
    cache_ttl_seconds=600,
    seo_title_template="Backlot Wire — Film & TV Production Radar | Greenlights, Filming & Release Updates",
    seo_desc_template="Real-time verified film & TV production updates. Track greenlights, filming schedules, casting, and release dates with zero clickbait.",
    feeds=[
        {
            "name": "Deadline TV",
            "url": "https://deadline.com/v/tv/feed/",
            "type": "tv"
        },
        {
            "name": "Deadline Film",
            "url": "https://deadline.com/v/film/feed/",
            "type": "film"
        },
        {
            "name": "Variety TV",
            "url": "https://variety.com/v/tv/feed/",
            "type": "tv"
        },
        {
            "name": "Variety Film",
            "url": "https://variety.com/v/film/feed/",
            "type": "film"
        },
        {
            "name": "The Hollywood Reporter",
            "url": "https://www.hollywoodreporter.com/c/movies/feed/",
            "type": "film"
        }
    ]
)

# Words to exclude (gossip, non-production lifestyle/fashion/awards party fluff)
EXCLUSION_KEYWORDS = [
    "red carpet fashion", "best dressed", "wardrobe malfunction", "divorce", "dating",
    "box office flop", "scandal", "real estate", "mansion", "arrested", "lawsuit settled",
    "feud", "ozempic", "diet secret", "horoscope"
]
