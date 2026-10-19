from typing import Optional, Dict, Any
from src.domains.entertainment.config import ENTERTAINMENT_CONFIG
from src.domains.entertainment.service import EntertainmentService

class DomainRegistry:
    def __init__(self):
        self.entertainment_service = EntertainmentService()
        self.host_map: Dict[str, str] = {}

        # Register Backlot Wire hosts
        for h in ENTERTAINMENT_CONFIG.hosts:
            self.host_map[h.lower()] = "entertainment"

    def resolve_domain(self, host: Optional[str]) -> str:
        """Resolve incoming HTTP Host header to a domain identifier."""
        if not host:
            return "entertainment"
        clean_host = host.split(":")[0].lower()
        return self.host_map.get(clean_host, "entertainment")

    def get_service(self, domain_id: str) -> Any:
        if domain_id == "entertainment":
            return self.entertainment_service
        # Fallback to entertainment
        return self.entertainment_service

registry = DomainRegistry()
