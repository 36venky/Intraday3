import yfinance as yf
import json
import pytz
import time as tm
from datetime import datetime, timedelta, time as dtime
import os
import logging

# --- Logging Setup ---
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "Main.log")
if not logging.getLogger().handlers:
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def save_live_1min_close(symbol: str):
    """
    Fetches and stores 1-min close prices for a given stock symbol:
      - If market is open (9:15–15:15), downloads today's data so far, then appends live data every minute.
      - If market is closed, downloads previous trading day's full 1-min data.
    Data is stored in ./data/<symbol>_1min.json
    """
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    json_dir = "data"
    os.makedirs(json_dir, exist_ok=True)
    json_file = os.path.join(json_dir, f"{symbol.replace('.NS', '')}_1min.json")

    now = datetime.now(kolkata_tz)
    current_time = now.time()

    # Load existing data if available
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as f:
                close_data = json.load(f)
        except json.JSONDecodeError:
            close_data = []
    else:
        close_data = []

    # Determine whether to fetch today's data or previous trading day's data
    if current_time < dtime(9, 15) or current_time > dtime(15, 15):
        start_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        logging.info(f"📅 Market closed. Fetching previous trading day's data for {symbol} ({start_date})...")
    else:
        start_date = now.strftime("%Y-%m-%d")
        logging.info(f"📊 Market open. Fetching today's data up to now for {symbol}...")

    try:
        # Fetch 1-min data for 1 day
        data = yf.download(symbol, interval="1m", period="1d", progress=False, auto_adjust=True)

        kolkata_data = []
        for idx, row in data.iterrows():
            utc_time = idx.to_pydatetime().replace(tzinfo=pytz.UTC)
            kolkata_time = utc_time.astimezone(kolkata_tz)
            time_str = kolkata_time.strftime("%H:%M")

            # ✅ FIXED: safely extract close value as float
            close_value = row["Close"]
            if hasattr(close_value, "iloc"):  # handle Series case
                close_value = close_value.iloc[0]
            kolkata_data.append({"timestamp": time_str, "close": float(close_value)})

        with open(json_file, "w") as f:
            json.dump(kolkata_data, f, indent=2)

        logging.info(f"✅ Saved {len(kolkata_data)} records for {symbol} to {json_file}")

    except Exception as e:
        logging.error(f"⚠️ Error fetching initial data for {symbol}: {e}")
        return

    if current_time < dtime(9, 15) or current_time > dtime(15, 15):
        logging.info("🛑 Market closed — collected full previous day's data only.")
        return

    logging.info("⏱ Now tracking live 1-min updates until 3:15 PM IST...")

    while True:
        now = datetime.now(kolkata_tz)
        current_time = now.time()

        if current_time >= dtime(15, 15):
            logging.info("🛑 Market closed (3:15 PM). Stopping live updates.")
            break

        try:
            data = yf.download(symbol, interval="1m", period="1d", progress=False, auto_adjust=True)

            if not data.empty:
                last_row = data.iloc[-1]
                utc_time = data.index[-1].to_pydatetime().replace(tzinfo=pytz.UTC)
                kolkata_time = utc_time.astimezone(kolkata_tz)
                time_str = kolkata_time.strftime("%H:%M")

                # ✅ FIXED again here
                close_value = last_row["Close"]
                if hasattr(close_value, "iloc"):
                    close_value = close_value.iloc[0]

                entry = {"timestamp": time_str, "close": float(close_value)}

                with open(json_file, "r") as f:
                    try:
                        close_data = json.load(f)
                    except json.JSONDecodeError:
                        close_data = []

                if not close_data or close_data[-1]["timestamp"] != time_str:
                    close_data.append(entry)
                    with open(json_file, "w") as f:
                        json.dump(close_data, f, indent=2)
                        
        except Exception as e:
            logging.error(f"⚠️ Error during live update: {e}")

        now = datetime.now()
        next_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait_seconds = (next_time - now).total_seconds()
        tm.sleep(wait_seconds)


# # --- Example usage ---
# if __name__ == "__main__":
#     save_live_1min_close("SCI.NS")
