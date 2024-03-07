from __future__ import annotations

# python built-in imports
from dataclasses import dataclass
from datetime import date


@dataclass
class Dummy:
    app: str
    rating: float
    reviews: int
    size: str
    installs: str
    type: str
    price: int
    content_rating: str
    genres: str
    last_updated: date
