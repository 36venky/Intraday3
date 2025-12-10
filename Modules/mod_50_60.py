import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Aanlyze_Sleep as AS
import logging

logging.info("🚀 Analyzer [5] started...")

tickers = ['725GS2063', '734GS2064', '754GS2036', 'ABLBL', 'ADVANCE', 'ALEMBICLTD', 'AMANTA', 'ARISINFRA', 'AXISGOLD', 'BALAJITELE', 'BOMDYEING', 'BSLGOLDETF', 'CANHLIFE', 'CONS', 'DBREALTY', 'DEVYANI', 'DIACABS', 'DIGITIDE', 'DREAMFOLKS', 'EDELWEISS', 'EGOLD', 'EKC', 'ELGNZ', 'EMIL', 'EXICOM', 'FEDFINA', 'FINBUD', 'GAEL', 'GANDHAR', 'GMRP&UI', 'GOLD1', 'GOLDETF', 'GOLDETFADD', 'GOLDIETF', 'GOLDSHARE', 'GPTINFRA', 'GROWWGOLD', 'GROWWLIQID', 'GSLSU', 'GULPOLY', 'HDFCGOLD', 'HEMIPROP', 'HIMATSEIDE', 'ICICIB22', 'INDOUS', 'INDUSINVIT', 'INOXWIND', 'IRFC', 'J&KBANK', 'JAICORPLTD', 'JSWCEMENT', 'KECL', 'KOPRAN', 'KRT', 'LAXMIINDIA', 'LOKESHMACH', 'MAGSON', 'MANINFRA', 'MASTERTR', 'MOGOLD', 'MPEL', 'MUFIN', 'NHIT', 'OCCLLTD', 'ORIENTHOT', 'PARKHOTELS', 'PRAKASH', 'PRIMECAB', 'PUSHPA', 'RAIN', 'RCF', 'REDTAPE', 'REMSONSIND', 'RGL', 'ROLEXRINGS', 'SAMBHV', 'SBFC', 'SDBL', 'STLTECH', 'TEXINFRA', 'TEXRAIL', 'THOMASCOOK', 'TOLINS', 'TOP10ADD', 'TRANSTEEL', 'TVSSCS', 'TVTODAY', 'UNIECOM', 'URBANCO', 'VERTIS', 'WCIL', 'WELSPUNLIV']#EX.Price.list(50, 60)
tickers = [t + '.NS' for t in tickers]

while True:
    AS.analyze_real_time(tickers)
    AS.wait_until_next_15_min()