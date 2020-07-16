mport bs4
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
sleep_time = 60*55
remove_character = ['\xa0', '-']
url = 'https://www.avanza.se/aktier/om-aktien.html/238449/tesla-inc'
inc = 'TSLA is now at `${}` Up `${}` from low point of `${}` today.'
dcr = 'TSLA is now at `${}` Down `${}` from high point of `${}` today.'
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def currentPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'pushBox roundCorners3'
    try:
        p = soup.find('span',{'class': c}).text
    except AttributeError:
        print (datetime.now().strftime('%H:%M'), ' An error occured.')
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

def highPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'highestPrice SText bold'
    try:
        p = soup.find('span',{'class': c}).text
    except AttributeError:
        print (datetime.now().strftime('%H:%M'), ' An error occured.')
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

def lowPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'lowestPrice SText bold'
    try:
        p = soup.find('span',{'class': c}).text
    except AttributeError:
        print (datetime.now().strftime('%H:%M'), ' An error occured.')
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

while True:
    message_sent = False
    date = datetime.today().isoweekday() < 6
    tt = datetime.now().strftime('%H:%M') > '13:30' and\
    datetime.now().strftime('%H:%M') < '20:00'
    try:
        current = +float(currentPrice())
        high = +float(highPrice())
        low = +float(lowPrice())
    except ValueError:
        print (datetime.now().strftime('%H:%M'), ' An error occured.')
    
    if tt and date:
        if ((low) + a) <= (current):
            if not message_sent:
                payload = {'chat_id': CHAT_ID, 'text':\
                inc.format(current, a, low), 'parse_mode': 'markdown'}
                r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                message_sent = True
                time.sleep(sleep_time)
        elif ((high) - a) >= (current):
            if not message_sent:
                payload = {'chat_id': CHAT_ID, 'text':\
                dcr.format(current, a, high), 'parse_mode': 'markdown'}
                r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                message_sent = True
                time.sleep(sleep_time)
        else:
            print (datetime.now().strftime('%H:%M'))
            time.sleep(poll_time)
    else:
        print (datetime.now().strftime('%H:%M'))
        time.sleep(poll_time)
