import uuid

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_token_and_customers_crud():
    r = client.post('/api/token', data={'username': 'admin', 'password': 'adminpass'})
    assert r.status_code == 200
    token = r.json().get('access_token')
    assert token
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'external_id': f'C-TEST-{uuid.uuid4()}',
        'gender': 'M',
        'age_group': '25-34',
        'membership_tier': 'Gold',
        'customer_type': 'Retail',
    }
    r = client.post('/api/customers', json=payload, headers=headers)
    assert r.status_code == 200
    created = r.json().get('created')
    assert 'customer_id' in created
    cid = created['customer_id']
    r = client.get(f'/api/customers/{cid}', headers=headers)
    assert r.status_code == 200
    assert r.json()['customer']['external_id'] == payload['external_id']
