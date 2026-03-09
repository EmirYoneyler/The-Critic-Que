from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .modules.movies.moviesRouters import router
from .shared.logger import configure_logging

configure_logging()

app = FastAPI(title="The Critic Que API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6767)