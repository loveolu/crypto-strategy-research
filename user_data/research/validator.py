"""
Strategy validation harness.

A strategy is a function `signal(df) -> Series` where the Series is in {-1, 0, 1}
representing target position (flat/long/short) for each bar. Position is taken at
the OPEN of bar t+1 from the signal made on the close of bar t (anti-lookahead).

The harness runs:
  1. Full-history backtest
  2. Year-by-year breakdown
  3. 70/15/15 train/val/test split
  4. Walk-forward (4 windows)
  5. Monte Carlo (shuffled trades, +slippage, +commission, +delayed exec)

A strategy PASSES if:
  - >= 5 years of data
  - Positive return in >= 60% of years
  - No single year > 40% of total $ profit
  - Max DD < 25%
  - Sharpe > 1.5
  - Profit factor > 1.5
  - >= 200 trades
  - Test-period Sharpe >= 0.5 * train Sharpe (no severe overfitting)
  - Walk-forward: positive in >= 50% of OOS windows
  - MC: 5th percentile Sharpe > 0 (robust to execution noise)

Kaufman Ch.21 audit diagnostics (added 2026-07-10, A-ValidatorAudit; reusable,
reporting-only — they do not change the pass bar above):
  - shock_day_mask / shock_pnl_decomposition / top_day_concentration:
    price-shock P&L decomposition of a daily return stream.
  - wf_window_stability / rolling_sharpe_series:
    walk-forward boundary-sensitivity + rolling 18-month Sharpe.
  - family_context / family_from_results_dir + Verdict.family_context:
    average-of-all-tests (not peak) reporting convention; validate() accepts an
    optional `family` argument to populate it.
"""

from __future__ import annotations
import json
import time
import warnings
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Callable, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

DATA_DIR = Path("C:/Users/Comec/Projects/freqtrade/user_data/data/okx")
RESULTS_DIR = Path("C:/Users/Comec/Projects/freqtrade/user_data/research/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Execution model
COMMISSION = 0.001          # 0.1% per side (OKX taker)
SLIPPAGE = 0.0005           # 0.05% per side
ANNUALIZATION_DAILY = 365   # crypto: 365 not 252


def load(symbol: str, timeframe: str) -> pd.DataFrame:
    fp = DATA_DIR / f"{symbol.replace('/', '_')}-{timeframe}.feather"
    df = pd.read_feather(fp)
    df = df.set_index("date").sort_index()
    return df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})


def signal_to_returns(df: pd.DataFrame, signal: pd.Series, fee: float = COMMISSION + SLIPPAGE) -> pd.DataFrame:
    """
    Take a signal series (-1/0/1) and produce bar returns net of fees.

    Convention (anti-lookahead):
      signal[t] uses info up through close[t].
      Earliest we can act is open[t+1].
      We hold position[t+1] = signal[t] from open[t+1] to close[t+1] and onward.
      Bar return realized at t is close[t+1]/open[t+1] for the entry bar,
      then close[t+k]/close[t+k-1] while held. Simplified with shift(2) on signal
      and close-to-close bar returns:

        position[t] = signal[t-2]        # signal at t-2 → exec at open[t-1] → held by close[t-1] onward
        bar_ret[t]  = close[t]/close[t-1] - 1

    Fees charged per side on any position change.
    """
    signal = signal.reindex(df.index).fillna(0).clip(-1, 1)
    position = signal.shift(2).fillna(0)  # 2-bar lag: signal at close[t-2] -> exec open[t-1] -> by close[t-1] in position

    c = df["close"]
    bar_ret = (c / c.shift(1)).fillna(1.0) - 1.0
    ret_gross = position * bar_ret

    # Fee on each position change
    pos_change = position.diff().abs().fillna(position.abs())
    ret_net = ret_gross - pos_change * fee

    equity = (1 + ret_net).cumprod()
    return pd.DataFrame({
        "position": position,
        "ret_gross": ret_gross,
        "ret_net": ret_net,
        "equity": equity,
    }, index=df.index)


def extract_trades(returns: pd.DataFrame) -> pd.DataFrame:
    """Convert position-by-bar returns into a trade log."""
    pos = returns["position"].values
    ret = returns["ret_net"].values
    idx = returns.index

    trades = []
    in_trade = False
    entry_i = 0
    cum = 0.0

    for i in range(len(pos)):
        if not in_trade and pos[i] != 0:
            in_trade = True
            entry_i = i
            cum = ret[i]
        elif in_trade and pos[i] == pos[entry_i] and pos[i] != 0:
            cum = (1 + cum) * (1 + ret[i]) - 1
        elif in_trade and (pos[i] == 0 or pos[i] != pos[entry_i]):
            trades.append({
                "entry": idx[entry_i],
                "exit": idx[i],
                "side": int(pos[entry_i]),
                "bars": i - entry_i,
                "pnl": cum,
            })
            if pos[i] != 0:
                in_trade = True
                entry_i = i
                cum = ret[i]
            else:
                in_trade = False
                cum = 0.0
    if in_trade:
        trades.append({
            "entry": idx[entry_i],
            "exit": idx[-1],
            "side": int(pos[entry_i]),
            "bars": len(pos) - entry_i,
            "pnl": cum,
        })

    return pd.DataFrame(trades)


def metrics(returns: pd.DataFrame, trades: pd.DataFrame, bars_per_year: int = ANNUALIZATION_DAILY) -> dict:
    ret = returns["ret_net"]
    eq = returns["equity"]
    final = float(eq.iloc[-1]) if len(eq) else 1.0
    n_bars = len(ret)
    years = n_bars / bars_per_year if bars_per_year else 1
    cagr = (final ** (1 / max(years, 1e-6)) - 1) if final > 0 else -1.0

    daily_std = ret.std()
    sharpe = (ret.mean() / daily_std) * np.sqrt(bars_per_year) if daily_std > 0 else 0.0

    downside = ret[ret < 0].std()
    sortino = (ret.mean() / downside) * np.sqrt(bars_per_year) if downside > 0 else 0.0

    peak = eq.cummax()
    dd = (eq / peak - 1).min()

    if len(trades):
        wins = trades[trades["pnl"] > 0]["pnl"].sum()
        losses = -trades[trades["pnl"] < 0]["pnl"].sum()
        pf = wins / losses if losses > 0 else (np.inf if wins > 0 else 0)
        win_rate = (trades["pnl"] > 0).mean()
        n_trades = len(trades)
    else:
        pf = 0
        win_rate = 0
        n_trades = 0

    return {
        "final_equity": round(final, 4),
        "total_return": round(final - 1, 4),
        "cagr": round(cagr, 4),
        "sharpe": round(float(sharpe), 4),
        "sortino": round(float(sortino), 4),
        "max_dd": round(float(dd), 4),
        "profit_factor": round(float(pf), 4) if pf != np.inf else 999.0,
        "win_rate": round(float(win_rate), 4),
        "n_trades": int(n_trades),
        "years": round(years, 2),
    }


def yearly_breakdown(returns: pd.DataFrame) -> pd.DataFrame:
    ret = returns["ret_net"]
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    return yearly


def yearly_pnl_dollar_concentration(returns: pd.DataFrame, starting: float = 1.0) -> dict:
    """Return max share of total $ profit from a single year."""
    eq = returns["equity"] * starting
    year_eq = eq.groupby(eq.index.year).last()
    year_pnl = year_eq.diff()
    year_pnl.iloc[0] = year_eq.iloc[0] - starting
    total = year_pnl.sum()
    if total <= 0:
        return {"max_year_share": np.nan, "year_pnl": year_pnl.to_dict()}
    shares = year_pnl / total
    return {"max_year_share": float(shares.abs().max()), "year_pnl": year_pnl.to_dict()}


def split_70_15_15(df: pd.DataFrame):
    n = len(df)
    i1 = int(n * 0.70)
    i2 = int(n * 0.85)
    return df.iloc[:i1], df.iloc[i1:i2], df.iloc[i2:]


def walk_forward(df: pd.DataFrame, signal_fn, windows: int = 4) -> list[dict]:
    """Anchored walk-forward: 4 OOS windows. Each window: prior 60%+ is IS, next 10% is OOS."""
    n = len(df)
    results = []
    for k in range(1, windows + 1):
        is_end = int(n * (0.5 + (k - 1) * 0.10))
        oos_end = int(n * (0.5 + k * 0.10))
        if oos_end > n:
            oos_end = n
        oos_df = df.iloc[is_end:oos_end]
        if len(oos_df) < 30:
            continue
        sig = signal_fn(oos_df)
        rets = signal_to_returns(oos_df, sig)
        trs = extract_trades(rets)
        m = metrics(rets, trs)
        m["window"] = k
        m["is_end"] = str(df.index[is_end])
        m["oos_end"] = str(df.index[oos_end - 1])
        results.append(m)
    return results


def monte_carlo(returns: pd.DataFrame, trades: pd.DataFrame, n_sims: int = 200, extra_slippage: float = 0.0005) -> dict:
    """Shuffle trade order + add extra slippage. Returns distribution of Sharpe and final equity."""
    if len(trades) < 30:
        return {"mc_p5_sharpe": np.nan, "mc_p50_sharpe": np.nan, "mc_p5_return": np.nan}
    pnl = trades["pnl"].values - extra_slippage  # per-trade extra cost
    sharpes = []
    finals = []
    rng = np.random.default_rng(42)
    for _ in range(n_sims):
        shuffled = rng.permutation(pnl)
        eq = np.cumprod(1 + shuffled)
        rets = pd.Series(shuffled)
        s = rets.mean() / rets.std() * np.sqrt(len(shuffled) / (len(returns) / ANNUALIZATION_DAILY)) if rets.std() > 0 else 0
        sharpes.append(s)
        finals.append(eq[-1] - 1)
    return {
        "mc_p5_sharpe": float(np.percentile(sharpes, 5)),
        "mc_p50_sharpe": float(np.percentile(sharpes, 50)),
        "mc_p95_sharpe": float(np.percentile(sharpes, 95)),
        "mc_p5_return": float(np.percentile(finals, 5)),
        "mc_p50_return": float(np.percentile(finals, 50)),
    }


# --------------------------------------------------------------------------- #
#  Kaufman Ch.21 audit diagnostics (added 2026-07-10, A-ValidatorAudit).
#  Three reusable, strategy-agnostic functions operating on daily return Series:
#    1. shock_pnl_decomposition — how much of total P&L comes from underlying
#       price-shock days (Kaufman: shock-concentrated profit = luck, not process).
#    2. wf_window_stability — is the walk-forward verdict robust to the arbitrary
#       choice of window count/boundaries? Plus rolling N-month Sharpe series.
#    3. family_context — report the AVERAGE of all tested variants, not the peak
#       (Kaufman's average-of-all-tests convention), as a Verdict field.
# --------------------------------------------------------------------------- #

def shock_day_mask(underlying_returns: pd.DataFrame,
                   method: str = "p99",
                   pctile: float = 0.99,
                   sigma_mult: float = 3.0,
                   vol_lookback: int = 30) -> pd.Series:
    """Boolean mask of shock days defined on UNDERLYING asset returns (both signs).

    underlying_returns: DataFrame of daily close-to-close returns, one column per
    asset. A day is a shock day if ANY asset qualifies (union across columns).

    method="p99":  |r_t| > full-window pctile of |r| (static, per asset).
    method="3sigma": |r_t| > sigma_mult * trailing vol_lookback-day std, std shifted
    one day (only information available before day t). Unclassifiable warmup days
    are non-shock.
    """
    mask = pd.Series(False, index=underlying_returns.index)
    for col in underlying_returns.columns:
        r = underlying_returns[col]
        if method == "p99":
            thr = r.abs().quantile(pctile)
            mask |= (r.abs() > thr).fillna(False)
        elif method == "3sigma":
            rolling = r.rolling(vol_lookback).std().shift(1)
            mask |= (r.abs() > sigma_mult * rolling).fillna(False)
        else:
            raise ValueError(f"unknown shock method: {method}")
    return mask


def _sharpe(ret: pd.Series, bars_per_year: int = ANNUALIZATION_DAILY) -> float:
    ret = ret.dropna()
    sd = ret.std()
    return float(ret.mean() / sd * np.sqrt(bars_per_year)) if sd > 0 else 0.0


def _total_return(ret: pd.Series) -> float:
    return float((1 + ret.dropna()).prod() - 1)


def _log_share(ret: pd.Series, subset_mask: pd.Series) -> float:
    """Share of total log-P&L attributable to masked days (exactly additive)."""
    lg = np.log1p(ret.fillna(0.0))
    total = lg.sum()
    if abs(total) < 1e-12:
        return float("nan")
    return float(lg[subset_mask.reindex(ret.index).fillna(False)].sum() / total)


def shock_pnl_decomposition(strategy_returns: pd.Series,
                            shock_mask: pd.Series,
                            top_ks: tuple = (5, 10, 20),
                            bars_per_year: int = ANNUALIZATION_DAILY) -> dict:
    """Kaufman Ch.21 price-shock decomposition of a daily return stream.

    Reports total return / Sharpe with all days; with ALL shock days excluded
    (dropped from the series, Kaufman's removal convention); with the top-k
    positive / negative / both shock days (ranked by the strategy's own P&L on
    shock days) removed; plus the log-P&L share of each removed set.
    """
    ret = strategy_returns.dropna()
    mask = shock_mask.reindex(ret.index).fillna(False)
    out = {
        "n_days": int(len(ret)),
        "n_shock_days": int(mask.sum()),
        "all": {"total_return": _total_return(ret), "sharpe": _sharpe(ret, bars_per_year)},
        "ex_all_shock": {
            "total_return": _total_return(ret[~mask]),
            "sharpe": _sharpe(ret[~mask], bars_per_year),
            "log_pnl_share_of_shock_days": _log_share(ret, mask),
        },
    }
    shock_ret = ret[mask]
    for k in top_ks:
        pos_days = shock_ret.nlargest(k).index
        neg_days = shock_ret.nsmallest(k).index
        both_days = pos_days.union(neg_days)
        pos_mask = pd.Series(ret.index.isin(pos_days), index=ret.index)
        out[f"top{k}"] = {
            "ex_best": {"total_return": _total_return(ret.drop(pos_days)),
                        "sharpe": _sharpe(ret.drop(pos_days), bars_per_year)},
            "ex_worst": {"total_return": _total_return(ret.drop(neg_days)),
                         "sharpe": _sharpe(ret.drop(neg_days), bars_per_year)},
            "ex_both": {"total_return": _total_return(ret.drop(both_days)),
                        "sharpe": _sharpe(ret.drop(both_days), bars_per_year)},
            "log_pnl_share_of_best": _log_share(ret, pos_mask),
        }
    return out


def top_day_concentration(strategy_returns: pd.Series,
                          top_ks: tuple = (5, 10, 20),
                          bars_per_year: int = ANNUALIZATION_DAILY) -> dict:
    """Share of total P&L from the strategy's own top-k best/worst single days
    (regardless of whether they are underlying shock days)."""
    ret = strategy_returns.dropna()
    out = {"all": {"total_return": _total_return(ret), "sharpe": _sharpe(ret, bars_per_year)}}
    for k in top_ks:
        pos_days = ret.nlargest(k).index
        neg_days = ret.nsmallest(k).index
        both_days = pos_days.union(neg_days)
        pos_mask = pd.Series(ret.index.isin(pos_days), index=ret.index)
        out[f"top{k}"] = {
            "ex_best": {"total_return": _total_return(ret.drop(pos_days)),
                        "sharpe": _sharpe(ret.drop(pos_days), bars_per_year)},
            "ex_worst": {"total_return": _total_return(ret.drop(neg_days)),
                         "sharpe": _sharpe(ret.drop(neg_days), bars_per_year)},
            "ex_both": {"total_return": _total_return(ret.drop(both_days)),
                        "sharpe": _sharpe(ret.drop(both_days), bars_per_year)},
            "log_pnl_share_of_best": _log_share(ret, pos_mask),
        }
    return out


def wf_window_stability(strategy_returns: pd.Series,
                        window_counts: tuple = (3, 4, 5, 6),
                        oos_start_frac: float = 0.5,
                        bars_per_year: int = ANNUALIZATION_DAILY) -> dict:
    """Walk-forward boundary-sensitivity diagnostic (Kaufman Ch.21).

    Splits the OOS region (default: second half of the stream, matching the
    phase15/16 walk-forward convention) into k equal contiguous windows for each
    k in window_counts. No re-fitting — this operates on an already-realized
    daily stream. A robust WF conclusion looks the same at 3 windows as at 6.
    """
    ret = strategy_returns.dropna()
    n = len(ret)
    i0 = int(n * oos_start_frac)
    oos = ret.iloc[i0:]
    out = {}
    for k in window_counts:
        bounds = [int(len(oos) * j / k) for j in range(k + 1)]
        sharpes, rets_, spans = [], [], []
        for j in range(k):
            w = oos.iloc[bounds[j]:bounds[j + 1]]
            sharpes.append(_sharpe(w, bars_per_year))
            rets_.append(_total_return(w))
            spans.append((str(w.index[0].date()), str(w.index[-1].date())))
        out[k] = {
            "windows_positive": int(sum(1 for x in rets_ if x > 0)),
            "windows_total": k,
            "majority_positive": sum(1 for x in rets_ if x > 0) > k / 2,
            "window_sharpes": [round(s, 3) for s in sharpes],
            "window_returns": [round(r, 4) for r in rets_],
            "worst_window_sharpe": round(min(sharpes), 3),
            "sharpe_spread": round(max(sharpes) - min(sharpes), 3),
            "window_spans": spans,
        }
    return out


def rolling_sharpe_series(strategy_returns: pd.Series,
                          window_days: int = 548,
                          bars_per_year: int = ANNUALIZATION_DAILY) -> pd.Series:
    """Trailing window_days (default 18 months) Sharpe, sampled at month ends."""
    ret = strategy_returns.dropna()
    month_ends = ret.groupby([ret.index.year, ret.index.month]).apply(lambda g: g.index[-1])
    vals, idx = [], []
    for t in month_ends:
        w = ret.loc[t - pd.Timedelta(days=window_days):t]
        if len(w) >= int(window_days * 0.9):
            vals.append(_sharpe(w, bars_per_year))
            idx.append(t)
    return pd.Series(vals, index=pd.DatetimeIndex(idx))


def family_context(candidate_name: str,
                   candidate_full_sharpe: float,
                   candidate_test_sharpe: float,
                   family: list[dict]) -> dict:
    """Kaufman's average-of-all-tests reporting convention.

    family: list of {"name", "full_sharpe", "test_sharpe"} for every variant in
    the search family the candidate was selected from (candidate excluded or
    included — ranks are computed against the provided list plus the candidate).
    Attach the result to Verdict.family_context so headline numbers always carry
    their selection context.
    """
    def _stats(vals, cand):
        vals = [v for v in vals if v is not None and np.isfinite(v)]
        if not vals:
            return {}
        allv = vals + [cand]
        rank = sum(1 for v in allv if v > cand) + 1
        return {
            "n_family": len(vals),
            "mean": round(float(np.mean(vals)), 3),
            "median": round(float(np.median(vals)), 3),
            "max": round(float(np.max(vals)), 3),
            "min": round(float(np.min(vals)), 3),
            "candidate": round(float(cand), 3),
            "candidate_rank": int(rank),
            "candidate_percentile": round(100.0 * (len(allv) - rank) / (len(allv) - 1), 1) if len(allv) > 1 else 100.0,
        }
    return {
        "candidate": candidate_name,
        "full_sharpe": _stats([f.get("full_sharpe") for f in family], candidate_full_sharpe),
        "test_sharpe": _stats([f.get("test_sharpe") for f in family], candidate_test_sharpe),
        "note": "Kaufman Ch.21: report the average of all tested variants, not the peak.",
    }


def family_from_results_dir(results_dir: Path = RESULTS_DIR) -> list[dict]:
    """Load the recorded search family from saved Verdict JSONs (does NOT re-run
    anything — reads the historical record)."""
    fam = []
    for fp in sorted(results_dir.glob("*.json")):
        try:
            with open(fp) as f:
                d = json.load(f)
            fam.append({
                "name": d.get("name", fp.stem),
                "full_sharpe": (d.get("full") or {}).get("sharpe"),
                "test_sharpe": (d.get("test") or {}).get("sharpe"),
            })
        except Exception:
            continue
    return fam


@dataclass
class Verdict:
    name: str
    passed: bool
    reasons: list[str] = field(default_factory=list)
    full: dict = field(default_factory=dict)
    train: dict = field(default_factory=dict)
    val: dict = field(default_factory=dict)
    test: dict = field(default_factory=dict)
    yearly: dict = field(default_factory=dict)
    wf: list = field(default_factory=list)
    mc: dict = field(default_factory=dict)
    # Kaufman Ch.21 reporting hook (added 2026-07-10, A-ValidatorAudit): where this
    # strategy sits inside the family of variants it was selected from. Populated via
    # family_context() / family_context_from_results(); empty when not applicable.
    family_context: dict = field(default_factory=dict)


def validate(name: str, df: pd.DataFrame, signal_fn: Callable[[pd.DataFrame], pd.Series],
             bars_per_year: int = ANNUALIZATION_DAILY,
             family: Optional[list] = None) -> Verdict:
    """Run the full pipeline. signal_fn(df) -> pd.Series of {-1, 0, 1} indexed by df.index.

    family (optional): list of {"name", "full_sharpe", "test_sharpe"} dicts for the
    search family this candidate was selected from; populates Verdict.family_context
    (Kaufman average-of-all-tests convention). Pass family_from_results_dir() to use
    the saved historical record. Omitting it leaves behavior unchanged.
    """
    t0 = time.time()
    sig = signal_fn(df)
    rets = signal_to_returns(df, sig)
    trs = extract_trades(rets)
    m_full = metrics(rets, trs, bars_per_year)
    yearly = yearly_breakdown(rets)
    yearly_dict = {int(y): float(v) for y, v in yearly.items()}
    concentration = yearly_pnl_dollar_concentration(rets)

    # 70/15/15
    df_tr, df_vl, df_te = split_70_15_15(df)
    sig_tr = signal_fn(df_tr)
    sig_vl = signal_fn(df_vl)
    sig_te = signal_fn(df_te)
    m_tr = metrics(*[signal_to_returns(df_tr, sig_tr)], pd.DataFrame()) if False else None
    rets_tr = signal_to_returns(df_tr, sig_tr); trs_tr = extract_trades(rets_tr); m_tr = metrics(rets_tr, trs_tr, bars_per_year)
    rets_vl = signal_to_returns(df_vl, sig_vl); trs_vl = extract_trades(rets_vl); m_vl = metrics(rets_vl, trs_vl, bars_per_year)
    rets_te = signal_to_returns(df_te, sig_te); trs_te = extract_trades(rets_te); m_te = metrics(rets_te, trs_te, bars_per_year)

    wf = walk_forward(df, signal_fn)
    mc = monte_carlo(rets, trs)

    reasons = []
    if m_full["years"] < 5: reasons.append(f"only {m_full['years']:.1f}y data (need 5+)")
    pos_years = sum(1 for v in yearly_dict.values() if v > 0)
    total_years = len(yearly_dict)
    if total_years and pos_years / total_years < 0.6: reasons.append(f"positive in {pos_years}/{total_years} years (<60%)")
    if concentration.get("max_year_share") and concentration["max_year_share"] > 0.40:
        reasons.append(f"one year = {concentration['max_year_share']*100:.0f}% of profit (>40%)")
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

    passed = not reasons
    fam_ctx = family_context(name, m_full["sharpe"], m_te["sharpe"], family) if family else {}
    return Verdict(
        name=name,
        passed=passed,
        reasons=reasons,
        full={**m_full, "max_year_share": concentration.get("max_year_share")},
        train=m_tr, val=m_vl, test=m_te,
        yearly=yearly_dict,
        wf=wf,
        mc=mc,
        family_context=fam_ctx,
    )


def save_verdict(v: Verdict):
    fp = RESULTS_DIR / f"{v.name}.json"
    with open(fp, "w") as f:
        json.dump(asdict(v), f, indent=2, default=str)
    return fp


def print_verdict(v: Verdict):
    print(f"\n{'='*70}")
    print(f"STRATEGY: {v.name}")
    print(f"{'='*70}")
    f = v.full
    print(f"Full window: return {f['total_return']*100:+.1f}%  CAGR {f['cagr']*100:+.1f}%  "
          f"Sharpe {f['sharpe']:.2f}  PF {f['profit_factor']:.2f}  "
          f"DD {f['max_dd']*100:.1f}%  trades {f['n_trades']}  years {f['years']}")
    print(f"  train  return {v.train['total_return']*100:+6.1f}%  Sharpe {v.train['sharpe']:.2f}  trades {v.train['n_trades']}")
    print(f"  val    return {v.val['total_return']*100:+6.1f}%  Sharpe {v.val['sharpe']:.2f}  trades {v.val['n_trades']}")
    print(f"  test   return {v.test['total_return']*100:+6.1f}%  Sharpe {v.test['sharpe']:.2f}  trades {v.test['n_trades']}")
    print(f"Yearly: " + " ".join(f"{y}:{r*100:+.0f}%" for y, r in v.yearly.items()))
    if v.wf:
        print("Walk-forward windows:")
        for w in v.wf:
            print(f"  W{w['window']}: ret {w['total_return']*100:+5.1f}%  Sharpe {w['sharpe']:5.2f}  trades {w['n_trades']}")
    if v.mc:
        print(f"Monte Carlo (200 sims, +slip): p5 Sharpe {v.mc.get('mc_p5_sharpe', float('nan')):.2f}  "
              f"p50 Sharpe {v.mc.get('mc_p50_sharpe', float('nan')):.2f}  p5 ret {v.mc.get('mc_p5_return', float('nan'))*100:+.1f}%")
    if v.family_context:
        ts = v.family_context.get("test_sharpe", {})
        if ts:
            print(f"Family context (avg-of-all-tests, n={ts.get('n_family')}): TEST Sharpe "
                  f"mean {ts.get('mean')} / median {ts.get('median')} / max {ts.get('max')}; "
                  f"candidate {ts.get('candidate')} (rank {ts.get('candidate_rank')})")
    print(f"\nVERDICT: {'PASS' if v.passed else 'FAIL'}")
    if v.reasons:
        for r in v.reasons:
            print(f"  - {r}")
