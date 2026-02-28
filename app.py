# -*- coding: utf-8 -*-
"""Film Management API — Flask Application."""

from flask import Flask
from dotenv import load_dotenv
from models import db
import os

# Load environment variables
load_dotenv()


def create_app(testing=False):
    """Application factory."""
    app = Flask(__name__)

    # Database configuration
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL', 'sqlite:///bookshelf.db'
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY', 'dev-secret-key-change-in-production'
    )

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.movies import movies_bp
    from routes.favorites import favorites_bp
    from routes.ratings import ratings_bp
    from routes.reviews import reviews_bp
    from routes.recommendations import recommendations_bp
    from routes.sentiment import sentiment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(ratings_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(sentiment_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


# Create the app instance for running directly
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)