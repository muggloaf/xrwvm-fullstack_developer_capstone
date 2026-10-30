"""Capture actual cURL commands and responses; stop on unsuccessful evidence."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--backend', default='http://127.0.0.1:3030')
parser.add_argument('--django', default='http://127.0.0.1:8000')
parser.add_argument('--sentiment', default='http://127.0.0.1:5050')
parser.add_argument('--output', required=True)
args = parser.parse_args()
output = Path(args.output)
output.mkdir(parents=True, exist_ok=True)
tasks = [
    ('getalldealers', args.backend + '/fetchDealers'),
    ('getdealerbyid', args.backend + '/fetchDealer/1'),
    ('getdealersbyState', args.backend + '/fetchDealers/Kansas'),
    ('getallcarmakes', args.django + '/djangoapp/get_cars'),
    ('analyzereview', args.sentiment + '/analyze/Fantastic%20services'),
]
for name, url in tasks:
    command = ['curl', '--fail-with-body', '-sS', '-X', 'GET', url]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data, f'{name}: empty response'
    if name == 'getdealersbyState':
        assert all(dealer['state'] == 'Kansas' for dealer in data)
    if name == 'getdealerbyid':
        assert data[0]['id'] == 1
    if name == 'getallcarmakes':
        assert data['CarModels']
    if name == 'analyzereview':
        assert data['sentiment'] == 'positive'
    (output / name).write_text(
        shlex.join(command) + '\n' + result.stdout + '\n', encoding='utf-8')
    print(f'{name}: captured and verified')

# Confirm Django proxies connect to both real upstream services.
for endpoint, key in [('get_dealers', 'dealers'), ('dealer/1', 'dealer'),
                      ('reviews/dealer/15', 'reviews')]:
    result = subprocess.run(
        ['curl', '--fail', '-sS', args.django + '/djangoapp/' + endpoint],
        capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)[key]
print('Django dealer and sentiment-enriched review proxies passed')

session = requests.Session()
account = {'userName': 'integration_driver', 'password': 'ci-demo-password',
           'firstName': 'Integration', 'lastName': 'Driver',
           'email': 'driver@example.com'}
session.post(args.django + '/djangoapp/register', json=account, timeout=15)
response = session.post(args.django + '/djangoapp/login', json=account,
                        timeout=15)
response.raise_for_status()
assert response.json()['status'] == 'Authenticated'
review = {'dealership': 1, 'review': 'Fantastic services', 'purchase': True,
          'purchase_date': '2026-10-30', 'car_make': 'Toyota',
          'car_model': 'Corolla', 'car_year': 2023}
response = session.post(args.django + '/djangoapp/add_review', json=review,
                        timeout=15)
response.raise_for_status()
assert response.json()['status'] == 200
response = session.get(args.django + '/djangoapp/reviews/dealer/1', timeout=60)
response.raise_for_status()
assert any(item['review'] == 'Fantastic services' and
           item['name'] == 'Integration Driver' and
           item['sentiment'] == 'positive'
           for item in response.json()['reviews'])
print('Authenticated review submission and sentiment persistence passed')
