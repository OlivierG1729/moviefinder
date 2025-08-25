
############################
# Paid links               #
#                          #
# Last update : 2025/08/24 #
############################

import requests
from typing import List
from .models import Movie

def search(query: str, max_results: int = 4) -> List[Movie]:
    q = requests.utils.quote(query)

    # Remplacements / précisions :
    # - JustWatch (FR) : agrégateur de disponibilité (abos/achat/location) très fiable
    # - YouTube (location/achat) : Google a déplacé les films payants de Google Play vers YouTube / Google TV
    # - Apple TV & Prime Video : recherches directes
    links = [
        (f"https://www.justwatch.com/fr/recherche?q={q}", "JustWatch (FR)"),
        # YouTube Movies : on biaise la requête vers l'achat/location en FR
        (f"https://www.youtube.com/results?search_query={q}%20film%20louer%20acheter", "YouTube (louer/acheter)"),
        (f"https://tv.apple.com/search?term={q}", "Apple TV"),
        (f"https://www.primevideo.com/search?phrase={q}", "Prime Video"),
    ]

    return [Movie(
        title=f"→ {label}",
        description="Voir disponibilité payante",
        stream_url=url,
        source="Options payantes"
    ) for url, label in links[:max_results]]

