#!/usr/bin/env python3

import requests
import os
import sys
import time
import logging
from pprint import pprint
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    ticker = str(sys.argv[1])
    usd = float(sys.argv[2]) # USD stock price increase or decrease
    load_dotenv()
    iex = os.getenv('IEX')
    token = os.getenv('TOKEN')
    chat_id = os.getenv('CHAT_ID')
    payload = {'token': iex}
    poll_time = 60*1
    sleep_time = 60*55
    url = f'https://cloud.iexapis.com/stable/stock/{ticker}/quote'
    telegram = f'https://api.telegram.org/bot{token}/sendMessage'
    r = requests.get('https://cloud.iexapis.com/stable/status', timeout=3)
    sy = requests.get('https://cloud.iexapis.com/stable/ref-data/iex/symbols', \
    timeout=3, params=payload)
    sy_list = sy.json()
    msg = ticker + ' at `${}` `{}` `({})` from previous close at `${}`.'
    msgup = ticker + ' at `${}` `+{}` `(+{})` from previous close at `${}`.'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    if ticker in [d['symbol'] for d in sy_list] and r.status_code == 200:    
        while True:
            payload = {'token': iex}
            g = requests.get(url, timeout=3, params=payload)
            g_dict = g.json()
            current = g_dict['latestPrice']
            close = g_dict['previousClose']
            isopen = g_dict['isUSMarketOpen']
            stamp = datetime.now().strftime('%H:%M')
            date = datetime.today().isoweekday() < 6
            tt = stamp > '15:30' and stamp < '22:00'
            after = stamp > '22:00' and stamp < '24:00'
            now = datetime.now()
            target = datetime(now.year, now.month, now.day, hour=15, minute=30)
            delta = target - now
            ah = datetime(now.year, now.month, now.day, \
            hour=23, minute=54, second=59)
            deltaAfter = ah - now

            if not tt and not date:
                weekend = now + timedelta(days=2)
                dwknd = weekend - now
                logging.info('Weekend. Sleeping for %s', \
                str(dwknd).split('.')[0])
                time.sleep(dwknd.total_seconds())
                logging.info('Weekday')
                stamp = datetime.now().strftime('%H:%M')

            if delta > timedelta(0):
                logging.info('Market closed. Sleeping for %s', \
                str(delta).split('.')[0])
                time.sleep(delta.total_seconds())
                logging.info('Market open')
                stamp = datetime.now().strftime('%H:%M')

            if after and deltaAfter > timedelta(0):
                logging.info('After hours. Sleeping for %s', \
                str(deltaAfter).split('.')[0])
                time.sleep(deltaAfter.total_seconds())
                logging.info('It is a brand new day')
                stamp = datetime.now().strftime('%H:%M')

            if current is not None and close is not None:
                per = '{:.2%}'.format((current - close) / close)
                diff = '{:.2f}'.format(current - close)

            elif close is None:
                logging.info('Value returned None. Sleeping for %s', \
                str(poll_time).split('.')[0])
                time.sleep(poll_time)
                stamp = datetime.now().strftime('%H:%M')

            if tt and date and isopen:
                if r.status_code == 200:
                    if ((close) + usd) <= (current):
                        payload = {'chat_id': chat_id, 'text':\
                        msgup.format(int(current), diff, per, int(close)),\
                        'parse_mode': 'markdown'}
                        r = requests.post(telegram, params=payload)
                        logging.info('Increased. Sleeping for %s', \
                        str(sleep_time).split('.')[0])
                        time.sleep(sleep_time)
                    elif ((close) - usd) >= (current):
                        payload = {'chat_id': chat_id, 'text':\
                        msg.format(int(current), diff, per, int(close)),\
                        'parse_mode': 'markdown'}
                        r = requests.post(telegram, params=payload)
                        logging.info('Decreased. Sleeping for %s', \
                        str(sleep_time).split('.')[0])
                        time.sleep(sleep_time)
                    else:
                        logging.info('Not enough change. Sleeping for %s', \
                        str(poll_time).split('.')[0])
                        time.sleep(poll_time)
                else:
                    logging.info('HTTP response code (%s) is not OK. \
                    Sleeping for %s', r.status_code, \
                    str(poll_time).split('.')[0])
                    time.sleep(poll_time)
            else:
                logging.info('Market closed. Sleeping for %s', \
                str(deltaAfter).split('.')[0])
                time.sleep(deltaAfter.total_seconds())
    else:
        logging.info('Ticker (%s) does not match any IEX symbol or', ticker)
        logging.info('HTTP response code (%s) is not OK. Retry', r.status_code)

if __name__ == "__main__":
    main()
