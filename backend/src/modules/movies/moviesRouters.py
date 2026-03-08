from fastapi import APIRouter
from typing import Optional
from .moviesApplication import movie_app

roter = APIRouter()

@roter.get("/movies")
def get_movie_by_query(movie_name: Optional[str] = None):
    if movie_name:
        return movie_app.get_movie(movie_name)

    movies = movie_app.get_movies()
    if not movies:
        return {
            "status": "empty",
            "message": "No movies cached yet. Fetch one first with /movies/{movie_name} or /movies?movie_name=Fight Club.",
            "items": [],
        }

    return movies

@roter.get("/movies/{movie_name}")
def get_movie_by_name(movie_name: str):
    return movie_app.get_movie(movie_name)
