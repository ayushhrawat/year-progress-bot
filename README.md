# Year Progress Bot for Telegram

A Telegram bot that sends daily updates about the year's progress to a channel, including a visual progress bar, percentage, and information about festivals using the Calendarific API.

> **Note:** Due to compatibility issues with newer Python versions, we've created a simplified version ([simple_bot.py](file:///c:/Users/rawat/Desktop/Year%20Progress%20Bot/simple_bot.py)) that uses asynchronous HTTP requests for better performance and reliability.

## Features

- 📊 Daily progress updates with visual progress bar
- 🎉 Festival information integration using Calendarific API
- ⏰ Automated daily posts at 5:00 AM
- 🔐 Admin-only controls for sending manual updates
- 🌍 Support for Indian festivals (can be customized)

## Prerequisites

1. Python 3.7 or higher
2. A Telegram bot token from [@BotFather](https://t.me/BotFather)
3. A Telegram channel where the bot is an administrator
4. Calendarific API key from [calendarific.com](https://calendarific.com/)

## Installation

1. Clone or download this repository

2. Install the required packages:
   ```
   pip install -r requirements.txt
   pip install aiohttp
   ```

3. Configure the bot by editing the `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   CHANNEL_ID=your_channel_id_here
   ADMIN_ID=your_admin_id_here
   CALENDARIFIC_API_KEY=your_calendarific_api_key_here
   ```

## Configuration Details

### Getting Your Telegram Bot Token
1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the token provided by BotFather

### Setting Up Your Channel
1. Create a new Telegram channel
2. Add your bot as an administrator:
   - Go to channel settings
   - Select "Administrators"
   - Click "Add Administrator"
   - Search for your bot and add it
3. Note the channel ID:
   - Forward a message from the channel to [@username_to_id_bot](https://t.me/username_to_id_bot)
   - Or enable developer mode in Telegram settings and copy the channel ID

### Getting Your Admin ID
1. Send a message to your bot
2. Go to `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for your user ID in the response

### Getting Calendarific API Key
1. Visit [calendarific.com](https://calendarific.com/)
2. Sign up for a free account
3. Get your API key from the dashboard

## Usage

Run the bot:
```
python launch_bot.py
```

Or for a quick test message:
```
python test_message.py
```

The bot will automatically send updates to your channel every day at 5:00 AM.

### Manual Commands
Only the admin can use these commands:

- `/post` - Manually send today's progress update
- `/festivals` - Show all festivals for the current year
- `/start` or `/help` - Show help information

## Customization

To customize for other countries:
1. Modify the `country` parameter in the `get_today_festivals()` and `festivals_command()` functions
2. Change 'IN' to the appropriate country code (e.g., 'US' for United States)

## Deployment for 24/7 Operation

To keep the bot running 24/7, you can:

1. **Using systemd (Linux)**:
   Create a service file `/etc/systemd/system/year-progress-bot.service`:
   ```
   [Unit]
   Description=Year Progress Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/your/bot
   ExecStart=/usr/bin/python3 /path/to/your/bot/launch_bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Using PM2 (Cross-platform)**:
   ```
   npm install -g pm2
   pm2 start launch_bot.py --name year-progress-bot --interpreter python3
   pm2 startup
   pm2 save
   ```

3. **Using screen (Linux/macOS)**:
   ```
   screen -S year-progress-bot
   python launch_bot.py
   # Press Ctrl+A, then D to detach
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.