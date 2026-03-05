import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class MoviesRepo:
    def __init__(self):
        self._db: Dict[str, Any] = {}
        logger.info("Movies Repository initialized (In-memory mode).")

    def check_movie_exists(self, movie_name: str) -> Optional[Dict]:
        name_key = movie_name.lower().strip()
        
        if name_key in self._db:
            logger.info(f"Movie found in DB: {movie_name}")
            return self._db[name_key]
        
        return None

    def save_movie(self, movie_data: Any) -> bool:
        
        try:
            data_to_save = movie_data.model_dump() if hasattr(movie_data, 'model_dump') else movie_data
            
            title = data_to_save.get("title") or data_to_save.get("omdb_data", {}).get("Title")
            
            if not title:
                raise ValueError("Movie title not found in data.")

            self._db[title.lower().strip()] = data_to_save
            logger.info(f"Successfully saved movie: {title}")
            return True
        except Exception as e:
            logger.error(f"Error saving movie: {str(e)}")
            return False

    def get_movie_by_name(self, movie_name: str) -> Optional[Dict]:
        return self.check_movie_exists(movie_name)

    #  Opsiyonel

    def get_all_movies(self) -> List[Dict]:
        return list(self._db.values())

    def delete_movie(self, movie_name: str) -> bool:
        name_key = movie_name.lower().strip()
        if name_key in self._db:
            del self._db[name_key]
            return True
        return False

movies_repo = MoviesRepo()