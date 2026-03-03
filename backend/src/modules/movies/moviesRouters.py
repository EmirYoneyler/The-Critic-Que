from fastapi import APIRouter

roter = APIRouter()

@roter.get("/movies")
def get_movies():
    return {
        "movies": [
            {
                "id": 1,
                "title": "The Shawshank Redemption",
                "year": 1994
            },
            {
                "id": 2,
                "title": "The Godfather",
                "year": 1972
            }
        ]
    }

