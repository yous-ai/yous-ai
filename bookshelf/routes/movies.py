# -*- coding: utf-8 -*-
"""Movies CRUD routes + top-rated and summary business logic endpoints."""

from flask import Blueprint, request
from models import db, Movie, Rating, Review, Favorite
from validators import (validate_required_string, validate_release_year,
                        validate_genre, check_dangerous_content,
                        check_required_fields)
from sqlalchemy import func

movies_bp = Blueprint('movies', __name__)


@movies_bp.get('/movies')
def get_movies():
    """List all movies with optional genre and release_year filters."""
    try:
        query = Movie.query

        genre = request.args.get('genre')
        if genre:
            query = query.filter(Movie.genre == genre)

        release_year = request.args.get('release_year')
        if release_year:
            try:
                release_year = int(release_year)
                query = query.filter(Movie.release_year == release_year)
            except (ValueError, TypeError):
                return {"success": False, "error": "release_year must be an integer",
                        "code": "INVALID_FILTER"}, 400

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)

        pagination = query.order_by(Movie.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "success": True,
            "data": [m.to_dict() for m in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.get('/movies/top-rated')
def get_top_rated():
    """Return movies sorted by average rating (business logic)."""
    try:
        min_votes = request.args.get('min_votes', 3, type=int)

        results = (
            db.session.query(
                Movie,
                func.avg(Rating.score).label('avg_score'),
                func.count(Rating.id).label('vote_count')
            )
            .join(Rating, Rating.movie_id == Movie.id)
            .group_by(Movie.id)
            .having(func.count(Rating.id) >= min_votes)
            .order_by(func.avg(Rating.score).desc())
            .all()
        )

        if not results:
            return {
                "success": True,
                "data": [],
                "message": f"No movies found with at least {min_votes} ratings"
            }, 200

        data = []
        for movie, avg_score, vote_count in results:
            movie_dict = movie.to_dict()
            movie_dict['average_rating'] = round(float(avg_score), 2)
            movie_dict['vote_count'] = vote_count
            data.append(movie_dict)

        return {"success": True, "data": data}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.get('/movies/<int:movie_id>')
def get_movie(movie_id):
    """Get a single movie by ID."""
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404
        return {"success": True, "data": movie.to_dict()}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.post('/movies')
def create_movie():
    """Create a new movie."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['title', 'genre', 'release_year'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        # Validate title
        valid, err = validate_required_string(data['title'], 'title')
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_TITLE"}, 400
        valid, err = check_dangerous_content(data['title'])
        if not valid:
            return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400

        # Validate genre
        valid, err = validate_genre(data['genre'])
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_GENRE"}, 400

        # Validate release_year
        valid, err = validate_release_year(data['release_year'])
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_YEAR"}, 400

        # Validate description if provided
        description = data.get('description', '')
        if description:
            valid, err = check_dangerous_content(description)
            if not valid:
                return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400

        movie = Movie(
            title=data['title'].strip(),
            genre=data['genre'].strip(),
            release_year=int(data['release_year']),
            description=description.strip() if description else ''
        )
        db.session.add(movie)
        db.session.commit()

        return {"success": True, "data": movie.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.put('/movies/<int:movie_id>')
def update_movie(movie_id):
    """Update movie information."""
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        data = request.get_json(silent=True)
        if not data:
            return {"success": False, "error": "Request body is required",
                    "code": "MISSING_FIELDS"}, 400

        if 'title' in data:
            valid, err = validate_required_string(data['title'], 'title')
            if not valid:
                return {"success": False, "error": err, "code": "INVALID_TITLE"}, 400
            valid, err = check_dangerous_content(data['title'])
            if not valid:
                return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400
            movie.title = data['title'].strip()

        if 'genre' in data:
            valid, err = validate_genre(data['genre'])
            if not valid:
                return {"success": False, "error": err, "code": "INVALID_GENRE"}, 400
            movie.genre = data['genre'].strip()

        if 'release_year' in data:
            valid, err = validate_release_year(data['release_year'])
            if not valid:
                return {"success": False, "error": err, "code": "INVALID_YEAR"}, 400
            movie.release_year = int(data['release_year'])

        if 'description' in data:
            valid, err = check_dangerous_content(data['description'])
            if not valid:
                return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400
            movie.description = data['description'].strip() if data['description'] else ''

        db.session.commit()
        return {"success": True, "data": movie.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.delete('/movies/<int:movie_id>')
def delete_movie(movie_id):
    """Delete a movie and cascade to ratings, reviews, favorites."""
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        db.session.delete(movie)
        db.session.commit()
        return {"success": True, "data": {"message": f"Movie {movie_id} deleted successfully"}}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@movies_bp.get('/movies/<int:movie_id>/summary')
def get_movie_summary(movie_id):
    """Return a complete summary of a movie (business logic)."""
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        # Average rating and vote count
        rating_stats = db.session.query(
            func.avg(Rating.score).label('avg_score'),
            func.count(Rating.id).label('vote_count')
        ).filter(Rating.movie_id == movie_id).first()

        avg_score = round(float(rating_stats.avg_score), 2) if rating_stats.avg_score else None
        vote_count = rating_stats.vote_count or 0

        # 3 most recent non-hidden reviews
        recent_reviews = (
            Review.query
            .filter_by(movie_id=movie_id, is_hidden=False)
            .order_by(Review.created_at.desc())
            .limit(3)
            .all()
        )

        # Favorites count
        favorites_count = Favorite.query.filter_by(movie_id=movie_id).count()

        # Optional: check if a specific user has this movie in favorites / their rating
        user_id = request.args.get('user_id', type=int)
        user_favorite = None
        user_rating = None
        if user_id:
            fav = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
            user_favorite = fav is not None
            rat = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
            user_rating = rat.score if rat else None

        summary = {
            "movie": movie.to_dict(),
            "average_rating": avg_score,
            "vote_count": vote_count,
            "recent_reviews": [r.to_dict() for r in recent_reviews],
            "favorites_count": favorites_count,
        }

        if user_id:
            summary["current_user"] = {
                "is_favorite": user_favorite,
                "user_rating": user_rating,
            }

        return {"success": True, "data": summary}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
