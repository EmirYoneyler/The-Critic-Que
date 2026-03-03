

class MovieApplication:

    def __init__(self):
        pass

    @staticmethod
    def get_movie(movie_name):
        return {
            "id": 1,
            "title": movie_name,
            "year": 1994
        }



movie_app = MovieApplication()