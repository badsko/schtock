Tracking prices of stock and sending alert to Telegram.

# Running the script
Add TOKEN and CHAT_ID to .env

## Start the Docker container
`docker build --tag schtock:1.0`
`docker run -d --restart unless-stopped schtock:1.0`
