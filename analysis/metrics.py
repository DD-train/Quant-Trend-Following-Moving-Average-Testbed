
# analysis/metrics.py
# Revised metrics module (research-repo friendly)
# - Works with either:
#   (A) result has 'ret' (strategy daily returns), or
#   (B) result has 'equity' (equity curve), or
#   (C) legacy 'portfolio' (equity curve)
# - Uses effective return sample count for annualization (more robust than len(df))
# - Turnover uses sum(|pos_t - pos_{t-1}|) and supports missing 'position'

from __future__ import annotations

import numpy as np
import pandas as pd


def _require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"metrics: missing required columns: {missing}. "
                         f"Available columns: {list(df.columns)}")


def ensure_ret_equity(result: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure dataframe has both:
      - ret: strategy periodic returns
      - equity: equity curve (starts at 1.0 if built from ret)
    Accepts input containing at least one of:
      - 'ret'
      - 'equity'
      - 'portfolio' (legacy name for equity)
    """
    out = result.copy()

    # Normalize equity column name
    if "equity" in out.columns:
        out["equity"] = out["equity"].astype(float)
    elif "portfolio" in out.columns:
        out = out.rename(columns={"portfolio": "equity"})
        out["equity"] = out["equity"].astype(float)

    # Build equity if only ret is provided
    if "equity" not in out.columns:
        if "ret" not in out.columns:
            raise ValueError("metrics: need one of ['ret', 'equity', 'portfolio'] in result.")
        out["ret"] = out["ret"].astype(float)
        out["equity"] = (1.0 + out["ret"]).cumprod()

    # Build ret if only equity is provided
    if "ret" not in out.columns:
        out["ret"] = out["equity"].pct_change()

    return out


def add_performance_columns(result: pd.DataFrame) -> pd.DataFrame:
    """
    Add:
      - cum_max, drawdown
      - pos_change (if 'position' exists)
    """
    out = ensure_ret_equity(result).copy()

    out["cum_max"] = out["equity"].cummax()
    out["drawdown"] = out["equity"] / out["cum_max"] - 1

    if "position" in out.columns:
        out["pos_change"] = out["position"].astype(float).diff().abs()
    else:
        # Keep column present for downstream code; turnover becomes NaN/0 depending on usage
        out["pos_change"] = np.nan

    return out


def max_drawdown(result: pd.DataFrame) -> float:
    out = result if "drawdown" in result.columns else add_performance_columns(result)
    dd = out["drawdown"].dropna()
    return float(dd.min()) if len(dd) else np.nan


def sharpe_ratio(result: pd.DataFrame, trading_days: int = 252) -> float:
    out = ensure_ret_equity(result)
    r = out["ret"].dropna()
    if len(r) < 2:
        return np.nan
    std = r.std()
    if std == 0 or np.isnan(std):
        return np.nan
    return float(r.mean() / std * np.sqrt(trading_days))


def annual_return(result: pd.DataFrame, trading_days: int = 252) -> float:
    """
    Robust annual return:
      - Uses equity endpoints
      - Annualizes using effective number of return observations (non-NaN ret)
    """
    out = ensure_ret_equity(result)

    equity = out["equity"].dropna()
    if len(equity) < 2:
        return np.nan

    initial = float(equity.iloc[0])
    final = float(equity.iloc[-1])

    n = out["ret"].dropna().shape[0]  # effective sample count
    if n <= 0:
        return np.nan
    years = n / trading_days
    if years <= 0:
        return np.nan

    return float((final / initial) ** (1 / years) - 1)


def total_turnover(result: pd.DataFrame) -> float:
    """
    Total turnover proxy:
      sum_t |position_t - position_{t-1}|
    Works for:
      - long-only 0/1
      - long-short -1/0/1
      - continuous weights
    If 'position' not present, returns NaN.
    """
    out = result if "pos_change" in result.columns else add_performance_columns(result)
    if "pos_change" not in out.columns:
        return np.nan
    pc = out["pos_change"].dropna()
    return float(pc.sum()) if len(pc) else np.nan


def summary(result: pd.DataFrame, trading_days: int = 252) -> dict:
    out = add_performance_columns(result)
    return {
        # 收益
        "Annual Return": annual_return(out, trading_days),
        # 风险
        "Max Drawdown": max_drawdown(out),
        "Sharpe": sharpe_ratio(out, trading_days),
        # 交易强度
        "Total Turnover": total_turnover(out),
        # N_obs：用于统计绩效指标的“有效收益观测点数量” -> 样本可信度
        "N_obs": int(out["ret"].dropna().shape[0]), 
        # .dropna()：去掉所有无效收益,如:NaN 
        # .shape[0]: 取行数
    }
