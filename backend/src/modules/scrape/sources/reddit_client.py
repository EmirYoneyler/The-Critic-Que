from __future__ import annotations

from urllib.parse import quote_plus

import requests

from ....shared.logger import get_logger

logger = get_logger(__name__)

REDDIT_BASE = "https://www.reddit.com"
HEADERS = {"User-Agent": "TheCriticQueBot/1.0"}
REQUEST_TIMEOUT_SECONDS = 6


def _safe_get(url: str) -> dict | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.info("Reddit request failed for %s: %s", url, exc)
        return None


def fetch_reddit_reviews(movie_name: str, limit: int = 10) -> dict:
    subreddits = ["movies", "TrueFilm", "moviecritic"]
    posts: list[dict] = []

    for subreddit in subreddits:
        query = quote_plus(f'title:"{movie_name}" review')
        search_url = (
            f"{REDDIT_BASE}/r/{subreddit}/search.json?"
            f"q={query}&restrict_sr=on&sort=top&t=all&limit=12"
        )
        payload = _safe_get(search_url)
        if not payload:
            continue

        posts.extend(payload.get("data", {}).get("children", []))

    if not posts:
        return {"reviews": [], "rating": None, "url": None}

    review_items: list[dict] = []
    upvote_ratios: list[float] = []
    seen_post_links: set[str] = set()
    title_key = movie_name.lower().strip()

    for post in posts:
        data = post.get("data", {})
        post_title = (data.get("title") or "").lower()
        if title_key not in post_title:
            continue

        permalink = data.get("permalink")
        if not permalink or permalink in seen_post_links:
            continue
        seen_post_links.add(permalink)

        upvote_ratio = data.get("upvote_ratio")
        if isinstance(upvote_ratio, (int, float)):
            upvote_ratios.append(float(upvote_ratio))

        comments_url = f"{REDDIT_BASE}{permalink}.json?sort=top&limit=20"
        comment_payload = _safe_get(comments_url)
        if not isinstance(comment_payload, list) or len(comment_payload) < 2:
            continue

        comments = comment_payload[1].get("data", {}).get("children", [])
        for comment in comments:
            comment_data = comment.get("data", {})
            body = (comment_data.get("body") or "").strip()
            author = comment_data.get("author") or ""
            if not body or body in {"[deleted]", "[removed]"} or author in {"[deleted]", "AutoModerator"}:
                continue

            review_items.append(
                {
                    "source": "Reddit",
                    "author": author,
                    "text": body,
                    "url": f"{REDDIT_BASE}{permalink}",
                    "rating": None,
                }
            )
            if len(review_items) >= limit:
                break

        if len(review_items) >= limit:
            break

    rating = None
    if upvote_ratios:
        rating = round((sum(upvote_ratios) / len(upvote_ratios)) * 10, 2)

    first_url = review_items[0]["url"] if review_items else None
    return {"reviews": review_items[:limit], "rating": rating, "url": first_url}
