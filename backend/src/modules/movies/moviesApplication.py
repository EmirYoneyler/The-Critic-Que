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
        pass

    def scrape_movie_data(movie_name):
        pass



movie_app = MovieApplication()