from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from ....shared.logger import get_logger

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.metacritic.com/",
}
REQUEST_TIMEOUT_SECONDS = 6


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def fetch_metacritic_reviews(movie_name: str, limit: int = 10) -> dict:
    slug = _slugify(movie_name)
    url = f"https://www.metacritic.com/movie/{slug}/critic-reviews/"

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return {"reviews": [], "rating": None, "url": None}

        soup = BeautifulSoup(response.text, "html.parser")
        reviews: list[dict] = []
        seen: set[str] = set()
        rating = None

        score_node = soup.select_one(".product-reviews-score__card .c-siteReviewScore span")
        if score_node:
            score_match = re.search(r"(\d+(?:\.\d+)?)", score_node.get_text(" ", strip=True))
            if score_match:
                try:
                    raw_score = float(score_match.group(1))
                    # Metacritic critic score is typically out of 100.
                    rating = round(raw_score / 10, 2) if raw_score > 10 else raw_score
                except ValueError:
                    rating = None

        selectors = [
            ".review-card",
            ".review-card__quote",
            ".review-card__content",
        ]

        for selector in selectors:
            for quote_node in soup.select(selector):
                if selector == ".review-card":
                    quote = quote_node.select_one(".review-card__quote")
                    text = quote.get_text(" ", strip=True) if quote else ""
                    author_node = quote_node.select_one(".movie-review-footer__author-link, .movie-review-footer__author")
                else:
                    text = quote_node.get_text(" ", strip=True)
                    author_node = quote_node.find_parent().select_one(".movie-review-footer__author-link, .movie-review-footer__author") if quote_node.find_parent() else None

                if not text or text in seen:
                    continue

                seen.add(text)
                author = "Metacritic Critic"
                if author_node:
                    author = author_node.get_text(" ", strip=True)

                reviews.append(
                    {
                        "source": "Metacritic",
                        "author": author,
                        "text": text,
                        "url": url,
                        "rating": None,
                    }
                )
                if len(reviews) >= limit:
                    break
            if len(reviews) >= limit:
                break

        return {"reviews": reviews, "rating": rating, "url": url if reviews else None}
    except requests.RequestException as exc:
        logger.info("Metacritic request failed for %s: %s", movie_name, exc)
        return {"reviews": [], "rating": None, "url": None}
