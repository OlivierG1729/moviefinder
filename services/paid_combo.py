
############################
# Paid combo               #
#                          #
# Last update : 2025/08/25 #
############################


from typing import List
from .models import Movie
from . import (
    paid_dynamic,
    paid_itunes,
    paid_google_play,
    paid_amazon,
    paid_rakuten,
)


def search(
    query: str,
    max_results: int = 20,
    country: str = "FR",
    include_subscriptions: bool = False,
) -> List[Movie]:
    """Aggregate paid offers from various providers.

    The dynamic provider (JustWatch) is queried first, then direct
    store lookups such as iTunes, Google Play, Amazon/Prime Video and
    Rakuten. Results are deduplicated based on their URL.
    """

    offers: List[Movie] = []
    seen_urls = set()

    def add(items: List[Movie]) -> None:
        for it in items:
            url = it.stream_url
            if url and url not in seen_urls:
                offers.append(it)
                seen_urls.add(url)

    add(
        paid_dynamic.search(
            query,
            max_results=max_results,
            country=country,
            include_subscriptions=include_subscriptions,
        )
    )

    add(paid_itunes.search(query, max_results=max_results, country=country))
    add(paid_google_play.search(query, country=country))
    add(paid_amazon.search(query, country=country))
    add(paid_rakuten.search(query, country=country))

    return offers[:max_results]
