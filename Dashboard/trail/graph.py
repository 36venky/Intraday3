'''
This module provides a Streamlit dashboard for visualizing stock price data using candlestick charts. 
It allows users to input multiple stock tickers, select the desired time interval and period, 
and then generates interactive candlestick charts for each ticker.

Key Features:
- User-friendly interface for inputting stock tickers and selecting time intervals.
- Utilizes yfinance to fetch historical stock data and mplfinance for plotting candlestick charts.
- Handles data cleaning and timezone adjustments to ensure accurate visualizations.
'''
import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd

st.set_page_config(page_title="Candlestick Chart", layout="wide")

st.title("📈 Stock Candlestick Viewer")

tickers_input = st.text_input(
    "Enter Tickers (comma separated)",
    "RELIANCE.NS,INFY.NS,TCS.NS"
)
tickers = [t.strip() for t in tickers_input.split(",")]

interval = st.selectbox("Interval", ["1m", "15m","1d"])
period = st.selectbox("Period", ["1d", "5d"])

def download_and_plot(ticker, interval, period):

    data = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if data.empty:
        st.error("No data found")
        return

    # 🔥 FIX 1: Flatten columns if MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 🔥 FIX 2: Ensure correct columns exist
    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in data.columns for col in required_cols):
        st.error(f"Missing columns: {data.columns}")
        return

    df = data[required_cols].copy()

    # 🔥 FIX 3: Convert timezone
    try:
        df.index = df.index.tz_convert('Asia/Kolkata')
    except:
        df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

    # 🔥 FIX 4: Filter trading hours
    df = df.between_time("09:15", "15:30")

    # 🔥 FIX 5: Force numeric
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    # 🔥 DEBUG (optional)
    # st.write(df.dtypes)

    if df.empty:
        st.error("No valid numeric data after cleaning")
        return

    # Plot
    fig, axlist = mpf.plot(
        df,
        type='candle',
        style='charles',
        mav=(9, 21),
        returnfig=True
    )

    st.pyplot(fig)

def plot_multiple_grid(tickers, interval, period):

    cols = st.columns(3)  # 🔥 3 charts per row

    for i, ticker in enumerate(tickers):

        with cols[i % 3]:   # cycle through 3 columns

            st.markdown(f"### {ticker}")

            data = yf.download(
                ticker,
                interval=interval,
                period=period,
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                st.warning("No data")
                continue

            # Fix MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            df = data[['Open', 'High', 'Low', 'Close']].copy()

            # Timezone fix
            try:
                df.index = df.index.tz_convert('Asia/Kolkata')
            except:
                df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

            # Market hours
            df = df.between_time("09:15", "15:30")

            # Numeric fix
            df = df.apply(pd.to_numeric, errors='coerce').dropna()

            if df.empty:
                st.warning("No valid data")
                continue

            # Plot
            mc = mpf.make_marketcolors(
            up='lime',
            down='red',
            edge='inherit',
            wick='white',
            volume='inherit'
            )

            dark_style = mpf.make_mpf_style(
                base_mpf_style='nightclouds',
                marketcolors=mc,
                facecolor='black',
                figcolor='black',
                gridcolor='gray'
            )

            fig, _ = mpf.plot(
                df,
                type='candle',
                style=dark_style,
                mav=(9, 21),
                figratio=(16, 9),   # 🔥 rectangular shape
                figscale=0.9,       # fit nicely in grid
                returnfig=True
            )

            st.pyplot(fig)

# if st.button("Plot Chart"):
#     download_and_plot(ticker, interval, period)

if st.button("Plot Multiple Charts"):
    plot_multiple_grid(tickers, interval, period)