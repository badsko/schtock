FROM python:3.9.10-slim-buster

COPY schtock.py requirements.txt .env /
RUN apt-get -y update
RUN apt-get -y upgrade
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python", "-u", "./schtock.py" ]
