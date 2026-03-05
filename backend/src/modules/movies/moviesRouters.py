from fastapi import APIRouter
from .moviesApplication import movie_app

roter = APIRouter()

@roter.get("/movies")
def get_movies():
    return movie_app.get_movie("Hellossdsd")

@roter.get("/movies/{movie_name}")
def get_movies(movie_name: str):
    return movie_app.get_movie(movie_name)
