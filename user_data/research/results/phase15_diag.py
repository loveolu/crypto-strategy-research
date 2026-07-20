"""Post-hoc diagnostics for phase15 (reporting only, no new constructs):
1. Average exposure full/TEST for baseline vs GK30 — explains the TEST Sharpe drop.
2. DSR at n_trials=98 reference (pre-registration named 98; honest spend was 97).
3. Where the TEST-split P&L difference comes from (monthly).
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from phase15_rangevol import (dfs, closes2, SYMS2, basket_weights, net_from_weights,
                              rv_cc, rv_gk, rets, deflated_sharpe_ratio)

Wb = basket_weights(dfs, rv_cc, SYMS2)
Wg = basket_weights(dfs, rv_gk, SYMS2)
rb, rg = rets['base'], rets['gk']
n = len(rb)
te0 = int(n * 0.85)
te_idx = rb.index[te0:]

for tag, W in [('cc30', Wb), ('GK30', Wg)]:
    pos = W.shift(2).reindex(rb.index).fillna(0).sum(axis=1)
    print(f"{tag}: mean exposure FULL {pos.mean():.3f}  TEST {pos.loc[te_idx].mean():.3f}  "
          f"in-mkt days TEST {(pos.loc[te_idx] > 0).sum()}")

turn_b = Wb.shift(2).diff().abs().sum(axis=1).reindex(te_idx).sum()
turn_g = Wg.shift(2).diff().abs().sum(axis=1).reindex(te_idx).sum()
print(f"TEST-split turnover: cc30 {turn_b:.1f}  GK30 {turn_g:.1f} (fee drag x0.0015)")

diff = (rg - rb).loc[te_idx]
by_m = diff.groupby([diff.index.year, diff.index.month]).sum().sort_values()
print("\nTEST monthly P&L difference (GK minus baseline), worst 5 / best 5:")
print(by_m.head(5).to_string())
print(by_m.tail(5).to_string())

print("\nDSR at n_trials=98 (reference; honest spend was 97):")
for tag, r in [('baseline cc30', rb), ('GK30', rg)]:
    res = deflated_sharpe_ratio(r.tolist(), n_trials=98)
    print(f"  {tag:<15} DSR={res['dsr']:.4f}")
