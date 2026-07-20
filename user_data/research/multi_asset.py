"""
Multi-asset strategies and validation.

Each strategy takes a dict {symbol: df} and returns a dict {symbol: position_series}.
The portfolio combiner runs signal_to_returns on each, then averages with weights.
"""
from __future__ import annotations
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import json
from dataclasses import asdict
from typing import Callable, Optional

import numpy as np
import pandas as pd

from validator import (
    load, signal_to_returns, extract_trades, metrics,
    yearly_breakdown, yearly_pnl_dollar_concentration,
    split_70_15_15, monte_carlo, Verdict, save_verdict, print_verdict,
    ANNUALIZATION_DAILY, COMMISSION, SLIPPAGE,
)
import strategies as S


def portfolio_returns(
    data: dict[str, pd.DataFrame],
    positions: dict[str, pd.Series],
    weights: Optional[dict[str, float]] = None,
    fee: float = COMMISSION + SLIPPAGE,
) -> pd.DataFrame:
    """Combine per-asset positions into a portfolio equity curve.

    Weights are normalized internally each bar by SUM of absolute weights of
    assets actually in position. This keeps gross exposure at 1.0 (no leverage).
    """
    symbols = list(data.keys())
    if weights is None:
        weights = {s: 1.0 for s in symbols}

    all_ret = pd.DataFrame(index=sorted(set().union(*[d.index for d in data.values()])))
    per = {}
    for s in symbols:
        df = data[s]
        pos = positions[s].reindex(df.index).fillna(0).clip(-1, 1)
        pos = pos.shift(2).fillna(0)
        c = df["close"]
        bar_ret = (c / c.shift(1)).fillna(1.0) - 1.0
        per[s] = pd.DataFrame({"pos": pos, "ret": bar_ret}, index=df.index)

    # Align all on common index
    idx = sorted(set().union(*[v.index for v in per.values()]))
    aligned = {s: per[s].reindex(idx) for s in symbols}

    # Compute portfolio weights bar by bar
    pos_mat = pd.DataFrame({s: aligned[s]["pos"] for s in symbols}, index=idx).fillna(0)
    ret_mat = pd.DataFrame({s: aligned[s]["ret"] for s in symbols}, index=idx).fillna(0)
    w_mat = pd.DataFrame({s: float(weights[s]) for s in symbols}, index=idx)

    # Effective weight: only on assets currently in position; normalize to gross 1
    in_pos = pos_mat.abs() > 0
    raw_w = w_mat * in_pos
    norm = raw_w.abs().sum(axis=1).replace(0, np.nan)
    eff_w = (raw_w.div(norm, axis=0)).fillna(0)

    # Gross portfolio return = sum_s pos_s * w_s * ret_s
    port_ret_gross = (pos_mat * eff_w * ret_mat).sum(axis=1)

    # Fee on changes in (effective position * weight)
    eff_pos = pos_mat * eff_w
    pos_change = eff_pos.diff().abs().fillna(eff_pos.abs()).sum(axis=1)
    port_ret_net = port_ret_gross - pos_change * fee

    equity = (1 + port_ret_net).cumprod()
    # For trade extraction: portfolio position = sum of abs effective positions
    port_pos = pos_mat.abs().sum(axis=1).clip(0, 1)

    return pd.DataFrame({
        "position": port_pos,
        "ret_gross": port_ret_gross,
        "ret_net": port_ret_net,
        "equity": equity,
    }, index=idx)


def validate_multi(
    name: str,
    data: dict[str, pd.DataFrame],
    signal_fn: Callable[[dict[str, pd.DataFrame]], dict[str, pd.Series]],
    bars_per_year: int = ANNUALIZATION_DAILY,
) -> Verdict:
    sigs = signal_fn(data)
    rets = portfolio_returns(data, sigs)

    # Synthesize trade log from portfolio equity changes (gross position transitions)
    pos = rets["position"]
    pos_state = (pos > 0).astype(int)
    transitions = pos_state.diff().fillna(0).abs()
    trade_starts = pos_state.diff() > 0
    trade_ends = pos_state.diff() < 0

    starts = list(rets.index[trade_starts])
    ends = list(rets.index[trade_ends])
    if pos_state.iloc[-1] == 1 and (not ends or starts[-1] > ends[-1]):
        ends.append(rets.index[-1])
    trades = []
    for s, e in zip(starts, ends):
        if e <= s:
            continue
        slc = rets.loc[s:e, "ret_net"]
        pnl = (1 + slc).prod() - 1
        trades.append({"entry": s, "exit": e, "side": 1, "bars": len(slc), "pnl": pnl})
    trs = pd.DataFrame(trades)

    m_full = metrics(rets, trs, bars_per_year)
    yearly = yearly_breakdown(rets)
    yearly_dict = {int(y): float(v) for y, v in yearly.items()}
    conc = yearly_pnl_dollar_concentration(rets)

    # 70/15/15 on the COMMON time index
    idx = rets.index
    n = len(idx)
    i1 = int(n * 0.70); i2 = int(n * 0.85)
    tr_idx, vl_idx, te_idx = idx[:i1], idx[i1:i2], idx[i2:]

    def slice_data(slc_idx):
        return {s: data[s].loc[slc_idx[0]:slc_idx[-1]] for s in data}

    def slice_rets(slc_idx):
        return rets.loc[slc_idx[0]:slc_idx[-1]]

    rets_tr = slice_rets(tr_idx); rets_vl = slice_rets(vl_idx); rets_te = slice_rets(te_idx)
    # recompute trade logs per slice
    def trades_from(rets_sub):
        ps = (rets_sub["position"] > 0).astype(int)
        sd = ps.diff().fillna(0)
        ss = list(rets_sub.index[sd > 0])
        ee = list(rets_sub.index[sd < 0])
        if ps.iloc[-1] == 1 and (not ee or ss[-1] > ee[-1]):
            ee.append(rets_sub.index[-1])
        out = []
        for s, e in zip(ss, ee):
            if e <= s: continue
            slc = rets_sub.loc[s:e, "ret_net"]
            out.append({"entry": s, "exit": e, "side": 1, "bars": len(slc), "pnl": (1 + slc).prod() - 1})
        return pd.DataFrame(out)

    m_tr = metrics(rets_tr, trades_from(rets_tr), bars_per_year)
    m_vl = metrics(rets_vl, trades_from(rets_vl), bars_per_year)
    m_te = metrics(rets_te, trades_from(rets_te), bars_per_year)

    # Walk-forward: 4 OOS windows on the portfolio index
    wf = []
    for k in range(1, 5):
        is_end = int(n * (0.5 + (k - 1) * 0.10))
        oos_end = min(int(n * (0.5 + k * 0.10)), n)
        oos_range = idx[is_end:oos_end]
        if len(oos_range) < 30: continue
        d_sub = slice_data(oos_range)
        s_sub = signal_fn(d_sub)
        r_sub = portfolio_returns(d_sub, s_sub)
        t_sub = trades_from(r_sub)
        mm = metrics(r_sub, t_sub, bars_per_year)
        mm["window"] = k
        wf.append(mm)

    mc = monte_carlo(rets, trs)

    reasons = []
    if m_full["years"] < 5: reasons.append(f"only {m_full['years']:.1f}y data (need 5+)")
    pos_years = sum(1 for v in yearly_dict.values() if v > 0)
    total_years = len(yearly_dict)
    if total_years and pos_years / total_years < 0.6:
        reasons.append(f"positive in {pos_years}/{total_years} years (<60%)")
    if conc.get("max_year_share") and conc["max_year_share"] > 0.40:
        reasons.append(f"one year = {conc['max_year_share']*100:.0f}% of profit (>40%)")
    if m_full["max_dd"] < -0.25: reasons.append(f"max DD {m_full['max_dd']*100:.1f}% (worse than -25%)")
    if m_full["sharpe"] < 1.5: reasons.append(f"sharpe {m_full['sharpe']:.2f} (<1.5)")
    if m_full["profit_factor"] < 1.5: reasons.append(f"PF {m_full['profit_factor']:.2f} (<1.5)")
    if m_full["n_trades"] < 200: reasons.append(f"only {m_full['n_trades']} trades (<200)")
    if m_tr["sharpe"] > 0 and m_te["sharpe"] < 0.5 * m_tr["sharpe"]:
        reasons.append(f"test Sharpe {m_te['sharpe']:.2f} < 0.5*train {m_tr['sharpe']:.2f}")
    if wf:
        wf_pos = sum(1 for w in wf if w["total_return"] > 0)
        if wf_pos / len(wf) < 0.5: reasons.append(f"WF profitable in {wf_pos}/{len(wf)} windows")
    if mc.get("mc_p5_sharpe") is not None and not np.isnan(mc["mc_p5_sharpe"]) and mc["mc_p5_sharpe"] < 0:
        reasons.append(f"MC p5 sharpe {mc['mc_p5_sharpe']:.2f} < 0")

    return Verdict(
        name=name, passed=not reasons, reasons=reasons,
        full={**m_full, "max_year_share": conc.get("max_year_share")},
        train=m_tr, val=m_vl, test=m_te,
        yearly=yearly_dict, wf=wf, mc=mc,
    )


# ---------- MULTI-ASSET STRATEGIES ----------

def trend_overlay(data: dict[str, pd.DataFrame], sma_n: int = 200) -> dict[str, pd.Series]:
    """Each asset: long when close > SMA200. Independent per asset."""
    out = {}
    for s, df in data.items():
        sma = df["close"].rolling(sma_n).mean()
        out[s] = (df["close"] > sma).astype(float)
    return out


def trend_overlay_with_slope(data: dict[str, pd.DataFrame], sma_n: int = 200, slope_lookback: int = 20) -> dict[str, pd.Series]:
    out = {}
    for s, df in data.items():
        sma = df["close"].rolling(sma_n).mean()
        rising = sma.diff(slope_lookback) > 0
        out[s] = ((df["close"] > sma) & rising).astype(float)
    return out


def cross_sectional_momentum(data: dict[str, pd.DataFrame], lookback: int = 90) -> dict[str, pd.Series]:
    """Long the asset(s) with positive momentum and rank above median.
    For 2 assets: long the one with higher momentum if its momentum > 0."""
    syms = list(data.keys())
    mom = {s: data[s]["close"].pct_change(lookback) for s in syms}
    idx = sorted(set().union(*[m.index for m in mom.values()]))
    mom_df = pd.DataFrame({s: mom[s].reindex(idx) for s in syms}).ffill()
    # rank each row, long top-1 if > 0
    out = {s: pd.Series(0.0, index=idx) for s in syms}
    for i in range(len(idx)):
        row = mom_df.iloc[i]
        if row.isna().any():
            continue
        top = row.idxmax()
        if row[top] > 0:
            out[top].iloc[i] = 1.0
    return {s: out[s].reindex(data[s].index).fillna(0) for s in syms}


def pairs_spread_revert(data: dict[str, pd.DataFrame], n: int = 30, z_in: float = 2.0, z_out: float = 0.5) -> dict[str, pd.Series]:
    """BTC-ETH log spread mean reversion. Long underperformer / flat outperformer when z > z_in."""
    assert len(data) == 2, "pairs needs exactly 2 assets"
    a, b = list(data.keys())
    idx = sorted(set(data[a].index) & set(data[b].index))
    pa = data[a]["close"].reindex(idx).ffill()
    pb = data[b]["close"].reindex(idx).ffill()
    spread = np.log(pa / pb)
    mu = spread.rolling(n).mean()
    sd = spread.rolling(n).std()
    z = (spread - mu) / sd

    sig_a = pd.Series(np.nan, index=idx)
    sig_b = pd.Series(np.nan, index=idx)

    # spread very high → a overpriced vs b → b is cheap → long b
    sig_a[z > z_in] = 0.0
    sig_b[z > z_in] = 1.0
    # spread very low → a cheap → long a
    sig_a[z < -z_in] = 1.0
    sig_b[z < -z_in] = 0.0
    # exit when z reverts to band
    sig_a[z.abs() < z_out] = 0.0
    sig_b[z.abs() < z_out] = 0.0

    return {
        a: sig_a.ffill().fillna(0).reindex(data[a].index).fillna(0),
        b: sig_b.ffill().fillna(0).reindex(data[b].index).fillna(0),
    }


def vol_adjusted_basket_trend(data: dict[str, pd.DataFrame], sma_n: int = 200, vol_n: int = 30, vol_target: float = 0.40) -> dict[str, pd.Series]:
    """Each asset: long if above SMA, scaled by inverse 30d vol toward 40% target. Capped at 1."""
    out = {}
    for s, df in data.items():
        sma = df["close"].rolling(sma_n).mean()
        ret = df["close"].pct_change()
        rv = ret.rolling(vol_n).std() * np.sqrt(365)
        scale = (vol_target / rv).clip(0, 1)
        out[s] = ((df["close"] > sma).astype(float)) * scale.fillna(0)
    return out


def trend_with_atr_trailing(data: dict[str, pd.DataFrame], sma_n: int = 100, atr_mult: float = 3.0) -> dict[str, pd.Series]:
    """Per asset: enter long on close > SMA100, exit on close < trailing stop (close - atr_mult*ATR(14))."""
    out = {}
    for s, df in data.items():
        sma = df["close"].rolling(sma_n).mean()
        # ATR
        h, l, c = df["high"], df["low"], df["close"]
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1 / 14, adjust=False).mean()

        pos = np.zeros(len(c))
        trail = -np.inf
        in_pos = False
        for i in range(len(c)):
            if pd.isna(sma.iloc[i]) or pd.isna(atr.iloc[i]):
                continue
            if not in_pos:
                if c.iloc[i] > sma.iloc[i]:
                    in_pos = True
                    trail = c.iloc[i] - atr_mult * atr.iloc[i]
            else:
                new_trail = c.iloc[i] - atr_mult * atr.iloc[i]
                if new_trail > trail:
                    trail = new_trail
                if c.iloc[i] < trail:
                    in_pos = False
                    trail = -np.inf
            pos[i] = 1.0 if in_pos else 0.0
        out[s] = pd.Series(pos, index=c.index)
    return out


if __name__ == "__main__":
    import time
    btc1d = load("BTC/USDT", "1d")
    eth1d = load("ETH/USDT", "1d")
    common_start = max(btc1d.index.min(), eth1d.index.min())
    btc1d = btc1d.loc[common_start:]
    eth1d = eth1d.loc[common_start:]
    data = {"BTC": btc1d, "ETH": eth1d}
    print(f"Multi-asset window: {common_start} to {btc1d.index.max()}, {len(btc1d)} bars")

    tests = [
        ("trend_overlay_btc_eth_1d", lambda d: trend_overlay(d, 200)),
        ("trend_overlay_slope_btc_eth_1d", lambda d: trend_overlay_with_slope(d, 200, 20)),
        ("xsect_mom_90d_btc_eth", lambda d: cross_sectional_momentum(d, 90)),
        ("xsect_mom_60d_btc_eth", lambda d: cross_sectional_momentum(d, 60)),
        ("xsect_mom_30d_btc_eth", lambda d: cross_sectional_momentum(d, 30)),
        ("pairs_spread_30_2_btc_eth", lambda d: pairs_spread_revert(d, 30, 2.0, 0.5)),
        ("pairs_spread_60_1.5_btc_eth", lambda d: pairs_spread_revert(d, 60, 1.5, 0.3)),
        ("vol_adj_basket_btc_eth", lambda d: vol_adjusted_basket_trend(d, 200, 30, 0.40)),
        ("trend_atr_trail_btc_eth", lambda d: trend_with_atr_trailing(d, 100, 3.0)),
    ]

    passed = []
    for name, fn in tests:
        t0 = time.time()
        try:
            v = validate_multi(name, data, fn, bars_per_year=ANNUALIZATION_DAILY)
        except Exception as e:
            print(f"[{name}] ERROR: {e}")
            import traceback; traceback.print_exc()
            continue
        save_verdict(v)
        print_verdict(v)
        print(f"  (took {time.time() - t0:.1f}s)")
        if v.passed:
            passed.append(name)

    print("\n" + "="*70)
    print(f"MULTI-ASSET BATCH: {len(passed)}/{len(tests)} passed")
    print("="*70)
    for p in passed:
        print(f"  PASS: {p}")
