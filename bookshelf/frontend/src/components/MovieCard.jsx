import { useNavigate } from 'react-router-dom'

export default function MovieCard({ movie }) {
  const navigate = useNavigate()

  return (
    <div
      className="product-card"
      onClick={() => navigate(`/movies/${movie.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && navigate(`/movies/${movie.id}`)}
    >
      <div className="product-card-header">
        <span className="product-category">{movie.genre}</span>
        <span className="product-price">{movie.release_year}</span>
      </div>
      <h3 className="product-name">{movie.title}</h3>
      <p className="product-description">
        {movie.description
          ? movie.description.length > 100
            ? movie.description.slice(0, 100) + '...'
            : movie.description
          : 'Aucune description disponible.'}
      </p>
      {movie.average_rating != null && (
        <div className="product-rating">
          <span className="stars">
            {'★'.repeat(Math.round(movie.average_rating))}
            {'☆'.repeat(5 - Math.round(movie.average_rating))}
          </span>
          <span className="rating-value">
            {Number(movie.average_rating).toFixed(1)} / 5
          </span>
        </div>
      )}
    </div>
  )
}
