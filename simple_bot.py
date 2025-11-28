import os
import requests
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import aiohttp
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
CALENDARIFIC_API_KEY = os.getenv('CALENDARIFIC_API_KEY')

# Calendarific API endpoint
CALENDARIFIC_URL = "https://calendarific.com/api/v2/holidays"

def get_year_progress():
    """Calculate the year progress percentage and create a progress bar"""
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    end_of_year = datetime(now.year + 1, 1, 1)
    
    total_days_in_year = (end_of_year - start_of_year).days
    days_passed = (now - start_of_year).days
    
    progress_percentage = (days_passed / total_days_in_year) * 100
    
    # Create progress bar (10 characters wide)
    filled_length = int(10 * days_passed // total_days_in_year)
    bar = '█' * filled_length + '░' * (10 - filled_length)
    
    return progress_percentage, bar, days_passed, total_days_in_year

def get_today_festivals():
    """Get today's festivals from Calendarific API"""
    try:
        today = datetime.now()
        params = {
            'api_key': CALENDARIFIC_API_KEY,
            'country': 'IN',  # India - change if needed
            'year': today.year,
            'month': today.month,
            'day': today.day
        }
        
        response = requests.get(CALENDARIFIC_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['meta']['code'] == 200:
            holidays = data['response'].get('holidays', [])
            festival_names = [holiday['name'] for holiday in holidays]
            return festival_names
        else:
            logger.error(f"Calendarific API error: {data}")
            return []
    except Exception as e:
        logger.error(f"Error fetching festivals: {e}")
        return []

def create_progress_message():
    """Create the complete progress message with festivals"""
    progress_percentage, bar, days_passed, total_days = get_year_progress()
    
    # Calculate days remaining
    days_remaining = total_days - days_passed
    
    # Format the message exactly as requested
    message = f"📅 Year progress — {datetime.now().strftime('%d %b %Y')}\n\n"
    message += "────────────────────────\n\n"
    message += f"Day {days_passed} of {total_days}\n\n"
    message += f"Progress: {progress_percentage:.2f}% |{bar}|\n\n"
    message += f"Time remaining: {days_remaining} days (until Jan 1, {datetime.now().year + 1})\n\n"
    
    # Add festival information if any
    festivals = get_today_festivals()
    if festivals:
        message += "Today's Festivals:\n"
        for festival in festivals:
            message += f"• {festival}\n"
    
    return message

async def send_message_async(session, text):
    """Send message to Telegram channel asynchronously"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            if result.get("ok"):
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {result}")
                return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

async def send_daily_update():
    """Send the daily update to the channel"""
    try:
        message = create_progress_message()
        async with aiohttp.ClientSession() as session:
            await send_message_async(session, message)
    except Exception as e:
        logger.error(f"Error sending daily update: {e}")

def run_daily_update():
    """Synchronous wrapper for daily update"""
    asyncio.run(send_daily_update())

def main():
    """Main function to run the bot scheduler"""
    logger.info("Year Progress Bot started")
    logger.info("Daily updates scheduled for 5:00 AM")
    
    # Schedule the daily update at 5 AM
    schedule.every().day.at("05:00").do(run_daily_update)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()