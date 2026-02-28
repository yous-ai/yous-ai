import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createMovie } from '../api/movies.js'

const GENRES = [
  'Action', 'Comedy', 'Drama', 'Horror', 'Science-Fiction',
  'Thriller', 'Romance', 'Animation', 'Documentary', 'Crime'
]

export default function AddMoviePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    genre: '',
    release_year: '',
    description: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    if (!form.title.trim() || !form.genre || !form.release_year) {
      setError('Le titre, le genre et l\'année de sortie sont obligatoires.')
      return
    }

    const year = Number(form.release_year)
    if (year < 1888 || year > new Date().getFullYear()) {
      setError(`L'année doit être comprise entre 1888 et ${new Date().getFullYear()}.`)
      return
    }

    setLoading(true)
    try {
      const result = await createMovie({
        title: form.title.trim(),
        genre: form.genre,
        release_year: year,
        description: form.description.trim(),
      })
      const newId = result.data?.id ?? result.id
      navigate(newId ? `/movies/${newId}` : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-narrow">
      <div className="page-header">
        <h1>Ajouter un film</h1>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Titre du film *</label>
          <input
            id="title"
            name="title"
            type="text"
            value={form.title}
            onChange={handleChange}
            placeholder="Ex : Inception"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="genre">Genre *</label>
            <select id="genre" name="genre" value={form.genre} onChange={handleChange} required>
              <option value="">Sélectionner un genre</option>
              {GENRES.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="release_year">Année de sortie *</label>
            <input
              id="release_year"
              name="release_year"
              type="number"
              min="1888"
              max={new Date().getFullYear()}
              value={form.release_year}
              onChange={handleChange}
              placeholder="Ex : 2010"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            rows={4}
            value={form.description}
            onChange={handleChange}
            placeholder="Décrivez le film..."
          />
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
            Annuler
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Création...' : 'Créer le film'}
          </button>
        </div>
      </form>
    </div>
  )
}
