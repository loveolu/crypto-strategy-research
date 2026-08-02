import requests
import json
import time
import os

endpoints = [
    "https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=1D",
    "https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio?ccy=BTC&period=1D",
    "https://www.okx.com/api/v5/rubik/stat/taker-volume?ccy=BTC&instType=CONTRACTS&period=1D"
]

print("| Endpoint | HTTP Status | Earliest Retrievable Timestamp | Granularity |")
print("|---|---|---|---|")

os.makedirs("research/results/T-031_transcripts", exist_ok=True)

for i, url in enumerate(endpoints):
    time.sleep(0.3)
    r = requests.get(url)
    
    with open(f"research/results/T-031_transcripts/P6_survey_{i}.json", "w") as f:
        f.write(r.text)
        
    status = r.status_code
    earliest = "N/A"
    granularity = "1D"
    
    if status == 200:
        data = r.json().get("data", [])
        if data:
            # Assuming the data is sorted newest-first or oldest-first, let's find the min ts
            # Each record is typically an array where [0] is timestamp, or a list of objects.
            # Usually Rubik API returns list of arrays [ts, ...]
            # We'll just parse the first element.
            min_ts = float("inf")
            for row in data:
                try:
                    ts = int(row[0])
                    if ts < min_ts: min_ts = ts
                except:
                    pass
            if min_ts != float("inf"):
                from datetime import datetime
                earliest = datetime.utcfromtimestamp(min_ts/1000).isoformat() + "Z"
            
    # For markdown table
    short_url = url.replace("https://www.okx.com/api/v5/rubik/stat/", "")
    print(f"| `{short_url}` | {status} | {earliest} | {granularity} |")
