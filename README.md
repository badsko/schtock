Tracking prices of stock and sending alert to Telegram when the price is up or down x amount.

# Create a Telegram bot with BotFather
https://core.telegram.org/bots

# Modify .env
Add TOKEN and CHAT_ID to .env

# Build Docker image and run schtock.py detached
`docker build --tag schtock:1.0`

`docker run -d --restart unless-stopped schtock:1.0`
