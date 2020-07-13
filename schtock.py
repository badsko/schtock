import bs4
import requests
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
a = 100
inc = 'TSLA is now at ${}. Up ${} from closing at ${}.'
dcr = 'TSLA is now at ${}. Down ${} from closing at ${}.'
date = datetime.today().isoweekday() < 6
tt = datetime.now().strftime('%H:%M') > '11:30' and\
datetime.now().strftime('%H:%M') < '20:00'
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def parsePrice():
    r=requests.get('https://finance.yahoo.com/quote/TSLA?p=TSLA')
    soup=bs4.BeautifulSoup(r.text,"lxml")
    price=soup.find('div',{'class':'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text.replace(',','')
    return price

def closePrice():
    r=requests.get('https://finance.yahoo.com/quote/TSLA?p=TSLA')
    soup=bs4.BeautifulSoup(r.text,"lxml")
    price=soup.find('td',{'data-test':'PREV_CLOSE-value'}).find('span')\
    .text.replace(",","")
    return price

while True:
    message_sent = False
    current = parsePrice()
    close = closePrice()
    
    if tt and date:
        if (float(close) + a) <= float(current):
            if not message_sent:
                payload = {'chat_id': CHAT_ID, 'text':\
                inc.format(current, a, close)}
                r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                message_sent = True
                time.sleep(28800)
        elif (float(close) - a) >= float(current):
            if not message_sent:
                payload = {'chat_id': CHAT_ID, 'text':\
                dcr.format(current, a, close)}
                r = requests.post(TELEGRAM_API_SEND_MSG, params=payload)
                message_sent = True
                time.sleep(28800)
    else:
        print (datetime.now().strftime("%H:%M"))
        time.sleep(15)
