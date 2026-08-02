import os
import csv
from datetime import datetime

INSTRUMENTS = [
    "BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP",
    "BNB-USDT-SWAP", "ADA-USDT-SWAP", "AVAX-USDT-SWAP",
    "DOT-USDT-SWAP", "LINK-USDT-SWAP", "UNI-USDT-SWAP"
]

DATA_DIR = "user_data/research/data/funding"

print("| Instrument | Record Count | Earliest UTC | Latest UTC | Retention (Days) | Gaps > 8h |")
print("|---|---|---|---|---|---|")

for instId in INSTRUMENTS:
    filepath = os.path.join(DATA_DIR, f"{instId}.csv")
    if not os.path.exists(filepath):
        print(f"| {instId} | 0 | - | - | 0 | - |")
        continue
    
    times = []
    earliest_utc = None
    latest_utc = None
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ft = int(r["funding_time_ms"])
            times.append(ft)
            ft_utc = r["funding_time_utc"]
            if earliest_utc is None or ft_utc < earliest_utc:
                earliest_utc = ft_utc
            if latest_utc is None or ft_utc > latest_utc:
                latest_utc = ft_utc

    times.sort()
    
    if len(times) > 0:
        depth = (times[-1] - times[0]) / (1000 * 60 * 60 * 24)
    else:
        depth = 0
        
    gaps = []
    for i in range(1, len(times)):
        diff_hours = (times[i] - times[i-1]) / (1000 * 60 * 60)
        if diff_hours > 8.0:
            dt1 = datetime.utcfromtimestamp(times[i-1]/1000).isoformat() + "Z"
            dt2 = datetime.utcfromtimestamp(times[i]/1000).isoformat() + "Z"
            gaps.append(f"{dt1} to {dt2} ({diff_hours:.1f}h)")
            
    gap_str = ", ".join(gaps) if gaps else "None"
    print(f"| {instId} | {len(times)} | {earliest_utc} | {latest_utc} | {depth:.1f} | {gap_str} |")
