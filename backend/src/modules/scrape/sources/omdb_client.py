import requests
from dotenv import load_dotenv
import os

from ....shared.logger import get_logger


load_dotenv()
api_key = os.getenv("OMDB_API_KEY")
api_url = os.getenv("OMDB_API_URL")
logger = get_logger(__name__)

def request_omdb_api(movie_name: str):
    if not api_key or not api_url:
        logger.error("OMDB_API_KEY or OMDB_API_URL is missing.")
        return None

    params = {
        "apikey": api_key,
        "t": movie_name
    }

    try:
        response = requests.get(api_url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return data
        logger.info("Movie not found in OMDB: %s", movie_name)
        return None
    except requests.exceptions.RequestException as e:
        logger.exception("Error fetching data from OMDB API: %s", e)
        return None