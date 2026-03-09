import React, { useEffect, useMemo, useState } from 'react';
import { Search, Star, MessageSquare, Film } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:6767';

const MovieDashboard = () => {
  const [query, setQuery] = useState('Inception');
  const [movieData, setMovieData] = useState(null);
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
    } catch {
      setMovieData(null);
      setError('Cannot reach backend. Make sure API is running on localhost:6767.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchMovie('Inception');
  }, []);

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    searchMovie();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-12">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-800 pb-8">
          <div>
            <h1 className="text-4xl font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              THE CRITIC QUE
            </h1>
            <p className="text-slate-400 mt-2">Movie Intelligence Platform</p>
          </div>

          <form className="relative w-full md:w-96" onSubmit={handleSearchSubmit}>
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

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4 space-y-6">
            <div className="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-emerald-900/10">
              <img
                src={omdb.Poster && omdb.Poster !== 'N/A' ? omdb.Poster : 'https://via.placeholder.com/400x600?text=No+Poster'}
                alt={movieData?.title || 'Poster'}
                className="w-full object-cover"
              />
            </div>

            <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-yellow-500 font-bold">
                  <Star fill="currentColor" size={18} /> IMDB: {omdb.imdbRating || 'N/A'}
                </span>
                <span className="flex items-center gap-2 text-emerald-400 font-bold">
                  <Film size={18} /> Letterboxd: {omdb.letterboxd_rating || 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-8">
            <section className="space-y-4">
              <h2 className="text-5xl font-bold tracking-tight">{movieData?.title || 'Search a movie'}</h2>
              <div className="flex flex-wrap gap-3">
                {genres.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-slate-800 rounded-md text-sm font-medium border border-slate-700">
                    {tag}
                  </span>
                ))}
              </div>
              <p className="text-lg text-slate-300 leading-relaxed max-w-2xl">
                {omdb.Plot || 'Enter a title and press Search to fetch details from your backend.'}
              </p>
            </section>

            <section className="space-y-4">
              <h3 className="text-xl font-semibold flex items-center gap-2 border-l-4 border-cyan-500 pl-3">
                <Star size={20} /> Review Rating Bars
              </h3>
              <div className="space-y-3">
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
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-slate-400 italic">
                    Source ratings are not available for this title.
                  </div>
                )}
              </div>
            </section>

            <section className="space-y-4">
              <h3 className="text-xl font-semibold flex items-center gap-2 border-l-4 border-emerald-500 pl-3">
                <MessageSquare size={20} /> Multi-source Reviews
              </h3>
              <div className="grid gap-4">
                {externalReviews.length > 0 ? (
                  externalReviews.map((review, index) => (
                    <div key={`${review.source}-${index}`} className="bg-slate-900 border border-slate-800 p-5 rounded-xl hover:border-slate-600 transition-colors">
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
                    </div>
                  ))
                ) : (
                  <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl hover:border-slate-600 transition-colors">
                    <p className="text-slate-400 italic">No external reviews found for this title.</p>
                  </div>
                )}
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
};

export default MovieDashboard;
