from fastapi import FastAPI
from src.modules.movies.moviesRouters import roter

app = FastAPI()

app.include_router(roter)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
