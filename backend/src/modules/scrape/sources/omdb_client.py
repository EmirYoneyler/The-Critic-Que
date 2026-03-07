import requests
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("OMDB_API_KEY")
api_url = os.getenv("OMDB_API_URL")

def request_omdb_api(movie_name: str):

    params = {
        "apikey": api_key,
        "t": movie_name
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            print(data)
            return data
        else:
            print(f"Movie not found: {data.get('Error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OMDB API: {e}")
        return None

request_omdb_api("Fight Club")