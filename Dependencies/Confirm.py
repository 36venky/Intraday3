import yfinance as yf
import pandas as pd
import numpy as np

def comfirm(symbol):
    df = yf.download(
        symbol,
        period="7d",
        interval="1h",
        auto_adjust=True,
        progress=False
    )

    if df is None or df.empty or len(df) < 6:
        #print(f"❌ Not enough data for {symbol}")
        return

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

    # ---- Current candle (force as ndarray) ----
    current = df.iloc[-1]

    # ---- Previous 5 candles ----
    previous_5 = df.iloc[-6:-1]

    # ---------- Volume ----------
    avg_vol_prev_5 = np.mean(previous_5['Volume'].values)
    current_vol = current['Volume'].item()

    volume_condition = current_vol > avg_vol_prev_5

    # ---------- Wick & Body ----------
    open_price  = current['Open'].item()
    close_price = current['Close'].item()
    high_price  = current['High'].item()

    body = abs(close_price - open_price)

    if body == 0:
        #print(f"❌ {symbol} skipped (zero body candle)")
        return

    upper_wick = high_price - max(open_price, close_price)
    wick_condition = upper_wick < (0.5 * body)

    # ---------- Output ----------
    # print("\n----------------------------------")
    # print(f"Stock: {symbol}")
    # print(f"Current Volume: {current_vol}")
    # print(f"Average Volume (prev 5): {avg_vol_prev_5}")
    # print(f"Body Size: {body}")
    # print(f"Upper Wick: {upper_wick}")

    if volume_condition and wick_condition:
        #print("✅ CONDITION PASSED")
        return True
    else:
        #print("❌ CONDITION FAILED")
        return False

    # return {
    #     "symbol": symbol,
    #     "volume_condition": volume_condition,
    #     "wick_condition": wick_condition,
    #     "current_volume": current_vol,
    #     "avg_volume_prev_5": avg_vol_prev_5,
    #     "body": body,
    #     "upper_wick": upper_wick
    # }


# # ✅ Test
# print(check_volume_and_wick("PARADEEP.NS"))