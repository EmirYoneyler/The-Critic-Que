# The Critic Que

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=0A0A0A)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The Critic Que is a movie intelligence platform that combines OMDb metadata with Letterboxd signals and multi-source review collection. It provides a FastAPI backend and a modern React dashboard for search, discovery, and director-focused exploration.

## Why This Project

- Search any movie and get enriched metadata, ratings, and review snippets.
- Explore a homepage "Top 10" feed.
- Click directors in movie details to load that director's top movies.
- Handle real-world scraping issues with resilient backend fallbacks.
...
## Core Features

- Movie search with metadata: title, year, director, actors, runtime, awards, and more.
- Multi-source rating bars: IMDb, Letterboxd, Rotten Tomatoes, Metacritic, Reddit.
- External review cards with source attribution.
- Homepage discovery: Letterboxd Top 10 style listing.
- Director discovery: Top movies by selected director.
- Scraping fallback strategy for environments where Letterboxd list pages are blocked.

## Tech Stack

- Backend: FastAPI, Pydantic, Requests, BeautifulSoup
- Frontend: React, Vite, Tailwind CSS, lucide-react
- Runtime: Python 3.11+, Node.js 20+
- Dev/Run: Docker Compose, PowerShell/BAT scripts

## Architecture

```text
frontend (React + Vite)
	 -> calls REST API
backend (FastAPI)
	 -> movies module (query + cache orchestration)
	 -> scrape module (OMDb + Letterboxd + review sources)
	 -> in-memory repository (cached movie responses)
```

## Project Structure

```text
backend/
	src/
		main.py
		modules/
			movies/
			scrape/
		shared/
	run-dev.ps1
	run-dev.bat

backend/src/Frontend/
	src/
	package.json

docker-compose.yml
Dockerfile
requirements.txt
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- (Optional) Docker + Docker Compose

### 2. Environment Variables

Create `.env` at repo root:

```env
OMDB_API_KEY=your_omdb_api_key
OMDB_API_URL=http://www.omdbapi.com/
```

### 3. Run Locally (Backend + Frontend)

Option A: Script (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\run-dev.ps1
```

Option B: Docker

```powershell
docker compose up --build
```

### 4. URLs

- Frontend: `http://localhost:5173`
- API: `http://localhost:6767`
- API docs (Swagger): `http://localhost:6767/docs`

## API Reference

- `GET /health`
	- Health probe endpoint.

- `GET /movies/{movie_name}`
	- Fetch movie data and enrich with external sources.

- `GET /movies?movie_name=<title>`
	- Query-style movie fetch.

- `GET /movies`
	- Return cached movie entries from in-memory store.

- `GET /discover/top-movies?limit=10`
	- Return homepage top movie list.

- `GET /discover/director/{director_name}/top-movies?limit=10`
	- Return top movies for a given director.

## Product Notes

- OMDb is the primary metadata provider.
- Letterboxd data is best-effort and can be blocked in some environments.
- When list pages are blocked, fallback ranking logic is used to keep the experience functional.
- The current repository uses in-memory caching; data resets on service restart.

## Roadmap

- Persistent storage (PostgreSQL or Redis cache)
- User accounts and saved watchlists
- Better analytics dashboards (trend lines, source confidence)
- Deployment profile (cloud-ready config + CI)

## License

Distributed under the MIT License. See `LICENSE` for details.
