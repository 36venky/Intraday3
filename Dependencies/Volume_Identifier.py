import yfinance as yf
import pandas as pd

def intraday_avg_volume_ratio(
    ticker: str,
    lookback_days: int = 5,
    interval: str = "15m"
):
    """
    Computes:
        volume_ratio = today_avg_volume / past_avg_volume

    where:
    - today_avg_volume = average volume per candle today (so far)
    - past_avg_volume  = average volume per candle over last N days
                          aligned to the same intraday time
    """

    # Download data
    df = yf.download(
        ticker,
        period=f"{lookback_days+3}d",
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise ValueError("No data fetched")

    # Flatten MultiIndex columns (yfinance safety)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Drop running candle
    df = df.iloc[:-1]

    # Add date column
    df["date"] = df.index.date
    unique_days = list(df["date"].unique())

    if len(unique_days) < lookback_days + 1:
        raise ValueError("Insufficient completed days")

    # Identify today and past days
    today = unique_days[-1]
    past_days = unique_days[-(lookback_days + 1):-1]

    # --- TODAY ---
    today_df = df[df["date"] == today]
    candle_count = len(today_df)

    if candle_count == 0:
        raise ValueError("No completed candles today")

    today_avg_volume = today_df["Volume"].mean()

    # --- PAST DAYS (time-aligned) ---
    past_avg_volumes = []

    for day in past_days:
        day_df = df[df["date"] == day]

        if len(day_df) >= candle_count:
            aligned_df = day_df.iloc[:candle_count]
            past_avg_volumes.append(aligned_df["Volume"].mean())

    if not past_avg_volumes:
        raise ValueError("No valid past days for comparison")

    past_avg_volume = sum(past_avg_volumes) / len(past_avg_volumes)

    # --- FINAL METRIC ---
    volume_ratio = today_avg_volume / past_avg_volume

    return volume_ratio, today_avg_volume, past_avg_volume


# # Example usage:
# ratio, today_avg, past_avg = intraday_avg_volume_ratio(
#     "BBOX.NS",
#     lookback_days=5
# )

# print(f"Today avg volume : {today_avg:,.0f}")
# print(f"Past avg volume  : {past_avg:,.0f}")
# print(f"Volume ratio     : {ratio:.2f}")
