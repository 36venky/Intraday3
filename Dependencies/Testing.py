import numpy as np
import yfinance as yf
import logging
import matplotlib.pyplot as plt

import numpy as np

def variance_stability(prices, window=20, tolerance=0.15):
    prices = np.asarray(prices, dtype=float)

    if len(prices) < window * 2:
        return False

    returns = np.diff(prices)

    first = np.var(returns[:window])
    last  = np.var(returns[-window:])

    if first == 0:
        return False
    frac = last / first
    return (frac) < tolerance , frac

def drift_is_small(prices, max_drift_pct=1.5):
    prices = np.asarray(prices, dtype=float)
    drift = abs(prices[-1] - prices[0]) / prices[0] * 100
    return drift < max_drift_pct , drift

def frequent_direction_changes(prices, min_flips_ratio=0.4):
    prices = np.asarray(prices, dtype=float)

    diffs = np.diff(prices)
    signs = np.sign(diffs)

    flips = np.sum(signs[1:] * signs[:-1] < 0)
    return flips / len(signs) > min_flips_ratio , flips / len(signs)

def matches_your_pattern(prices):
    return (
        variance_stability(prices) and
        drift_is_small(prices) and
        frequent_direction_changes(prices)
    )

def Download(tickers):
    try:
        data = yf.download(
            tickers=tickers,
            interval='1m',
            period='1d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )
    except Exception as e:
        logging.error(f"Download error : {e}")
        return
    
    for ticker in tickers:
        try:
            df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
        except KeyError:
            logging.warning(f"[{ticker}] Data not found.")
            continue
        # Convert to IST and filter market hours
        try:
            df.index = df.index.tz_convert('Asia/Kolkata')
        except:
            df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

        df = df.between_time("09:15", "15:30")
        # plt.plot(df['Close'])
        # plt.show()
        #print(df["Close"].tolist())
        dc = df["Close"][:135]
        print(variance_stability(dc),ticker)

tickers = ['GVT&D','BAJAJHFL','TIMKEN','TIMKEN','GUJTHEM','VIPIND','NUVAMA','THERMAX','APOLLOHOSP','ROUTE','DSSL','NEOGEN','ADANIPOWER', 'APOLLO', 'ASHOKLEY', 'AXISBANK', 'BAJFINANCE', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BCG', 'BEL', 'BELRISE', 'BHARTIARTL', 'BHEL', 'BPCL', 'BSOFT', 'CANBK', 'CENTRALBK', 'DAVANGERE', 'DHARAN', 'EMMVEE', 'ETERNAL', 'EXCELSOFT', 'FEDERALBNK', 'FILATFASH', 'GAIL', 'GATECH', 'GMRAIRPORT', 'GOLDBEES', 'GOLDCASE', 'GROWW', 'GSPL', 'GTLINFRA', 'HDFCBANK', 'HDFCSILVER', 'HFCL', 'HINDPETRO', 'ICICIBANK', 'IDBI', 'IDFCFIRSTB', 'IEX', 'INDUSTOWER', 'INFIBEAM', 'INFY', 'IOB', 'IOC', 'IREDA', 'ITBEES', 'ITC', 'JAMNAAUTO', 'JIOFIN', 'JMFINANCIL', 'KTKBANK', 'LIQUIDCASE', 'MCLOUD', 'METALIETF', 'MMFL', 'MOTHERSON', 'NATCOPHARM', 'NATIONALUM', 'NBCC', 'NECLIFE', 'NHPC', 'NIFTYBEES', 'NMDC', 'NTPC', 'NTPCGREEN', 'OLAELEC', 'ONGC', 'PAISALO', 'PATELENG', 'PCJEWELLER', 'PFOCUS', 'PNB', 'POWERGRID', 'PROSTARM', 'PWL', 'RECLTD', 'BRITANNIA', 'RELIANCE', 'RHETAN', 'RICOAUTO', 'RPOWER', 'RTNPOWER', 'SAGILITY', 'SAIL', 'SALASAR', 'SAMMAANCAP', 'SBC', 'SBIN', 'SCI', 'SEPC', 'SETFGOLD', 'SHRIRAMFIN', 'SIGACHI', 'SILVERBEES', 'SILVERCASE', 'SILVERIETF', 'SINDHUTRAD', 'SOUTHBANK', 'SPARC', 'SUZLON', 'SWIGGY', 'TATAGOLD', 'TATASTEEL', 'TATSILV', 'TFCILTD', 'TMCV', 'TMPV', 'UCOBANK', 'UJJIVANSFB', 'UNIONBANK', 'UTKARSHBNK', 'VCL', 'VEDL', 'VIKRAN', 'VINCOFE', 'VMM', 'WEBELSOLAR', 'WIPRO', 'WOCKPHARMA', 'ZEEL']#EX.Price.list(10, 20)
tickers = [t + '.NS' for t in tickers]
Download(tickers)