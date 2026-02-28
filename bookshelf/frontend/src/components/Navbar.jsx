import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { login, logout, getUser } from '../api/movies.js'

export default function Navbar() {
  const location = useLocation()
  const [user, setUser] = useState(getUser())
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Sync user state on navigation
  useEffect(() => {
    setUser(getUser())
  }, [location])

  async function handleLogin(e) {
    e.preventDefault()
    if (!username.trim()) return
    setError(null)
    setLoading(true)
    try {
      const data = await login(username.trim())
      setUser(data.user)
      setUsername('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    logout()
    setUser(null)
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🎬 Films</Link>
      </div>

      <div className="navbar-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          Films
        </Link>
        <Link
          to="/movies/add"
          className={location.pathname === '/movies/add' ? 'active' : ''}
        >
          + Ajouter un film
        </Link>
      </div>

      <div className="navbar-auth">
        {user ? (
          <div className="auth-logged-in">
            <span className="auth-username">👤 {user.username}</span>
            <button className="btn btn-logout" onClick={handleLogout}>
              Déconnexion
            </button>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleLogin}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Votre pseudo..."
              className="auth-input"
              disabled={loading}
            />
            <button type="submit" className="btn btn-login" disabled={loading || !username.trim()}>
              {loading ? '...' : 'Connexion'}
            </button>
            {error && <span className="auth-error">{error}</span>}
          </form>
        )}
      </div>
    </nav>
  )
}
