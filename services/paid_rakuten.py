############################
# Paid Rakuten             #
#                          #
# Last update : 2025/08/25 #
############################

import requests
from typing import List
from .models import Movie


def search(query: str, max_results: int = 1, country: str = "FR") -> List[Movie]:
    """Return a Rakuten TV search link.

    No open Rakuten TV API is available without authentication,
    thus we provide a search URL that points to the Rakuten TV catalog.
    """
    q = requests.utils.quote(query)
    base = "www.rakuten.tv"
    url = f"https://{base}/{country.lower()}/search?query={q}"
    return [
        Movie(
            title=f"→ Rakuten TV : {query}",
            description="Recherche Rakuten TV (achat/location)",
            stream_url=url,
            source="Rakuten TV",
        )
    ]
