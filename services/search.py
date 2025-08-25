
############################
# Search                   #
#                          #
# Last update : 2025/08/24 #
############################

from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from .models import Movie
from . import archive_org, youtube_free, paid_links
from . import tmdb

PROVIDERS = {
    "archive": archive_org.search,
    "youtube": youtube_free.search,
    "paid": paid_links.search,
}
DEFAULT_ORDER = ["archive", "youtube", "paid"]

def run_search(
    query: str,
    max_results: int = 20,
    order: List[str] | None = None,
    enrich_tmdb: bool = True,
    mode: str = "films",  # 'films' | 'autres' | 'tout'
) -> Dict[str, List[Movie]]:
    order = order or DEFAULT_ORDER
    results: Dict[str, List[Movie]] = {}

    # Construction de la liste de providers actifs selon le mode
    active = []
    for key in order:
        if key not in PROVIDERS:
            continue
        if mode == "autres" and key in ("youtube", "paid"):
            # “Autres” = on exclut YouTube (orienté films) et payant
            continue
        active.append(key)

    # Requêtes en parallèle
    with ThreadPoolExecutor(max_workers=min(8, len(active))) as ex:
        futures = {}
        for k in active:
            if k == "archive":
                # Passer le mode au provider Archive.org pour filtrage par mediatype
                futures[ex.submit(PROVIDERS[k], query, max_results, mode)] = k
            else:
                futures[ex.submit(PROVIDERS[k], query, max_results)] = k

        for fut in futures:
            key = futures[fut]
            try:
                lst = fut.result()
                if enrich_tmdb and key != "paid":
                    for m in lst:
                        if not m.poster_url:
                            m.poster_url = tmdb.poster_for(m.title, m.year)
                results[key] = lst
            except Exception:
                results[key] = []
    return results
