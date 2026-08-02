import json
with open("research/results/T-031_transcripts/P1_probe_btc.txt", "rb") as f:
    text = f.read().decode("utf-16le")
parts = text.split("\r\n\r\n", 1)
if len(parts) == 2:
    headers, body = parts
    d = json.loads(body)
    print("HTTP Code:", headers.split("\r\n")[0])
    print("JSON Code:", d.get("code"))
    print("Record Count:", len(d.get("data", [])))
    if d.get("data"):
        print("Newest Time:", d["data"][0].get("fundingTime"))
