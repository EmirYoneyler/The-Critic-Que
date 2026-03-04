from fastapi import APIRouter
from .moviesApplication import movie_app

roter = APIRouter()

@roter.get("/movies")
def get_movies():
    return movie_app.get_movie("Hellossdsd")
