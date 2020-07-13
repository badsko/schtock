Tracking prices of stock and sending alert to Telegram when the price is up or down x amount.

# Create a Telegram bot with BotFather
[https://core.telegram.org/bots](https://core.telegram.org/bots)

Find your Token and chat id.

# Modify .env
Add TOKEN and CHAT_ID

# Build Docker image and run Container
`docker build --tag schtock:1.0`

`docker run -d --restart unless-stopped schtock:1.0`
