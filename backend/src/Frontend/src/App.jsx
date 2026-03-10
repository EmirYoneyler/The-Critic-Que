import React, { useEffect, useMemo, useState } from 'react';
import { Search, Star, MessageSquare, Film } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:6767';

const MovieDashboard = () => {
  const [query, setQuery] = useState('Inception');
  const [activeView, setActiveView] = useState('home');
  const [movieData, setMovieData] = useState(null);
  const [homeTopMovies, setHomeTopMovies] = useState([]);
  const [directorTopMovies, setDirectorTopMovies] = useState([]);
  const [selectedDirector, setSelectedDirector] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const omdb = movieData?.omdb_data || {};

  const genres = useMemo(() => {
    if (!omdb.Genre) {
      return [];
    }

    return omdb.Genre.split(',').map((genre) => genre.trim());
  }, [omdb.Genre]);

  const externalReviews = useMemo(() => {
    const reviews = omdb.external_reviews;
    if (!Array.isArray(reviews)) {
      return [];
    }

    return reviews
      .filter((review) => review && typeof review.text === 'string' && review.text.trim())
      .slice(0, 30);
  }, [omdb.external_reviews]);

  const sourceRatings = useMemo(() => {
    const ratings = omdb.source_ratings;
    if (!ratings || typeof ratings !== 'object') {
      return [];
    }

    return Object.entries(ratings)
      .filter(([, value]) => typeof value === 'number' && Number.isFinite(value))
      .map(([source, value]) => {
        const isLetterboxd = source === 'Letterboxd';
        const displayMax = isLetterboxd ? 5 : 10;
        const displayValue = Math.max(0, Math.min(displayMax, value));
        const barPercent = (displayValue / displayMax) * 100;

        return {
          source,
          displayValue,
          displayMax,
          barPercent,
        };
      });
  }, [omdb.source_ratings]);

  const movieFacts = useMemo(
    () => [
      { label: 'Year', value: omdb.Year },
      { label: 'Released', value: omdb.Released },
      { label: 'Runtime', value: omdb.Runtime },
      { label: 'Director', value: omdb.Director },
      { label: 'Writer', value: omdb.Writer },
      { label: 'Actors', value: omdb.Actors },
      { label: 'Language', value: omdb.Language },
      { label: 'Country', value: omdb.Country },
      { label: 'Awards', value: omdb.Awards },
      { label: 'Box Office', value: omdb.BoxOffice },
    ].filter((fact) => fact.value && fact.value !== 'N/A'),
    [
      omdb.Year,
      omdb.Released,
      omdb.Runtime,
      omdb.Director,
      omdb.Writer,
      omdb.Actors,
      omdb.Language,
      omdb.Country,
      omdb.Awards,
      omdb.BoxOffice,
    ],
  );

  const directors = useMemo(() => {
    if (!omdb.Director || omdb.Director === 'N/A') {
      return [];
    }

    return omdb.Director.split(',').map((name) => name.trim()).filter(Boolean);
  }, [omdb.Director]);

  const searchMovie = async (movieNameInput = query) => {
    const movieName = movieNameInput.trim();
    if (!movieName) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/movies/${encodeURIComponent(movieName)}`);

      if (!response.ok) {
        throw new Error('Backend request failed.');
      }

      const data = await response.json();

      if (data?.status === 'error') {
        setMovieData(null);
        setError(data.message || 'Movie not found.');
        return;
      }

      setMovieData(data);
      setActiveView('movie');
    } catch {
      setMovieData(null);
      setError('Cannot reach backend. Make sure API is running on localhost:6767.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHomeTopMovies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/discover/top-movies?limit=10`);
      if (!response.ok) {
        throw new Error('Top movies request failed.');
      }

      const data = await response.json();
      setHomeTopMovies(Array.isArray(data?.items) ? data.items : []);
    } catch {
      setHomeTopMovies([]);
    }
  };

  const fetchDirectorTopMovies = async (directorName) => {
    const cleanName = directorName?.trim();
    if (!cleanName) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${API_BASE_URL}/discover/director/${encodeURIComponent(cleanName)}/top-movies?limit=10`,
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Director endpoint not found. Restart backend so new routes are loaded.');
        }
        throw new Error('Director top movies request failed.');
      }

      const data = await response.json();
      setSelectedDirector(cleanName);
      setDirectorTopMovies(Array.isArray(data?.items) ? data.items : []);
      setActiveView('director');
      if (!Array.isArray(data?.items) || data.items.length === 0) {
        setError(data?.message || 'No Letterboxd movies returned for this director.');
      }
    } catch (err) {
      setDirectorTopMovies([]);
      setError(err?.message || 'Could not fetch director top movies from Letterboxd.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHomeTopMovies();
  }, []);

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    searchMovie();
  };

  const goHome = () => {
    setActiveView('home');
    setError('');
  };

  const HomeSection = () => (
    <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5 md:p-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Letterboxd Top 10 Movies</h2>
        <button
          type="button"
          onClick={fetchHomeTopMovies}
          className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
        >
          Refresh
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {homeTopMovies.length > 0 ? (
          homeTopMovies.map((movie, index) => (
            <article key={`${movie.title}-${index}`} className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="rounded-lg overflow-hidden border border-slate-800 bg-slate-950 mb-3">
                <img
                  src={movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}
                  alt={movie.title}
                  className="w-full h-56 object-cover"
                />
              </div>
              <p className="text-xs text-slate-500 mb-1">#{index + 1}</p>
              <p className="font-semibold text-slate-100">{movie.title}</p>
              {movie.letterboxd_url ? (
                <a
                  href={movie.letterboxd_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-2 text-xs text-emerald-400 hover:text-emerald-300"
                >
                  Open on Letterboxd
                </a>
              ) : null}
            </article>
          ))
        ) : (
          <div className="md:col-span-2 xl:col-span-3 bg-slate-900 border border-slate-800 p-4 rounded-xl text-slate-400 italic">
            Top movies are not available right now.
          </div>
        )}
      </div>
    </section>
  );

  const DirectorSection = () => (
    <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5 md:p-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">
          Top 10 for {selectedDirector || 'Selected Director'}
        </h2>
        <button
          type="button"
          onClick={goHome}
          className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
        >
          Back to Home
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {directorTopMovies.length > 0 ? (
          directorTopMovies.map((movie, index) => (
            <article key={`${movie.title}-${index}`} className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="rounded-lg overflow-hidden border border-slate-800 bg-slate-950 mb-3">
                <img
                  src={movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}
                  alt={movie.title}
                  className="w-full h-56 object-cover"
                />
              </div>
              <p className="text-xs text-slate-500 mb-1">#{index + 1}</p>
              <p className="font-semibold text-slate-100">{movie.title}</p>
              {typeof movie.rating === 'number' ? (
                <p className="mt-1 text-xs text-amber-300">Letterboxd: {movie.rating.toFixed(2)} / 5</p>
              ) : null}
              {movie.letterboxd_url ? (
                <a
                  href={movie.letterboxd_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-2 text-xs text-emerald-400 hover:text-emerald-300"
                >
                  Open on Letterboxd
                </a>
              ) : null}
            </article>
          ))
        ) : (
          <div className="md:col-span-2 xl:col-span-3 bg-slate-900 border border-slate-800 p-4 rounded-xl text-slate-400 italic">
            Could not find a ranked list for this director.
          </div>
        )}
      </div>
    </section>
  );

  const MovieSection = () => (
    <main className="grid grid-cols-1 xl:grid-cols-12 gap-6">
      <aside className="xl:col-span-4 space-y-5">
        <div className="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-emerald-900/10 bg-slate-900/50">
          <img
            src={omdb.Poster && omdb.Poster !== 'N/A' ? omdb.Poster : 'https://via.placeholder.com/400x600?text=No+Poster'}
            alt={movieData?.title || 'Poster'}
            className="w-full object-cover"
          />
        </div>

        <div className="bg-slate-900/70 p-5 rounded-2xl border border-slate-800">
          <h3 className="text-sm uppercase tracking-wide text-slate-400 mb-4">Quick Scores</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-slate-700 bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">IMDb</p>
              <p className="mt-1 flex items-center gap-2 text-yellow-500 font-bold">
                <Star fill="currentColor" size={16} /> {omdb.imdbRating || 'N/A'}
              </p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">Letterboxd</p>
              <p className="mt-1 flex items-center gap-2 text-emerald-400 font-bold">
                <Film size={16} /> {omdb.letterboxd_rating || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </aside>

      <section className="xl:col-span-8 space-y-6">
        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5 md:p-6">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">{movieData?.title || 'Search a movie'}</h2>
          <div className="flex flex-wrap gap-3">
            {genres.map((tag) => (
              <span key={tag} className="px-3 py-1 bg-slate-800 rounded-md text-sm font-medium border border-slate-700">
                {tag}
              </span>
            ))}
          </div>
          <p className="text-base md:text-lg text-slate-300 leading-relaxed">
            {omdb.Plot || 'Enter a title and press Search to fetch details from your backend.'}
          </p>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
            <h3 className="text-xl font-semibold flex items-center gap-2 border-l-4 border-amber-500 pl-3">
              <Film size={20} /> Movie Details
            </h3>
            {movieFacts.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {movieFacts.map((fact) => (
                  <div key={fact.label} className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                    <p className="text-xs uppercase tracking-wide text-slate-500">{fact.label}</p>
                    {fact.label === 'Director' ? (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {directors.map((director) => (
                          <button
                            key={director}
                            type="button"
                            onClick={() => fetchDirectorTopMovies(director)}
                            className="px-2.5 py-1 rounded-lg border border-cyan-700/50 bg-cyan-900/20 text-cyan-300 hover:border-cyan-500 hover:text-cyan-200 transition-colors text-sm"
                          >
                            {director}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-200 mt-1">{fact.value}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-slate-400 italic">
                Detailed metadata is not available for this title.
              </div>
            )}
          </div>

          <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
            <h3 className="text-xl font-semibold flex items-center gap-2 border-l-4 border-cyan-500 pl-3">
              <Star size={20} /> Review Ratings
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sourceRatings.length > 0 ? (
                sourceRatings.map((item) => (
                  <div key={item.source} className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-2 text-sm">
                      <span className="font-semibold text-slate-200">{item.source}</span>
                      <span className="text-emerald-300">{item.displayValue.toFixed(1)} / {item.displayMax}</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400" style={{ width: `${item.barPercent}%` }} />
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-slate-400 italic sm:col-span-2">
                  Source ratings are not available for this title.
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
          <h3 className="text-xl font-semibold flex items-center gap-2 border-l-4 border-emerald-500 pl-3">
            <MessageSquare size={20} /> Multi-source Reviews
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {externalReviews.length > 0 ? (
              externalReviews.map((review, index) => (
                <article key={`${review.source}-${index}`} className="bg-slate-900 border border-slate-800 p-5 rounded-xl hover:border-slate-600 transition-colors h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-1 text-xs font-semibold rounded-md bg-slate-800 border border-slate-700 text-cyan-300">
                      {review.source}
                    </span>
                    <span className="text-xs text-slate-500">{review.author || 'Unknown'}</span>
                  </div>
                  <p className="text-slate-300 italic">"{review.text}"</p>
                  {review.url ? (
                    <a href={review.url} target="_blank" rel="noreferrer" className="inline-block mt-2 text-xs text-emerald-400 hover:text-emerald-300">
                      Open source comment
                    </a>
                  ) : null}
                </article>
              ))
            ) : (
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl hover:border-slate-600 transition-colors md:col-span-2">
                <p className="text-slate-400 italic">No external reviews found for this title.</p>
              </div>
            )}
          </div>
        </section>
      </section>
    </main>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-slate-800 pb-6">
          <div>
            <button
              type="button"
              onClick={goHome}
              className="text-left text-4xl font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent hover:from-emerald-300 hover:to-cyan-300 transition-colors"
            >
              THE CRITIC QUE
            </button>
            <p className="text-slate-400 mt-2">Movie Intelligence Platform</p>
          </div>

          <form className="relative w-full xl:w-[30rem]" onSubmit={handleSearchSubmit}>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-full py-3 px-6 pl-12 pr-24 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
              placeholder="Search movie..."
            />
            <Search className="absolute left-4 top-3.5 text-slate-500" size={20} />
            <button
              type="submit"
              className="absolute right-2 top-1.5 px-4 py-1.5 rounded-full bg-emerald-500 text-slate-900 font-semibold hover:bg-emerald-400"
            >
              Search
            </button>
          </form>
        </header>

        {error ? <p className="text-red-400">{error}</p> : null}
        {loading ? <p className="text-emerald-300">Searching...</p> : null}

        {activeView === 'home' ? <HomeSection /> : null}
        {activeView === 'movie' ? <MovieSection /> : null}
        {activeView === 'director' ? <DirectorSection /> : null}
      </div>
    </div>
  );
};

export default MovieDashboard;
