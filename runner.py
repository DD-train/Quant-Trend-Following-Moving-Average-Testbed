# runner.py
import pandas as pd
import numpy as np

from data.loaders import load_price_data
from signals.ma import ma_signal
from analysis.metrics import summary as summary_metrics
from risk.vol_target import vol_target_scale
from risk.risk_off_gate import risk_off_gate_vol

def load_and_slice_data(cfg):
    df = load_price_data(cfg.DATA_PATH)
    df = df.loc[cfg.START: cfg.END].copy()

    if df.empty:
        raise ValueError("Data empty after slicing. Check date parsing.")

    return df


def generate_position(df, cfg):
    price = df[cfg.PRICE_COL].astype(float)
    price_ret = price.pct_change()
    
    # 1) signal -> direction
    signal = ma_signal(df, window=cfg.MA_WINDOW, price_col=cfg.PRICE_COL)
    signal_exec = signal.shift(cfg.EXEC_DELAY) # 把今天生成的交易信号，推迟EXEC_DELAY天执行，避免 look-ahead bias（未来函数）
    # signal_exec = signal.shift(1) 
    
    # 2) base position (direction only)
    if cfg.LONG_ONLY:
        position = signal_exec.clip(lower=0)
    else:
        position = signal_exec.clip(-1, 1) # 把持仓限制在[-1,+1]之间，“安全护栏”
    
    
    # 3) risk layer (size only)
    # 方向来自 signal（不变），scale 来自风险（只影响仓位大小）
    # scale 用 returns 算出来，所以本质是 “risk-aware sizing”
    
    # volatiliy targeting
    if getattr(cfg, "RISK_MODE", "none") == "vol_target":
        scale = vol_target_scale(
            price_ret=price_ret,
            lookback=cfg.VOL_LOOKBACK,
            target_vol_annual=cfg.TARGET_VOL_ANNUAL,
            min_scale=cfg.MIN_SCALE,
            max_scale=cfg.MAX_SCALE,
        )
        # NOTE:
        # scale is NaN at early periods due to rolling volatility estimation;
        # this is expected behavior and avoids look-ahead bias.   
        position = position * scale
    
    # ---------- risk-off gate ----------
    gate = None
    if getattr(cfg, "USE_RISK_OFF_GATE", False):
        gate = risk_off_gate_vol(
            price_ret=price_ret,
            lookback=cfg.GATE_LOOKBACK,
            vol_threshold_annual=cfg.GATE_VOL_THRESHOLD_ANNUAL,
        )
        position = position * gate
    
    
    
    return price, price_ret, signal, position, gate


def run(cfg):
    df = load_and_slice_data(cfg)
    price, price_ret, signal, position, gate = generate_position(df, cfg)


    # position - position.shift(1): 今天的仓位 − 昨天的仓位
    turnover = (position.fillna(0) - position.fillna(0).shift(1)).abs() 
    #.fillna(0): NaN在这表示还没建仓，用0填充，即：没仓位=空仓

    # pnl = 赚钱 − 付钱
    pnl = position * price_ret - turnover * cfg.COST_RATE

    result = pd.DataFrame(
        {
            "price": price,
            "price_ret": price_ret,
            "signal": signal,
            "position": position,
            "turnover": turnover,
            "ret": pnl,
            "equity": (1 + pnl.fillna(0)).cumprod(),
        },
        index=df.index,
    )
    
    if gate is not None:
        result["gate"] = gate

    summary = summary_metrics(result)
    return result, summary
