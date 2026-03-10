import requests
import json
import re
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from ....shared.logger import get_logger

logger = get_logger(__name__)
REQUEST_TIMEOUT_SECONDS = 10
LETTERBOXD_BASE_URL = "https://letterboxd.com"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
FALLBACK_HOME_TITLES = [
    "The Dark Knight",
    "Parasite",
    "The Godfather",
    "The Godfather Part II",
    "12 Angry Men",
    "Seven Samurai",
    "Spirited Away",
    "The Lord of the Rings: The Return of the King",
    "In the Mood for Love",
    "Portrait of a Lady on Fire",
    "Goodfellas",
    "Interstellar",
    "The Shawshank Redemption",
    "Whiplash",
    "City of God",
]


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


def _request_html(url: str) -> BeautifulSoup | None:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return None
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException:
        return None


def _extract_film_entries(soup: BeautifulSoup, limit: int = 10) -> list[dict]:
    entries: list[dict] = []
    seen: set[str] = set()

    film_items = soup.select("ul.poster-list li.poster-container")

    for item in film_items:
        poster = item.select_one("div.film-poster")
        if not poster:
            continue

        title = _normalize_text(poster.get("data-film-name") or "")
        if not title:
            img = item.select_one("img[alt]")
            if img and img.get("alt"):
                title = _normalize_text(img.get("alt"))

        slug = poster.get("data-film-slug") or ""
        if not slug:
            link = item.select_one("a[href*='/film/']")
            href = link.get("href") if link else None
            if href and "/film/" in href:
                slug = href.split("/film/")[-1].strip("/")

        if not title or title.lower() in seen:
            continue

        seen.add(title.lower())
        film_url = f"{LETTERBOXD_BASE_URL}/film/{slug}/" if slug else None
        poster_url = None
        image = item.select_one("img")
        if image and image.get("src"):
            src = image.get("src")
            poster_url = src if src.startswith("http") else urljoin(LETTERBOXD_BASE_URL, src)

        entries.append(
            {
                "title": title,
                "letterboxd_url": film_url,
                "poster_url": poster_url,
            }
        )

        if len(entries) >= limit:
            break

    return entries


def _get_director_film_titles_from_wikidata(director_name: str, max_titles: int = 40) -> list[str]:
    # Fallback source when Letterboxd director pages are blocked by anti-bot protections.
    query = f'''
    SELECT DISTINCT ?filmLabel WHERE {{
      ?person wdt:P31 wd:Q5 ; rdfs:label "{director_name}"@en .
      ?film wdt:P31/wdt:P279* wd:Q11424 ; wdt:P57 ?person .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    '''

    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "TheCriticQue/1.0 (letterboxd fallback)",
    }

    try:
        response = requests.get(
            WIKIDATA_SPARQL_URL,
            params={"format": "json", "query": query},
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    titles: list[str] = []
    seen: set[str] = set()

    for row in data.get("results", {}).get("bindings", []):
        label = row.get("filmLabel", {}).get("value", "").strip()
        if not label:
            continue

        key = label.lower()
        if key in seen:
            continue

        seen.add(key)
        titles.append(label)
        if len(titles) >= max_titles:
            break

    return titles


def _fetch_letterboxd_rating_for_title(title: str) -> dict | None:
    data = scrape_letterboxd_json(title)
    if not data:
        return None

    rating = data.get("rating")
    url = data.get("url")
    normalized_title = data.get("title") or title

    if rating is None:
        return None

    return {
        "title": normalized_title,
        "letterboxd_url": url,
        "poster_url": data.get("poster_url"),
        "rating": float(rating),
    }


def _rank_titles_by_letterboxd(candidate_titles: list[str], limit: int) -> list[dict]:
    if not candidate_titles:
        return []

    ranked_items: list[dict] = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_fetch_letterboxd_rating_for_title, title) for title in candidate_titles]
        for future in as_completed(futures):
            item = future.result()
            if item:
                ranked_items.append(item)

    ranked_items.sort(key=lambda item: item["rating"], reverse=True)

    # Keep API shape similar to the main list endpoint while preserving rating for UI use.
    return ranked_items[:limit]


def _rank_director_titles_by_letterboxd(director_name: str, limit: int) -> list[dict]:
    candidate_titles = _get_director_film_titles_from_wikidata(director_name)
    return _rank_titles_by_letterboxd(candidate_titles, limit)


def _resolve_director_url(director_name: str) -> str | None:
    slug = director_name.lower().replace(" ", "-")
    direct_url = f"{LETTERBOXD_BASE_URL}/director/{slug}/"
    soup = _request_html(direct_url)
    if soup is not None:
        return direct_url

    search_url = f"{LETTERBOXD_BASE_URL}/search/{quote_plus(director_name)}/"
    search_soup = _request_html(search_url)
    if search_soup is None:
        return None

    for anchor in search_soup.select("a[href^='/director/']"):
        href = anchor.get("href")
        if not href:
            continue
        return urljoin(LETTERBOXD_BASE_URL, href)

    return None


def get_top_movies(limit: int = 10) -> list[dict]:
    # Letterboxd's all-time highest-rated list is the best "top movies" source for a home page.
    top_url = f"{LETTERBOXD_BASE_URL}/films/by/rating/"
    soup = _request_html(top_url)
    if soup is None:
        logger.info("Could not fetch Letterboxd top movies page.")
        return _rank_titles_by_letterboxd(FALLBACK_HOME_TITLES, limit)

    entries = _extract_film_entries(soup, limit=limit)
    if entries:
        return entries

    return _rank_titles_by_letterboxd(FALLBACK_HOME_TITLES, limit)


def get_top_movies_by_director(director_name: str, limit: int = 10) -> list[dict]:
    director_url = _resolve_director_url(director_name)
    if not director_url:
        logger.info("Could not resolve director URL for %s", director_name)
        return _rank_director_titles_by_letterboxd(director_name, limit)

    ranked_url = director_url.rstrip("/") + "/by/rating/"
    soup = _request_html(ranked_url)
    if soup is None:
        return _rank_director_titles_by_letterboxd(director_name, limit)

    entries = _extract_film_entries(soup, limit=limit)
    if entries:
        return entries

    return _rank_director_titles_by_letterboxd(director_name, limit)


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
        poster_url = None

        poster_node = soup.select_one("meta[property='og:image']")
        if poster_node and poster_node.get("content"):
            raw_poster = poster_node.get("content")
            poster_url = raw_poster if raw_poster.startswith("http") else urljoin(LETTERBOXD_BASE_URL, raw_poster)

        return {
            "title": movie_obj.get("name"),
            "rating": rating,
            "url": url,
            "poster_url": poster_url,
            "reviews": reviews,
        }
        
    except Exception as e:
        logger.exception("Letterboxd extraction failed for %s: %s", movie_name, e)
        return None

