import bs4
import requests
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
a = 100
p = 1
poll_time = 60*5
sleep_time = 60*75
pmin = poll_time//60
remove_character = ['\xa0', '-']
url = 'https://www.avanza.se/aktier/om-aktien.html/238449/tesla-inc'
inc = 'TSLA at `${}`. Increased `{}` from low point of `${}` today.'
dcr = 'TSLA at `${}`. Decreased `{}` from high point of `${}` today.'
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

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
    stamp = datetime.now().strftime('%H:%M')
    date = datetime.today().isoweekday() < 6
    tt = stamp > '13:30' and stamp < '20:00'
    current = +float(currentPrice())
    high = highPrice()
    low = lowPrice()

    if high is not None:
        high = +float(high)
        low = +float(low)
        pinc = '{:.2%}'.format((current-low)/current)
        pdcr = '{:.2%}'.format((current-high)/current)
    elif high is None:
        print (stamp, '- Value returned None. Pausing', pmin, 'min.')
        time.sleep(sleep_time)

    if tt and date:
        if low is not None and high is not None:
            if ((low) + a) <= (current):
                if not message_sent:
                    current = '{:g}'.format(current)
                    low = '{:g}'.format(low)
                    payload = {'chat_id': CHAT_ID, 'text':\
                    inc.format(current, pinc, low), 'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    print (stamp, '- Increased. Pausing', pmin, 'min.')
                    time.sleep(sleep_time)
            elif ((high) - a) >= (current):
                if not message_sent:
                    current = '{:g}'.format(current)
                    high = '{:g}'.format(high)
                    payload = {'chat_id': CHAT_ID, 'text':\
                    dcr.format(current, pdcr, high), 'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    print (stamp, '- Decreased. Pausing', pmin, 'min.')
                    message_sent = True
                    time.sleep(sleep_time)
            else:
                print (stamp, '- Not enough change. Pausing', pmin, 'min.')
                time.sleep(poll_time)
    else:
        print (stamp, '- Market closed. Pausing', pmin, 'min.')
        time.sleep(poll_time)
