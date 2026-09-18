import logging
import sys
import config
from bot.handlers import (
    start_conv_handler,
    itinerary_handler,
    handle_message,
    simulate_reminder_command,
    help_command,
    global_error_handler,
    ACTIVE_USERS,
)
from scheduler.jobs import setup_scheduler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Configure application-wide logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("GoaConcierge.Main")

def main():
    """
    Main entry point for starting the Goa Trip Concierge Telegram Bot.
    """
    try:
        # Verify BOT_TOKEN configuration
        if not config.BOT_TOKEN or config.BOT_TOKEN == "your_telegram_bot_token_here":
            logger.error("BOT_TOKEN is missing or set to default placeholder in .env!")
            print("\n[ERROR] Valid BOT_TOKEN not found in .env file.")
            print("Please set your Telegram Bot Token in .env file (see .env.example).\n")
            sys.exit(1)

        logger.info("Initializing Telegram Bot Application...")
        application = ApplicationBuilder().token(config.BOT_TOKEN).build()

        # Initialize APScheduler background jobs
        setup_scheduler(bot=application.bot, active_users=ACTIVE_USERS)

        # Register conversation and command handlers
        application.add_handler(start_conv_handler)                                            # /start stay area setup
        application.add_handler(itinerary_handler)                                             # /itinerary day-by-day planner
        application.add_handler(CommandHandler("help", help_command))                          # /help command
        application.add_handler(CommandHandler("simulate_reminder", simulate_reminder_command)) # Demo instant reminder
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # Free-text smart LLM handler

        # Register global error handler for uncaught exceptions
        application.add_error_handler(global_error_handler)

        logger.info("Goa Trip Concierge Bot setup complete. Starting polling mode...")
        print("🤖 Goa Trip Concierge Bot is running with APScheduler & Error Handling! Press Ctrl+C to stop.")
        application.run_polling()

    except Exception as e:
        logger.critical(f"Critical error in bot main thread: {e}", exc_info=True)

if __name__ == '__main__':
    main()
