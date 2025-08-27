
############################
# Paid combo               #
#                          #
# Last update : 2025/08/25 #
############################


# services/paid_combo.py
from typing import List
from .models import Movie
from . import paid_dynamic, paid_static

def search(query: str, max_results: int = 20, country: str = "FR") -> List[Movie]:
    """Combine JustWatch (réel) puis fallback liens de recherche si rien n'est trouvé."""
    dyn = paid_dynamic.search(query, max_results=max_results, country=country)
    if dyn:
        return dyn[:max_results]
    return paid_static.search(query, max_results=max_results, country=country)
