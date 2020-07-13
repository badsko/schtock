Live tracking stock price and sending alert to Telegram when the price is up or down.

# Create a Telegram bot with BotFather
[https://core.telegram.org/bots](https://core.telegram.org/bots)

Grab your Token from BotFather.

Find your chat ID by inviting @RawDataBot to your channel.

# Modify .env
Add TOKEN and CHAT_ID

# Build Docker image and run Container
`docker build --tag schtock:1.0 .`

`docker run -d --restart unless-stopped schtock:1.0`
