from .sources.omdb_client import request_omdb_api
from .sources.letterboxd_scraper import scrape_letterboxd

class ScrapeApplication:

    @staticmethod
    def fetch_movie_data(movie_name: str):

        # There is two types of scraping that will happen in this function
        # first is omdb api request and handling the data from that api request_omdb_api()
        # second is scraping the data from letterboxd scrape_letterboxd() function




         if request_omdb_api(movie_name) and scrape_letterboxd():
             return True

         else:
             pass


scrapper_app = ScrapeApplication()