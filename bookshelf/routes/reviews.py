# -*- coding: utf-8 -*-
"""Reviews CRUD routes + report system (business logic)."""

from flask import Blueprint, request, g
from models import db, Review, Report, User, Movie
from validators import (validate_positive_int, validate_required_string,
                        check_dangerous_content, check_required_fields)
from middleware import token_required, token_optional

REPORT_THRESHOLD = 5  # Auto-hide review after this many reports

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.get('/reviews/<int:movie_id>')
def get_reviews(movie_id):
    """List all non-hidden reviews for a movie, with sentiment analysis."""
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        reviews = (
            Review.query
            .filter_by(movie_id=movie_id, is_hidden=False)
            .order_by(Review.created_at.desc())
            .all()
        )

        # Analyze sentiment for each review
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        reviews_data = []
        for r in reviews:
            review_dict = r.to_dict()
            try:
                from routes.sentiment import sentiment_pipeline
                result = sentiment_pipeline(r.content[:512])[0]
                label = result["label"].lower()
                if label == "positive":
                    review_dict["sentiment"] = "positive"
                    sentiments["positive"] += 1
                elif label == "negative":
                    review_dict["sentiment"] = "negative"
                    sentiments["negative"] += 1
                else:
                    review_dict["sentiment"] = "neutral"
                    sentiments["neutral"] += 1
            except Exception:
                review_dict["sentiment"] = "neutral"
                sentiments["neutral"] += 1
            reviews_data.append(review_dict)

        return {
            "success": True,
            "data": reviews_data,
            "sentiments": sentiments
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@reviews_bp.post('/reviews')
@token_required
def create_review():
    """Add a new review for a movie."""
    try:
        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['movie_id', 'content'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        valid, err = validate_positive_int(data['movie_id'], 'movie_id')
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_MOVIE_ID"}, 400

        # Validate content
        valid, err = validate_required_string(data['content'], 'content', max_length=2000)
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_CONTENT"}, 400

        valid, err = check_dangerous_content(data['content'])
        if not valid:
            return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400

        user_id = g.current_user.id
        movie_id = int(data['movie_id'])

        if not db.session.get(Movie, movie_id):
            return {"success": False, "error": "Movie not found", "code": "NOT_FOUND"}, 404

        review = Review(
            user_id=user_id,
            movie_id=movie_id,
            content=data['content'].strip()
        )
        db.session.add(review)
        db.session.commit()

        return {"success": True, "data": review.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@reviews_bp.put('/reviews/<int:review_id>')
def update_review(review_id):
    """Update a review (user_id in body to verify ownership)."""
    try:
        review = db.session.get(Review, review_id)
        if not review:
            return {"success": False, "error": "Review not found", "code": "NOT_FOUND"}, 404

        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['user_id', 'content'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        # Verify ownership
        user_id = int(data['user_id'])
        if review.user_id != user_id:
            return {"success": False, "error": "You can only edit your own reviews",
                    "code": "FORBIDDEN"}, 403

        # Validate content
        valid, err = validate_required_string(data['content'], 'content', max_length=2000)
        if not valid:
            return {"success": False, "error": err, "code": "INVALID_CONTENT"}, 400

        valid, err = check_dangerous_content(data['content'])
        if not valid:
            return {"success": False, "error": err, "code": "DANGEROUS_CONTENT"}, 400

        review.content = data['content'].strip()
        db.session.commit()

        return {"success": True, "data": review.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@reviews_bp.delete('/reviews/<int:review_id>')
def delete_review(review_id):
    """Delete a review (user_id in body to verify ownership)."""
    try:
        review = db.session.get(Review, review_id)
        if not review:
            return {"success": False, "error": "Review not found", "code": "NOT_FOUND"}, 404

        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['user_id'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        user_id = int(data['user_id'])
        if review.user_id != user_id:
            return {"success": False, "error": "You can only delete your own reviews",
                    "code": "FORBIDDEN"}, 403

        db.session.delete(review)
        db.session.commit()

        return {"success": True, "data": {"message": "Review deleted successfully"}}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500


@reviews_bp.post('/reviews/<int:review_id>/report')
def report_review(review_id):
    """Report a review as inappropriate (business logic)."""
    try:
        review = db.session.get(Review, review_id)
        if not review:
            return {"success": False, "error": "Review not found", "code": "NOT_FOUND"}, 404

        data = request.get_json(silent=True)
        valid, err = check_required_fields(data, ['user_id'])
        if not valid:
            return {"success": False, "error": err, "code": "MISSING_FIELDS"}, 400

        user_id = int(data['user_id'])

        if not db.session.get(User, user_id):
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}, 404

        # Cannot report own review
        if review.user_id == user_id:
            return {"success": False, "error": "You cannot report your own review",
                    "code": "SELF_REPORT"}, 400

        # Cannot report same review twice
        existing_report = Report.query.filter_by(review_id=review_id, user_id=user_id).first()
        if existing_report:
            return {"success": False, "error": "You have already reported this review",
                    "code": "DUPLICATE_REPORT"}, 409

        report = Report(review_id=review_id, user_id=user_id)
        db.session.add(report)

        # Check if threshold is reached — auto-hide
        report_count = Report.query.filter_by(review_id=review_id).count()
        if report_count >= REPORT_THRESHOLD:
            review.is_hidden = True

        db.session.commit()

        return {
            "success": True,
            "data": {
                "message": "Review reported successfully",
                "report_count": report_count,
                "is_hidden": review.is_hidden,
            }
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e), "code": "INTERNAL_ERROR"}, 500
