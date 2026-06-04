import psutil
import os
import time
import datetime

process = psutil.Process(os.getpid())

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
cycle = 0

while True:
    cycle += 1
    start_time = time.time()

    print(f"\n🔁 Cycle {cycle} started")

    for ticker in tickers:
        stock_start = time.time()

        result = ticker
        print(result)

        stock_time = round(time.time() - stock_start, 3)
        print(f"   ⏱ {ticker} processed in {stock_time}s")

    # 🔹 Performance metrics
    execution_time = round(time.time() - start_time, 3)
    memory_usage = round(process.memory_info().rss / 1024 / 1024, 2)
    now = datetime.datetime.now().strftime("%H:%M:%S")

    log_line = f"[{now}] Cycle {cycle} | Time: {execution_time}s | RAM: {memory_usage} MB"
    print(log_line)

    with open("performance.log", "a") as f:
        f.write(log_line + "\n")

    # 🔹 Stop at 2 PM
    if datetime.datetime.now().time() >= datetime.time(14, 0):
        print("⛔ Stopping analyzer at 2 PM")
        break

    time.sleep(60)