from typing import Optional

from fastapi import APIRouter, HTTPException

from .moviesApplication import movie_app
from .schema.dto.moviesResponse import MovieErrorResponse, MovieResponse

router = APIRouter(tags=["movies"])

@router.get("/movies")
def get_movie_by_query(movie_name: Optional[str] = None) -> list[dict] | dict:
    if movie_name:
        movie = movie_app.get_movie(movie_name)
        if not movie:
            return MovieErrorResponse(message="Movie could not be found.").model_dump()
        return MovieResponse(**movie).model_dump()

    movies = movie_app.get_movies()
    if not movies:
        return {
            "status": "empty",
            "message": "No movies cached yet. Fetch one first with /movies/{movie_name} or /movies?movie_name=Fight Club.",
            "items": [],
        }

    return [MovieResponse(**movie).model_dump() for movie in movies]

@router.get("/movies/{movie_name}")
def get_movie_by_name(movie_name: str) -> dict:
    movie = movie_app.get_movie(movie_name)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie could not be found.")
    return MovieResponse(**movie).model_dump()


# Backward-compatible alias for existing imports.
roter = router
