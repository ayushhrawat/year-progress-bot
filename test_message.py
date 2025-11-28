import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from simple_bot import create_progress_message

# Load environment variables
load_dotenv()

# Get configuration from environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

async def send_test_message():
    """Send a test message to the channel"""
    message = create_progress_message()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            if result.get("ok"):
                print("✅ Test message sent successfully!")
                print("Check your Telegram channel to see the message.")
            else:
                print("❌ Failed to send test message:")
                print(result)

if __name__ == "__main__":
    asyncio.run(send_test_message())