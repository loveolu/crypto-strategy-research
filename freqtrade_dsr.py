"""
freqtrade_dsr.py — Overfitting guardrails for a Freqtrade pipeline.

Two tools in one drop-in module:

1. Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014)
   Corrects an in-sample Sharpe for SELECTION bias: the strategy you deploy is
   the *best* of N hyperopt epochs, so its observed Sharpe is upward-biased.
   DSR ~= P(true Sharpe > the selection-adjusted benchmark). DSR is in [0, 1];
   >= 0.95 is the conventional "this edge is probably not a fishing artifact" bar.
   The single most important input is n_trials = your hyperopt epoch count.

2. Legitimacy gates
   Cheap structural checks that a robustness stage actually produced real
   evidence (enough folds / simulations / iterations) before you trust its
   verdict. Useful when you build out walk-forward / Monte-Carlo / jitter stages
   so a stage can't silently "pass" on an empty payload.

DSR math ported from Forven (github.com/judder659/Forven, AGPL-3.0). If you only
run this privately for your own backtests the AGPL imposes nothing on you; the
copyleft obligation only triggers if you offer a *modified* version to others as
a network service. Keep this header if you redistribute.

Deps: scipy (Freqtrade already pulls it). pandas only for the Freqtrade adapter.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

_EULER_GAMMA = 0.5772156649015329


# --------------------------------------------------------------------------- #
#  Deflated Sharpe Ratio
# --------------------------------------------------------------------------- #
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    from scipy.stats import norm  # inverse CDF; scipy ships with Freqtrade

    return float(norm.ppf(p))


def probabilistic_sharpe_ratio(
    sr_hat: float, sr_benchmark: float, n_obs: int, skew: float, kurt: float
) -> float:
    """P(true Sharpe > sr_benchmark) given an observed per-period Sharpe.

    `kurt` is NON-excess (normal == 3). `sr_hat` is per-period (NOT annualised).
    """
    if n_obs < 2:
        return 0.0
    denom = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)
    if denom <= 0:
        return 0.0
    z = (sr_hat - sr_benchmark) * math.sqrt(n_obs - 1) / math.sqrt(denom)
    return float(_norm_cdf(z))


def expected_max_sharpe(trial_sharpe_var: float, n_trials: int) -> float:
    """Expected maximum per-period Sharpe under the null across n_trials draws.

    This is the benchmark the winning strategy must beat to not be explained by
    'we tried a lot of things and kept the luckiest one'.
    """
    n = max(int(n_trials), 1)
    if n <= 1 or trial_sharpe_var <= 0:
        return 0.0
    sd = math.sqrt(trial_sharpe_var)
    a = _norm_ppf(1.0 - 1.0 / n)
    b = _norm_ppf(1.0 - 1.0 / (n * math.e))
    return float(sd * ((1.0 - _EULER_GAMMA) * a + _EULER_GAMMA * b))


def deflated_sharpe_ratio(
    returns: Iterable[float],
    n_trials: int,
    trial_sharpe_var: float | None = None,
) -> dict:
    """Deflated Sharpe Ratio from per-period (or per-trade) returns.

    Args:
        returns: per-trade profit ratios (e.g. Freqtrade `profit_ratio`) or any
                 per-period return series. Scale-invariant (ratio or % both fine).
        n_trials: number of optimizer trials the winner was selected from.
                  For Freqtrade this is your hyperopt --epochs count. If you did
                  NOT hyperopt, the honest value is still > 1 (every parameter you
                  eyeballed and discarded is a trial); use a conservative >= 20.
        trial_sharpe_var: cross-trial variance of optimizer Sharpe estimates, if
                  you persisted all epochs. Usually None -> Lo (2002) estimator
                  proxy is used (a conservative stand-in).

    Returns dict with `dsr` (the headline 0..1 probability) plus diagnostics.
    """
    rs = [float(r) for r in returns if r is not None and math.isfinite(float(r))]
    t = len(rs)
    if t < 2:
        return {"dsr": None, "reason": "insufficient_returns", "n_obs": t}

    mean_r = sum(rs) / t
    var_r = sum((r - mean_r) ** 2 for r in rs) / t  # population variance
    sd_r = math.sqrt(var_r)
    if sd_r <= 1e-12:
        return {"dsr": None, "reason": "zero_variance", "n_obs": t}
    sr_hat = mean_r / sd_r

    if t >= 3:
        m3 = sum((r - mean_r) ** 3 for r in rs) / t
        skew = m3 / (sd_r ** 3)
    else:
        skew = 0.0
    if t >= 4:
        m4 = sum((r - mean_r) ** 4 for r in rs) / t
        kurt = m4 / (sd_r ** 4)  # non-excess (normal == 3)
    else:
        kurt = 3.0

    if trial_sharpe_var is not None and trial_sharpe_var > 0:
        v = float(trial_sharpe_var)
        v_source = "trials"
    else:
        # Variance of the Sharpe estimator (Lo 2002, skew/kurt-adjusted).
        v = max((1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)) / (t - 1), 1e-9)
        v_source = "estimator_proxy"

    sr0 = expected_max_sharpe(v, n_trials)
    dsr = probabilistic_sharpe_ratio(sr_hat, sr0, t, skew, kurt)
    return {
        "dsr": round(float(dsr), 5),
        "sr_hat_per_trade": round(float(sr_hat), 5),
        "sr0_benchmark": round(float(sr0), 5),
        "n_obs": t,
        "n_trials": int(max(n_trials, 1)),
        "skew": round(float(skew), 4),
        "kurtosis": round(float(kurt), 4),
        "trial_var_source": v_source,
    }


# --------------------------------------------------------------------------- #
#  Freqtrade adapter
# --------------------------------------------------------------------------- #
def returns_from_freqtrade(backtest_source: Any) -> list[float]:
    """Extract per-trade returns from a Freqtrade backtest result.

    Accepts:
      - a path to a backtest result .zip / .json in user_data/backtest_results/
      - an already-loaded trades DataFrame (must have a `profit_ratio` column)
      - a list of dicts each holding `profit_ratio`
    """
    # Already a DataFrame?
    try:
        import pandas as pd

        if isinstance(backtest_source, pd.DataFrame):
            return [float(x) for x in backtest_source["profit_ratio"].tolist()]
    except ImportError:
        pd = None  # type: ignore

    # A path -> use Freqtrade's loader if available, else raw json fallback.
    if isinstance(backtest_source, str):
        try:
            from freqtrade.data.btanalysis import load_backtest_data

            df = load_backtest_data(backtest_source)
            return [float(x) for x in df["profit_ratio"].tolist()]
        except Exception:
            import json
            import zipfile

            raw: dict
            if backtest_source.endswith(".zip"):
                with zipfile.ZipFile(backtest_source) as zf:
                    name = next(n for n in zf.namelist() if n.endswith(".json"))
                    raw = json.loads(zf.read(name))
            else:
                with open(backtest_source) as fh:
                    raw = json.load(fh)
            # Freqtrade nests results under strategy name -> "trades".
            out: list[float] = []
            strat_blob = raw.get("strategy", raw)
            for _strat, payload in strat_blob.items():
                if isinstance(payload, dict):
                    for tr in payload.get("trades", []):
                        pr = tr.get("profit_ratio")
                        if pr is not None and math.isfinite(float(pr)):
                            out.append(float(pr))
            return out

    # A list of trade dicts.
    if isinstance(backtest_source, list):
        out = []
        for tr in backtest_source:
            pr = tr.get("profit_ratio") if isinstance(tr, dict) else None
            if pr is not None and math.isfinite(float(pr)):
                out.append(float(pr))
        return out

    raise TypeError(f"unsupported backtest_source type: {type(backtest_source)!r}")


def evaluate_freqtrade(
    backtest_source: Any,
    n_hyperopt_epochs: int,
    dsr_threshold: float = 0.95,
) -> dict:
    """One-call verdict for a Freqtrade backtest.

    n_hyperopt_epochs is the --epochs you ran (the selection-bias count). Pass a
    conservative >= 20 if you hand-tuned instead of running hyperopt.
    """
    returns = returns_from_freqtrade(backtest_source)
    res = deflated_sharpe_ratio(returns, n_hyperopt_epochs)
    dsr = res.get("dsr")
    res["threshold"] = dsr_threshold
    res["verdict"] = (
        "PASS" if (dsr is not None and dsr >= dsr_threshold)
        else "REJECT" if dsr is not None
        else "INCONCLUSIVE"
    )
    res["interpretation"] = _interpret(res)
    return res


def _interpret(res: dict) -> str:
    dsr = res.get("dsr")
    if dsr is None:
        return f"Could not compute DSR ({res.get('reason', 'unknown')})."
    pct = f"{dsr * 100:.1f}%"
    if dsr >= res.get("threshold", 0.95):
        return (
            f"After deflating for {res['n_trials']} trials, there's a {pct} chance "
            f"the edge is real, not a selection artifact. Worth paper-trading."
        )
    return (
        f"After deflating for {res['n_trials']} trials, only a {pct} chance the "
        f"edge survives selection bias. Most likely an overfit. Do not deploy."
    )


# --------------------------------------------------------------------------- #
#  Legitimacy gates (for when you build a multi-stage gauntlet)
# --------------------------------------------------------------------------- #
def _f(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return float(default)


def validate_robustness_payload(stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Reject a robustness stage that didn't actually produce evidence.

    Stages: walk_forward | monte_carlo | parameter_jitter | cost_stress | regime_split
    Returns {"ok": bool, "reason": str}. Call this BEFORE trusting a stage's
    pass/fail so an empty or errored payload can't silently graduate a strategy.
    """
    if not isinstance(payload, dict):
        return {"ok": False, "reason": "payload is not an object"}
    if payload.get("error"):
        return {"ok": False, "reason": str(payload.get("error"))}

    if stage == "walk_forward":
        n = int(_f(payload.get("n_folds") or len(payload.get("folds", []) or []), 0))
        return ({"ok": True, "reason": "has fold evidence"} if n >= 2
                else {"ok": False, "reason": "needs >= 2 out-of-sample folds"})

    if stage == "monte_carlo":
        sims = int(_f(payload.get("n_simulations") or payload.get("simulations"), 0))
        trades = int(_f(payload.get("n_trades") or payload.get("trade_count"), 0))
        if sims < 100 and not payload.get("equity_paths_sample"):
            return {"ok": False, "reason": "needs >= 100 simulations or sampled paths"}
        if trades < 10:
            return {"ok": False, "reason": "needs >= 10 baseline trades"}
        return {"ok": True, "reason": "has simulation evidence"}

    if stage == "parameter_jitter":
        iters = int(_f(payload.get("n_iterations") or payload.get("iterations"), 0))
        has_rate = any(k in payload for k in ("pass_rate", "stable_pct", "pct_positive_sharpe"))
        return ({"ok": True, "reason": "has stability evidence"} if iters >= 10 and has_rate
                else {"ok": False, "reason": "needs >= 10 iterations and a pass/stability rate"})

    if stage == "cost_stress":
        has = any(k in payload for k in ("stressed_sharpe", "min_sharpe", "degradation_pct"))
        return ({"ok": True, "reason": "has stressed-cost evidence"} if has
                else {"ok": False, "reason": "needs stressed performance metrics"})

    if stage == "regime_split":
        n = int(_f(payload.get("n_regimes") or len(payload.get("regimes", []) or []), 0))
        return ({"ok": True, "reason": "has multi-regime evidence"} if n >= 2
                else {"ok": False, "reason": "needs >= 2 regimes"})

    return {"ok": False, "reason": f"unknown stage: {stage}"}


# --------------------------------------------------------------------------- #
#  CLI:  python freqtrade_dsr.py <backtest.zip> <hyperopt_epochs>
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print("usage: python freqtrade_dsr.py <backtest_result.zip|.json> <hyperopt_epochs>")
        raise SystemExit(2)
    report = evaluate_freqtrade(sys.argv[1], int(sys.argv[2]))
    print(json.dumps(report, indent=2))
