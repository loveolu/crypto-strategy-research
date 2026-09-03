"""A-011 (operator-directed, 2026-09-02): OKX microstructure fetch for the
maker-vs-taker cost measurement. Public endpoints only, `requests` only.
Writes ONLY under user_data/research/data/okx_micro/ (external-axis carve-out).
REFUSES to overwrite an existing raw artifact. Never touches user_data/data/."""
import sys, json, time, requests
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"user_data"/"research"/"data"/"okx_micro"; OUT.mkdir(parents=True,exist_ok=True)
BASE="https://www.okx.com"
INST=["BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOT","LINK"]
IDS=[f"{i}-USDT-SWAP" for i in INST]
UA={"User-Agent":"freqtrade-research/A-011"}

def get(path,**params):
    for k in range(5):
        r=requests.get(BASE+path,params=params,headers=UA,timeout=20)
        if r.status_code==429: time.sleep(1.5); continue
        j=r.json()
        if j.get("code")=="0": return j["data"]
        time.sleep(0.5)
    raise RuntimeError(f"{path} {params} failed")

def sample_books(n=40, gap=1.5):
    fp=OUT/"book_samples.jsonl"
    if fp.exists(): print("book_samples.jsonl exists; refusing to overwrite"); return
    with fp.open("w",encoding="utf-8") as f:
        for k in range(n):
            for iid in IDS:
                d=get("/api/v5/market/books",instId=iid,sz=10)[0]
                f.write(json.dumps({"instId":iid,"fetched":datetime.now(timezone.utc).isoformat(),"book":d})+"\n")
            time.sleep(gap)
    print("book samples done:",n,"rounds x",len(IDS))

def fetch_candles(days=30):
    log=[]
    for iid in IDS:
        fp=OUT/f"{iid}_1m_raw.jsonl"
        if fp.exists(): print(fp.name,"exists; refusing to overwrite"); continue
        cutoff=int((time.time()-days*86400)*1000)
        after=None; n=0; oldest=None
        with fp.open("w",encoding="utf-8") as f:
            while True:
                p={"instId":iid,"bar":"1m","limit":100}
                if after: p["after"]=after
                d=get("/api/v5/market/history-candles",**p)
                if not d: break
                f.write(json.dumps({"fetched":datetime.now(timezone.utc).isoformat(),"params":p,"data":d})+"\n")
                n+=len(d); oldest=int(d[-1][0]); after=str(oldest)
                if oldest<cutoff: break
                time.sleep(0.12)
        log.append({"instId":iid,"rows":n,"oldest_utc":datetime.fromtimestamp(oldest/1000,tz=timezone.utc).isoformat() if oldest else None})
        print(iid,n,"candles, oldest",log[-1]["oldest_utc"],flush=True)
    (OUT/"fetch_log.json").write_text(json.dumps({"fetched_at":datetime.now(timezone.utc).isoformat(),"days_requested":days,"per_instrument":log},indent=2))

if __name__=="__main__":
    what=sys.argv[1] if len(sys.argv)>1 else "all"
    if what in("books","all"): sample_books()
    if what in("candles","all"): fetch_candles()
