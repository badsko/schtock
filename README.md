# Web Scraper for Tracking and Alerting Stock Price
Simple Python script that scrapes Avanza for stock change and alerts on price up or down by a set amount.

## Telegram
[https://core.telegram.org/bots](https://core.telegram.org/bots)

Grab your Token from @BotFather.

Find your Chat ID (e.g., by inviting @RawDataBot to your channel).

## Modify `.env`
```
TOKEN=123:ABC
CHAT_ID=123
```

## Docker
`docker build --tag schtock:1.0 .`

`docker run -d --restart unless-stopped schtock:1.0`

## License
[GPL-3.0 License](https://github.com/badsko/schtock/blob/master/LICENSE)
