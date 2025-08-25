############################
# Searching youtube movies #
#                          #
# Last update : 2025/08/24 #
############################


import streamlit as st
import requests
from typing import List
from .models import Movie

API_URL = "https://www.googleapis.com/youtube/v3/search"

def search(query: str, max_results: int = 20) -> List[Movie]:
    api_key = st.secrets.get("YOUTUBE_API_KEY")
    if not api_key:
        return []
    params = {
        "part": "snippet",
        "q": query + " full movie",
        "type": "video",
        "maxResults": min(max_results, 50),
        "videoDuration": "long",
        "safeSearch": "moderate",
        "key": api_key,
    }
    data = requests.get(API_URL, params=params, timeout=20).json()
    out: List[Movie] = []
    for item in data.get("items", []):
        sn = item.get("snippet", {})
        vid = item.get("id", {}).get("videoId")
        if not vid:
            continue
        out.append(Movie(
            title=sn.get("title"),
            description=sn.get("description"),
            poster_url=sn.get("thumbnails", {}).get("high", {}).get("url"),
            stream_url=f"https://www.youtube.com/watch?v={vid}",
            source="YouTube (gratuit)",
            extra={"channel": sn.get("channelTitle")},
        ))
    return out
