import os
import json
import urllib.request
import urllib.parse
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class TMDbClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_multi(self, query: str) -> List[Dict[str, Any]]:
        """Search both movies and TV series."""
        if not self.is_configured():
            return self._mock_search(query)

        try:
            params = urllib.parse.urlencode({
                "api_key": self.api_key,
                "query": query,
                "include_adult": "false"
            })
            url = f"{self.BASE_URL}/search/multi?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "BacklotWire/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("results", [])[:5]:
                media_type = item.get("media_type")
                if media_type not in ["movie", "tv"]:
                    continue

                title = item.get("name") if media_type == "tv" else item.get("title")
                release_date = item.get("first_air_date") if media_type == "tv" else item.get("release_date")
                poster_path = item.get("poster_path")

                results.append({
                    "id": item.get("id"),
                    "title": title,
                    "media_type": media_type,
                    "overview": item.get("overview", "")[:300],
                    "release_date": release_date,
                    "poster_url": f"{self.IMAGE_BASE}{poster_path}" if poster_path else None,
                    "backdrop_url": f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                    "vote_average": item.get("vote_average", 0.0)
                })
            return results
        except Exception as e:
            logger.warning(f"TMDb query failed: {e}")

        return self._mock_search(query)

    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """Fallback mock database when TMDB_API_KEY is not configured."""
        MOCK_CATALOG = [
            {
                "id": 66732,
                "title": "Stranger Things",
                "media_type": "tv",
                "overview": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl.",
                "release_date": "2016-07-15",
                "poster_url": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
                "vote_average": 8.6
            },
            {
                "id": 100088,
                "title": "The Last of Us",
                "media_type": "tv",
                "overview": "Twenty years after modern civilization has been destroyed, Joel is hired to smuggle Ellie, a 14-year-old girl, out of an oppressive quarantine zone.",
                "release_date": "2023-01-15",
                "poster_url": "https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2V7JMrRI.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/uDgy6hyPd82kOHh6I95FLtLnj6p.jpg",
                "vote_average": 8.6
            },
            {
                "id": 94997,
                "title": "House of the Dragon",
                "media_type": "tv",
                "overview": "The Targaryen dynasty is at the absolute apex of its power, with more than 15 dragons under their yoke. Most empires fall from without; Targaryens fall from within.",
                "release_date": "2022-08-21",
                "poster_url": "https://image.tmdb.org/t/p/w500/t9Xke5724fqW346KuDuIKqqAD05.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/etjA2oF0z0ojFk0g4UaCjU2vC94.jpg",
                "vote_average": 8.4
            },
            {
                "id": 106379,
                "title": "Fallout",
                "media_type": "tv",
                "overview": "The story of haves and have-nots in a world in which there's almost nothing left to have. 200 years after the apocalypse, gentle denizens of luxury fallout shelters leave to explore the irradiated wasteland.",
                "release_date": "2024-04-10",
                "poster_url": "https://image.tmdb.org/t/p/w500/AnsZuLp1y5lG86G0y0s9F2xQ2zM.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/mo0aA1zU2x1G6a0y0s9F2xQ2zM.jpg",
                "vote_average": 8.5
            },
            {
                "id": 414906,
                "title": "The Batman Part II",
                "media_type": "movie",
                "overview": "The sequel to Matt Reeves' 2022 noir detective film starring Robert Pattinson as Bruce Wayne / Batman.",
                "release_date": "2026-10-02",
                "poster_url": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
                "backdrop_url": None,
                "vote_average": 7.8
            }
        ]

        q_lower = query.lower()
        matches = [m for m in MOCK_CATALOG if q_lower in m["title"].lower()]
        return matches if matches else MOCK_CATALOG[:3]
