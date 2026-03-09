import requests
import json
import re
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from ....shared.logger import get_logger

logger = get_logger(__name__)
REQUEST_TIMEOUT_SECONDS = 10
LETTERBOXD_BASE_URL = "https://letterboxd.com"


def _normalize_text(text: str) -> str:
    return text.replace("\xa0", " ").replace("Â", "").strip()


def _extract_numeric_rating(raw_text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)", raw_text or "")
    if not match:
        return None

    try:
        return float(match.group(1))
    except ValueError:
        return None


def _resolve_film_url(movie_name: str) -> str | None:
    slug = movie_name.lower().replace(" ", "-")
    direct_url = f"{LETTERBOXD_BASE_URL}/film/{slug}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        direct_response = requests.get(direct_url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        if direct_response.status_code == 200:
            return direct_url
    except requests.RequestException:
        pass

    search_url = f"{LETTERBOXD_BASE_URL}/search/{quote_plus(movie_name)}/"
    try:
        search_response = requests.get(search_url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        if search_response.status_code != 200:
            return None

        soup = BeautifulSoup(search_response.text, "html.parser")
        for anchor in soup.select("ul.results li.film a[href], .results li a[href]"):
            href = anchor.get("href")
            if not href or "/film/" not in href:
                continue
            return urljoin(LETTERBOXD_BASE_URL, href)
    except requests.RequestException:
        return None

    return None


def _extract_letterboxd_rating(soup: BeautifulSoup, movie_obj: dict) -> float | None:
    rating = _extract_numeric_rating(str(movie_obj.get("aggregateRating", {}).get("ratingValue", "")))
    if rating is not None:
        return rating

    rating_node = soup.select_one("meta[name='twitter:data2']")
    if rating_node and rating_node.get("content"):
        rating = _extract_numeric_rating(rating_node.get("content", ""))
        if rating is not None:
            return rating

    rating_node = soup.select_one("[itemprop='ratingValue'], .average-rating")
    if rating_node:
        rating = _extract_numeric_rating(rating_node.get_text(" ", strip=True))
        if rating is not None:
            return rating

    return None


def _extract_review_snippets(soup: BeautifulSoup, limit: int = 5) -> list[str]:
    # Letterboxd film pages render "popular reviews" as ordered production-viewing cards.
    primary_cards = soup.select("article.production-viewing.-viewing.js-production-viewing")
    fallback_selectors = [
        ".js-review .body-text p",
        ".body-text p",
    ]

    snippets: list[str] = []
    seen: set[str] = set()

    for card in primary_cards:
        paragraph = card.select_one(".body-text p")
        if not paragraph:
            continue

        text = _normalize_text(paragraph.get_text(" ", strip=True))
        if not text or text in seen:
            continue

        seen.add(text)
        snippets.append(text)
        if len(snippets) >= limit:
            return snippets

    for selector in fallback_selectors:
        for paragraph in soup.select(selector):
            text = _normalize_text(paragraph.get_text(" ", strip=True))
            if not text or text in seen:
                continue

            seen.add(text)
            snippets.append(text)
            if len(snippets) >= limit:
                return snippets

    return snippets

def scrape_letterboxd_json(movie_name: str):
    url = _resolve_film_url(movie_name)
    if not url:
        logger.info("Letterboxd URL could not be resolved for %s", movie_name)
        return None

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        logger.info("Letterboxd lookup failed for %s with status %s", movie_name, response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag or not script_tag.text:
            logger.info("Letterboxd JSON-LD not found for %s", movie_name)
            return None

        json_text = script_tag.text.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "").strip()
        data = json.loads(json_text)
        
        # 1. Normalize to a list just in case it returns a single dict
        if isinstance(data, dict):
            data = [data]
            
        # 2. Extract the specific dictionary that contains the Movie data
        movie_obj = next((item for item in data if item.get("@type") == "Movie"), {})
        reviews = _extract_review_snippets(soup)
        rating = _extract_letterboxd_rating(soup, movie_obj)

        return {
            "title": movie_obj.get("name"),
            "rating": rating,
            "url": url,
            "reviews": reviews,
        }
        
    except Exception as e:
        logger.exception("Letterboxd extraction failed for %s: %s", movie_name, e)
        return None

