import { useState, useEffect } from 'react'
import { fetchMovies } from '../api/movies.js'
import MovieCard from '../components/MovieCard.jsx'

const GENRES = [
  '', 'Action', 'Comedy', 'Drama', 'Horror', 'Science-Fiction',
  'Thriller', 'Romance', 'Animation', 'Documentary', 'Crime'
]

export default function MoviesPage() {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [genre, setGenre] = useState('')

  useEffect(() => {
    loadMovies()
  }, [genre])

  async function loadMovies() {
    setLoading(true)
    setError(null)
    try {
      const filters = {}
      if (genre) filters.genre = genre
      const data = await fetchMovies(filters)
      setMovies(data.data ?? data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Catalogue de films</h1>
        <p>{movies.length} film{movies.length !== 1 ? 's' : ''}</p>
      </div>

      <div className="filters">
        <select value={genre} onChange={(e) => setGenre(e.target.value)}>
          <option value="">Tous les genres</option>
          {GENRES.filter(Boolean).map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
        <button className="btn btn-secondary" onClick={loadMovies}>
          Actualiser
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading">Chargement des films...</div>
      ) : movies.length === 0 ? (
        <div className="empty-state">Aucun film trouvé.</div>
      ) : (
        <div className="products-grid">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      )}
    </div>
  )
}
