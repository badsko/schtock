Scraper for tracking stock price and sending alert to Telegram when the price is up or down by a set amount.

# Create a Telegram Bot With BotFather
[https://core.telegram.org/bots](https://core.telegram.org/bots)

Grab your Token from BotFather.

Find your chat ID by inviting @RawDataBot to your channel.

# Build Docker Image and Run Container
Add your data to `TOKEN` and `CHAT_ID` in `.env`

`docker build --tag schtock:1.0 .`

`docker run -d --restart unless-stopped schtock:1.0`
