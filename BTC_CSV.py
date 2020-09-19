import csv
import json
import signal
import sys
from datetime import datetime
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import ta
from bs4 import BeautifulSoup

import _pickle as pickle


def signal_handler(sig, frame):
    # CTRL + C to quit
    print()
    print('Ok, bye.')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

last_open = []
last_high = []
last_low = []
last_close = []

while True:

    now = datetime.now()

    now_timestamp = int(datetime.timestamp(now))

    now_time = datetime.fromtimestamp(now_timestamp)

    URL = "https://ajax.luno.com/ajax/1/udf/history?symbol=XBTMYR&resolution=60&from=&to=" + \
        str(now_timestamp)

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    for a in soup:
        a = json.loads(a)

    Timestamp = list(a["t"])
    Open_Price = list(a["o"])
    High_Price = list(a["h"])
    Low_Price = list(a["l"])
    Close_Price = list(a["c"])

    Volume = list(a["v"])

    Request_Status = list(a["s"])

    with open('btc_his.csv', 'w', newline='') as f:
        fieldnames = ['DateTime', 'Open', 'High', 'Low', 'Close']
        thewriter = csv.DictWriter(f, fieldnames=fieldnames)

        f.truncate()

    x = -1
    for i in Open_Price:
        x = x + 1

        with open('btc_his.csv', 'a+', newline='') as f:
            fieldnames = ['DateTime', 'Open', 'High', 'Low', 'Close']
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)

            if x == 0:
                thewriter.writeheader()

            thewriter.writerow({'DateTime': str(datetime.fromtimestamp(Timestamp[x])),
                                'Open': Open_Price[x],
                                'High': High_Price[x],
                                'Low': Low_Price[x],
                                'Close': Close_Price[x]})

    ########################################################################################################


    plt.style.use('bmh')
    df = pd.read_csv('btc_his.csv')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    # Datetime conversion
    df['DateTime'] = pd.to_datetime(df.DateTime)
    # Setting the index
    df.set_index('DateTime', inplace=True)

    # TA's RSI
    df['ta_rsi'] = ta.momentum.rsi(df.Close)
    # TA's Stochastic Oscillator
    df['ta_stoch_k'] = ta.momentum.stoch(df.High, df.Low, df.Close)
    df['ta_stoch_d'] = ta.momentum.stoch_signal(df.High, df.Low, df.Close)

    # print(df)
    df.to_csv('btc_his_stochrsi.csv')

    with open('btc_his_stochrsi.csv', 'r') as f:
        thereader = csv.DictReader(f)

        for row in thereader:
            Now_Open_Price = int(row['Open'])
            Now_High_Price = int(row['High'])
            Now_Low_Price = int(row['Low'])
            Now_Close_Price = int(row['Close'])
            Now_RSI = row['ta_rsi']
            Now_Stoch_K = row['ta_stoch_k']
            Now_Stoch_D = row['ta_stoch_d']

        # print(str(Now_Close_Price) + " " + str(Now_RSI) +
        #       " " + str(Now_Stoch_D) + " " + str(Now_Stoch_K))

    '''#
    
    Buy if Stoch_K > Stoch_D 
    %K and %D <= 10% 
    RSI <= 40
     
    Sell if Stoch_K < Stoch_D
    %K and %D >= 97%
    RSI >= 60
    
    #'''

    # Buy Signal
    if (Now_Stoch_K > Now_Stoch_D) and (float(Now_RSI) <= 40) and (float(Now_Stoch_K) <= 10) and (float(Now_Stoch_D) <= 10):
        print("Buy Signal | " + str(Now_Close_Price) + " | " +
              str(Now_RSI) + " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))

    # Sell Signal
    if (Now_Stoch_K < Now_Stoch_D) and (float(Now_RSI) >= 60) and (float(Now_Stoch_K) >= 97) and (float(Now_Stoch_D) >= 97):
        print("Sell Signal | " + str(Now_Close_Price) + " | " +
              str(Now_RSI) + " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))

    # No Signal
    else:
        print("No Signal | " + str(Now_Close_Price) + " | " + str(Now_RSI) +
              " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))

    print(" ")
    # sleep(30)

# if (Open_Price != last_open) or (High_Price != last_high) or (Low_Price != last_low) or (Close_Price != last_close):
#     print("timestamp =", str(now_timestamp))
#     print("Open Price " + str(Open_Price[-5:]))
#     print("High Price " + str(High_Price[-5:]))
#     print("Low Price " + str(Low_Price[-5:]))
#     print("Close Price" + str(Close_Price[-5:]))
#     last_open = Open_Price
#     last_high = High_Price
#     last_low = Low_Price
#     last_close = Close_Price
#     print(" ")
