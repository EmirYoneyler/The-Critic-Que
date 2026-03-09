# The-Critic-Que

The Critic Que is a movie intelligence application that combines OMDb metadata with Letterboxd rating insights.
It includes a FastAPI backend for movie retrieval/enrichment and a React frontend for search and visualization.

## Tech Stack

- Backend: FastAPI, Pydantic, Requests, BeautifulSoup
- Frontend: React, Vite, Tailwind CSS
- Runtime: Python 3.11+, Node 20+

## Project Structure

```text
backend/src/
	main.py
	modules/
		movies/
		scrape/
	shared/
```

## Local Development

### Backend only

```powershell
cd backend
python -m src.main
```

API base URL: `http://localhost:6767`

### Frontend only

```powershell
cd backend/src/Frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### Backend + Frontend together

Option 1 (Docker):

```powershell
docker compose up --build
```

Option 2 (Windows script):

```powershell
.\run-dev.bat
```

## API Endpoints

- `GET /health` : Service health probe
- `GET /movies/{movie_name}` : Fetch and enrich a movie by title
- `GET /movies?movie_name=<title>` : Query-style movie fetch
- `GET /movies` : Return cached movies from in-memory store

## Notes

- OMDb credentials are read from `.env` (`OMDB_API_KEY`, `OMDB_API_URL`).
- Letterboxd enrichment is best-effort and optional; OMDb data is sufficient for a successful response.