import requests
import json
from bs4 import BeautifulSoup

def scrape_letterboxd_json(movie_name: str):
    url = f"https://letterboxd.com/film/{movie_name.lower().replace(' ', '-')}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed with status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        script_tag = soup.find("script", type="application/ld+json")
        json_text = script_tag.text.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "").strip()
        data = json.loads(json_text)
        
        # 1. Normalize to a list just in case it returns a single dict
        if isinstance(data, dict):
            data = [data]
            
        # 2. Extract the specific dictionary that contains the Movie data
        movie_obj = next((item for item in data if item.get("@type") == "Movie"), {})
        
        # 3. Handle 'releasedEvent' which can also be nested inside a list
        releases = movie_obj.get("releasedEvent", [{}])
        if isinstance(releases, list):
            release_year = releases[0].get("startDate", "")[:4] # Gets "2010" from "2010-07-14"
        else:
            release_year = releases.get("startDate", "")[:4]

        return {
            "rating": movie_obj.get("aggregateRating", {}).get("ratingValue")
        }
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

if __name__ == "__main__":
    print(scrape_letterboxd_json("Inception"))