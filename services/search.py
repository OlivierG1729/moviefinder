
############################
# Search                   #
#                          #
# Last update : 2025/08/24 #
############################

from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from .models import Movie
from . import archive_org, youtube_free, tmdb
from . import paid_combo as paid_links   # ⬅️ combo dynamique + fallback



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
    mode: str = "films",
    country: str = "FR",   # pays fixé ici
    include_subscriptions: bool = False,
) -> Dict[str, List[Movie]]:
    order = order or DEFAULT_ORDER
    results: Dict[str, List[Movie]] = {}

    active = []
    for key in order:
        if key not in PROVIDERS:
            continue
        if mode == "autres" and key in ("youtube", "paid"):
            continue
        active.append(key)

    with ThreadPoolExecutor(max_workers=min(8, len(active))) as ex:
        futures = {}
        for k in active:
            if k == "archive":
                futures[ex.submit(PROVIDERS[k], query, max_results, mode)] = k
            elif k == "paid":
                futures[ex.submit(PROVIDERS[k], query, max_results, country, include_subscriptions)] = k
            else:
                futures[ex.submit(PROVIDERS[k], query, max_results)] = k

        for fut in futures:
            key = futures[fut]
            try:
                lst = fut.result()
                if enrich_tmdb and key != "paid":
                    for m in lst:
                        poster, runtime = tmdb.info_for(m.title, m.year)
                        if not m.poster_url:
                            m.poster_url = poster
                        if runtime and not m.duration_minutes:
                            m.duration_minutes = runtime
                results[key] = lst
            except Exception:
                results[key] = []
    return results
