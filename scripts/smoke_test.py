import httpx

BASE='http://127.0.0.1:8000'

with httpx.Client(timeout=10) as c:
    r = c.post(f'{BASE}/api/token', data={'username':'admin','password':'adminpass'})
    print('token status', r.status_code, r.text)
    r.raise_for_status()
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create supplier
    payload = {'name': 'Smoke Supplier', 'contact': 'smoke@example.com'}
    r = c.post(f'{BASE}/api/suppliers', json=payload, headers=headers)
    print('create supplier', r.status_code, r.text)

    # list suppliers
    r = c.get(f'{BASE}/api/suppliers')
    print('list suppliers', r.status_code, r.text)

    # create customer (requires manager/admin)
    payload = {'name': 'Smoke Customer', 'email': 'cust@example.com'}
    r = c.post(f'{BASE}/api/customers', json=payload, headers=headers)
    print('create customer', r.status_code, r.text)

    # health
    r = c.get(f'{BASE}/api/health')
    print('health', r.status_code, r.text)
