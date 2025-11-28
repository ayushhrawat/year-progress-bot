"""
Year Progress Bot Launcher
==========================

This script launches the simplified Year Progress Bot that sends daily updates
about the year's progress to a Telegram channel.
"""

import os
import time
from dotenv import load_dotenv
from simple_bot import main, run_daily_update

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = ['TELEGRAM_BOT_TOKEN', 'CHANNEL_ID']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nPlease check your .env file and try again.")
    exit(1)

print("✅ All required environment variables are present.")
print("🚀 Launching Year Progress Bot...")
print("The bot will send daily updates at 5:00 AM.")
print("For GitHub Actions, running for 5 minutes then exiting...")

# For GitHub Actions: Run for 5 minutes then exit
start_time = time.time()
while time.time() - start_time < 295:  # 5 minutes
    # Check if it's time to send daily update (5:00 AM)
    import schedule
    schedule.run_pending()
    time.sleep(10)  # Check every 10 seconds

print("⏰ Stopping bot after 5 minutes (GitHub Actions limit)")