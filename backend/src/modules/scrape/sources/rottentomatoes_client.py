from __future__ import annotations

import json
import re

import requests
from bs4 import BeautifulSoup

from ....shared.logger import get_logger

logger = get_logger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REQUEST_TIMEOUT_SECONDS = 6


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return slug


def fetch_rotten_tomatoes_reviews(movie_name: str, limit: int = 10) -> dict:
    slug = _slugify(movie_name)
    url = f"https://www.rottentomatoes.com/m/{slug}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return {"reviews": [], "rating": None, "url": None}

        soup = BeautifulSoup(response.text, "html.parser")
        reviews: list[dict] = []
        seen: set[str] = set()
        rating = None
        consensus = None

        props_tag = soup.find("script", {"data-json": "props"})
        if props_tag and props_tag.text:
            try:
                props = json.loads(props_tag.text)
                media = props.get("media", {})
                score_value = media.get("tomatometerScore", {}).get("value")
                if isinstance(score_value, (int, float)):
                    rating = round(float(score_value) / 10, 2)

                raw_consensus = media.get("criticsConsensus") or media.get("consensus")
                if isinstance(raw_consensus, str) and raw_consensus.strip():
                    consensus = raw_consensus.strip()
            except (json.JSONDecodeError, TypeError):
                pass

        for quote_node in soup.select("[data-qa='review-quote'], .review_quote, .the_review"):
            text = quote_node.get_text(" ", strip=True)
            if not text or text in seen:
                continue

            seen.add(text)
            parent = quote_node.parent
            author_node = None
            if parent:
                author_node = parent.select_one("[data-qa='review-critic'], .critic_name, .display-name")

            reviews.append(
                {
                    "source": "Rotten Tomatoes",
                    "author": author_node.get_text(" ", strip=True) if author_node else "Rotten Tomatoes Critic",
                    "text": text,
                    "url": url,
                    "rating": None,
                }
            )
            if len(reviews) >= limit:
                break

        if not reviews and consensus:
            reviews.append(
                {
                    "source": "Rotten Tomatoes",
                    "author": "Rotten Tomatoes Consensus",
                    "text": consensus,
                    "url": url,
                    "rating": None,
                }
            )

        return {"reviews": reviews, "rating": rating, "url": url if reviews else None}
    except requests.RequestException as exc:
        logger.info("Rotten Tomatoes request failed for %s: %s", movie_name, exc)
        return {"reviews": [], "rating": None, "url": None}
