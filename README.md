# Intraday Stock Analysis System

This project is a modular, Python-based framework for intraday stock analysis, signal generation, and backtesting. It leverages real-time and historical data from Yahoo Finance, applies technical indicators, and uses custom logic to identify buy/sell signals for Indian stocks.

## Features

- **Real-Time Analysis:** Concurrently runs multiple analyzers for different stock price bands.
- **Technical Indicators:** Includes EMA, RSI, VWAP, and custom volume/angle logic.
- **Signal Generation:** Detects buy/sell signals based on price action, volume, and statistical patterns.
- **Data Handling:** Fetches, processes, and stores intraday data efficiently.
- **Logging & Alerts:** Custom logging levels and optional WhatsApp alerts via Twilio.
- **Extensible Modules:** Organized by price bands and analysis type for easy extension.
- **MongoDB Integration:** Stores signals and regression results for further analysis.

## Project Structure

- Main.py — Launches all analyzer modules concurrently.
- Aanlyze_Sleep.py — Core real-time analysis logic, indicator computation, and signal writing.
- CleanUp.py — Utility to clean up logs and temporary files.
- Dependencies — Core logic for indicators, volume, angle, logging, messaging, and more.
- Indicators — Standalone technical indicator implementations (EMA, RSI, VWAP, Volume).
- Modules — Analyzer scripts for different price bands (e.g., mod_10_20.py).
- Trail — Additional analysis and plotting scripts.
- intraday — Python virtual environment and dependencies.

## How It Works

1. **Run Main.py:** This script finds and launches all `mod_*.py` analyzer modules in parallel.
2. **Each Analyzer:** Loads a list of tickers, fetches 15-min data, computes indicators, and applies buy/sell logic.
3. **Signal Storage:** Valid signals are written to text files and MongoDB collections.
4. **Logging:** All events are logged with custom levels for easy debugging and monitoring.

## Requirements

- Python 3.8+
- Packages: `yfinance`, `pandas`, `numpy`, `matplotlib`, `dtaidistance`, `pymongo`, `python-dotenv`, `twilio`, `scikit-learn`
- MongoDB (for signal storage)
- Twilio account (for WhatsApp alerts, optional)

## Setup

1. **Clone the repository.**
2. **Set up the Python environment:**
   ```
   python -m venv intraday
   intraday\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Create a .env file with your MongoDB URI and Twilio credentials.
4. **Run the main script:**
   ```
   python Main.py
   ```

## Customization

- Add or modify analyzer modules in Modules for different price bands or strategies.
- Adjust indicator parameters and thresholds in Aanlyze_Sleep.py and Dependencies.
- Extend logging, messaging, or data storage as needed.

## Disclaimer

This project is for educational and research purposes only. It is **not** financial advice. Use at your own risk.

---

Let me know if you want this saved as a `README.md` file or need further customization!
