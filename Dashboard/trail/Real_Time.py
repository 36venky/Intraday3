import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, time
import pytz
import time as t

st.markdown("""
<style>
/* Reduce padding */
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}

/* Compact inputs */
div[data-baseweb="select"] > div {
    min-height: 35px;
}

input {
    height: 35px !important;
}

/* Smaller warning/info boxes */
.stAlert {
    padding: 8px !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)


# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(layout="wide")
st.title("📈 Real-Time Candlestick Chart (NSE)")

# -------------------------------
# MARKET TIME CHECK (IST)
# -------------------------------
def is_market_open():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    market_start = time(9, 15)
    market_end = time(15, 30)

    if now.weekday() >= 5:
        return False

    return market_start <= now.time() <= market_end


# -------------------------------
# VALID PERIODS BASED ON INTERVAL
# -------------------------------
def get_valid_periods(interval):
    if interval == "1m":
        return ["1d", "5d", "7d"]
    elif interval in ["2m", "5m", "15m"]:
        return ["1d", "5d", "1mo"]
    else:
        return ["1d", "5d", "1mo", "3mo"]


# -------------------------------
# UI LAYOUT (SIDE BY SIDE)
# -------------------------------
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    ticker_input = st.text_input("Tickers (comma separated)", "RELIANCE.NS")

with col2:
    interval_options = ["1m", "2m", "5m", "15m", "30m", "60m"]
    selected_interval = st.selectbox("Interval", interval_options)

with col3:
    valid_periods = get_valid_periods(selected_interval)
    selected_period = st.selectbox("Period", valid_periods)

with col4:
    refresh_rate = st.number_input("Refresh(s)", 5, 120, 30)


# -------------------------------
# INTERVAL CONTROL (MARKET CLOSED)
# -------------------------------
market_open = is_market_open()

if not market_open:
    st.caption("⚠️ Market CLOSED → Using interval ≥ 5m")

    if selected_interval in ["1m", "2m"]:
        selected_interval = "5m"
        st.caption("Interval auto-adjusted to 5m")


# -------------------------------
# DATA FETCH
# -------------------------------
@st.cache_data(ttl=60)
def load_data(ticker, interval, period):
    try:
        df = yf.download(
            tickers=ticker,
            interval=interval,
            period=period,
            auto_adjust=False,   # important for trading
            progress=False,
            threads=False
        )
        return df
    except Exception as e:
        return None

tickers = [t.strip().upper() for t in ticker_input.split(",")]
data = load_data(tickers, selected_interval, selected_period)


# # -------------------------------
# # DEBUG (OPTIONAL)
# # -------------------------------
# with st.expander("🔍 Debug Data"):
#     if data is not None:
#         st.write("Shape:", data.shape)
#         st.dataframe(data.tail())
#     else:
#         st.write("No data returned")

# -------------------------------
# DATA CLEANING FOR PLOTLY
# -------------------------------
if data is not None and not data.empty:

    # Flatten MultiIndex columns if present
    if isinstance(data.columns, tuple) or hasattr(data.columns, "levels"):
        data.columns = data.columns.get_level_values(0)

    # Standardize column names
    data.columns = [col.capitalize() for col in data.columns]

    # Ensure required columns exist
    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in data.columns for col in required_cols):
        st.error(f"Missing columns: {data.columns}")
        st.stop()

    # Convert index to datetime
    data.index = data.index.tz_localize(None)

    # Convert to numeric
    for col in required_cols:
        data[col] = data[col].astype(float)

    # Drop NaN
    data = data.dropna()


# -------------------------------
# MULTI STOCK PLOTS
# -------------------------------
if tickers:

    cols = st.columns(2)  # 2 charts per row

    for i, ticker in enumerate(tickers):

        data = load_data(ticker, selected_interval, selected_period)

        if data is not None and not data.empty:

            # CLEAN DATA
            if hasattr(data.columns, "levels"):
                data.columns = data.columns.get_level_values(0)

            data.columns = [col.capitalize() for col in data.columns]
            data.index = data.index.tz_localize(None)
            data = data.dropna()

            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=ticker
            ))

            fig.update_layout(
                title=ticker,
                template="plotly_dark",
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_rangeslider_visible=False,

                xaxis=dict(
                    rangebreaks=[
                        dict(bounds=["sat", "mon"])
                    ]
                )
            )

            with cols[i % 2]:
                st.plotly_chart(fig, width="stretch")

        else:
            with cols[i % 2]:
                st.warning(f"No data: {ticker}")

# -------------------------------
# AUTO REFRESH
# -------------------------------
refresh_rate = st.slider("Refresh (seconds)", 10, 120, 30)

st.caption(f"Refreshing every {refresh_rate} sec")

t.sleep(refresh_rate)
st.rerun()