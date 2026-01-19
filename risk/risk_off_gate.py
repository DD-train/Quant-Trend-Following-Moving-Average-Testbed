
### realized vol gate

# risk/risk_off_gate.py
import numpy as np
import pandas as pd

TRADING_DAYS = 252

def realized_vol_daily(price_ret: pd.Series, lookback: int = 20, shift: int = 1) -> pd.Series:
    vol = price_ret.rolling(lookback).std()
    if shift:
        vol = vol.shift(shift)
    return vol

def risk_off_gate_vol(
    price_ret: pd.Series,
    lookback: int = 20,
    vol_threshold_annual: float = 0.30,   # 例：年化30%进入risk-off
    shift: int = 1,
) -> pd.Series:
    """
    Gate = 0 when realized vol (annualized) > threshold, else 1.
    Uses only past info via shift to avoid lookahead.
    """
    vol_daily = price_ret.rolling(lookback).std()
    vol_annual = vol_daily * np.sqrt(TRADING_DAYS)
    if shift:
        vol_annual = vol_annual.shift(shift)

    gate = (vol_annual <= vol_threshold_annual).astype(float)

    # 前 lookback 段会 NaN，保守起见：gate=0（先不开仓）或 gate=1（照常）
    # 这里建议 0，更严格
    gate = gate.fillna(0.0)

    return gate
