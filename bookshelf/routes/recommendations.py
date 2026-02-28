# -*- coding: utf-8 -*-
"""Recommendations route (business logic)."""

from flask import Blueprint
from models import db, Movie, Favorite, Rating, User
from sqlalchemy import func

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.get('/movies/recommendations/<int:user_id>')
def get_recommendations(user_id):
    """Recommend movies based on user's favorite genres (business logic)."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        # Get the user's favorite movie IDs
        favorite_movie_ids = [
            f.movie_id for f in Favorite.query.filter_by(user_id=user_id).all()
        ]

        if not favorite_movie_ids:
            # No favorites — return top-rated movies globally
            results = (
                db.session.query(
                    Movie,
                    func.avg(Rating.score).label('avg_score'),
                    func.count(Rating.id).label('vote_count')
                )
                .join(Rating, Rating.movie_id == Movie.id)
                .group_by(Movie.id)
                .order_by(func.avg(Rating.score).desc())
                .limit(10)
                .all()
            )

            data = []
            for movie, avg_score, vote_count in results:
                movie_dict = movie.to_dict()
                movie_dict['average_rating'] = round(float(avg_score), 2)
                movie_dict['vote_count'] = vote_count
                movie_dict['reason'] = "Top rated (no favorites yet)"
                data.append(movie_dict)

            return {
                "success": True,
                "data": data,
                "message": "No favorites found. Showing top-rated movies."
            }, 200

        # Find the most popular genres in user's favorites
        top_genres = (
            db.session.query(Movie.genre, func.count(Movie.genre).label('cnt'))
            .filter(Movie.id.in_(favorite_movie_ids))
            .group_by(Movie.genre)
            .order_by(func.count(Movie.genre).desc())
            .limit(3)
            .all()
        )
        genre_names = [g[0] for g in top_genres]

        # Find movies in those genres NOT already in favorites
        recommended_query = (
            db.session.query(
                Movie,
                func.avg(Rating.score).label('avg_score'),
                func.count(Rating.id).label('vote_count')
            )
            .outerjoin(Rating, Rating.movie_id == Movie.id)
            .filter(Movie.genre.in_(genre_names))
            .filter(~Movie.id.in_(favorite_movie_ids))
            .group_by(Movie.id)
            .order_by(func.avg(Rating.score).desc().nullslast())
            .limit(10)
            .all()
        )

        data = []
        for movie, avg_score, vote_count in recommended_query:
            movie_dict = movie.to_dict()
            movie_dict['average_rating'] = round(float(avg_score), 2) if avg_score else None
            movie_dict['vote_count'] = vote_count
            movie_dict['reason'] = f"Based on your favorite genre(s): {', '.join(genre_names)}"
            data.append(movie_dict)

        return {"success": True, "data": data}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
