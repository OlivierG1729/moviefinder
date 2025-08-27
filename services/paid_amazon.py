############################
# Paid Amazon              #
#                          #
# Last update : 2025/08/25 #
############################

import requests
from typing import List
from .models import Movie


def search(query: str, max_results: int = 1, country: str = "FR") -> List[Movie]:
    """Return an Amazon/Prime Video search link.

    Amazon does not provide a simple unauthenticated API for Prime Video,
    so we return a search page URL as a fallback.
    """
    q = requests.utils.quote(query)
    domain = "www.primevideo.com"
    url = f"https://{domain}/search?phrase={q}"
    return [
        Movie(
            title=f"→ Prime Video : {query}",
            description="Recherche Prime Video (achat/location)",
            stream_url=url,
            source="Amazon Prime Video",
        )
    ]
