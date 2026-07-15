import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# get token
r = client.post('/api/token', data={'username':'admin','password':'adminpass'})
print('token', r.status_code, r.text)
assert r.status_code==200
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# create supplier
payload = {'name': 'Local Smoke Supplier', 'contact_info': 'local@example.com'}
r = client.post('/api/suppliers', json=payload, headers=headers)
print('create supplier', r.status_code, r.text)

# create customer
payload = {'external_id': 'ext-smoke-1', 'age_group': '25-34'}
r = client.post('/api/customers', json=payload, headers=headers)
print('create customer', r.status_code, r.text)
