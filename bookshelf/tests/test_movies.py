# -*- coding: utf-8 -*-
"""Tests for Movies CRUD + top-rated + summary endpoints."""

import json


def _create_user(client, username="testuser", email="test@test.com"):
    resp = client.post('/users', json={"username": username, "email": email})
    return json.loads(resp.data)['data']['id']


def _create_movie(client, title="Inception", genre="Science-Fiction",
                  release_year=2010, description="A great movie"):
    resp = client.post('/movies', json={
        "title": title, "genre": genre,
        "release_year": release_year, "description": description
    })
    return json.loads(resp.data)['data']['id']


class TestMoviesEndpoints:
    """Test suite for /movies endpoints."""

    def test_get_movies_empty(self, client):
        resp = client.get('/movies')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data'] == []

    def test_create_movie_success(self, client):
        resp = client.post('/movies', json={
            "title": "Inception", "genre": "Science-Fiction",
            "release_year": 2010, "description": "Dream theft"
        })
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['data']['title'] == 'Inception'

    def test_create_movie_missing_title(self, client):
        resp = client.post('/movies', json={
            "genre": "Action", "release_year": 2020
        })
        assert resp.status_code == 400

    def test_create_movie_invalid_genre(self, client):
        resp = client.post('/movies', json={
            "title": "Test", "genre": "InvalidGenre", "release_year": 2020
        })
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data['code'] == 'INVALID_GENRE'

    def test_create_movie_invalid_year(self, client):
        resp = client.post('/movies', json={
            "title": "Test", "genre": "Action", "release_year": 1800
        })
        assert resp.status_code == 400

    def test_create_movie_future_year(self, client):
        resp = client.post('/movies', json={
            "title": "Test", "genre": "Action", "release_year": 2099
        })
        assert resp.status_code == 400

    def test_get_movie_by_id(self, client):
        movie_id = _create_movie(client)
        resp = client.get(f'/movies/{movie_id}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['title'] == 'Inception'

    def test_get_movie_not_found(self, client):
        resp = client.get('/movies/9999')
        assert resp.status_code == 404

    def test_update_movie_success(self, client):
        movie_id = _create_movie(client)
        resp = client.put(f'/movies/{movie_id}', json={"title": "Inception 2"})
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['title'] == 'Inception 2'

    def test_delete_movie_success(self, client):
        movie_id = _create_movie(client)
        resp = client.delete(f'/movies/{movie_id}')
        assert resp.status_code == 200

    def test_filter_by_genre(self, client):
        _create_movie(client, "A", "Action", 2020)
        _create_movie(client, "B", "Comedy", 2020)
        resp = client.get('/movies?genre=Action')
        data = json.loads(resp.data)
        assert len(data['data']) == 1
        assert data['data'][0]['genre'] == 'Action'

    def test_filter_by_year(self, client):
        _create_movie(client, "A", "Action", 2020)
        _create_movie(client, "B", "Action", 2021)
        resp = client.get('/movies?release_year=2020')
        data = json.loads(resp.data)
        assert len(data['data']) == 1

    def test_dangerous_title(self, client):
        resp = client.post('/movies', json={
            "title": "<script>alert('xss')</script>",
            "genre": "Action", "release_year": 2020
        })
        assert resp.status_code == 400


class TestTopRated:
    """Tests for GET /movies/top-rated."""

    def test_top_rated_no_movies(self, client):
        resp = client.get('/movies/top-rated')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data'] == []

    def test_top_rated_with_ratings(self, client):
        movie_id = _create_movie(client)
        for i in range(3):
            uid = _create_user(client, f"user{i}", f"user{i}@test.com")
            client.post('/ratings', json={
                "user_id": uid, "movie_id": movie_id, "score": 4.5
            })
        resp = client.get('/movies/top-rated')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data['data']) >= 1
        assert data['data'][0]['average_rating'] == 4.5


class TestMovieSummary:
    """Tests for GET /movies/:id/summary."""

    def test_summary_basic(self, client):
        movie_id = _create_movie(client)
        resp = client.get(f'/movies/{movie_id}/summary')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['movie']['title'] == 'Inception'
        assert data['data']['vote_count'] == 0

    def test_summary_not_found(self, client):
        resp = client.get('/movies/9999/summary')
        assert resp.status_code == 404

    def test_summary_with_user_context(self, client):
        user_id = _create_user(client)
        movie_id = _create_movie(client)
        client.post('/favorites', json={"user_id": user_id, "movie_id": movie_id})
        client.post('/ratings', json={"user_id": user_id, "movie_id": movie_id, "score": 4})
        resp = client.get(f'/movies/{movie_id}/summary?user_id={user_id}')
        data = json.loads(resp.data)
        assert data['data']['current_user']['is_favorite'] is True
        assert data['data']['current_user']['user_rating'] == 4
