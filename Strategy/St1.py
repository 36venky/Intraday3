import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Data_Manager.data import previous_day_levels, get_data, Download
logging.basicConfig(level=logging.INFO)
from Dependencies import *
from datetime import datetime
# =========================================================
# BREAKOUT CHECK WITH TIMESTAMP
# =========================================================

def breakout_confirmation(ticker):

    # =====================================================
    # PREVIOUS DAY LEVELS
    # =====================================================

    prev_high, prev_low = previous_day_levels(ticker)

    if prev_high is None or prev_low is None:
        return

    # =====================================================
    # FETCH 15m DATA
    # =====================================================

    df_15m = get_data(ticker, "15m")

    if df_15m is None:
        return

    # =====================================================
    # FILTER TODAY DATA
    # =====================================================

    today = df_15m.index.date[-1]

    df_today = df_15m[
        df_15m.index.date == today
    ]

    # =====================================================
    # FIND VALID BULLISH BREAKOUT
    # =====================================================

    breakout_index = None

    breakout_high = None

    breakout_time = None

    for i, (idx, row) in enumerate(df_today.iterrows()):

        if (row['Open'] < prev_high and row['Open'] > prev_low and row['Close'] > prev_high):

            breakout_index = i

            breakout_high = row['High']

            breakout_time = idx

            break

    # =====================================================
    # NO BREAKOUT
    # =====================================================

    if breakout_index is None:
        return

    # =====================================================
    # NEXT 15m CANDLE
    # =====================================================

    if breakout_index + 1 >= len(df_today):
        return

    next_candle = df_today.iloc[breakout_index + 1]

    # =====================================================
    # SIGNAL LOGIC
    # =====================================================

    bearish_next = (next_candle['Close'] < next_candle['Open'])

    close_below_prev_high = (next_candle['Close'] < prev_high)

    no_high_break = (next_candle['High'] <= breakout_high)

    # =====================================================
    # FINAL SIGNAL
    # =====================================================

    signal = "BUY"

    if bearish_next and (close_below_prev_high or no_high_break):
        signal = "SELL"


    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sig,r2=is_fluctuation(ticker)
    if r2 > 0.75:
        write("1Breakouts.txt", f"{current_time},{ticker},{breakout_time},{signal},{r2:.2f}\n")
    else:
        pass
        #write("2Breakouts.txt", f"{current_time},{ticker},{breakout_time},{signal},{r2:.2f}\n")


def main(): #Test Usage
    tickers = ['ALKYLAMINE','SCI']#,'AURIONPRO','MTARTECH','UTIAMC','TRIVENI','BAJAJHFL','TIMKEN','TIMKEN','GUJTHEM','VIPIND','NUVAMA','THERMAX','APOLLOHOSP','ROUTE','DSSL','NEOGEN','ADANIPOWER', 'APOLLO', 'ASHOKLEY', 'AXISBANK', 'BAJFINANCE', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BCG', 'BEL', 'BELRISE', 'BHARTIARTL', 'BHEL', 'BPCL', 'BSOFT', 'CANBK', 'CENTRALBK', 'DAVANGERE', 'DHARAN', 'EMMVEE', 'ETERNAL', 'EXCELSOFT', 'FEDERALBNK', 'FILATFASH', 'GAIL', 'GATECH', 'GMRAIRPORT', 'GOLDBEES', 'GOLDCASE', 'GROWW', 'GSPL', 'GTLINFRA', 'HDFCBANK', 'HDFCSILVER', 'HFCL', 'HINDPETRO', 'ICICIBANK', 'IDBI', 'IDFCFIRSTB', 'IEX', 'INDUSTOWER', 'INFIBEAM', 'INFY', 'IOB', 'IOC', 'IREDA', 'ITBEES', 'ITC', 'JAMNAAUTO', 'JIOFIN', 'JMFINANCIL', 'KTKBANK', 'LIQUIDCASE', 'MCLOUD', 'METALIETF', 'MMFL', 'MOTHERSON', 'NATCOPHARM', 'NATIONALUM', 'NBCC', 'NECLIFE', 'NHPC', 'NIFTYBEES', 'NMDC', 'NTPC', 'NTPCGREEN', 'OLAELEC', 'ONGC', 'PAISALO', 'PATELENG', 'PCJEWELLER', 'PFOCUS', 'PNB', 'POWERGRID', 'PROSTARM', 'PWL', 'RECLTD', 'BRITANNIA', 'RELIANCE', 'RHETAN', 'RICOAUTO', 'RPOWER', 'RTNPOWER', 'SAGILITY', 'SAIL', 'SALASAR', 'SAMMAANCAP', 'SBC', 'SBIN', 'SCI', 'SEPC', 'SETFGOLD', 'SHRIRAMFIN', 'SIGACHI', 'SILVERBEES', 'SILVERCASE', 'SILVERIETF', 'SINDHUTRAD', 'SOUTHBANK', 'SPARC', 'SUZLON', 'SWIGGY', 'TATAGOLD', 'TATASTEEL', 'TATSILV', 'TFCILTD', 'TMCV', 'TMPV', 'UCOBANK', 'UJJIVANSFB', 'UNIONBANK', 'UTKARSHBNK', 'VCL', 'VEDL', 'VIKRAN', 'VINCOFE', 'VMM', 'WEBELSOLAR', 'WIPRO', 'WOCKPHARMA', 'ZEEL']#EX.Price.list(10, 20)
    tickers = [t + '.NS' for t in tickers]
    Download(tickers)
    for ticker in tickers:
        breakout_confirmation(ticker)

if __name__ == "__main__":
    main()
