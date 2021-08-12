#!/usr/bin/env python3

import bs4
import requests
import os
import time
import logging
import sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

TICKER = str(sys.argv[1])
a = float(sys.argv[2]) # USD stock price increase or decrease
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
p = None
poll_time = 60*5
sleep_time = 60*75
pmin = poll_time // 60
smin = sleep_time // 60
remove_character = ['\xa0', '-'] 
url = f'https://finance.yahoo.com/quote/{TICKER}?p={TICKER}'
msg = TICKER + ' at `${}` `{}` `({})` from previous close at `${}`.'
msgup = TICKER + ' at `${}` `+{}` `(+{})` from previous close at `${}`.'
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def currentPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    p = soup.find("span", 
    attrs={"class":"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
    for character in remove_character:
        p = p.replace(',', '').replace(character, '')
    if p == '':
        return
    else:
        return p

def closePrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    p = soup.find(attrs={"data-test":"PREV_CLOSE-value"}).text
    for character in remove_character:
        p = p.replace(',', '').replace(character, '')
    if p == '':
        return
    else:
        return p

while True:
    message_sent = False
    current = float(currentPrice())
    close = float(closePrice())
    stamp = datetime.now().strftime('%H:%M')
    date = datetime.today().isoweekday() < 6
    tt = stamp > '15:30' and stamp < '22:00'
    after = stamp > '22:00' and stamp < '24:00'
    now = datetime.now()
    target = datetime(now.year, now.month, now.day, hour=15, minute=30)
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
        close = None

    if after and deltaAfter > timedelta(0):
        logging.info('After hours. Pausing until tomorrow')
        time.sleep(deltaAfter.total_seconds())
        stamp = datetime.now().strftime('%H:%M')
        logging.info('It is a brand new day')

    if current is not None and close is not None:
        per = '{:.2%}'.format((current - close) / close)
        diff = '{:.2f}'.format(current - close)

    elif close is None:
        logging.info('Value returned None')
        time.sleep(poll_time)
        stamp = datetime.now().strftime('%H:%M')
        
    if tt and date:
        if current is not None and close is not None:
            if ((close) + a) <= (current):
                if not message_sent:
                    payload = {'chat_id': CHAT_ID, 'text':\
                    msgup.format(int(current), diff, per, int(close)),\
                    'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    logging.info('Increased')
                    time.sleep(sleep_time)
            elif ((close) - a) >= (current):
                if not message_sent:
                    payload = {'chat_id': CHAT_ID, 'text':\
                    msg.format(int(current), diff, per, int(close)),\
                    'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    logging.info('Decreased')
                    time.sleep(sleep_time)
            else:
                logging.info('Not enough change')
                time.sleep(poll_time)
        else:
            logging.info('Error! low or high returned None')
    else:
        logging.info('Outside open hours')
        time.sleep(poll_time)
