# -*- coding: utf-8 -*-
"""Ratings CRUD routes + smart update with history (business logic)."""

from flask import Blueprint, request, g
from models import db, Rating, RatingHistory, User, Movie
from validators import (validate_positive_int, validate_rating_score,
                        check_required_fields)
from middleware import token_required

ratings_bp = Blueprint('ratings', __name__)


@ratings_bp.get('/ratings/<int:user_id>')
def get_user_ratings(user_id):
    """List all ratings by a user."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        ratings = (
            Rating.query
            .filter_by(user_id=user_id)
            .order_by(Rating.created_at.desc())
            .all()
        )

        data = []
        for rat in ratings:
            entry = rat.to_dict()
            movie = db.session.get(Movie, rat.movie_id)
            if movie:
                entry['movie_title'] = movie.title
            data.append(entry)

        return {"success": True, "data": data}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@ratings_bp.post('/ratings')
@token_required
def create_rating():
    """Add a new rating for a movie."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['movie_id', 'score'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        valid, err = validate_positive_int(data['movie_id'], 'movie_id')
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_MOVIE_ID"}, 400

        valid, err = validate_rating_score(data['score'])
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_RATING"}, 400

        user_id = g.current_user.id
        movie_id = int(data['movie_id'])
        score = float(data['score'])

        if not db.session.get(Movie, movie_id):
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        # Check if rating already exists
        existing = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing:
            return {"success": False, "error": "Rating already exists. Use PUT to update.",
                    "code": "DUPLICATE_RATING"}, 409

        rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
        db.session.add(rating)
        db.session.commit()

        return {"success": True, "data": rating.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@ratings_bp.put('/ratings')
@token_required
def update_rating():
    """Smart update: update existing rating and record history (business logic)."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['movie_id', 'score'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        valid, err = validate_rating_score(data['score'])
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_RATING"}, 400

        user_id = g.current_user.id
        movie_id = int(data['movie_id'])
        new_score = float(data['score'])

        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not rating:
            return {"success": False, "error": "No existing rating found for this user/movie pair",
                    "code": "NOT_FOUND"}, 404

        old_score = rating.score

        # Record history
        history_entry = RatingHistory(
            rating_id=rating.id,
            old_score=old_score,
            new_score=new_score
        )
        db.session.add(history_entry)

        # Update the rating
        rating.score = new_score
        db.session.commit()

        delta = round(new_score - old_score, 2)

        return {
            "success": True,
            "data": {
                "rating": rating.to_dict(),
                "previous_score": old_score,
                "new_score": new_score,
                "delta": delta,
            }
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@ratings_bp.delete('/ratings')
def delete_rating():
    """Delete a rating."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['user_id', 'movie_id'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        user_id = int(data['user_id'])
        movie_id = int(data['movie_id'])

        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not rating:
            return {"success": False, "error": "Rating not found", "code": "NOT_FOUND"}, 404

        db.session.delete(rating)
        db.session.commit()

        return {"success": True, "data": {"message": "Rating deleted successfully"}}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
