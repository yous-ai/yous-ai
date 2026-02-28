# -*- coding: utf-8 -*-
"""Favorites CRUD routes."""

from flask import Blueprint, request, g
from models import db, Favorite, User, Movie
from validators import validate_positive_int, check_required_fields
from middleware import token_required

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.get('/favorites/<int:user_id>')
def get_favorites(user_id):
    """List all favorite movies for a user."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        favorites = (
            Favorite.query
            .filter_by(user_id=user_id)
            .order_by(Favorite.added_at.desc())
            .all()
        )

        data = []
        for fav in favorites:
            movie = db.session.get(Movie, fav.movie_id)
            entry = fav.to_dict()
            if movie:
                entry['movie'] = movie.to_dict()
            data.append(entry)

        return {"success": True, "data": data}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@favorites_bp.post('/favorites')
@token_required
def add_favorite():
    """Add a movie to user's favorites."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['movie_id'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        valid, err = validate_positive_int(data['movie_id'], 'movie_id')
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_MOVIE_ID"}, 400

        user_id = g.current_user.id
        movie_id = int(data['movie_id'])

        # Check movie exists
        if not db.session.get(Movie, movie_id):
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        # Check duplicate
        existing = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing:
            return {"success": False, "error": "Movie is already in favorites",
                    "code": "DUPLICATE_FAVORITE"}, 409

        favorite = Favorite(user_id=user_id, movie_id=movie_id)
        db.session.add(favorite)
        db.session.commit()

        return {"success": True, "data": favorite.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@favorites_bp.delete('/favorites')
def remove_favorite():
    """Remove a movie from user's favorites."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['user_id', 'movie_id'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        user_id = int(data['user_id'])
        movie_id = int(data['movie_id'])

        favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not favorite:
            return {"success": False, "error": "Favorite not found", "code": "NOT_FOUND"}, 404

        db.session.delete(favorite)
        db.session.commit()

        return {"success": True, "data": {"message": "Favorite removed successfully"}}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
