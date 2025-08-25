
############################
# Archives                 #
#                          #
# Last update : 2025/08/24 #
############################


import requests
from typing import List
from .models import Movie

SEARCH_URL = "https://archive.org/advancedsearch.php"

def _mediatype_clause(mode: str) -> str:
    """
    'films'  -> mediatype:(movies)
    'autres' -> -mediatype:(movies)
    'tout'   -> pas de filtre mediatype
    """
    m = (mode or "films").lower()
    if m == "films":
        return "AND mediatype:(movies)"
    if m == "autres":
        return "AND -mediatype:(movies)"
    return ""  # tout

def search(query: str, max_results: int = 20, mode: str = "films") -> List[Movie]:
    q = f"({query}) {_mediatype_clause(mode)}".strip()
    params = {
        "q": q,
        "fl[]": ["identifier", "title", "description", "year", "downloads", "mediatype"],
        "rows": max_results,
        "page": 1,
        "output": "json",
        "sort[]": ["downloads desc"],
    }
    data = requests.get(SEARCH_URL, params=params, timeout=20).json()
    docs = data.get("response", {}).get("docs", [])
    out: List[Movie] = []
    for d in docs:
        identifier = d.get("identifier")
        title = d.get("title") or identifier
        try:
            year = int(d.get("year")) if d.get("year") else None
        except Exception:
            year = None
        page = f"https://archive.org/details/{identifier}"
        out.append(Movie(
            title=title,
            year=year,
            description=d.get("description"),
            poster_url=f"https://archive.org/services/img/{identifier}",
            stream_url=page,
            download_url=page,
            source=f"Archive.org ({d.get('mediatype','')})",
            extra={"identifier": identifier},
        ))
    return out
