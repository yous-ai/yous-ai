# -*- coding: utf-8 -*-
"""Input validators and sanitizers for the Film Management API."""

import re
from datetime import datetime

# Allowed genres for movies
ALLOWED_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Fantasy", "Horror", "Musical", "Mystery", "Romance",
    "Science-Fiction", "Thriller", "War", "Western",
]

# Patterns to detect potentially malicious content
DANGEROUS_HTML_PATTERN = re.compile(r'<\s*(script|iframe|object|embed|form|link|style)', re.IGNORECASE)
SQL_INJECTION_PATTERN = re.compile(
    r'\b(DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|'
    r'SELECT\s+\*|UNION\s+SELECT|ALTER\s+TABLE|EXEC\s*\(|EXECUTE\s*\()\b|'
    r'(--|;)\s*$',
    re.IGNORECASE
)
EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

MAX_TEXT_LENGTH = 2000
MAX_FIELD_LENGTH = 300


def validate_email(email):
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    email = email.strip()
    if not EMAIL_PATTERN.match(email):
        return False, "Invalid email format"
    if len(email) > MAX_FIELD_LENGTH:
        return False, f"Email must be less than {MAX_FIELD_LENGTH} characters"
    return True, None


def validate_required_string(value, field_name, max_length=MAX_FIELD_LENGTH):
    """Validate a required string field. Returns (is_valid, error_message)."""
    if not value or not isinstance(value, str) or not value.strip():
        return False, f"{field_name} is required and must be a non-empty string"
    if len(value.strip()) > max_length:
        return False, f"{field_name} must be less than {max_length} characters"
    return True, None


def validate_rating_score(score):
    """Validate a rating score (1-5, decimals allowed). Returns (is_valid, error_message)."""
    if score is None:
        return False, "Score is required"
    try:
        score = float(score)
    except (ValueError, TypeError):
        return False, "Score must be a number"
    if score < 1 or score > 5:
        return False, "Score must be between 1 and 5"
    return True, None


def validate_release_year(year):
    """Validate movie release year. Returns (is_valid, error_message)."""
    if year is None:
        return False, "Release year is required"
    try:
        year = int(year)
    except (ValueError, TypeError):
        return False, "Release year must be an integer"
    current_year = datetime.now().year
    if year < 1888 or year > current_year:
        return False, f"Release year must be between 1888 and {current_year}"
    return True, None


def validate_genre(genre):
    """Validate movie genre against allowed list. Returns (is_valid, error_message)."""
    if not genre or not isinstance(genre, str):
        return False, "Genre is required"
    if genre.strip() not in ALLOWED_GENRES:
        return False, f"Genre must be one of: {', '.join(ALLOWED_GENRES)}"
    return True, None


def validate_positive_int(value, field_name):
    """Validate that a value is a positive integer. Returns (is_valid, error_message)."""
    if value is None:
        return False, f"{field_name} is required"
    try:
        value = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be an integer"
    if value <= 0:
        return False, f"{field_name} must be a positive integer"
    return True, None


def check_dangerous_content(text):
    """Check text for potentially dangerous content (HTML/JS injection, SQL injection).
    Returns (is_safe, error_message)."""
    if not text or not isinstance(text, str):
        return True, None
    if DANGEROUS_HTML_PATTERN.search(text):
        return False, "Content contains potentially dangerous HTML/JavaScript tags"
    if SQL_INJECTION_PATTERN.search(text):
        return False, "Content contains potentially dangerous SQL patterns"
    if len(text) > MAX_TEXT_LENGTH:
        return False, f"Content must be less than {MAX_TEXT_LENGTH} characters"
    return True, None


def check_required_fields(data, fields):
    """Check that all required fields exist in data dict.
    Returns (is_valid, missing_field_name or None)."""
    if not data or not isinstance(data, dict):
        return False, "Request body is required"
    for field in fields:
        if field not in data or data[field] is None:
            return False, f"{field} is required"
    return True, None
