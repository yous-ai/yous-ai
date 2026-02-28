# -*- coding: utf-8 -*-
"""JWT authentication middleware."""

import jwt
from functools import wraps
from flask import request, g, current_app
from models import db, User


def token_required(f):
    """Decorator: route requires a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return {
                "success": False,
                "error": "Token d'authentification requis",
                "code": "AUTH_REQUIRED"
            }, 401

        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user = db.session.get(User, payload['user_id'])
            if not user:
                return {
                    "success": False,
                    "error": "Utilisateur introuvable",
                    "code": "USER_NOT_FOUND"
                }, 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return {
                "success": False,
                "error": "Token expiré",
                "code": "TOKEN_EXPIRED"
            }, 401
        except jwt.InvalidTokenError:
            return {
                "success": False,
                "error": "Token invalide",
                "code": "TOKEN_INVALID"
            }, 401

        return f(*args, **kwargs)
    return decorated


def token_optional(f):
    """Decorator: extracts user from JWT if present, but doesn't block."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        g.current_user = None

        if token:
            try:
                payload = jwt.decode(
                    token,
                    current_app.config['JWT_SECRET_KEY'],
                    algorithms=['HS256']
                )
                user = db.session.get(User, payload['user_id'])
                if user:
                    g.current_user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass  # Silently ignore bad tokens on optional routes

        return f(*args, **kwargs)
    return decorated


def _extract_token():
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None
