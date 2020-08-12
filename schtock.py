#!/usr/bin/env python3

import bs4
import requests
import os
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
# USD stock price increase or decrease
# TODO Change a to 12 before 2020-08-31 13:30
a = 60
p = None
poll_time = 60*5
sleep_time = 60*75
pmin = poll_time // 60
smin = sleep_time // 60
remove_character = ['\xa0', '-']
url = 'https://www.avanza.se/aktier/om-aktien.html/238449/tesla-inc'
inc = 'TSLA at `${}`. Increased `{}` from low point of `${}` today.'
dcr = 'TSLA at `${}`. Decreased `{}` from high point of `${}` today.'
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def currentPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'pushBox roundCorners3'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    if p == '':
        return
    else:
        return p

def highPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'highestPrice SText bold'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    if p == '':
        return
    else:
        return p

def lowPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'lowestPrice SText bold'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    if p == '':
        return
    else:
        return p

while True:
    message_sent = False
    current = float(currentPrice())
    high = highPrice()
    low = lowPrice()
    stamp = datetime.now().strftime('%H:%M')
    date = datetime.today().isoweekday() < 6
    tt = stamp > '13:30' and stamp < '20:00'
    after = stamp > '20:00' and stamp < '24:00'
    now = datetime.now()
    target = datetime(now.year, now.month, now.day, hour=13, minute=30)
    delta = target - now
    ah = datetime(now.year, now.month, now.day, hour=23, minute=59, second=59)
    deltaAfter = ah - now

    if not tt and not date:
        weekend = now + timedelta(days=2)
        dwknd = weekend - now
        logging.info('Weekend. Pausing until next business day')
        time.sleep(dwknd.total_seconds())
        stamp = datetime.now().strftime('%H:%M')
        logging.info('Weekday')

    if delta > timedelta(0):
        logging.info('Market closed. Pausing until it opens')
        time.sleep(delta.total_seconds())
        stamp = datetime.now().strftime('%H:%M')
        logging.info('Market open')

    if after and deltaAfter > timedelta(0):
        logging.info('After hours. Pausing until tomorrow')
        time.sleep(deltaAfter.total_seconds())
        stamp = datetime.now().strftime('%H:%M')
        logging.info('It is a brand new day')

    if high is not None:
        high = float(high)
        low = float(low)
        pinc = '{:.2%}'.format((current - low) / current)
        pdcr = '{:.2%}'.format((current - high) / current)
    elif high is None:
        logging.info('Value returned None')
        time.sleep(poll_time)
        stamp = datetime.now().strftime('%H:%M')

    if tt and date:
        if low is not None and high is not None:
            if ((low) + a) <= (current):
                if not message_sent:
                    current = int(current)
                    low = int(low)
                    payload = {'chat_id': CHAT_ID, 'text':\
                    inc.format(current, pinc, low), 'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    logging.info('Increased')
                    time.sleep(sleep_time)
            elif ((high) - a) >= (current):
                if not message_sent:
                    current = int(current)
                    high = int(high)
                    payload = {'chat_id': CHAT_ID, 'text':\
                    dcr.format(current, pdcr, high), 'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    logging.info('Decreased')
                    time.sleep(sleep_time)
            else:
                logging.info('Not enough change.')
                time.sleep(poll_time)
        else:
            logging.info('Error! low or high returned None')
    else:
        logging.info('Outside open hours')
        time.sleep(poll_time)
