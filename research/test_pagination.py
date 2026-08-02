import requests
import json

url = "https://www.okx.com/api/v5/public/funding-rate-history"
params = {"instId": "BTC-USDT-SWAP", "limit": "2"}
r = requests.get(url, params=params)
data = r.json()["data"]
print("Initial:", [d["fundingTime"] for d in data])

params_before = {"instId": "BTC-USDT-SWAP", "limit": "2", "before": data[-1]["fundingTime"]}
r_before = requests.get(url, params=params_before)
print("Before:", [d["fundingTime"] for d in r_before.json().get("data", [])])

params_after = {"instId": "BTC-USDT-SWAP", "limit": "2", "after": data[-1]["fundingTime"]}
r_after = requests.get(url, params=params_after)
print("After:", [d["fundingTime"] for d in r_after.json().get("data", [])])
