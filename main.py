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


async def post_init(application):
    """
    Hook executed after python-telegram-bot starts its asyncio event loop.
    Guarantees AsyncIOScheduler starts inside a running event loop.
    """
    logger.info("Event loop running. Starting APScheduler in post_init hook...")
    setup_scheduler(bot=application.bot, active_users=ACTIVE_USERS)


def main():
    """
    Main entry point for starting the Goa Trip Concierge Telegram Bot.
    Deploy as a Render Background Worker — no HTTP port required.
    """
    try:
        # Verify BOT_TOKEN configuration
        if not config.BOT_TOKEN or config.BOT_TOKEN == "your_telegram_bot_token_here":
            logger.error("BOT_TOKEN is missing or set to default placeholder in .env!")
            sys.exit(1)

        logger.info("Initializing Telegram Bot Application...")
        application = (
            ApplicationBuilder()
            .token(config.BOT_TOKEN)
            .post_init(post_init)  # Ensures event loop is active before starting APScheduler
            .build()
        )

        # Register conversation and command handlers
        application.add_handler(start_conv_handler)
        application.add_handler(itinerary_handler)
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("simulate_reminder", simulate_reminder_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Register global error handler
        application.add_error_handler(global_error_handler)

        logger.info("Goa Trip Concierge Bot is running! Press Ctrl+C to stop.")
        application.run_polling()

    except Exception as e:
        logger.critical(f"Critical error in bot main thread: {e}", exc_info=True)


if __name__ == '__main__':
    main()
