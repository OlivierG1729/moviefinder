
############################
# Searching tmdb movies    #
#                          #
# Last update : 2025/08/24 #
############################

import streamlit as st
import requests
from typing import Optional

IMG = "https://image.tmdb.org/t/p/w342"

def poster_for(title: str, year: Optional[int] = None) -> Optional[str]:
    api_key = st.secrets.get("TMDB_API_KEY")
    if not api_key:
        return None
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
            return None
        p = res[0].get("poster_path")
        return f"{IMG}{p}" if p else None
    except Exception:
        return None
