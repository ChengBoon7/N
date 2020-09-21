#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import itertools
import json
import logging
from datetime import datetime

import dateutil
import feedparser
import requests
from bs4 import BeautifulSoup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import ta
import pandas as pd
from matplotlib import pyplot as plt
import csv

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

toggle = itertools.cycle(['on', 'off']).__next__


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Press /help to learn how to use me.')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        '''You can control me by sending these commands:      
                                
/help - Get info on how to use me

/echo - I will repeat whatever you tell me. Type [On / Off] at the end to enable or disable echo

/bitcoin - Get latest Bitcoin price in Malaysian Ringgit(RM)

/headlines - I will get you latest news headline for you. Type [Number of headline]
'''
    )


def repeater(update, context):
    if context.user_data[echo]:
        update.message.reply_text(update.message.text)


def echo(update, context):
    try:
        command = context.args[0].lower()
    except:
        command = toggle()
    if("on" == command):
        context.user_data[echo] = True
        update.message.reply_text("Repeater Started")
    elif("off" == command):
        context.user_data[echo] = False
        update.message.reply_text("Repeater Stopped")


def Bitcoin_Price(update, context):
    """Send Bitcoin Price."""
    
    now = datetime.now()

    now_timestamp = int(datetime.timestamp(now))

    now_time = datetime.fromtimestamp(now_timestamp)

    URL = "https://ajax.luno.com/ajax/1/udf/history?symbol=XBTMYR&resolution=60&from=&to=" + \
        str(now_timestamp)

    try:
        page = requests.get(URL)
    except:
        page = requests.get(URL)
        
    soup = BeautifulSoup(page.content, 'html.parser')

    for a in soup:
        a = json.loads(a)

    Timestamp = list(a["t"])
    Open_Price = list(a["o"])
    High_Price = list(a["h"])
    Low_Price = list(a["l"])
    Close_Price = list(a["c"])

    price_msg = str("RM " + str(Close_Price[-1:]).replace('[', '').replace(']', ''))
    
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
    
    Buy Signal
    if Stoch_K > Stoch_D 
    %K and %D <= 10% 
    RSI <= 40
     
    Sell Signal
    if Stoch_K < Stoch_D
    %K and %D >= 97%
    RSI >= 60
    
    ____________________\nBuy Signal\nif Stoch_K > Stoch_D\n%K and %D <= 10%\nRSI <= 40\n\nSell Signal\nif Stoch_K < Stoch_D\n%K and %D >= 97%\nRSI >= 60
    
    #'''

    # Buy Signal
    if (float(Now_Stoch_K) > float(Now_Stoch_D)) and (float(Now_RSI) <= 40) and (float(Now_Stoch_K) <= 10) and (float(Now_Stoch_D) <= 10):
        signal = 'Buy Signal'
        full_signal = "Buy Signal\nPrice RM " + str(Now_Close_Price)[:2] + ',' + str(Now_Close_Price)[2:] + "\nRSI " + str(Now_RSI)[:5] + "%\n%K " + str(Now_Stoch_K)[:5] + "%\n%D " + str(Now_Stoch_D)[:5] + "%"
        # print("Buy Signal | " + str(Now_Close_Price) + " | " +
        #       str(Now_RSI) + " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))

    # Sell Signal
    elif (float(Now_Stoch_K) < float(Now_Stoch_D)) and (float(Now_RSI) >= 60) and (float(Now_Stoch_K) >= 97) and (float(Now_Stoch_D) >= 97):
        signal = 'Sell Signal'
        full_signal = "Sell Signal\nPrice RM " + str(Now_Close_Price)[:2] + ',' + str(Now_Close_Price)[2:] + "\nRSI " + str(Now_RSI)[:5] + "%\n%K " + str(Now_Stoch_K)[:5] + "%\n%D " + str(Now_Stoch_D)[:5] + "%"
        # print("Sell Signal | " + str(Now_Close_Price) + " | " +
        #       str(Now_RSI) + " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))

    # No Signal
    else:
        signal = 'No Signal'
        full_signal = "No Signal\nPrice RM " + str(Now_Close_Price)[:2] + ',' + str(Now_Close_Price)[2:] + "\nRSI " + str(Now_RSI)[:5] + "%\n%K " + str(Now_Stoch_K)[:5] + "%\n%D " + str(Now_Stoch_D)[:5] + "%"
        # print("No Signal | " + str(Now_Close_Price) + " | " + str(Now_RSI) +
        #       " | " + str(Now_Stoch_D) + " | " + str(Now_Stoch_K))
    
    try:
        command = context.args[0].lower()
    except:
       command = 'price'
   
    if("price" == command):
        update.message.reply_text(price_msg)
        
    elif("signal" == command):
        update.message.reply_text(signal)
    
    elif ("fullsignal" == command):
        update.message.reply_text(full_signal)    
    
    # "\n\n━━━━━━━━━━\n\nBuy Signal\nif Stoch_K > Stoch_D\n%K and %D <= 10%\nRSI <= 40\n\nSell Signal\nif Stoch_K < Stoch_D\n%K and %D >= 97%\nRSI >= 60"


def parseRSS(rss_url):
    return feedparser.parse(rss_url)


def getHeadlinesFromAUrl(rss_url):
    headlines = []
    feed = parseRSS(rss_url)
    for newsitem in feed.get('items'):
        headlines.append(newsitem.get('title'))
    return headlines


def getHeadlinesForAllDictUrls(newsurls):
    allheadlines = []
    for key, url in newsurls.items():
        allheadlines.extend(getHeadlinesFromAUrl(url))
    return allheadlines


def sendRssFeeds(update, context):
    newsurls = {
        'googlenews': 'https://news.google.com/news/rss?hl=en-MY&amp;gl=MY&amp;gl=MY&amp;ceid=MY:en',
    }
    allheadlines = getHeadlinesForAllDictUrls(newsurls)

    try:
        command = int(context.args[0].lower())
    except:
        command = 5

    a = 0
    for i in allheadlines:
        a = a + 1
        if(a <= command):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=str(i))


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        "1333044470:AAH7W2O0mdPisC6C23YdqgbZJ4F66vqFsTw", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler("bitcoin", Bitcoin_Price))
    dp.add_handler(CommandHandler("headlines", sendRssFeeds))

    '''
    help - Get help
    echo - [On/Off] Repeat after you
    bitcoin - Bitcoin price in RM
    headlines - [1 - 10] Get news headlines
    '''

    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, repeater))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
