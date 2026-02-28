# -*- coding: utf-8 -*-
"""Tests for Users CRUD + stats endpoint."""

import json


class TestUsersEndpoints:
    """Test suite for /users endpoints."""

    # --- GET /users ---
    def test_get_users_empty(self, client):
        resp = client.get('/users')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['data'] == []

    def test_get_users_with_data(self, client):
        client.post('/users', json={"username": "alice", "email": "alice@test.com"})
        resp = client.get('/users')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data['data']) == 1
        assert data['data'][0]['username'] == 'alice'

    # --- GET /users/:id ---
    def test_get_user_by_id(self, client):
        create_resp = client.post('/users', json={"username": "bob", "email": "bob@test.com"})
        user_id = json.loads(create_resp.data)['data']['id']
        resp = client.get(f'/users/{user_id}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['username'] == 'bob'

    def test_get_user_not_found(self, client):
        resp = client.get('/users/9999')
        data = json.loads(resp.data)
        assert resp.status_code == 404
        assert data['success'] is False

    # --- POST /users ---
    def test_create_user_success(self, client):
        resp = client.post('/users', json={"username": "charlie", "email": "charlie@test.com"})
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['data']['username'] == 'charlie'
        assert data['data']['email'] == 'charlie@test.com'

    def test_create_user_missing_username(self, client):
        resp = client.post('/users', json={"email": "test@test.com"})
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data['success'] is False

    def test_create_user_missing_email(self, client):
        resp = client.post('/users', json={"username": "test"})
        data = json.loads(resp.data)
        assert resp.status_code == 400

    def test_create_user_invalid_email(self, client):
        resp = client.post('/users', json={"username": "test", "email": "not-an-email"})
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data['code'] == 'INVALID_EMAIL'

    def test_create_user_duplicate_email(self, client):
        client.post('/users', json={"username": "user1", "email": "dup@test.com"})
        resp = client.post('/users', json={"username": "user2", "email": "dup@test.com"})
        data = json.loads(resp.data)
        assert resp.status_code == 409
        assert data['code'] == 'DUPLICATE_EMAIL'

    def test_create_user_empty_body(self, client):
        resp = client.post('/users', json={})
        data = json.loads(resp.data)
        assert resp.status_code == 400

    def test_create_user_dangerous_content(self, client):
        resp = client.post('/users', json={
            "username": "<script>alert('xss')</script>",
            "email": "xss@test.com"
        })
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data['code'] == 'DANGEROUS_CONTENT'

    # --- PUT /users/:id ---
    def test_update_user_success(self, client):
        create_resp = client.post('/users', json={"username": "old", "email": "old@test.com"})
        user_id = json.loads(create_resp.data)['data']['id']
        resp = client.put(f'/users/{user_id}', json={"username": "new"})
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['username'] == 'new'

    def test_update_user_not_found(self, client):
        resp = client.put('/users/9999', json={"username": "new"})
        assert resp.status_code == 404

    # --- DELETE /users/:id ---
    def test_delete_user_success(self, client):
        create_resp = client.post('/users', json={"username": "todelete", "email": "del@test.com"})
        user_id = json.loads(create_resp.data)['data']['id']
        resp = client.delete(f'/users/{user_id}')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['success'] is True

    def test_delete_user_not_found(self, client):
        resp = client.delete('/users/9999')
        assert resp.status_code == 404

    # --- GET /users/:id/stats ---
    def test_get_user_stats_empty(self, client):
        create_resp = client.post('/users', json={"username": "stats", "email": "stats@test.com"})
        user_id = json.loads(create_resp.data)['data']['id']
        resp = client.get(f'/users/{user_id}/stats')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['data']['favorites_count'] == 0
        assert data['data']['ratings_count'] == 0
        assert data['data']['reviews_count'] == 0
        assert data['data']['favorite_genre'] is None

    def test_get_user_stats_not_found(self, client):
        resp = client.get('/users/9999/stats')
        assert resp.status_code == 404
