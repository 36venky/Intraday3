import json
import os
import logging
from datetime import datetime
from typing import Tuple, List

# ============================================================
# CONFIG
# ============================================================
R2_FILE = "r2_store.jsonl"
LOG_FILE = "logs/r2_store.log"

MEAN_DIFF_THRESHOLD = 0.15
MIN_LATEST_R2 = 0.70
MAX_LOOKBACK = 10   # read last N per ticker

# ============================================================
# LOGGING SETUP (WINDOWS SAFE)
# ============================================================
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)

logger = logging.getLogger("R2")

# ============================================================
# STORE (APPEND ONLY — MULTI PROCESS SAFE)
# ============================================================
def store_r2(ticker: str, r2: float) -> None:
    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "ticker": ticker,
        "r2": round(float(r2), 4)
    }

    with open(R2_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    logger.info(f"Stored R2 | {ticker} | r2={r2:.4f}")

# ============================================================
# READ LAST N R2 FOR TICKER
# ============================================================
def _read_last_r2(ticker: str, limit: int = MAX_LOOKBACK) -> List[float]:
    if not os.path.exists(R2_FILE):
        return []

    values = []

    # Read file backwards efficiently
    with open(R2_FILE, "r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            if rec.get("ticker") == ticker:
                values.append(rec["r2"])
                if len(values) >= limit:
                    break

    return list(reversed(values))

# ============================================================
# SIGNAL LOGIC
# ============================================================
def r2_signal(
    ticker: str,
    mean_threshold: float = MEAN_DIFF_THRESHOLD,
    min_latest_r2: float = MIN_LATEST_R2
) -> Tuple[bool, float, float]:
    """
    Returns:
    (signal, mean_diff, latest_r2)
    Always returns floats (never None)
    """

    r2_vals = _read_last_r2(ticker, limit=3)

    if len(r2_vals) < 3:
        latest = r2_vals[-1] if r2_vals else 0.0
        return False, 0.0, latest

    diffs = [
        r2_vals[1] - r2_vals[0],
        r2_vals[2] - r2_vals[1]
    ]

    mean_diff = round(sum(diffs) / len(diffs), 4)
    latest_r2 = r2_vals[-1]

    signal = (
        mean_diff >= mean_threshold
        and latest_r2 >= min_latest_r2
    )

    logger.info(
        f"{ticker} | r2={r2_vals} | mean_diff={mean_diff:.4f} | signal={signal}"
    )

    return signal, mean_diff, latest_r2

# ============================================================
# TEST
# ============================================================
# if __name__ == "__main__":
#     ticker = "TCS.NS"

#     for r2 in [0.52, 0.66, 0.82]:
#         store_r2(ticker, r2)
#         signal, mean, latest = r2_signal(ticker)

#         if signal:
#             logger.warning(f"VALID | {ticker} | mean={mean} | r2={latest}")
#         else:
#             logger.info(f"NO SIGNAL | {ticker} | mean={mean} | r2={latest}")
