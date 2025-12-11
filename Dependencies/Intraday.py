import yfinance as yf
import pandas as pd


intra = {
            "ETERNAL.NS" : True,"MMP.NS" : False,'NARMADA.NS' : False,'CCCL.NS' : False,'TARACHAND.NS' : False,'NIRAJ.NS' : False,'TARC.NS' : False,"MVGJL.NS" : True,'NILASPACES.NS' : False,'SHALBY.NS' : False,'MUKKA.NS' : False,'MAANALU.NS' : False,'STALLION.NS' : False,'DGCONTENT.NS' : False,'WEL.NS' : False,'MANAKCOAT.NS' : False,'RELIABLE.NS' : False,'DRCSYSTEMS.NS' : False,'PRIMO.NS' : False,'MUNJALAU.NS' : False,'BPL.NS' : False,'DJML.NS' : False,'GPTHEALTH.NS' : False,'SURANAT&P.NS' : False,'AVONMORE.NS' : False,'DWARKESH.NS' : False,'KROSS.NS' : False,'DBOL.NS' : False,
            'GLOBAL.NS' : False,'ALEMBICLTD.NS' : False,'RPPINFRA.NS' : False,'SUMEETINDS.NS' : False,'APTECHT.NS' : False,'MWL.NS' : False,'TBZ.NS' : False,'JTEKTINDIA.NS' : False,'INDSWFTLAB.NS' : False,'MEDICO.NS' : False,'RAMANEWS.NS' : False,'ESSARSHPNG.NS' : False,'BGRENERGY.NS' : False,'NDLVENTURE.NS' : False,
            'MUKANDLTD.NS' : False,'COASTCORP.NS' : False,'OMINFRAL.NS' : False,'SATIN.NS' : False,'UNIECOM.NS' : False,'RKEC.NS' : False,'MANOMAY.NS' : False,'VGL.NS' : False,'ALPA.NS' : False,'BRITANNIA.NS' : True,'KOTAKBANK.NS' : True,
        }

def check_intraday_tradable_yf(symbol: str) -> bool:
    """
    Determine if a stock is likely intraday-tradable using recent 15-min data from Yahoo Finance.
    """
    if symbol in intra:
        return intra[symbol]
    else:
        ticker = symbol.upper()
    
        # Explicitly specify auto_adjust to avoid future warnings
        data = yf.download(ticker, interval="15m", period="5d", progress=False, auto_adjust=False)

        if data.empty:
            print(f"⚠️  No data found for {symbol}")
            return False

        # --- Compute metrics safely ---
        avg_volume = data["Volume"].mean()
        avg_price = data["Close"].mean()
        volatility_series = ((data["High"] - data["Low"]) / data["Close"] * 100)
        volatility = volatility_series.mean()

        # Convert Series → float safely using .item() (preferred way)
        if hasattr(avg_volume, "item"):
            avg_volume = avg_volume.item()
        if hasattr(avg_price, "item"):
            avg_price = avg_price.item()
        if hasattr(volatility, "item"):
            volatility = volatility.item()

        candle_count = len(data)

        # --- Apply numeric thresholds ---
        is_liquid1 = avg_volume > 3_000
        is_stable1 = 0.3 < volatility < 6

        # is_liquid2 = avg_volume > 1_000
        # is_stable2 = 0.6 < volatility < 6
        # is_active2 = candle_count > 100

        # --- Write output with UTF-8 encoding ---
        with open("Intraday.txt", "a", encoding="utf-8") as f:
            if is_liquid1 and is_stable1 :
                line = f"'{symbol}' : False,\n"
            else:
                line = f"'{symbol}' : True,\n"
            f.write(line)
            #print(line.strip())
        
        if is_liquid1 and is_stable1 :
            return True
        else:
            return False

# #Example usage:
# result = check_intraday_tradable_yf("NIRAJ.NS")
# print(result)