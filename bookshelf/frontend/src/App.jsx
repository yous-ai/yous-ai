import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import MoviesPage from './pages/MoviesPage.jsx'
import AddMoviePage from './pages/AddMoviePage.jsx'
import MovieDetailPage from './pages/MovieDetailPage.jsx'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<MoviesPage />} />
          <Route path="/movies/add" element={<AddMoviePage />} />
          <Route path="/movies/:id" element={<MovieDetailPage />} />
        </Routes>
      </main>
    </div>
  )
}
