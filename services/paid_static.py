
############################
# Paid static              #
#                          #
# Last update : 2025/08/25 #
############################

# services/paid_static.py
import requests
from typing import List
from .models import Movie

def search(query: str, max_results: int = 6, country: str = "FR") -> List[Movie]:
    q = requests.utils.quote(query)
    links = [
        (f"https://www.justwatch.com/{country.lower()}/recherche?q={q}", "JustWatch (recherche)"),
        (f"https://www.youtube.com/results?search_query={q}%20film%20louer%20acheter", "YouTube (louer/acheter)"),
        (f"https://tv.apple.com/search?term={q}", "Apple TV (recherche)"),
        (f"https://www.primevideo.com/search?phrase={q}", "Prime Video (recherche)"),
        (f"https://rakuten.tv/fr/search?query={q}", "Rakuten TV (recherche)"),
        (f"https://www.canalvod.com/search/{q}", "CANAL VOD (recherche)"),
    ]
    out: List[Movie] = []
    for url, label in links[:max_results]:
        out.append(Movie(
            title=f"→ {label}",
            description="Liens génériques pour explorer manuellement si JustWatch ne remonte rien.",
            stream_url=url,
            source="Options payantes (fallback)",
        ))
    return out

