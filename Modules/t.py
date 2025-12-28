# import numpy as np
# import yfinance as yf
# import logging
# def slanted_trend_full(prices, slope_thresh=(0.0, 0.1), r2_thresh=0.8, vol_thresh=0.002, reversal_pct=0.005):
#     """
#     Detect low-volatility slanted trends and early reversals using the complete price series.

#     Parameters
#     ----------
#     prices : np.ndarray
#         1D array of prices (closing prices or Heikin-Ashi close)
#     slope_thresh : tuple
#         Min and max slope to consider as a slanted trend
#     r2_thresh : float
#         Minimum R² to consider a valid trend
#     vol_thresh : float
#         Maximum normalized volatility to consider trend stable
#     reversal_pct : float
#         Early reversal threshold in relative price change (e.g., 0.5% = 0.005)

#     Returns
#     -------
#     trend : int
#         1 = uptrend, -1 = downtrend, 0 = no trend
#     early_exit : bool
#         True if early reversal is detected
#     slope : float
#         Regression slope over full data
#     r2 : float
#         R² of regression fit
#     volatility : float
#         Normalized volatility over full data
#     """
#     prices = np.asarray(prices)
#     n = len(prices)
#     x = np.arange(n)
    
#     # Linear regression
#     A = np.vstack([x, np.ones(n)]).T
#     slope, intercept = np.linalg.lstsq(A, prices, rcond=None)[0]
#     y_pred = slope * x + intercept
    
#     # R² calculation
#     ss_res = np.sum((prices - y_pred)**2)
#     ss_tot = np.sum((prices - np.mean(prices))**2)
#     r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
    
#     # Normalized volatility (std / mean)
#     volatility = np.std(prices) / np.mean(prices) if np.mean(prices) != 0 else 0
    
#     # Trend detection
#     trend = 0
#     if slope_thresh[0] <= slope <= slope_thresh[1] and r2 >= r2_thresh and volatility <= vol_thresh:
#         trend = 1 if slope > 0 else -1
    
#     # Early reversal detection (if last price moves opposite beyond reversal_pct)
#     early_exit = False
#     if trend != 0:
#         rel_change = (prices[-1] - prices[-2]) / prices[-2]
#         if (trend == 1 and rel_change < -reversal_pct) or (trend == -1 and rel_change > reversal_pct):
#             early_exit = True
    
#     return trend, early_exit, slope, r2, volatility

# # Example usage
# if __name__ == "__main__":
#     ticker = 'BLUEJET.NS'
#     try:
#         data = yf.download(
#             tickers=ticker,
#             interval='1m',
#             period='1d',
#             progress=False,
#             auto_adjust=True,
#             group_by='ticker'
#         )
#     except Exception as e:
#         logging.error(f"Download error for {ticker}: {e}")
#         print(False , 0)

#     try:
#         df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
#     except KeyError:
#         logging.warning(f"[{ticker}] Data not found.")
#         print(False , 0)

#     # Convert to IST and filter market hours
#     try:
#         df.index = df.index.tz_convert('Asia/Kolkata')
#     except:
#         df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

#     prices = df['Close']
#     trend, early_exit, slope, r2, vol = slanted_trend_full(prices)
#     print(f"Trend: {trend}, Early exit: {early_exit}, Slope: {slope:.5f}, R²: {r2:.3f}, Volatility: {vol:.5f}")

from collections import defaultdict

h = defaultdict(list)

def add_value(key, value):
    h[key].append(value)

    if len(h[key]) < 3:
        return False,0.0,0.0

    last3 = h[key][-3:]
    diffs = [
        last3[1] - last3[0],
        last3[2] - last3[1]
    ]

    mean_diff = round(sum(diffs) / len(diffs), 2)
    latest = last3[-1]
    if mean_diff >= 0.15 and latest >= 0.70:
        return True,mean_diff, latest
    return False,mean_diff,latest

print(add_value("AAPL", 0.32))
print(add_value("AAPL", 0.51))
print(add_value("AAPL", 0.61))
print(add_value("AAPL", 0.75))