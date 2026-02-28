import { useState } from 'react'
import { createReview, createRating, getUser } from '../api/movies.js'

export default function ReviewForm({ movieId, onSuccess }) {
  const [score, setScore] = useState(3)
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const user = getUser()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    if (!content.trim()) {
      setError('Veuillez renseigner votre avis.')
      return
    }

    setLoading(true)
    try {
      await createRating({ movie_id: movieId, score: Number(score) })
      await createReview({ movie_id: movieId, content: content.trim() })
      setSuccess(true)
      setContent('')
      setScore(3)
      if (onSuccess) onSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // If not logged in, show a message
  if (!user) {
    return (
      <div className="review-form">
        <h4>Laisser un avis</h4>
        <p className="no-data">Connectez-vous pour laisser un avis.</p>
      </div>
    )
  }

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h4>Laisser un avis en tant que <strong>{user.username}</strong></h4>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">Avis ajouté avec succès !</div>}

      <div className="form-group">
        <label>Note (1 – 5)</label>
        <div className="star-selector">
          {[1, 2, 3, 4, 5].map((s) => (
            <button
              key={s}
              type="button"
              className={`star-btn ${s <= score ? 'selected' : ''}`}
              onClick={() => setScore(s)}
            >
              ★
            </button>
          ))}
          <span className="score-label">{score} / 5</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="content">Votre avis</label>
        <textarea
          id="content"
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Partagez votre avis sur ce film..."
          maxLength={2000}
          required
        />
        <small>{content.length} / 2000 caractères</small>
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Envoi...' : 'Envoyer'}
      </button>
    </form>
  )
}
