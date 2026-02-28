const BASE_URL = '/api'

// --- Auth helpers ---

export function getToken() {
  return localStorage.getItem('jwt_token')
}

export function getUser() {
  const raw = localStorage.getItem('current_user')
  return raw ? JSON.parse(raw) : null
}

export function logout() {
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('current_user')
}

function authHeaders() {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

// --- Auth ---

export async function login(username) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error || 'Erreur de connexion')

  localStorage.setItem('jwt_token', json.data.token)
  localStorage.setItem('current_user', JSON.stringify(json.data.user))
  return json.data
}

// --- Movies ---

export async function fetchMovies(filters = {}) {
  const params = new URLSearchParams()
  if (filters.genre) params.append('genre', filters.genre)
  if (filters.release_year) params.append('release_year', filters.release_year)

  const url = `${BASE_URL}/movies${params.toString() ? '?' + params.toString() : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Erreur lors du chargement des films')
  return res.json()
}

export async function fetchMovie(id) {
  const res = await fetch(`${BASE_URL}/movies/${id}`)
  if (!res.ok) throw new Error('Film introuvable')
  return res.json()
}

export async function createMovie(data) {
  const res = await fetch(`${BASE_URL}/movies`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error || 'Erreur lors de la création du film')
  return json
}

// --- Reviews ---

export async function fetchMovieReviews(movieId) {
  const res = await fetch(`${BASE_URL}/reviews/${movieId}`)
  if (!res.ok) throw new Error('Erreur lors du chargement des avis')
  return res.json()
}

export async function createReview(data) {
  const res = await fetch(`${BASE_URL}/reviews`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error || "Erreur lors de l'ajout de l'avis")
  return json
}

// --- Ratings ---

export async function createRating(data) {
  const res = await fetch(`${BASE_URL}/ratings`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error || "Erreur lors de l'ajout de la note")
  return json
}
