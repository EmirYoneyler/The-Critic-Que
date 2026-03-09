from typing import Any

from ..scrape.scraperApplication import scraper_app
from .moviesRepo import movies_repo
from ...shared.logger import get_logger

logger = get_logger(__name__)

class MovieApplication:
    def __init__(self) -> None:
        self._repo = movies_repo

    def get_movie(self, movie_name: str) -> dict[str, Any] | None:
        existing_movie = self.check_movie_exists(movie_name)
        if existing_movie:
            existing_reviews = []
            source_count = 0
            if isinstance(existing_movie, dict):
                omdb_data = existing_movie.get("omdb_data", {})
                existing_reviews = omdb_data.get("external_reviews", [])
                if isinstance(existing_reviews, list):
                    source_count = len(
                        {
                            item.get("source")
                            for item in existing_reviews
                            if isinstance(item, dict) and item.get("source")
                        }
                    )

            # Re-scrape if data looks stale (few sources) even when cached reviews exist.
            if isinstance(existing_reviews, list) and len(existing_reviews) >= 10 and source_count >= 3:
                return existing_movie

        scraped_data = self.scrape_movie_data(movie_name)
        if not scraped_data:
            return None

        saved = self.save_movie_to_db(scraped_data)
        if not saved:
            logger.warning("Movie fetched but could not be cached: %s", movie_name)

        return scraped_data

    def get_movies(self) -> list[dict[str, Any]]:
        return self._repo.get_all_movies()

    def check_movie_exists(self, movie_name: str) -> dict[str, Any] | None:
        return self._repo.check_movie_exists(movie_name)

    def scrape_movie_data(self, movie_name: str) -> dict[str, Any] | None:
        return scraper_app.fetch_movie_data(movie_name)

    def save_movie_to_db(self, scraped_data: dict[str, Any]) -> bool:
        return self._repo.save_movie(scraped_data)

movie_app = MovieApplication()