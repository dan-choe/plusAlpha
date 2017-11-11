# Add Account

import requests
import json

customerId = '5a063bc9a73e4942cdafe872'
apiKey = '1d0ff9c1ed84ac0b6db1e1347a926c73'

url = 'http://api.reimaginebanking.com/customers/{}/accounts?key={}'.format(customerId,apiKey)
payload = {
  "type": "Savings",
  "nickname": "DanChoe",
  "rewards": 10000,
  "balance": 10000,
}
# Create a Savings Account
response = requests.post(
	url,
	data=json.dumps(payload),
	headers={'content-type':'application/json'},
	)

if response.status_code == 201:
	print('account created')