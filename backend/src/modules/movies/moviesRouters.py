from fastapi import APIRouter
from typing import Optional
from .moviesApplication import movie_app

roter = APIRouter()

@roter.get("/movies")
def get_movie_by_query(movie_name: Optional[str] = None):
    if movie_name:
        return movie_app.get_movie(movie_name)
    return movie_app.get_movies()

@roter.get("/movies/{movie_name}")
def get_movie_by_name(movie_name: str):
    return movie_app.get_movie(movie_name)
