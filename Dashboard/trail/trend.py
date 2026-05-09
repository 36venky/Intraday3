import yfinance as yf
import mplfinance as mpf
import logging
import numpy as np
import pandas as pd


def detect_filtered_reversals(prices, min_move=0.005):

    prices = np.asarray(prices).flatten()
    prices = prices[~np.isnan(prices)]

    if len(prices) < 3:
        return [], []

    diff = np.diff(prices)

    raw_highs = []
    raw_lows = []

    # Detect slope reversals
    for i in range(1, len(diff)):
        if diff[i-1] > 0 and diff[i] < 0:
            raw_highs.append(i)

        elif diff[i-1] < 0 and diff[i] > 0:
            raw_lows.append(i)

    filtered_highs = []
    filtered_lows = []
    last_kept_index = 0

    # Minimum move filter
    for idx in sorted(raw_highs + raw_lows):

        move = abs(prices[idx] - prices[last_kept_index]) / prices[last_kept_index]

        if move >= min_move:

            if idx in raw_highs:
                filtered_highs.append(idx)

            else:
                filtered_lows.append(idx)

            last_kept_index = idx

    return filtered_lows, filtered_highs


def Download(tickers):

    try:
        data = yf.download(
            tickers=tickers,
            interval='15m',
            period='15d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )

    except Exception as e:
        logging.error(f"Download error : {e}")
        return

    for ticker in tickers:

        try:
            df = data[ticker][['Open','High','Low','Close']].copy()

        except KeyError:
            logging.warning(f"[{ticker}] Data not found.")
            continue


        # Convert timezone to IST
        try:
            df.index = df.index.tz_convert('Asia/Kolkata')

        except:
            df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')


        # Filter NSE trading hours
        df = df.between_time("09:15", "15:30")

        if df.empty:
            continue


        # Ensure numeric values
        df = df.apply(pd.to_numeric, errors='coerce').dropna()


        prices = df['Close'].to_numpy()

        lows, highs = detect_filtered_reversals(prices)


        # Apply candle structure filter
        filtered_lows = []
        filtered_highs = []

        for i in highs:

            upper_wick = abs(df['High'].iloc[i] - df['Close'].iloc[i])
            body = abs(df['Close'].iloc[i] - df['Open'].iloc[i])

            if 2 * upper_wick < body:
                filtered_highs.append(i)


        for i in lows:

            lower_wick = abs(df['Low'].iloc[i] - df['Close'].iloc[i])
            body = abs(df['Close'].iloc[i] - df['Open'].iloc[i])

            if 2 * lower_wick < body:
                filtered_lows.append(i)


        lows = filtered_lows
        highs = filtered_highs


        # Marker arrays
        low_markers = [np.nan]*len(df)
        high_markers = [np.nan]*len(df)


        # Offset markers slightly for visibility
        for i in lows:
            low_markers[i] = df['Low'].iloc[i] * 0.999

        for i in highs:
            high_markers[i] = df['High'].iloc[i] * 1.001


        # Plot markers
        apds = [
            mpf.make_addplot(
                low_markers,
                type='scatter',
                marker='o',
                markersize=40,
                color='red'
            ),

            mpf.make_addplot(
                high_markers,
                type='scatter',
                marker='o',
                markersize=40,
                color='lime'
            )
        ]


        # Dark chart style
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


        # Plot candlestick chart
        mpf.plot(
            df,
            type='candle',
            style=dark_style,
            addplot=apds,
            mav=(9,21),
            figratio=(16,9),
            figscale=1.2,
            title=f"{ticker} Reversal Detection"
        )


Download(["SCI.NS"])