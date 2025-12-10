# import pandas as pd

# df = pd.read_csv(r"Intraday\mod\Volume.csv")

# # Make sure TTL_TRD_QNTY is numeric (handles commas and non-numeric safely)
# df['TTL_TRD_QNTY'] = pd.to_numeric(
#     df['TTL_TRD_QNTY'].astype(str).str.replace(',', ''), errors='coerce'
# ).fillna(0).astype(int)

# # Filter for volumes between 3,000,000 and 5,000,000 (inclusive)
# low = 50_00_000
# high = 1000_00_000
# high_volume = df[(df['TTL_TRD_QNTY'] >= low) & (df['TTL_TRD_QNTY'] <= high)]# & (df['CLOSE_PRICE'] < 20)& (df['CLOSE_PRICE'] > 5)]

# symbol_list = high_volume['SYMBOL'].tolist()

# print(symbol_list)
# print("Count:", len(symbol_list))