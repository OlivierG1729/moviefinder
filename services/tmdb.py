
############################
# Searching tmdb movies    #
#                          #
# Last update : 2025/08/24 #
############################

import streamlit as st
import requests
from typing import Optional, Tuple

IMG = "https://image.tmdb.org/t/p/w342"

def info_for(title: str, year: Optional[int] = None) -> Tuple[Optional[str], Optional[int]]:
    api_key = st.secrets.get("TMDB_API_KEY")
    if not api_key:
        return None, None
    params = {"api_key": api_key, "query": title}
    if year:
        params["year"] = year
    try:
        data = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params=params,
            timeout=20
        ).json()
        res = data.get("results", [])
        if not res:
            return None, None
        first = res[0]
        p = first.get("poster_path")
        poster = f"{IMG}{p}" if p else None
        movie_id = first.get("id")
        runtime = None
        if movie_id:
            try:
                details = requests.get(
                    f"https://api.themoviedb.org/3/movie/{movie_id}",
                    params={"api_key": api_key},
                    timeout=20,
                ).json()
                runtime = details.get("runtime")
            except Exception:
                runtime = None
        return poster, runtime
    except Exception:
        return None, None

def poster_for(title: str, year: Optional[int] = None) -> Optional[str]:
    poster, _ = info_for(title, year)
    return poster
