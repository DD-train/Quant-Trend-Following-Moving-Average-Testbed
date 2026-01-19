
# data/loaders.py
'''
Goal: data load & preprocess
'''

import pandas as pd

def load_price_data(path: str) -> pd.DataFrame:
    """
    Load local CSV as price dataframe with a clean DatetimeIndex.

    Assumptions (same as your old code):
    - The FIRST column is date-like (index_col=0)
    - parse_dates=True
    - drop rows whose index cannot be parsed to datetime
    """
    # 1) read csv: first column as index, parse dates
    df = pd.read_csv(path, index_col=0, parse_dates=True)

    # 2) clean: drop rows whose index is not datetime-like
    idx = pd.to_datetime(df.index, errors="coerce")
    df = df[idx.notna()].copy()

    # 3) force DatetimeIndex
    df.index = pd.to_datetime(df.index)

    # 4) sort by time (good practice for slicing / rolling)
    df = df.sort_index()

    # 5) safety check: must be DatetimeIndex
    if df.index.dtype.kind != "M":
        raise TypeError(f"Index is not datetime after parsing. Got: {type(df.index)}")

    return df

