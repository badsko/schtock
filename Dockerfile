FROM python:3.8.5-slim-buster

COPY schtock.py requirements.txt .env /
RUN apt-get -y update
RUN apt-get -y upgrade
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python", "-u", "./schtock.py" ]
