import logging
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from bot.llm_client import call_llm
from bot.itinerary import generate_itinerary
from data.data_loader import filter_by_area, load_data
from scheduler.jobs import schedule_checkin_reminder

# Configure module logger
logger = logging.getLogger("GoaConcierge.Handlers")

# Set of active chat IDs for background broadcasts (e.g. weather alerts)
ACTIVE_USERS = set()

# User-facing fallback error message
GENERIC_ERROR_MSG = "⚠️ Kuch technical issue aa gaya hai. Kripya thodi der baad dobara try karein ya `/start` se restart karein."

# Conversation state for /start
AWAITING_STAY_AREA = 100

# Conversation states for /itinerary
ASK_AREA, ASK_DAYS, ASK_PREFERENCES = range(3)


# --- /help Command Handler ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for /help command. Lists all available commands and features.
    """
    try:
        chat_id = update.effective_chat.id
        logger.info(f"User {chat_id} requested /help")
        help_text = (
            "🌴 *Goa Trip Concierge - Help & Commands* 🌴\n\n"
            "Aap in commands aur features ka use kar sakte hain:\n\n"
            "📌 *Commands*:\n"
            "• `/start` - Bot start karein & stay location setup karein\n"
            "• `/itinerary` - Custom day-by-day trip plan banayein\n"
            "• `/simulate_reminder` - Demo check-in reminder test karein\n"
            "• `/help` - Sabhi commands ki list dekhein\n"
            "• `/cancel` - Ongoing conversation plan cancel karein\n\n"
            "💬 *Direct Questions*:\n"
            "Aap direct message mein kuch bhi pooch sakte hain:\n"
            "• _'Dinner ke liye best place kahan hai?'_\n"
            "• _'Cheapest transport option kya hai?'_\n"
            "• _'Baga beach pe kya famous hai?'_"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in help_command for chat {update.effective_chat.id}: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")


# --- /start Conversation Handler ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for /start command.
    """
    try:
        chat_id = update.effective_chat.id
        ACTIVE_USERS.add(chat_id)
        logger.info(f"User {chat_id} initiated /start command")

        await update.message.reply_text(
            "Welcome to Goa Trip Concierge! 🌴🌊\n\n"
            "Batao aap Goa mein kahan stay kar rahe ho? (e.g. *Anjuna*, *Panjim*, *Calangute*, *Baga*, *South Goa*):",
            parse_mode="Markdown"
        )
        return AWAITING_STAY_AREA
    except Exception as e:
        logger.error(f"Error in start_command: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


async def save_stay_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Saves the user's stay area in context.user_data['user_area'].
    """
    try:
        user_area = update.message.text.strip()
        chat_id = update.effective_chat.id
        context.user_data["user_area"] = user_area
        ACTIVE_USERS.add(chat_id)
        logger.info(f"User {chat_id} set stay area to '{user_area}'")

        # Schedule a sample checkin reminder for 2 days ahead
        sample_checkin_date = datetime.now() + timedelta(days=2)
        schedule_checkin_reminder(chat_id, sample_checkin_date, context.bot, stay_location=f"{user_area} Hotel")

        await update.message.reply_text(
            f"Awesome! Aapka stay location *{user_area}* save ho gaya hai. 👍\n\n"
            "Ab aap mujhse dinner places, beaches, transport, budget ya weather ke baare mein kuch bhi pooch sakte ho!\n\n"
            "💡 Type `/help` for commands or `/itinerary` for custom trip plan.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in save_stay_area for user {update.effective_chat.id}: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        AWAITING_STAY_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_stay_area)],
    },
    fallbacks=[CommandHandler("help", help_command)],
)


# --- Smart Free-Text Message Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Smart free-text message handler:
    1. Fetches user's current stay area from context.user_data
    2. Filters relevant JSON data for that area using data_loader.py
    3. Calls LLM asking for a short 2-4 line mobile-suited response
    """
    try:
        user_text = update.message.text
        if not user_text:
            return

        chat_id = update.effective_chat.id
        ACTIVE_USERS.add(chat_id)

        user_area = context.user_data.get("user_area", "Goa")
        logger.info(f"Free-text query from User {chat_id} (Area: '{user_area}'): '{user_text}'")

        # Filter JSON dataset for user's stay area
        area_data = filter_by_area(user_area)
        data_context = json.dumps(area_data, indent=2)

        system_prompt = f"""You are 'Goa Trip Concierge', a friendly and smart local AI travel assistant for Goa.

User's Stay Area: {user_area}

Relevant Local Data for {user_area}:
{data_context}

Instructions:
1. Respond to the user in friendly, natural Hinglish (Hindi + English).
2. Use the local dataset above to recommend restaurants, beaches, activities, or transport when relevant.
3. CRITICAL: Keep your response CONCISE, helpful, and mobile-friendly (STRICTLY 2 to 4 lines maximum).
"""

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        response_text = await call_llm(prompt=user_text, system_prompt=system_prompt)
        await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Error in handle_message for chat {update.effective_chat.id}: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")


# --- Demo Command /simulate_reminder ---

async def simulate_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Demo command to trigger an instant sample check-in reminder for pitch/demonstration.
    """
    try:
        chat_id = update.effective_chat.id
        ACTIVE_USERS.add(chat_id)
        user_area = context.user_data.get("user_area", "Anjuna, Goa")
        logger.info(f"User {chat_id} invoked /simulate_reminder")

        await update.message.reply_text(
            "⏱️ *Demo Mode Activated!*\n"
            "Instant sample check-in reminder 3 seconds mein aapke chat par aane wala hai...",
            parse_mode="Markdown"
        )

        target_time = datetime.now() + timedelta(seconds=3)
        schedule_checkin_reminder(
            chat_id=chat_id,
            checkin_date=target_time + timedelta(days=1),
            bot=context.bot,
            stay_location=f"{user_area} Luxury Beach Resort"
        )
    except Exception as e:
        logger.error(f"Error in simulate_reminder_command for chat {update.effective_chat.id}: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")


# --- /itinerary Conversation Handler ---

async def start_itinerary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for /itinerary command."""
    try:
        chat_id = update.effective_chat.id
        ACTIVE_USERS.add(chat_id)
        logger.info(f"User {chat_id} started /itinerary flow")

        default_area = context.user_data.get("user_area", "")
        area_msg = f" (Default: *{default_area}*)" if default_area else ""

        await update.message.reply_text(
            f"🏖️ *Goa Trip Itinerary Planner*\n\n"
            f"Konse area ka plan banana hai?{area_msg} (e.g., *North Goa*, *Anjuna*, *Panjim*, *South Goa*):",
            parse_mode="Markdown"
        )
        return ASK_AREA
    except Exception as e:
        logger.error(f"Error in start_itinerary: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


async def process_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Captures selected area and asks for trip duration."""
    try:
        user_area = update.message.text.strip()
        context.user_data["itinerary_area"] = user_area
        logger.info(f"Itinerary area set to '{user_area}' for user {update.effective_chat.id}")

        await update.message.reply_text(
            f"Great! Selected Area: *{user_area}* 👍\n\n"
            "Aap kitne din ke liye trip plan karna chahte ho? (e.g., 2, 3, 5):",
            parse_mode="Markdown"
        )
        return ASK_DAYS
    except Exception as e:
        logger.error(f"Error in process_area: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


async def process_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Captures trip duration and asks for preferences."""
    try:
        text = update.message.text.strip()
        if not text.isdigit() or int(text) <= 0 or int(text) > 14:
            await update.message.reply_text(
                "Please 1 se 14 ke beech number of days enter karein (e.g., 2, 3, 5):"
            )
            return ASK_DAYS

        num_days = int(text)
        context.user_data["itinerary_days"] = num_days
        logger.info(f"Itinerary duration set to {num_days} days for user {update.effective_chat.id}")

        await update.message.reply_text(
            f"Perfect, *{num_days} days* set ho gaye! 🗓️\n\n"
            "Koi specific preference hai? (e.g., *chill beaches*, *party & nightlife*, *seafood*, *family*, ya type *skip*):",
            parse_mode="Markdown"
        )
        return ASK_PREFERENCES
    except Exception as e:
        logger.error(f"Error in process_days: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


async def process_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calls generate_itinerary and sends final result to user."""
    try:
        preferences = update.message.text.strip()
        area = context.user_data.get("itinerary_area", context.user_data.get("user_area", "Goa"))
        num_days = context.user_data.get("itinerary_days", 3)
        chat_id = update.effective_chat.id

        logger.info(f"Generating {num_days}-day itinerary for area '{area}' (User {chat_id})")

        await update.message.reply_text(
            f"⏳ Generating {num_days}-day Goa itinerary for *{area}*... Please wait a moment!",
            parse_mode="Markdown"
        )
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        itinerary_text = await generate_itinerary(area=area, num_days=num_days, preferences=preferences)
        await update.message.reply_text(itinerary_text)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in process_preferences: {e}", exc_info=True)
        await update.message.reply_text(GENERIC_ERROR_MSG, parse_mode="Markdown")
        return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels any ongoing conversation."""
    try:
        logger.info(f"User {update.effective_chat.id} cancelled conversation flow")
        await update.message.reply_text("Action cancel kar di gayi hai. Aap kisi bhi samay new questions ya `/itinerary` try kar sakte ho!")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel_conversation: {e}", exc_info=True)
        return ConversationHandler.END


itinerary_handler = ConversationHandler(
    entry_points=[CommandHandler("itinerary", start_itinerary)],
    states={
        ASK_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_area)],
        ASK_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_days)],
        ASK_PREFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_preferences)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation), CommandHandler("help", help_command)],
)


# --- Global Uncaught Exception Handler ---

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global exception handler for the Telegram Application.
    """
    logger.error(f"Global Exception Handler caught error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=GENERIC_ERROR_MSG,
                parse_mode="Markdown"
            )
        except Exception as err:
            logger.error(f"Could not send error notification to chat: {err}")
