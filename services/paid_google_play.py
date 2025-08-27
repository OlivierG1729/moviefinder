############################
# Paid Google Play         #
#                          #
# Last update : 2025/08/25 #
############################

import requests
from typing import List
from .models import Movie


def search(query: str, max_results: int = 1, country: str = "FR") -> List[Movie]:
    """Return a Google Play Movies search link for the query.

    Google does not expose a public movies API without authentication.
    We therefore provide a direct search URL so the user can
    complete the purchase on Google Play manually.
    """
    q = requests.utils.quote(query)
    url = f"https://play.google.com/store/search?c=movies&q={q}&gl={country.upper()}"
    return [
        Movie(
            title=f"→ Google Play : {query}",
            description="Recherche Google Play (achat/location)",
            stream_url=url,
            source="Google Play",
        )
    ]
