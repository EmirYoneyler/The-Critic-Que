from fastapi import FastAPI
from .modules.movies.moviesRouters import roter

app = FastAPI()

app.include_router(roter)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6767)