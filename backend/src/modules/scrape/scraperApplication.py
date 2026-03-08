from .sources.omdb_client import request_omdb_api
from .sources.letterboxd_client import scrape_letterboxd_json

class ScrapeApplication:

    @staticmethod
    def fetch_movie_data(movie_name: str):

        # There is two types of scraping that will happen in this function
        # first is omdb api request and handling the data from that api request_omdb_api()
        # second is scraping the data from letterboxd scrape_letterboxd() function




        omdb_data = request_omdb_api(movie_name)
        print("FIRST OMDB data:", omdb_data)  # Debugging line
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
                print(f"Title mismatch: OMDB '{omdb_title}' vs Letterboxd '{letterboxd_title}'")
                # You can choose to still include the letterboxd rating or skip it
                omdb_data["letterboxd_rating"] = letterboxd_data.get("rating")

        print("OMDB data:", omdb_data)  # Debugging line

        return {
            "title": omdb_data.get("Title") or movie_name,
            "omdb_data": omdb_data
        }


scrapper_app = ScrapeApplication()