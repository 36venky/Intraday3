import yfinance as yf
import mplfinance as mpf
import streamlit as st
import pandas as pd

st.title("📈 Intraday Candlestick Chart")

ticker = st.text_input("Enter Ticker", "ETERNAL.NS")


def download_data(ticker):

    data = yf.download(
        ticker,
        interval="5m",
        period="1d",
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        return None

    # Flatten columns if MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    df = data[['Open','High','Low','Close','Volume']].copy()

    # Convert timezone to IST
    try:
        df.index = df.index.tz_convert("Asia/Kolkata")
    except:
        df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")

    # Market hours filter
    df = df.between_time("09:15","15:30")

    # Convert to float (critical for mplfinance)
    df = df.astype(float)

    df = df.dropna()

    return df


df = download_data(ticker)

if df is not None and not df.empty:

    mc = mpf.make_marketcolors(
        up="lime",
        down="red",
        edge="inherit",
        wick="white",
        volume="inherit"
    )

    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=mc,
        facecolor="black",
        figcolor="black",
        gridcolor="gray"
    )

    fig, ax = mpf.plot(
        df,
        type="candle",
        volume=True,
        style=style,
        mav=(9,21),
        figratio=(16,9),
        figscale=1.2,
        returnfig=True
    )

    st.pyplot(fig)

else:
    st.warning("No data available.")
