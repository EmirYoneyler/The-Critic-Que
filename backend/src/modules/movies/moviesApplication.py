# from modules.movies.schema.dto.moviesResponse import MovieDetailsResponse
from ..scrape.scraperApplication import scrapper_app
from .moviesRepo import movies_repo

class MovieApplication:
    def __init__(self):
        pass

    def get_movie(self, movie_name: str):

        existing_movie = self.check_movie_exists(movie_name)
        if existing_movie:
            return existing_movie
        
        scraped_data = self.scrape_movie_data(movie_name)

        if not scraped_data:
            return {"status": "error", "message": "Film couldn't be found."} 
        self.save_movie_to_db(scraped_data)
        return scraped_data

    def get_movies(self):
        return movies_repo.get_all_movies()
    


    def check_movie_exists(self, movie_name):
        return movies_repo.check_movie_exists(movie_name)

    def scrape_movie_data(self, movie_name):
        return scrapper_app.fetch_movie_data(movie_name)

    def save_movie_to_db(self, scraped_data):
        movies_repo.save_movie(scraped_data)

movie_app = MovieApplication()