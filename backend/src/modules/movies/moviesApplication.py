

from modules.movies.schema.dto.moviesResponse import MovieDetailsResponse
from scrape.scraper_service import fetch_movie_data #ıts for data when we create sql

class MovieApplication:
    def __init__(self):
        pass

    def get_movie(self, movie_name: str):

        existing_movie = self.check_movie_exists(movie_name)
        if existing_movie:
            return existing_movie
        
        scraped_data = self.scrape_movie_data(movie_name)

        if not scraped_data or "error" in scraped_data:
            return {"status": "error", "message": "Film couldn't be found."} 
        self.save_movie_to_db(scraped_data)
        return scraped_data
    


    def check_movie_exists(movie_name):
        return None

    def scrape_movie_data(movie_name):
        print(f"Scraping data for {movie_name}")
        scraped_data = fetch_movie_data(movie_name)
        if scraped_data:
            print(f"Scraped data for {movie_name}: {scraped_data}")
        else:
            print(f"No data found for {movie_name}")
        return scraped_data
    #    def save_movie_to_db(movie_data):
    
        



movie_app = MovieApplication()
