import pandas as pd

df = pd.read_csv("Modules/Fluctuation.txt", header=None)

df.columns = [
    "time",
    "ticker",
    "volatility",
    "angle",
    "range",
    "count",
    "r2"
]

# convert time for proper ordering
# df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S")

df["time"] = pd.to_datetime(
    df["time"],
    format="%H:%M:%S",
    errors="coerce"
)

df = df.dropna(subset=["time"])


WINDOW = 4
THRESHOLD = 0.20

signals = []

for ticker, g in df.groupby("ticker"):
    g = g.sort_values("time").reset_index(drop=True)

    for i in range(len(g) - WINDOW + 1):
        window = g.iloc[i:i+WINDOW]

        diffs = window["r2"].diff().dropna()
        mean_diff = diffs.mean()

        if mean_diff >= THRESHOLD:
            signals.append({
                "ticker": ticker,
                "start_time": window.iloc[0]["time"].time(),
                "end_time": window.iloc[-1]["time"].time(),
                "mean_r2_increase": round(mean_diff, 3),
                "r2_values": window["r2"].tolist()
            })

for sig in signals:
    print(f"{sig}\n")

print(len(sig))