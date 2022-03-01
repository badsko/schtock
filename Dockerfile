FROM python:3.9.10-slim-buster

WORKDIR /data
COPY requirements.txt /data/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY .env /data/

ENTRYPOINT [ "python", "./schtock.py" ]
