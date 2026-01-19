
# signals/ma.py

import pandas as pd
import numpy as np

def ma_signal(
    df: pd.DataFrame,
    window: int,
    price_col: str = "Close"
) -> pd.Series:
    """
    MA-based directional signal:
    +1 if price > MA
    -1 if price < MA
    0  if undefined
    """
    price = df[price_col]
    ma = price.rolling(window).mean()

    signal = np.sign(price - ma)
    return signal
