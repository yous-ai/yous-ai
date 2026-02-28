# -*- coding: utf-8 -*-
"""Authentication routes — login with username, get JWT token."""

import jwt
import datetime
from flask import Blueprint, request, g, current_app
from models import db, User
from middleware import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/auth/login')
def login():
    """Login with username. Auto-creates user if not found. Returns JWT."""
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('username'):
            return {
                "success": False,
                "error": "Le champ 'username' est requis",
                "code": "MISSING_FIELDS"
            }, 400

        username = data['username'].strip()
        if not username or len(username) < 2:
            return {
                "success": False,
                "error": "Le username doit contenir au moins 2 caractères",
                "code": "INVALID_USERNAME"
            }, 400

        if len(username) > 100:
            return {
                "success": False,
                "error": "Le username ne doit pas dépasser 100 caractères",
                "code": "INVALID_USERNAME"
            }, 400

        # Find or create user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                email=f"{username.lower().replace(' ', '_')}@films.local"
            )
            db.session.add(user)
            db.session.commit()

        # Generate JWT token (expires in 24h)
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )

        return {
            "success": True,
            "data": {
                "token": token,
                "user": user.to_dict()
            }
        }, 200
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "error": str(e),
            "code": "INTERNAL_ERROR"
        }, 500


@auth_bp.get('/auth/me')
@token_required
def get_me():
    """Return current user info from JWT token."""
    try:
        return {
            "success": True,
            "data": g.current_user.to_dict()
        }, 200
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": "INTERNAL_ERROR"
        }, 500
