# Film Management API + Frontend

Application complète de gestion de films avec API REST Flask et frontend React.

## Tech Stack

- **Backend :** Python 3, Flask, SQLAlchemy, SQLite, PyJWT, HuggingFace Transformers
- **Frontend :** React 18, Vite, React Router v6

## Project Structure

```
bookshelf/
├── app.py                  # App factory, config, blueprint registration
├── models.py               # Database models (User, Movie, Rating, Review, etc.)
├── middleware.py            # JWT auth decorators (token_required / token_optional)
├── validators.py           # Input validation & security (XSS, SQL injection)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
│
├── routes/                 # API route blueprints
│   ├── auth.py             # POST /auth/login, GET /auth/me (JWT)
│   ├── users.py            # /users CRUD + /users/:id/stats
│   ├── movies.py           # /movies CRUD + top-rated + summary
│   ├── favorites.py        # /favorites CRUD (JWT protected)
│   ├── ratings.py          # /ratings CRUD + smart update (JWT protected)
│   ├── reviews.py          # /reviews CRUD + report + sentiment analysis
│   ├── recommendations.py  # /movies/recommendations/:user_id
│   └── sentiment.py        # POST /sentiment (NLP via HuggingFace)
│
├── frontend/               # React + Vite (port 5173)
│   └── src/
│       ├── api/movies.js   # Fetch functions + JWT token management
│       ├── components/     # Navbar, MovieCard, ReviewForm, SentimentChart
│       └── pages/          # MoviesPage, AddMoviePage, MovieDetailPage
│
├── tests/                  # pytest tests
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_movies.py
│   └── test_business.py
│
└── instance/               # SQLite database (auto-generated)
```

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows
# source .venv/bin/activate       # macOS/Linux

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Start the backend (port 5000)
python app.py

# 4. Install and start frontend (new terminal)
cd frontend
npm install
npm run dev
# → Frontend at http://localhost:5173

# 5. Run tests
python -m pytest tests/ -v
```

## Authentication (JWT)

L'app utilise des **JSON Web Tokens (JWT)** pour l'authentification.

1. L'utilisateur entre un **pseudo** dans la navbar
2. `POST /auth/login` → le backend crée l'utilisateur s'il n'existe pas → retourne un JWT
3. Le frontend stocke le token dans `localStorage`
4. Toutes les requêtes d'écriture incluent `Authorization: Bearer <token>`

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| POST | `/auth/login` | Login (auto-create user) | ❌ |
| GET | `/auth/me` | Current user info | ✅ |

## API Endpoints

### Users
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/users` | List all users (paginated) |
| GET | `/users/:id` | Get user by ID |
| POST | `/users` | Create user |
| PUT | `/users/:id` | Update user |
| DELETE | `/users/:id` | Delete user (cascade) |
| GET | `/users/:id/stats` | User activity summary |

### Movies
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/movies` | List movies (filter: `genre`, `release_year`) |
| GET | `/movies/:id` | Get movie by ID |
| POST | `/movies` | Create movie |
| PUT | `/movies/:id` | Update movie |
| DELETE | `/movies/:id` | Delete movie (cascade) |
| GET | `/movies/top-rated` | Top-rated movies (min_votes param) |
| GET | `/movies/:id/summary` | Full movie summary |
| GET | `/movies/recommendations/:user_id` | Personalized recommendations |

### Favorites / Ratings / Reviews (🔒 JWT Required)
| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| GET | `/favorites/:user_id` | User's favorites | ❌ |
| POST | `/favorites` | Add favorite | ✅ |
| DELETE | `/favorites` | Remove favorite | ❌ |
| GET | `/ratings/:user_id` | User's ratings | ❌ |
| POST | `/ratings` | Create rating (1-5) | ✅ |
| PUT | `/ratings` | Smart update (with history) | ✅ |
| DELETE | `/ratings` | Delete rating | ❌ |
| GET | `/reviews/:movie_id` | Movie reviews + sentiments | ❌ |
| POST | `/reviews` | Create review | ✅ |
| PUT | `/reviews/:review_id` | Update own review | ❌ |
| DELETE | `/reviews/:review_id` | Delete own review | ❌ |
| POST | `/reviews/:review_id/report` | Report review | ❌ |

### Sentiment Analysis (NLP)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/sentiment` | Analyze text sentiment (DistilBERT) |

> `GET /reviews/:movie_id` retourne automatiquement l'analyse de sentiment de chaque avis + un agrégat `{ positive, neutral, negative }` pour le graphique.

## Frontend Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | MoviesPage | Catalogue de films avec filtre par genre |
| `/movies/add` | AddMoviePage | Formulaire d'ajout de film |
| `/movies/:id` | MovieDetailPage | Détails + avis + graphique de sentiments + formulaire d'avis |
