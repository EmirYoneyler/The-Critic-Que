

class MovieApplication:


    def get_movie(movie_name):

        if movie_app.check_movie_exists(movie_name):
            pass
        elif movie_app.scrape_movie_data(movie_name):
            pass
        else:
            pass

        return {
            "id": 1,
            "title": movie_name,
            "year": 1994
        }


    def check_movie_exists(movie_name):
        pass

    def scrape_movie_data(movie_name):
        pass



movie_app = MovieApplication()