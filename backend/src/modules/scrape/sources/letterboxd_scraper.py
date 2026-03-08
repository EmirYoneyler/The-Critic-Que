import logging
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class LetterboxdScraper:
    def __init__(self) -> None:
        self.base_url = "https://letterboxd.com"
        self.wait_seconds = 10
        self.options = self._build_options()

    def _build_options(self) -> Options:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=en-US")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        return options

    def _get_driver(self) -> webdriver.Chrome:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=self.options)

    def scrape_letterboxd(self, movie_name: str) -> Dict[str, Any]:
        cleaned = (movie_name or "").strip()
        if not cleaned:
            return {"error": "Movie name cannot be empty."}

        search_url = f"{self.base_url}/search/films/{quote_plus(cleaned)}/"

        try:
            with self._get_driver() as driver:
                driver.get(search_url)
                wait = WebDriverWait(driver, self.wait_seconds)
                first_item = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.results li div.film-poster"))
                )

                movie_path = first_item.get_attribute("data-target-link")
                if not movie_path:
                    return {"error": "Movie not found on Letterboxd."}

                driver.get(f"{self.base_url}{movie_path}")
                return self._extract_details(driver, movie_path)
        except Exception as exc:
            logger.exception("Letterboxd scraping failed for %s: %s", cleaned, exc)
            return {"error": "Letterboxd scraping failed."}

    def _extract_details(self, driver: webdriver.Chrome, path: str) -> Dict[str, Any]:
        rating = self._extract_rating(driver)
        year_released = self._extract_year(driver)
        reviews = self._extract_reviews(driver)

        return {
            "slug": path.strip("/").split("/")[-1],
            "rating": rating,
            "year_released": year_released,
            "popular_reviews": reviews,
            "url": driver.current_url,
            "available": True,
        }

    def _extract_rating(self, driver: webdriver.Chrome) -> float:
        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, "meta[name='twitter:data2']")
            rating_text = (rating_element.get_attribute("content") or "").split(" ")[0]
            return float(rating_text)
        except Exception:
            return 0.0

    def _extract_year(self, driver: webdriver.Chrome) -> Optional[int]:
        try:
            year_text = driver.find_element(By.CSS_SELECTOR, "div.releaseyear a").text.strip()
            return int(year_text) if year_text.isdigit() else None
        except Exception:
            return None

    def _extract_reviews(self, driver: webdriver.Chrome) -> list[str]:
        reviews: list[str] = []
        for element in driver.find_elements(By.CSS_SELECTOR, ".film-details .collapsible-text p")[:3]:
            text = element.text.strip()
            if text:
                reviews.append(text)
        return reviews


letterboxd_scraper = LetterboxdScraper()


def scrape_letterboxd(movie_name: str) -> Dict[str, Any]:
    return letterboxd_scraper.scrape_letterboxd(movie_name)


