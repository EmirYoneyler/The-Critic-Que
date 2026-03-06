from .sources.omdb_client import request_omdb_api
from .sources.letterboxd_scraper import scrape_letterboxd

class ScrapeApplication:

    @staticmethod
    def fetch_movie_data(movie_name: str):

        # There is two types of scraping that will happen in this function
        # first is omdb api request and handling the data from that api request_omdb_api()
        # second is scraping the data from letterboxd scrape_letterboxd() function




        omdb_data = request_omdb_api(movie_name)
        if not omdb_data:
            return None

        # Letterboxd is optional: OMDB data alone is enough to return a movie.
        letterboxd_data = scrape_letterboxd(movie_name)

        return {
            "title": omdb_data.get("Title") or movie_name,
            "omdb_data": omdb_data,
            "letterboxd_data": letterboxd_data,
        }


scrapper_app = ScrapeApplication()