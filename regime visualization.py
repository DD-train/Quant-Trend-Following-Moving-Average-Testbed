
# visualize regimes


import pandas as pd
import numpy as np

# ===== 1) Load & clean =====
path = "/mnt/data/SPY_2015_2025.csv"  # 你的文件路径
raw = pd.read_csv(path)

# 你的csv第一列叫 "Price"，但第1行其实是"Date"占位，需要清掉
df = raw[raw["Price"] != "Date"].copy()

# parse date
df["Date"] = pd.to_datetime(df["Price"], errors="coerce")
df = df.drop(columns=["Price"])

# numeric columns
for c in ["Close", "Open", "High", "Low", "Volume"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# sort & set index
df = df.sort_values("Date").dropna(subset=["Date", "Close"]).reset_index(drop=True)
df = df.set_index("Date")

# ===== 2) Returns & rolling stats =====
df["ret"] = df["Close"].pct_change()

# rolling vol (annualized)
TRADING_DAYS = 252
df["vol_60d"]  = df["ret"].rolling(60).std()  * np.sqrt(TRADING_DAYS)
df["vol_120d"] = df["ret"].rolling(120).std() * np.sqrt(TRADING_DAYS)

# rolling return (annualized, simple approximation)
df["ann_ret_60d"]  = df["ret"].rolling(60).mean()  * TRADING_DAYS
df["ann_ret_120d"] = df["ret"].rolling(120).mean() * TRADING_DAYS

# ===== 3) Drawdown =====
df["cum"] = (1 + df["ret"].fillna(0)).cumprod()
df["peak"] = df["cum"].cummax()
df["dd"] = df["cum"] / df["peak"] - 1.0  # drawdown (<=0)

# (optional) log price for nicer plots
df["log_close"] = np.log(df["Close"])

df.head()
