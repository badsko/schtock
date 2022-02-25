FROM python:3.9.10-slim-buster

WORKDIR /data
COPY requirements.txt .env /data/
RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "./schtock.py" ]
