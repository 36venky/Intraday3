import pandas as pd 

def EMA(df, length):
    close = df.get("Close")
    if close is None or close.empty:
        return pd.Series(dtype=float)

    out = close.ewm(span=length, adjust=False).mean()
    df[f"EMA_{length}"] = out
    return df[f"EMA_{length}"]

