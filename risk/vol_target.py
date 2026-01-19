
# risk/vol_target.py

import numpy as np
import pandas as pd

TRADING_DAYS = 252

def realized_vol(
    price_ret: pd.Series,
    lookback: int = 20,
    annualize: bool = False,
) -> pd.Series:
    """
    Rolling realized volatility from returns.
    - price_ret: e.g. Close.pct_change()
    - lookback: rolling window
    - annualize: if True, * sqrt(252)
    """
    vol = price_ret.rolling(lookback).std()
    if annualize:
        vol = vol * np.sqrt(TRADING_DAYS)
    return vol

def vol_target_scale(
    price_ret: pd.Series,
    lookback: int = 20,
    target_vol_annual: float = 0.10,
    min_scale: float = 0.0,
    max_scale: float = 2.0,
    vol_floor: float = 1e-8,
    shift: int = 1,
) -> pd.Series:
    """
    Volatility targeting: scale exposure inversely with recent realized vol.

    scale_t uses ONLY information up to t-1 (default shift=1) to avoid lookahead
    when positions are applied at t.

    scale = target_daily_vol / realized_daily_vol
    clipped to [min_scale, max_scale]
    """
    target_daily_vol = target_vol_annual / np.sqrt(TRADING_DAYS)

    vol = realized_vol(price_ret, lookback=lookback, annualize=False)
    if shift is not None and shift != 0:
        vol = vol.shift(shift)

    scale = target_daily_vol / vol.clip(lower=vol_floor)
    scale = scale.clip(lower=min_scale, upper=max_scale)

    return scale
