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
inc = 'TSLA is now at `${}` Up `${}` from low point of `${}` today.'
dcr = 'TSLA is now at `${}` Down `${}` from high point of `${}` today.'
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def currentPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'pushBox roundCorners3'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

def highPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'highestPrice SText bold'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

def lowPrice():
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    c = 'lowestPrice SText bold'
    p = soup.find('span',{'class': c}).text
    for character in remove_character:
        p = p.replace(',', '.').replace(character, '')
    return p

while True:
    message_sent = False
    stamp = datetime.now().strftime('%H:%M')
    date = datetime.today().isoweekday() < 6
    tt = datetime.now().strftime('%H:%M') > '13:30' and\
    datetime.now().strftime('%H:%M') < '20:00'
    try:
        current = +float(currentPrice())
        high = +float(highPrice())
        low = +float(lowPrice())
    except ValueError:
        print (stamp, '- An error occured.')
        continue
    
    if tt and date:
        if low is not None and high is not None:
            if ((low) + a) <= (current):
                if not message_sent:
                    payload = {'chat_id': CHAT_ID, 'text':\
                    inc.format(current, a, low), 'parse_mode': 'markdown'}
                    r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                    message_sent = True
                    print (stamp, '- Increased. Pausing', pmin, 'min.')
                    time.sleep(sleep_time)
            elif ((high) - a) >= (current):
                if not message_sent:
                    payload = {'chat_id': CHAT_ID, 'text':\
                    dcr.format(current, a, high), 'parse_mode': 'markdown'}
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
