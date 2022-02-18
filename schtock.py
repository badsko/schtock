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
    sleep_time = 60*60
    pmin = poll_time // 60
    smin = sleep_time // 60
    p = None
    url = f'https://cloud.iexapis.com/stable/stock/{ticker}/quote'
    telegram = f'https://api.telegram.org/bot{token}/sendMessage'
    msg = ticker + ' at `${}` `{}` `({})` from previous close at `${}`.'
    msgup = ticker + ' at `${}` `+{}` `(+{})` from previous close at `${}`.'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    r = requests.get('https://cloud.iexapis.com/stable/status', timeout=3)

    if r.status_code == 200:

        while True:
            message_sent = False
            r = requests.get(url, timeout=3, params=payload)
            r_dict = r.json()
            current = r_dict['latestPrice']
            close = r_dict['previousClose']
            stamp = datetime.now().strftime('%H:%M')
            date = datetime.today().isoweekday() < 6
            tt = stamp > '15:30' and stamp < '22:00'
            after = stamp > '22:00' and stamp < '24:00'
            now = datetime.now()
            target = datetime(now.year, now.month, now.day, hour=15, minute=30)
            delta = target - now
            ah = datetime(now.year, now.month, now.day, \
            hour=23, minute=59, second=59)
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
                    if ((close) + usd) <= (current):
                        if not message_sent:
                            payload = {'chat_id': chat_id, 'text':\
                            msgup.format(int(current), diff, per, int(close)),\
                            'parse_mode': 'markdown'}
                            r = requests.post(telegram, params=payload)
                            message_sent = True
                            logging.info('Increased')
                            time.sleep(sleep_time)
                    elif ((close) - usd) >= (current):
                        if not message_sent:
                            payload = {'chat_id': chat_id, 'text':\
                            msg.format(int(current), diff, per, int(close)),\
                            'parse_mode': 'markdown'}
                            r = requests.post(telegram, params=payload)
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
                close = None
                time.sleep(poll_time)

    else:
        print(r.status_code)

if __name__ == "__main__":
    main()