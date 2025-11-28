import os
import requests
import schedule
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

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

def send_daily_update(context: CallbackContext):
    """Send the daily update to the channel"""
    try:
        message = create_progress_message()
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        logger.info("Daily update sent successfully")
    except Exception as e:
        logger.error(f"Error sending daily update: {e}")

def post_command(update: Update, context: CallbackContext):
    """Allow admin to manually trigger a post"""
    if str(update.effective_user.id) != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    try:
        message = create_progress_message()
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        update.message.reply_text("✅ Daily update posted successfully!")
    except Exception as e:
        logger.error(f"Error sending manual update: {e}")
        update.message.reply_text("❌ Error posting update.")

def festivals_command(update: Update, context: CallbackContext):
    """Show all festivals for the current year"""
    if str(update.effective_user.id) != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    try:
        # Get all holidays for the current year
        today = datetime.now()
        params = {
            'api_key': CALENDARIFIC_API_KEY,
            'country': 'IN',  # India - change if needed
            'year': today.year
        }
        
        response = requests.get(CALENDARIFIC_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['meta']['code'] == 200:
            holidays = data['response'].get('holidays', [])
            
            # Filter only Indian festivals (you can modify this as needed)
            festivals = [h for h in holidays if h.get('primary_type') == 'Local holiday' or h.get('type')[0] in ['Observance', 'Season']]
            
            if festivals:
                message = f"🎊 <b>All Festivals in {today.year}:</b>\n\n"
                # Sort by date
                festivals.sort(key=lambda x: datetime.strptime(x['date']['iso'], '%Y-%m-%d'))
                
                for holiday in festivals:
                    date_str = holiday['date']['iso']
                    name = holiday['name']
                    message += f"• {date_str}: {name}\n"
                
                update.message.reply_text(message, parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text("No festivals found for this year.")
        else:
            update.message.reply_text("Error fetching festivals data.")
    except Exception as e:
        logger.error(f"Error fetching yearly festivals: {e}")
        update.message.reply_text("❌ Error fetching festivals.")

def start_command(update: Update, context: CallbackContext):
    """Handle the /start command"""
    welcome_message = (
        "👋 Welcome to the Year Progress Bot!\n\n"
        "I send daily updates about the year's progress to a channel.\n"
        "Only admins can control me.\n\n"
        "Available commands:\n"
        "/post - Manually send today's progress update\n"
        "/festivals - Show all festivals for this year\n"
        "/help - Show this help message"
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext):
    """Handle the /help command"""
    help_message = (
        "🤖 <b>Year Progress Bot Help</b>\n\n"
        "I automatically send daily updates with:\n"
        "• Year progress bar and percentage\n"
        "• Today's date information\n"
        "• Festival information (if any)\n\n"
        "<b>Admin Commands:</b>\n"
        "/post - Manually send today's progress update\n"
        "/festivals - Show all festivals for this year\n"
        "/start or /help - Show this help message"
    )
    update.message.reply_text(help_message, parse_mode=ParseMode.HTML)

def main():
    """Main function to start the bot"""
    # Create the updater and pass it the bot's token
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register command handlers
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("post", post_command))
    dp.add_handler(CommandHandler("festivals", festivals_command))
    
    # Schedule the daily update at 5 AM
    schedule.every().day.at("05:00").do(lambda: send_daily_update(updater.bot))
    
    # Start the bot
    updater.start_polling()
    
    # Run the scheduling in a separate thread
    import threading
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    
    logger.info("Bot started successfully!")
    logger.info("Daily updates scheduled for 5:00 AM")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()