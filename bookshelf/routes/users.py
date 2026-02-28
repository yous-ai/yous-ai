# -*- coding: utf-8 -*-
"""Users CRUD routes + user stats endpoint."""

from flask import Blueprint, request
from models import db, User, Favorite, Rating, Review, Movie
from validators import (validate_email, validate_required_string,
                        check_dangerous_content, check_required_fields)
from sqlalchemy import func

users_bp = Blueprint('users', __name__)


@users_bp.get('/users')
def get_users():
    """List all users with optional pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # cap at 100

        pagination = User.query.order_by(User.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "success": True,
            "data": [u.to_dict() for u in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.get('/users/<int:user_id>')
def get_user(user_id):
    """Get a single user by ID."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404
        return {"success": True, "data": user.to_dict()}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.post('/users')
def create_user():
    """Create a new user."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['username', 'email'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        # Validate username
        valid, err = validate_required_string(data['username'], 'username')
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_USERNAME"}, 400
        valid, err = check_dangerous_content(data['username'])
        if not valid:
            return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400

        # Validate email
        valid, err = validate_email(data['email'])
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_EMAIL"}, 400

        # Check uniqueness
        if User.query.filter_by(email=data['email'].strip()).first():
            return {"success": False, "error": "An account already exists with this email",
                    "code": "DUPLICATE_EMAIL"}, 409

        user = User(username=data['username'].strip(), email=data['email'].strip())
        db.session.add(user)
        db.session.commit()

        return {"success": True, "data": user.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.put('/users/<int:user_id>')
def update_user(user_id):
    """Update user information."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        data = request.get_json(silent=True)
        if not data:
            return {"success": False, "error": "Request body is required",
                    "code": "MISSING_FIELDS"}, 400

        if 'username' in data:
            valid, err = validate_required_string(data['username'], 'username')
            if not valid:
                return {"success": False, "error": err, "code": "INVALID_USERNAME"}, 400
            valid, err = check_dangerous_content(data['username'])
            if not valid:
                return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400
            user.username = data['username'].strip()

        if 'email' in data:
            valid, err = validate_email(data['email'])
            if not valid:
                return {"success": False, "error": err, "code": "INVALID_EMAIL"}, 400
            existing = User.query.filter_by(email=data['email'].strip()).first()
            if existing and existing.id != user_id:
                return {"success": False, "error": "An account already exists with this email",
                        "code": "DUPLICATE_EMAIL"}, 409
            user.email = data['email'].strip()

        db.session.commit()
        return {"success": True, "data": user.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.delete('/users/<int:user_id>')
def delete_user(user_id):
    """Delete a user and cascade to favorites, ratings, reviews."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"success": True, "data": {"message": f"User {user_id} deleted successfully"}}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.get('/users/<int:user_id>/stats')
def get_user_stats(user_id):
    """Return a summary of user activity (business logic endpoint)."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        # Count favorites
        favorites_count = Favorite.query.filter_by(user_id=user_id).count()

        # Count ratings and calculate average
        ratings_count = Rating.query.filter_by(user_id=user_id).count()
        avg_rating = db.session.query(func.avg(Rating.score)).filter(
            Rating.user_id == user_id
        ).scalar()

        # Count reviews
        reviews_count = Review.query.filter_by(user_id=user_id).count()

        # Find favorite genre (most present genre in favorites)
        favorite_genre = None
        genre_result = (
            db.session.query(Movie.genre, func.count(Movie.genre).label('cnt'))
            .join(Favorite, Favorite.movie_id == Movie.id)
            .filter(Favorite.user_id == user_id)
            .group_by(Movie.genre)
            .order_by(func.count(Movie.genre).desc())
            .first()
        )
        if genre_result:
            favorite_genre = genre_result[0]

        return {
            "success": True,
            "data": {
                "user": user.to_dict(),
                "favorites_count": favorites_count,
                "ratings_count": ratings_count,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "reviews_count": reviews_count,
                "favorite_genre": favorite_genre,
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
