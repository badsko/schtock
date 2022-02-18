# Tracking and Alerting Stock Price
Simple Python script to get price of a ticker and alert to telegram chat on a set amount of increase or decrease.

## Telegram
[https://core.telegram.org/bots](https://core.telegram.org/bots)

Grab your Token from @BotFather.

Find your Chat ID (e.g., by inviting @RawDataBot to your channel).

## IEX
Register for a free token.
[https://iexcloud.io/cloud-login#/register](https://iexcloud.io/cloud-login#/register)

## Modify `.env`
```
TOKEN=123:ABC
CHAT_ID=123
IEX=123
```

## Docker
`docker build --tag schtock:1.0 .`

`docker run -d --restart unless-stopped schtock:1.0 TICKER USD`

## Example
Container using timezone CET.

`docker run -e TZ=Europe/Amsterdam -d --name TSLA --restart unless-stopped schtock:1.0 TSLA 12`

## License
[GPL-3.0 License](https://github.com/badsko/schtock/blob/master/LICENSE)