# -*- coding: utf-8 -*-
"""Tests for Favorites, Ratings, Reviews, Reports, and Recommendations."""

import json


def _create_user(client, username="testuser", email="test@test.com"):
    resp = client.post('/users', json={"username": username, "email": email})
    return json.loads(resp.data)['data']['id']


def _create_movie(client, title="Inception", genre="Science-Fiction",
                  release_year=2010):
    resp = client.post('/movies', json={
        "title": title, "genre": genre, "release_year": release_year,
        "description": "Test movie"
    })
    return json.loads(resp.data)['data']['id']


# --- FAVORITES ---
class TestFavorites:

    def test_add_favorite(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/favorites', json={"user_id": uid, "movie_id": mid})
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['success'] is True

    def test_add_duplicate_favorite(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/favorites', json={"user_id": uid, "movie_id": mid})
        resp = client.post('/favorites', json={"user_id": uid, "movie_id": mid})
        assert resp.status_code == 409

    def test_get_favorites(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/favorites', json={"user_id": uid, "movie_id": mid})
        resp = client.get(f'/favorites/{uid}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data['data']) == 1

    def test_remove_favorite(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/favorites', json={"user_id": uid, "movie_id": mid})
        resp = client.delete('/favorites', json={"user_id": uid, "movie_id": mid})
        assert resp.status_code == 200

    def test_add_favorite_user_not_found(self, client):
        mid = _create_movie(client)
        resp = client.post('/favorites', json={"user_id": 9999, "movie_id": mid})
        assert resp.status_code == 404

    def test_add_favorite_movie_not_found(self, client):
        uid = _create_user(client)
        resp = client.post('/favorites', json={"user_id": uid, "movie_id": 9999})
        assert resp.status_code == 404


# --- RATINGS ---
class TestRatings:

    def test_create_rating(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/ratings', json={
            "user_id": uid, "movie_id": mid, "score": 4.5
        })
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['data']['score'] == 4.5

    def test_create_rating_invalid_score(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/ratings', json={
            "user_id": uid, "movie_id": mid, "score": 6
        })
        assert resp.status_code == 400

    def test_create_rating_zero_score(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/ratings', json={
            "user_id": uid, "movie_id": mid, "score": 0
        })
        assert resp.status_code == 400

    def test_duplicate_rating(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/ratings', json={"user_id": uid, "movie_id": mid, "score": 3})
        resp = client.post('/ratings', json={"user_id": uid, "movie_id": mid, "score": 4})
        assert resp.status_code == 409

    def test_smart_update_rating(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/ratings', json={"user_id": uid, "movie_id": mid, "score": 3})
        resp = client.put('/ratings', json={"user_id": uid, "movie_id": mid, "score": 5})
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['previous_score'] == 3
        assert data['data']['new_score'] == 5
        assert data['data']['delta'] == 2.0

    def test_get_user_ratings(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/ratings', json={"user_id": uid, "movie_id": mid, "score": 4})
        resp = client.get(f'/ratings/{uid}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data['data']) == 1

    def test_delete_rating(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/ratings', json={"user_id": uid, "movie_id": mid, "score": 4})
        resp = client.delete('/ratings', json={"user_id": uid, "movie_id": mid})
        assert resp.status_code == 200


# --- REVIEWS ---
class TestReviews:

    def test_create_review(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid, "content": "Great movie!"
        })
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['data']['content'] == 'Great movie!'

    def test_create_review_dangerous_content(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid,
            "content": "<script>alert('xss')</script>"
        })
        assert resp.status_code == 400

    def test_create_review_sql_injection(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid,
            "content": "DROP TABLE users;--"
        })
        assert resp.status_code == 400

    def test_get_reviews(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        client.post('/reviews', json={
            "user_id": uid, "movie_id": mid, "content": "Nice film"
        })
        resp = client.get(f'/reviews/{mid}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data['data']) == 1

    def test_update_own_review(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid, "content": "Good"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        resp = client.put(f'/reviews/{review_id}', json={
            "user_id": uid, "content": "Updated review"
        })
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['content'] == 'Updated review'

    def test_update_other_user_review(self, client):
        uid1 = _create_user(client, "user1", "u1@test.com")
        uid2 = _create_user(client, "user2", "u2@test.com")
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid1, "movie_id": mid, "content": "My review"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        resp = client.put(f'/reviews/{review_id}', json={
            "user_id": uid2, "content": "Hacked review"
        })
        assert resp.status_code == 403

    def test_delete_own_review(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid, "content": "To delete"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        resp = client.delete(f'/reviews/{review_id}', json={"user_id": uid})
        assert resp.status_code == 200


# --- REPORTS ---
class TestReports:

    def test_report_review(self, client):
        uid1 = _create_user(client, "author", "author@test.com")
        uid2 = _create_user(client, "reporter", "reporter@test.com")
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid1, "movie_id": mid, "content": "Offensive content"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        resp = client.post(f'/reviews/{review_id}/report', json={"user_id": uid2})
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['data']['report_count'] == 1

    def test_cannot_report_own_review(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid, "movie_id": mid, "content": "My review"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        resp = client.post(f'/reviews/{review_id}/report', json={"user_id": uid})
        assert resp.status_code == 400

    def test_cannot_report_twice(self, client):
        uid1 = _create_user(client, "author", "a@test.com")
        uid2 = _create_user(client, "reporter", "r@test.com")
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": uid1, "movie_id": mid, "content": "Content"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        client.post(f'/reviews/{review_id}/report', json={"user_id": uid2})
        resp = client.post(f'/reviews/{review_id}/report', json={"user_id": uid2})
        assert resp.status_code == 409

    def test_auto_hide_after_threshold(self, client):
        author = _create_user(client, "author", "author@test.com")
        mid = _create_movie(client)
        create_resp = client.post('/reviews', json={
            "user_id": author, "movie_id": mid, "content": "Bad review"
        })
        review_id = json.loads(create_resp.data)['data']['id']
        # Create 5 reporters and report
        for i in range(5):
            reporter = _create_user(client, f"reporter{i}", f"rep{i}@test.com")
            resp = client.post(f'/reviews/{review_id}/report', json={"user_id": reporter})
        data = json.loads(resp.data)
        assert data['data']['is_hidden'] is True


# --- RECOMMENDATIONS ---
class TestRecommendations:

    def test_recommendations_no_favorites(self, client):
        uid = _create_user(client)
        mid = _create_movie(client)
        # Add a rating so there's a top-rated movie
        uid2 = _create_user(client, "rater", "rater@test.com")
        client.post('/ratings', json={"user_id": uid2, "movie_id": mid, "score": 5})
        resp = client.get(f'/movies/recommendations/{uid}')
        data = json.loads(resp.data)
        assert resp.status_code == 200

    def test_recommendations_with_favorites(self, client):
        uid = _create_user(client)
        # Create sci-fi movies
        mid1 = _create_movie(client, "Interstellar", "Science-Fiction", 2014)
        mid2 = _create_movie(client, "The Matrix", "Science-Fiction", 1999)
        mid3 = _create_movie(client, "Blade Runner", "Science-Fiction", 1982)
        # Add one to favorites
        client.post('/favorites', json={"user_id": uid, "movie_id": mid1})
        # Recommendations should include the others
        resp = client.get(f'/movies/recommendations/{uid}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        rec_ids = [m['id'] for m in data['data']]
        assert mid1 not in rec_ids  # should not recommend what's already a favorite

    def test_recommendations_user_not_found(self, client):
        resp = client.get('/movies/recommendations/9999')
        assert resp.status_code == 404
