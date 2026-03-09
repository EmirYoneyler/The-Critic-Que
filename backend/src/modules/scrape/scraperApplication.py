from concurrent.futures import ThreadPoolExecutor

from .sources.omdb_client import request_omdb_api
from .sources.letterboxd_client import scrape_letterboxd_json
from .sources.reddit_client import fetch_reddit_reviews
from .sources.rottentomatoes_client import fetch_rotten_tomatoes_reviews
from .sources.metacritic_client import fetch_metacritic_reviews
from ...shared.logger import get_logger

logger = get_logger(__name__)

class ScrapeApplication:

    @staticmethod
    def _get_omdb_rating(omdb_data: dict, source_name: str) -> float | None:
        ratings = omdb_data.get("Ratings", [])
        for item in ratings:
            if item.get("Source") != source_name:
                continue

            value = item.get("Value", "")
            if value.endswith("%"):
                try:
                    return round(float(value.replace("%", "")) / 10, 2)
                except ValueError:
                    return None

            if "/100" in value:
                try:
                    return round(float(value.split("/")[0]) / 10, 2)
                except ValueError:
                    return None

            if "/10" in value:
                try:
                    return float(value.split("/")[0])
                except ValueError:
                    return None

        metascore = omdb_data.get("Metascore")
        if source_name == "Metacritic" and metascore and metascore != "N/A":
            try:
                return round(float(metascore) / 10, 2)
            except ValueError:
                return None

        return None

    @staticmethod
    def fetch_movie_data(movie_name: str):
        omdb_data = request_omdb_api(movie_name)
        if not omdb_data:
            return None

        # Letterboxd is optional: OMDB data alone is enough to return a movie.
        letterboxd_data = scrape_letterboxd_json(movie_name)

        # add the letterboxd data to the omdb data and return it as a single dictionary
        if letterboxd_data:
            omdb_title = omdb_data.get("Title", "").lower()
            letterboxd_title = letterboxd_data.get("title", "").lower()

            if omdb_title == letterboxd_title:
                omdb_data["letterboxd_rating"] = letterboxd_data.get("rating")
            else:
                logger.info("Title mismatch between OMDB and Letterboxd for %s", movie_name)
                omdb_data["letterboxd_rating"] = letterboxd_data.get("rating")

            omdb_data["letterboxd_reviews"] = letterboxd_data.get("reviews", [])
            omdb_data["letterboxd_url"] = letterboxd_data.get("url")

        # Fetch external sources concurrently to avoid long end-to-end waits.
        with ThreadPoolExecutor(max_workers=3) as executor:
            reddit_future = executor.submit(fetch_reddit_reviews, movie_name)
            rt_future = executor.submit(fetch_rotten_tomatoes_reviews, movie_name)
            metacritic_future = executor.submit(fetch_metacritic_reviews, movie_name)

            reddit_data = reddit_future.result()
            rt_data = rt_future.result()
            metacritic_data = metacritic_future.result()

        external_reviews: list[dict] = []

        if letterboxd_data:
            for text in letterboxd_data.get("reviews", []):
                external_reviews.append(
                    {
                        "source": "Letterboxd",
                        "author": "Letterboxd User",
                        "text": text,
                        "url": letterboxd_data.get("url"),
                        "rating": None,
                    }
                )

        external_reviews.extend(reddit_data.get("reviews", []))
        external_reviews.extend(rt_data.get("reviews", []))
        external_reviews.extend(metacritic_data.get("reviews", []))

        rt_rating = rt_data.get("rating") or ScrapeApplication._get_omdb_rating(omdb_data, "Rotten Tomatoes")
        metacritic_rating = metacritic_data.get("rating") or ScrapeApplication._get_omdb_rating(omdb_data, "Metacritic")

        if not rt_data.get("reviews") and rt_rating is not None:
            external_reviews.append(
                {
                    "source": "Rotten Tomatoes",
                    "author": "Rotten Tomatoes",
                    "text": f"Tomatometer score for this title is {rt_rating * 10:.0f}%.",
                    "url": "https://www.rottentomatoes.com/",
                    "rating": None,
                }
            )

        if not metacritic_data.get("reviews") and metacritic_rating is not None:
            external_reviews.append(
                {
                    "source": "Metacritic",
                    "author": "Metacritic",
                    "text": f"Metacritic score for this title is {metacritic_rating * 10:.0f}/100.",
                    "url": "https://www.metacritic.com/",
                    "rating": None,
                }
            )

        source_ratings = {
            "Letterboxd": float(omdb_data.get("letterboxd_rating"))
            if omdb_data.get("letterboxd_rating") not in {None, "N/A"}
            else None,
            "Reddit": reddit_data.get("rating"),
            "Rotten Tomatoes": rt_rating,
            "Metacritic": metacritic_rating,
            "IMDb": ScrapeApplication._get_omdb_rating(omdb_data, "Internet Movie Database"),
        }

        omdb_data["external_reviews"] = external_reviews[:60]
        omdb_data["source_ratings"] = source_ratings

        return {
            "title": omdb_data.get("Title") or movie_name,
            "omdb_data": omdb_data
        }


scraper_app = ScrapeApplication()

# Backward-compatible alias for existing imports.
scrapper_app = scraper_app