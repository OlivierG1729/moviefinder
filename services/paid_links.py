
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
    links = [
        (f"https://www.justwatch.com/fr/recherche?q={q}", "JustWatch (FR)"),
        (f"https://tv.apple.com/search?term={q}", "Apple TV"),
        (f"https://play.google.com/store/search?q={q}&c=movies", "Google TV"),
        (f"https://www.primevideo.com/search?phrase={q}", "Prime Video"),
    ]
    return [Movie(
        title=f"→ {label}",
        description="Voir disponibilité payante",
        stream_url=url,
        source="Options payantes"
    ) for url, label in links[:max_results]]
