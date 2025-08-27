
############################
# Paid dynamic             #
#                          #
# Last update : 2025/08/25 #
############################


from typing import List, Dict, Optional, Set
from .models import Movie
import logging
import requests

try:
    from justwatch import JustWatch
except Exception:
    JustWatch = None

logger = logging.getLogger(__name__)

MONETIZATION_PRIORITIES = ["buy", "rent", "flatrate", "ads", "free"]

def _best_offer_per_provider(offers: List[Dict]) -> Dict[int, Dict]:
    by_provider: Dict[int, Dict] = {}
    for off in offers or []:
        pid = off.get("provider_id")
        if pid is None:
            continue
        cur = by_provider.get(pid)
        if cur is None:
            by_provider[pid] = off
        else:
            def prio(o: Dict) -> int:
                try:
                    return MONETIZATION_PRIORITIES.index(o.get("monetization_type", "zzz"))
                except ValueError:
                    return 999
            if prio(off) < prio(cur):
                by_provider[pid] = off
    return by_provider

def _label_monetization(m: Optional[str]) -> str:
    return {"buy":"achat","rent":"location","flatrate":"abonnement","ads":"avec pub","free":"gratuit"}.get((m or "").lower(), m or "")

def search(
    query: str,
    max_results: int = 20,
    country: str = "FR",
    include_subscriptions: bool = False,
) -> List[Movie]:
    if not JustWatch:
        return []

    jw = JustWatch(country=country, api_domain="https://apiv2.justwatch.com")
    try:
        data = jw.search_for_item(query=query, content_types=["movie"])
    except requests.HTTPError as err:
        logger.exception("JustWatch HTTP error during search: %s", err)
        return []
    except Exception:
        return []

    items = data.get("items", []) if isinstance(data, dict) else []
    out: List[Movie] = []
    used_urls: Set[str] = set()

    try:
        providers_map = {p["id"]: p["clear_name"] for p in jw.get_providers()}
    except Exception:
        providers_map = {}

    for it in items[:8]:
        title = it.get("title") or query
        year = it.get("original_release_year") or None
        full_path = it.get("full_path")

        offers = it.get("offers")
        if offers is None:
            try:
                details = jw.get_title(content_type="movie", title_id=it.get("id"), language="fr")
                offers = details.get("offers", [])
                full_path = details.get("full_path", full_path)
            except requests.HTTPError as err:
                logger.exception("JustWatch HTTP error during title fetch: %s", err)
                return []
            except Exception:
                offers = []

        allowed = {"buy", "rent"} | ({"flatrate"} if include_subscriptions else set())
        offers = [
            o
            for o in (offers or [])
            if o.get("country") == country and o.get("monetization_type") in allowed
        ]
        if not offers:
            continue

        best = _best_offer_per_provider(offers)
        if not best:
            continue

        justwatch_title_url = f"https://www.justwatch.com{full_path}" if full_path else None

        for pid, off in best.items():
            prov_name = providers_map.get(pid, f"Plateforme {pid}")
            mono = _label_monetization(off.get("monetization_type"))
            urls = off.get("urls") or {}
            url = urls.get("standard_web") or off.get("standard_web_url") or justwatch_title_url
            if not url or url in used_urls:
                continue
            used_urls.add(url)

            out.append(Movie(
                title=title,
                year=year,
                description=f"Disponible sur {prov_name} – {mono}",
                stream_url=url,
                source=f"{prov_name} ({mono})",
                extra={"monetization": mono, "provider_id": pid},
            ))
            if len(out) >= max_results:
                return out
    return out
