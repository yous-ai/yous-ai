# -*- coding: utf-8 -*-
"""Sentiment analysis route using HuggingFace Transformers."""

from flask import Blueprint, request
from transformers import pipeline

# Load the sentiment analysis model (loaded once at import time)
sentiment_pipeline = pipeline("sentiment-analysis")

sentiment_bp = Blueprint('sentiment', __name__)


@sentiment_bp.post('/sentiment')
def analyze_sentiment():
    """Analyze the sentiment of a given text."""
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("text"):
            return {
                "success": False,
                "error": "text is required",
                "code": "MISSING_FIELDS"
            }, 400

        text = data["text"]

        if not isinstance(text, str) or not text.strip():
            return {
                "success": False,
                "error": "text must be a non-empty string",
                "code": "INVALID_TEXT"
            }, 400

        # Limit text length to avoid memory issues
        if len(text) > 5000:
            return {
                "success": False,
                "error": "text must be less than 5000 characters",
                "code": "TEXT_TOO_LONG"
            }, 400

        result = sentiment_pipeline(text)[0]

        return {
            "success": True,
            "data": {
                "label": result["label"],
                "score": round(result["score"], 4),
                "text": text
            }
        }, 200
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": "INTERNAL_ERROR"
        }, 500
