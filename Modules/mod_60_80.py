import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Aanlyze_Sleep as AS
import logging

logging.info("🚀 Analyzer [6] started...")

tickers = ['ADSL', 'AEROFLEX', 'AHCL', 'ARKADE', 'ASHOKA', 'AVANTEL', 'AXISILVER', 'BAJEL', 'BHAGERIA', 'BLISSGVS', 'CAMLINFINE', 'CASTROLIND', 'CESC', 'CGCL', 'DCBBANK', 'DCXINDIA', 'ENGINERSIN', 'ESILVER', 'FINPIPE', 'FRESHARA', 'FUSION', 'GEMAROMA', 'GIPCL', 'GKENERGY', 'GPPL', 'GREAVESCOT', 'GROWWSLVR', 'GSFC', 'HDFCSML250', 'HINDOILEXP', 'IGL', 'INDIGRID', 'IPL', 'IRCON', 'JINDALSAW', 'KALAMANDIR', 'KCP', 'KNRCON', 'KROSS', 'LEMONTREE', 'LOTUSDEV', 'LXCHEM', 'MAANALU', 'MAFANG', 'MARKSANS', 'MEGASOFT', 'MOSILVER', 'MRPL', 'MUTHOOTMF', 'NACLIND', 'NCC', 'NIACL', 'NOCIL', 'NXST', 'ORIENTCEM', 'ORIENTELEC', 'PARADEEP', 'PPLPHARMA', 'PTC', 'RAJESHEXPO', 'RATNAVEER', 'RELINFRA', 'RELTD', 'SAKSOFT', 'SAMHI', 'SBISILVER', 'SCODATUBES', 'SGLTL', 'SHAREINDIA', 'SHK', 'SILVER', 'SILVER1', 'SILVERADD', 'SILVERAG', 'SILVERETF', 'SPMLINFRA', 'SSWL', 'STALLION', 'SUVEN', 'TARC', 'TIMETECHNO', 'UDS', 'UGROCAP', 'VGL', 'WALCHANNAG', 'WEL', 'YATRA']#EX.Price.list(60, 80)
tickers = [t + '.NS' for t in tickers]

while True:
    AS.analyze_real_time(tickers)
    AS.wait_until_next_15_min()