"""Session-B research (branch session-b-research): five pre-registered strategies NOT previously
tested in this program, all at 4h on the nine OKX USDT perps, walk-forward, A-011 measured costs,
unleveraged. Self-contained: reads data from THIS worktree (relative ROOT), not the main tree.

  S1 LS-Cascade    B2 long (uptrend) + squeeze-fade SHORT with a strict bear gate
  S2 TSMOM-4h      15-day time-series momentum, long / short / L+S, vol-target sizing
  S3 AltBTC-MR     z-score reversion of alt/BTC ratios, dollar-neutral pairs
  S4 CascadeSpread systemic-cascade bars: long 3 hardest-hit, short 3 least-hit, dollar-neutral
  S5 GBM-Cascade   shallow gradient-boosted classifier on 7 causal features, WF re-fit

Execution convention everywhere: signal at bar-t close, execute at bar t+1 OPEN, exit at the open of
the bar after the exit condition. Costs: taker per side per instrument (half-spread + 5 bps fee +
$5k book-walk slippage, A-011). No leverage; a sleeve is 1/N of capital.
"""
from __future__ import annotations
import functools, numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # the WORKTREE root
FUT = ROOT / "user_data" / "data" / "okx" / "futures"
P9 = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
ALT7 = [p for p in P9 if p not in ("BTC", "ETH")]
_COSTS = pd.read_csv(ROOT / "user_data" / "research" / "data" / "okx_micro" / "adverse_selection_results.csv").set_index("inst")
SIDE = {i: float(_COSTS.loc[i, "half"] + 5.0 + _COSTS.loc[i, "slip_$5k"]) for i in P9}   # bps per side
PPY = 2190                                            # 4h bars per year
HOLD = 6                                              # 24h
W, PW = 42, 180                                       # 7d dispersion window, 30d percentile window

# ----------------------------------------------------------------------------- data
@functools.lru_cache(maxsize=None)
def h1(i):
    d = pd.read_feather(FUT / f"{i}_USDT_USDT-1h-futures.feather").set_index("date").sort_index()
    return d[~d.index.duplicated()]

@functools.lru_cache(maxsize=None)
def d1(i):
    d = pd.read_feather(FUT / f"{i}_USDT_USDT-1d-futures.feather").set_index("date").sort_index()
    return d[~d.index.duplicated()]

@functools.lru_cache(maxsize=None)
def h4(i):
    return h1(i).resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()

@functools.lru_cache(maxsize=None)
def idx4():
    ix = h4(P9[0]).index
    for i in P9[1:]:
        ix = ix.intersection(h4(i).index)
    return ix

@functools.lru_cache(maxsize=None)
def gates(i):
    """Daily gates, evaluated on completed daily bars and shifted one day so a 4h bar only sees the
    prior day's close. Returns (gate_up, gate_dn) as 4h-indexed float series."""
    c = d1(i)["close"]; sma = c.rolling(200).mean(); e20 = c.ewm(span=20).mean(); e50 = c.ewm(span=50).mean()
    up = ((c > sma) & (e20 > e50)).astype(float)
    dn = ((c < sma) & (sma < sma.shift(20)) & (e20 < e50)).astype(float)   # strict bear: price below a FALLING SMA200
    ix = idx4()
    return (up.reindex(ix, method="ffill").shift(HOLD).fillna(0.0), dn.reindex(ix, method="ffill").shift(HOLD).fillna(0.0))

@functools.lru_cache(maxsize=None)
def feats(i):
    """All causal features at 4h for instrument i, on the common index. fwd6 is a LABEL (forward), used
    only by S5's training target — never as a feature."""
    d = h4(i).reindex(idx4()); c = d["close"]; r = c / c.shift(1) - 1
    neg2 = np.minimum(r, 0) ** 2; pos2 = np.maximum(r, 0) ** 2
    dsd = np.sqrt(neg2.rolling(W).mean()); usd = np.sqrt(pos2.rolling(W).mean())
    bc = h4("BTC").reindex(idx4())["close"]
    gu, gd = gates(i)
    f = pd.DataFrame({
        "o": d["open"], "h": d["high"], "l": d["low"], "c": c, "r": r,
        "dsd_pct": dsd.rolling(PW).rank(pct=True), "usd_pct": usd.rolling(PW).rank(pct=True),
        "mom6": c / c.shift(6) - 1, "mom18": c / c.shift(18) - 1,
        "btc_mom6": bc / bc.shift(6) - 1,
        "vr": r.rolling(6).std() / r.rolling(W).std(),
        "gate_up": gu, "gate_dn": gd,
        "fwd6": d["open"].shift(-(HOLD + 1)) / d["open"].shift(-1) - 1,   # open[t+1] -> open[t+7]
    })
    return f

# ----------------------------------------------------------------------------- shared sim
def _sim(f, trig_mask, side_bps, short=False, exit_sig=None, exit_thr=0.50, hold=HOLD):
    """Non-overlapping trades from a boolean trigger mask. Returns (trades_df, per-bar net return series
    with the trade's return booked on its exit bar). side_bps = taker cost per side for this instrument."""
    o, n = f["o"].values, len(f); ret = np.zeros(n); rows = []
    trig = trig_mask.values; ex = exit_sig.values if exit_sig is not None else None
    t = 0
    while t < n - hold - 3:
        if not trig[t]:
            t += 1; continue
        e = t + 1; k = e; end = min(e + hold, n - 2)
        while k < end and not (ex is not None and ex[k] < exit_thr):
            k += 1
        ep, xp = o[e], o[k + 1]
        gross = (ep / xp - 1) if short else (xp / ep - 1)
        net = gross - 2 * side_bps / 1e4
        ret[k + 1] = net; rows.append((f.index[e], f.index[k + 1], gross, net, k + 1 - e)); t = k + 2
    return pd.DataFrame(rows, columns=["entry", "exit", "gross", "net", "bars"]), pd.Series(ret, index=f.index)

def _stats(s, lo=None, hi=None):
    s = s.dropna()
    if lo is not None: s = s[(s.index >= lo) & (s.index < hi)]
    if len(s) < 10 or s.std() == 0: return dict(ret=0, ann=0, dd=0, sh=0, so=0, cal=0, n_bars=len(s))
    eq = (1 + s).cumprod(); yrs = len(s) / PPY; ann = eq.iloc[-1] ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min(); neg = np.sqrt((np.minimum(s, 0) ** 2).mean())
    return dict(ret=(eq.iloc[-1] - 1) * 100, ann=ann * 100, dd=dd * 100,
                sh=s.mean() / s.std() * np.sqrt(PPY), so=(s.mean() / neg * np.sqrt(PPY)) if neg > 0 else 0,
                cal=(ann / abs(dd)) if dd < 0 else 0, n_bars=len(s))

# ----------------------------------------------------------------------------- S1 LS-Cascade
def s1_fit(a, b):
    """thresholds from the TRAIN window only: 25th pct of loose long entry mom6, 75th pct of loose short."""
    L, S = [], []
    for i in P9:
        f = feats(i); w = f[(f.index >= a) & (f.index < b)]
        L.append(w.mom6[(w.dsd_pct >= .80) & (w.mom6 < 0) & (w.btc_mom6 < 0) & (w.gate_up > 0)])
        S.append(w.mom6[(w.usd_pct >= .80) & (w.mom6 > 0) & (w.btc_mom6 > 0) & (w.gate_dn > 0)])
    L = pd.concat(L); S = pd.concat(S)
    return dict(thr_L=float(-np.percentile(L, 25)) if len(L) > 20 else 0.03,
                thr_S=float(np.percentile(S, 75)) if len(S) > 20 else 0.03)

def s1_run(p, b=None, c=None):
    """Returns dict of book series: long, short, combined (each = mean of 9 sleeves)."""
    Ls, Ss, nL, nS = [], [], 0, 0
    for i in P9:
        f = feats(i)
        tl, sl = _sim(f, (f.dsd_pct >= .80) & (f.mom6 <= -p["thr_L"]) & (f.btc_mom6 < 0) & (f.gate_up > 0), SIDE[i], False, f.dsd_pct)
        ts, ss = _sim(f, (f.usd_pct >= .80) & (f.mom6 >= p["thr_S"]) & (f.btc_mom6 > 0) & (f.gate_dn > 0), SIDE[i], True, f.usd_pct)
        if b is not None:
            sl = sl[(sl.index >= b) & (sl.index < c)]; ss = ss[(ss.index >= b) & (ss.index < c)]
            tl = tl[(tl.entry >= b) & (tl.entry < c)]; ts = ts[(ts.entry >= b) & (ts.entry < c)]
        Ls.append(sl); Ss.append(ss); nL += len(tl); nS += len(ts)
    L = pd.concat(Ls, axis=1).mean(axis=1); S = pd.concat(Ss, axis=1).mean(axis=1)
    return {"long": L, "short": S, "combined": L + S, "n_long": nL, "n_short": nS}

# ----------------------------------------------------------------------------- S2 TSMOM-4h
def s2_run(LB=90, mode="ls", b=None, c=None, vol_target=0.40):
    R = []
    for i in P9:
        f = feats(i); c_ = f["c"]; r = f["r"]
        sig = np.sign(c_ / c_.shift(LB) - 1)
        vol = r.rolling(30).std() * np.sqrt(PPY); w = (vol_target / vol).clip(0, 1)
        pos = sig * w
        if mode == "long": pos = pos.clip(lower=0)
        elif mode == "short": pos = pos.clip(upper=0)
        pos = pos.fillna(0)
        ret = pos.shift(1) * r - (pos.shift(1) - pos.shift(2)).abs() * SIDE[i] / 1e4
        R.append(ret)
    s = pd.concat(R, axis=1).mean(axis=1)
    if b is not None: s = s[(s.index >= b) & (s.index < c)]
    return s

# ----------------------------------------------------------------------------- S3 AltBTC-MR
def s3_run(b=None, c=None, z_in=2.0, z_out=0.5, win=180, max_hold=42):
    fb = feats("BTC"); R = []
    for a in ALT7:
        f = feats(a); lr = np.log(f["c"] / fb["c"]); z = (lr - lr.rolling(win).mean()) / lr.rolling(win).std()
        ra, rb = f["r"].values, fb["r"].values; zz = z.values; n = len(f)
        ret = np.zeros(n); state = 0; held = 0; cost = 0.5 * (SIDE[a] + SIDE["BTC"]) / 1e4
        for t in range(1, n):
            if state != 0:
                ret[t] += state * 0.5 * (ra[t] - rb[t]); held += 1
                if abs(zz[t - 1]) < z_out or held >= max_hold or np.isnan(zz[t - 1]):
                    ret[t] -= cost; state = 0; held = 0; continue
            if state == 0 and not np.isnan(zz[t - 1]):
                if zz[t - 1] <= -z_in: state = +1; held = 0; ret[t] -= cost      # long alt / short BTC
                elif zz[t - 1] >= z_in: state = -1; held = 0; ret[t] -= cost     # short alt / long BTC
        R.append(pd.Series(ret, index=f.index))
    s = pd.concat(R, axis=1).mean(axis=1)
    if b is not None: s = s[(s.index >= b) & (s.index < c)]
    return s

# ----------------------------------------------------------------------------- S4 CascadeSpread
def s4_run(b=None, c=None, k=3):
    F = {i: feats(i) for i in P9}; ix = idx4()
    Rm = pd.DataFrame({i: F[i]["r"] for i in P9}); M6 = pd.DataFrame({i: F[i]["mom6"] for i in P9})
    O = pd.DataFrame({i: F[i]["o"] for i in P9})
    bk = Rm.mean(axis=1); bdsd = np.sqrt((np.minimum(bk, 0) ** 2).rolling(W).mean()); bpct = bdsd.rolling(PW).rank(pct=True)
    bmom = (1 + bk).rolling(6).apply(np.prod, raw=True) - 1
    trig = ((bpct >= .80) & (bmom < 0)).values; n = len(ix); ret = np.zeros(n); t = 0; ntr = 0
    while t < n - HOLD - 3:
        if not trig[t]: t += 1; continue
        e = t + 1; x = e + HOLD
        m = M6.iloc[t].dropna()
        if len(m) < 2 * k: t += 1; continue
        longs = list(m.nsmallest(k).index); shorts = list(m.nlargest(k).index)
        lret = (O.iloc[x][longs].values / O.iloc[e][longs].values - 1).mean()
        sret = (O.iloc[e][shorts].values / O.iloc[x][shorts].values - 1).mean()
        cost = (sum(SIDE[j] for j in longs) / k + sum(SIDE[j] for j in shorts) / k) / 1e4   # per-side, both sides -> x2 below
        ret[x] = 0.5 * lret + 0.5 * sret - cost; ntr += 1; t = x + 1
    s = pd.Series(ret, index=ix)
    if b is not None: s = s[(s.index >= b) & (s.index < c)]
    return s, ntr

# ----------------------------------------------------------------------------- S5 GBM-Cascade
FEATS = ["dsd_pct", "usd_pct", "mom6", "mom18", "btc_mom6", "vr", "gate_up"]
def s5_window(a, b, c, p_thr=0.60, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    X, y = [], []
    for i in P9:
        f = feats(i); w = f[(f.index >= a) & (f.index < b)].dropna(subset=FEATS + ["fwd6"])
        X.append(w[FEATS]); y.append((w["fwd6"] > 2 * SIDE[i] / 1e4).astype(int))
    X = pd.concat(X); y = pd.concat(y)
    mdl = HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05, l2_regularization=1.0, random_state=seed).fit(X, y)
    R = []; ntr = 0
    for i in P9:
        f = feats(i); w = f[(f.index >= b) & (f.index < c)].copy()
        ok = w[FEATS].notna().all(axis=1)
        p = pd.Series(0.0, index=w.index); p[ok] = mdl.predict_proba(w.loc[ok, FEATS])[:, 1]
        tr, s = _sim(w, p >= p_thr, SIDE[i], False, None)
        R.append(s); ntr += len(tr)
    return pd.concat(R, axis=1).mean(axis=1), ntr, mdl, y.mean()

# ----------------------------------------------------------------------------- walk-forward
START, END = pd.Timestamp("2023-01-22", tz="UTC"), pd.Timestamp("2026-09-01", tz="UTC")
def windows(train_m=12, test_m=3, step_m=3):
    out = []; t0 = START
    while True:
        t1 = t0 + pd.DateOffset(months=train_m); t2 = min(t1 + pd.DateOffset(months=test_m), END)
        if t1 >= END: break
        out.append((t0, t1, t2)); t0 = t0 + pd.DateOffset(months=step_m)
    return out

def summarise(s, label):
    s = s.dropna(); m = _stats(s); yr = (1 + s).groupby(s.index.year).prod() - 1
    rec = {d: ((1 + s[s.index >= END - pd.Timedelta(days=d)]).prod() - 1) * 100 for d in (90, 365)}
    return dict(label=label, **m, y23=yr.get(2023, np.nan) * 100, y24=yr.get(2024, np.nan) * 100,
                y25=yr.get(2025, np.nan) * 100, y26=yr.get(2026, np.nan) * 100, r90=rec[90], r365=rec[365])
