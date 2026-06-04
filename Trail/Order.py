"""
Order Block Detector (Python Version)
Converted from Pine Script (LuxAlgo)

Requirements:
pip install pandas numpy matplotlib yfinance mplfinance
"""

import pandas as pd
import numpy as np
import yfinance as yf
import mplfinance as mpf

# =========================================================
# CONFIG
# =========================================================

TICKER = "APTUS.NS"
INTERVAL = "15m"
PERIOD = "15d"

length = 5
mitigation_method = "Wick"   # "Wick" or "Close"

bull_ext_last = 3
bear_ext_last = 3

# =========================================================
# DOWNLOAD DATA
# =========================================================

df = yf.download(
    TICKER,
    interval=INTERVAL,
    period=PERIOD,
    progress=False,
    auto_adjust=True
)

# =========================================================
# CLEAN COLUMNS
# =========================================================

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
df.dropna(inplace=True)

# =========================================================
# REMOVE MARKET CLOSED GAPS
# =========================================================
# mplfinance handles this automatically using:
# show_nontrading=False
# So no artificial overnight/weekend gaps appear

df.index = pd.to_datetime(df.index)

# =========================================================
# BASIC CALCULATIONS
# =========================================================

df["hl2"] = (df["High"] + df["Low"]) / 2

df["upper"] = df["High"].rolling(length).max()
df["lower"] = df["Low"].rolling(length).min()

# =========================================================
# MARKET STRUCTURE (os)
# =========================================================

os_list = [0] * len(df)

for i in range(length, len(df)):

    high_l = df["High"].iloc[i - length]
    low_l = df["Low"].iloc[i - length]

    upper = df["upper"].iloc[i]
    lower = df["lower"].iloc[i]

    prev_os = os_list[i - 1]

    if high_l > upper:
        os_list[i] = 0

    elif low_l < lower:
        os_list[i] = 1

    else:
        os_list[i] = prev_os

df["os"] = os_list

# =========================================================
# VOLUME PIVOT HIGH
# =========================================================

pivot_high = [False] * len(df)

for i in range(length, len(df) - length):

    current_vol = df["Volume"].iloc[i]

    left = df["Volume"].iloc[i - length:i]
    right = df["Volume"].iloc[i + 1:i + length + 1]

    combined = pd.concat([
        left,
        pd.Series([current_vol]),
        right
    ])

    if current_vol == combined.max():
        pivot_high[i] = True

df["phv"] = pivot_high

# =========================================================
# ORDER BLOCK STORAGE
# =========================================================

bullish_obs = []
bearish_obs = []

# =========================================================
# DETECT ORDER BLOCKS
# =========================================================

for i in range(length, len(df)):

    idx = i - length

    if idx < 0:
        continue

    phv = df["phv"].iloc[i]
    os_state = df["os"].iloc[i]

    # =====================================================
    # BULLISH ORDER BLOCK
    # =====================================================

    if phv and os_state == 1:

        top = df["hl2"].iloc[idx]
        bottom = df["Low"].iloc[idx]
        avg = (top + bottom) / 2

        bullish_obs.insert(0, {
            "left": df.index[idx],
            "top": top,
            "bottom": bottom,
            "avg": avg
        })

    # =====================================================
    # BEARISH ORDER BLOCK
    # =====================================================

    if phv and os_state == 0:

        top = df["High"].iloc[idx]
        bottom = df["hl2"].iloc[idx]
        avg = (top + bottom) / 2

        bearish_obs.insert(0, {
            "left": df.index[idx],
            "top": top,
            "bottom": bottom,
            "avg": avg
        })

    # =====================================================
    # MITIGATION TARGETS
    # =====================================================

    if mitigation_method == "Close":

        target_bull = df["Close"].iloc[max(0, i-length):i].min()
        target_bear = df["Close"].iloc[max(0, i-length):i].max()

    else:

        target_bull = df["Low"].iloc[max(0, i-length):i].min()
        target_bear = df["High"].iloc[max(0, i-length):i].max()

    # =====================================================
    # REMOVE MITIGATED BULLISH OB
    # =====================================================

    bullish_obs = [
        ob for ob in bullish_obs
        if not (target_bull < ob["bottom"])
    ]

    # =====================================================
    # REMOVE MITIGATED BEARISH OB
    # =====================================================

    bearish_obs = [
        ob for ob in bearish_obs
        if not (target_bear > ob["top"])
    ]

# =========================================================
# CREATE ORDER BLOCK PLOTS
# =========================================================

addplots = []

# =========================================================
# BULLISH ORDER BLOCKS
# =========================================================

for ob in bullish_obs[:bull_ext_last]:

    bull_top = pd.Series(np.nan, index=df.index)
    bull_bottom = pd.Series(np.nan, index=df.index)
    bull_avg = pd.Series(np.nan, index=df.index)

    bull_top.loc[df.index >= ob["left"]] = ob["top"]
    bull_bottom.loc[df.index >= ob["left"]] = ob["bottom"]
    bull_avg.loc[df.index >= ob["left"]] = ob["avg"]

    addplots.append(
        mpf.make_addplot(
            bull_top,
            color='green',
            width=1
        )
    )

    addplots.append(
        mpf.make_addplot(
            bull_bottom,
            color='green',
            width=1
        )
    )

    addplots.append(
        mpf.make_addplot(
            bull_avg,
            color='gray',
            linestyle='dashed',
            width=1
        )
    )

# =========================================================
# BEARISH ORDER BLOCKS
# =========================================================

for ob in bearish_obs[:bear_ext_last]:

    bear_top = pd.Series(np.nan, index=df.index)
    bear_bottom = pd.Series(np.nan, index=df.index)
    bear_avg = pd.Series(np.nan, index=df.index)

    bear_top.loc[df.index >= ob["left"]] = ob["top"]
    bear_bottom.loc[df.index >= ob["left"]] = ob["bottom"]
    bear_avg.loc[df.index >= ob["left"]] = ob["avg"]

    addplots.append(
        mpf.make_addplot(
            bear_top,
            color='red',
            width=1
        )
    )

    addplots.append(
        mpf.make_addplot(
            bear_bottom,
            color='red',
            width=1
        )
    )

    addplots.append(
        mpf.make_addplot(
            bear_avg,
            color='gray',
            linestyle='dotted',
            width=1
        )
    )

# =========================================================
# PLOT
# =========================================================

mpf.plot(
    df,
    type='candle',
    style='yahoo',
    volume=True,
    figsize=(18, 10),
    title=f"{TICKER} - Order Blocks",
    addplot=addplots,
    show_nontrading=False   # IMPORTANT: removes market-close gaps
)