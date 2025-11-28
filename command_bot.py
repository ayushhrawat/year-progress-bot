import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

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
PORT = os.getenv('PORT', 10000)

# Create Flask app
app = Flask(__name__)

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
            'country': 'IN',
            'year': today.year,
            'month': today.month,
            'day': today.day
        }
        
        response = requests.get("https://calendarific.com/api/v2/holidays", params=params)
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

def send_message(chat_id, text):
    """Send message to Telegram chat"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("Message sent successfully")
            return True
        else:
            logger.error(f"Failed to send message: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

@app.route('/')
def health_check():
    return {'status': 'ok', 'service': 'Year Progress Bot'}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        update = request.get_json()
        
        if not update:
            return jsonify({'status': 'error', 'message': 'No update data'})
        
        # Check if it's a message
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '')
            
            logger.info(f"Received message from {user_id}: {text}")
            
            # Handle commands
            if text == '/start':
                welcome_message = "👋 Welcome to the Year Progress Bot!\n\nI send daily updates about the year's progress.\n\nAvailable commands:\n/start - Show this message\n/progress - Get current year progress\n/help - Show help"
                send_message(chat_id, welcome_message)
                
            elif text == '/progress':
                progress_message = create_progress_message()
                send_message(chat_id, progress_message)
                
            elif text == '/help':
                help_message = "🤖 Year Progress Bot Help\n\nI automatically send daily updates with:\n• Year progress bar and percentage\n• Today's date information\n• Festival information (if any)\n\nCommands:\n/progress - Get current year progress\n/start - Show welcome message\n/help - Show this help message"
                send_message(chat_id, help_message)
                
            elif text == '/post' and str(user_id) == ADMIN_ID:
                # Admin command to manually post update
                progress_message = create_progress_message()
                if send_message(CHANNEL_ID, progress_message):
                    send_message(chat_id, "✅ Progress update posted to channel!")
                else:
                    send_message(chat_id, "❌ Failed to post update to channel!")
                    
            elif text == '/post':
                send_message(chat_id, "❌ You are not authorized to use this command.")
                
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set the webhook for the bot"""
    # You'll need to replace this with your actual Render URL
    render_url = request.args.get('url')
    if not render_url:
        return jsonify({'status': 'error', 'message': 'Missing url parameter'})
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": f"{render_url}/webhook"
        }
        response = requests.post(url, json=payload)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)