
############################
# Models                   #
#                          #
# Last update : 2025/08/24 #
############################


from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Movie:
    title: str
    year: Optional[int] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    stream_url: Optional[str] = None
    download_url: Optional[str] = None
    price: Optional[str] = None
    source: str = ""
    extra: Optional[Dict] = None
