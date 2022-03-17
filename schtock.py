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
    pin = f'https://api.telegram.org/bot{token}/pinChatMessage'
    unpin = f'https://api.telegram.org/bot{token}/unpinAllChatMessages'
    r = requests.get('https://cloud.iexapis.com/stable/status', timeout=3)
    sy = requests.get('https://cloud.iexapis.com/stable/ref-data/iex/symbols', \
    timeout=3, params=payload)
    sy_list = sy.json()
    msg = ticker + \
    ' at `${}` `{}` `({})` from previous close at `${}`. Opened at `${}`.'
    msgup = ticker + \
    ' at `${}` `+{}` `(+{})` from previous close at `${}`. Opened at `${}`.'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    def check_price():
        payload = {'token': iex}
        r = requests.get(url, timeout=3, params=payload)
        r_dict = r.json()
        return r_dict

    def check_open():
        # Check if market is open. If not, try three times.
        # Return True or False.
        payload = {'token': iex}
        r = requests.get(url, timeout=3, params=payload)
        r_dict = r.json()
        p_time = 60*5
        opened = r_dict['isUSMarketOpen']
        if opened:
            return True
        else:
            for i in range(3):
                r = requests.get(url, timeout=3, params=payload)
                r_dict = r.json()
                opened = r_dict['isUSMarketOpen']
                logging.info('Checking if market is open. Sleep %d s', \
                p_time)
                time.sleep(p_time)
                if opened:
                    return True
            return False

    if ticker in [d['symbol'] for d in sy_list] and r.status_code == 200:
        while True:
            g_dict = check_price()
            current = g_dict['latestPrice']
            close = g_dict['previousClose']
            isopen = g_dict['isUSMarketOpen']
            openp = g_dict['iexOpen']
            stamp = datetime.now().strftime('%H:%M')
            date = datetime.today().isoweekday() < 6
            tt = stamp >= '14:31' and stamp <= '21:00'
            after = stamp >= '21:00' and stamp <= '24:00'
            now = datetime.now()
            target = datetime(now.year, now.month, now.day, hour=14, minute=31)
            delta = target - now
            ah = datetime(now.year, now.month, now.day, \
            hour=23, minute=59, second=59)
            deltaAfter = ah - now
            dis = True

            if not tt and not date:
                weekend = now + timedelta(days=2)
                dwknd = weekend - now
                logging.info('Weekend. Sleeping for %s', \
                str(dwknd).split('.')[0])
                time.sleep(dwknd.total_seconds())
                logging.info('Weekday')
                stamp = datetime.now().strftime('%H:%M')
                now = datetime.now()

            if delta > timedelta(0):
                logging.info('Market closed. Sleeping for %s', \
                str(delta).split('.')[0])
                time.sleep(delta.total_seconds())
                logging.info('Market open')
                payl = {'chat_id': chat_id}
                rd = requests.post(unpin, timeout=3, params=payl)
                logging.info('Unpin everything')
                tt = False

            if after and deltaAfter > timedelta(0):
                deltaAfter = deltaAfter + timedelta(seconds=2)
                logging.info('After hours. Sleeping for %s', \
                str(deltaAfter).split('.')[0])
                time.sleep(deltaAfter.total_seconds())
                logging.info('It is a brand new day')
                stamp = datetime.now().strftime('%H:%M')

            if current is not None and close is not None:
                per = '{:.2%}'.format((current - close) / close)
                diff = '{:.2f}'.format(current - close)

            if not isopen:
                isopen = check_open()
                if isopen:
                    logging.info('US Market open')
                else:
                    logging.info('US Market closed')

            elif close is None:
                logging.info('Value returned None. Sleeping for %d s', \
                poll_time)
                time.sleep(poll_time)
                stamp = datetime.now().strftime('%H:%M')

            if date and isopen:
                if tt and r.status_code == 200:
                    if ((close) + usd) <= (current):
                        payload = {'chat_id': chat_id, 'text':\
                        msgup.format(current, diff, per, close, \
                        openp), 'parse_mode': 'markdown'}
                        r = requests.post(telegram, params=payload)
                        resp = r.json()
                        mid = resp['result']['message_id']
                        payload = {'chat_id': chat_id, 'message_id': mid, \
                        'disable_notification': dis}
                        r = requests.post(pin, params=payload)
                        logging.info('Increased. Sleeping for %d s', sleep_time)
                        time.sleep(sleep_time)
                    elif ((close) - usd) >= (current):
                        payload = {'chat_id': chat_id, 'text':\
                        msg.format(current, diff, per, close, \
                        openp),
                        'parse_mode': 'markdown'}
                        r = requests.post(telegram, params=payload)
                        resp = r.json()
                        mid = resp['result']['message_id']
                        payload = {'chat_id': chat_id, 'message_id': mid, \
                        'disable_notification': dis}
                        r = requests.post(pin, params=payload)
                        logging.info('Decreased. Sleeping for %d s', sleep_time)
                        time.sleep(sleep_time)
                    else:
                        logging.info('Not enough change. Sleeping for %d s', \
                        poll_time)
                        time.sleep(poll_time)
                else:
                    logging.info('HTTP response code (%s) OR tt False.', \
                    r.status_code)
                    logging.info('Sleeping for %d s', poll_time)
                    time.sleep(poll_time)
            else:
                deltaAfter = deltaAfter + timedelta(seconds=2)
                logging.info('Market closed. Sleeping for %s', \
                str(deltaAfter).split('.')[0])
                time.sleep(deltaAfter.total_seconds())
    else:
        logging.info('Ticker (%s) does not match any IEX symbol or', ticker)
        logging.info('HTTP response code (%s) is not OK. Retry', r.status_code)

if __name__ == "__main__":
    main()

