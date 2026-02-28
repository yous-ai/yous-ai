import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchMovie, fetchMovieReviews } from '../api/movies.js'
import ReviewForm from '../components/ReviewForm.jsx'
import SentimentChart from '../components/SentimentChart.jsx'

export default function MovieDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [movie, setMovie] = useState(null)
  const [reviews, setReviews] = useState([])
  const [sentiments, setSentiments] = useState({ positive: 0, neutral: 0, negative: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [id])

  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [movieData, reviewsData] = await Promise.all([
        fetchMovie(id),
        fetchMovieReviews(id),
      ])
      setMovie(movieData.data ?? movieData)

      const reviewsList = reviewsData.data ?? reviewsData
      setReviews(reviewsList)

      // Les sentiments viennent du modèle NLP via l'API
      if (reviewsData.sentiments) {
        setSentiments(reviewsData.sentiments)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Chargement...</div>
  if (error) return <div className="alert alert-error">{error}</div>
  if (!movie) return null

  return (
    <div className="page">
      <button className="btn btn-secondary back-btn" onClick={() => navigate('/')}>
        ← Retour
      </button>

      <div className="product-detail">
        <div className="product-detail-header">
          <div>
            <span className="product-category">{movie.genre}</span>
            <h1>{movie.title}</h1>
            {movie.description && <p className="product-description">{movie.description}</p>}
          </div>
          <div className="product-detail-meta">
            <div className="product-price-large">{movie.release_year}</div>
            {movie.average_rating != null && (
              <div className="product-rating">
                <span className="stars">
                  {'★'.repeat(Math.round(movie.average_rating))}
                  {'☆'.repeat(5 - Math.round(movie.average_rating))}
                </span>
                <span>{Number(movie.average_rating).toFixed(1)} / 5</span>
              </div>
            )}
          </div>
        </div>

        <div className="product-detail-body">
          <div className="reviews-section">
            <h3>Avis ({reviews.length})</h3>

            <SentimentChart sentiments={sentiments} />

            <div className="reviews-list">
              {reviews.length === 0 ? (
                <p className="no-data">Aucun avis pour ce film.</p>
              ) : (
                reviews.map((review) => (
                  <div key={review.id} className="review-card">
                    <div className="review-header">
                      <span className="review-author">Utilisateur #{review.user_id}</span>
                      <span className="review-date">
                        {new Date(review.created_at).toLocaleDateString('fr-FR')}
                      </span>
                      {review.sentiment && (
                        <span className={`review-sentiment sentiment-${review.sentiment}`}>
                          {review.sentiment}
                        </span>
                      )}
                    </div>
                    <p className="review-content">{review.content}</p>
                  </div>
                ))
              )}
            </div>

            <ReviewForm movieId={Number(id)} onSuccess={loadData} />
          </div>
        </div>
      </div>
    </div>
  )
}
