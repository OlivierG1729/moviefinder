############################
# Paid iTunes              #
#                          #
# Last update : 2025/08/25 #
############################

import requests
from typing import List
from .models import Movie


def search(query: str, max_results: int = 20, country: str = "FR") -> List[Movie]:
    """Search Apple iTunes Store for paid movie offers.

    Parameters
    ----------
    query: str
        Movie title to search for.
    max_results: int, optional
        Maximum number of results to return.
    country: str, optional
        Two-letter country code used by the API.
    """
    q = requests.utils.quote(query)
    url = (
        "https://itunes.apple.com/search"
        f"?term={q}&media=movie&entity=movie&country={country}&limit={max_results}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
    except Exception:
        return []

    out: List[Movie] = []
    for it in data.get("results", [])[:max_results]:
        title = it.get("trackName") or query
        stream_url = it.get("trackViewUrl")
        if not stream_url:
            continue
        description = it.get("longDescription") or it.get("shortDescription")
        poster = it.get("artworkUrl100")
        year = None
        rel = it.get("releaseDate")
        if rel:
            try:
                year = int(rel[:4])
            except ValueError:
                pass
        out.append(
            Movie(
                title=title,
                year=year,
                description=description,
                poster_url=poster,
                stream_url=stream_url,
                source="Apple iTunes",
            )
        )
        if len(out) >= max_results:
            break
    return out
