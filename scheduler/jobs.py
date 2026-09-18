import logging
from datetime import datetime, timedelta
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config

logger = logging.getLogger(__name__)

# Global APScheduler instance
scheduler = AsyncIOScheduler()

async def send_checkin_reminder_job(bot, chat_id: int, stay_location: str = "Goa Hotel & Resort"):
    """
    Callback function executed by APScheduler to send check-in reminder message.
    """
    message = (
        "🔔 *Reminder: Kal Aapka Check-in Hai!* 🏨\n\n"
        f"📍 *Location*: {stay_location}\n"
        "🅿️ *Parking Info*: Hotel campus mein free parking space available hai.\n"
        "📞 *Reception Contact*: +91-9876543210\n"
        "🧳 Have a safe and happy journey!"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        logger.info(f"Check-in reminder successfully sent to chat_id: {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send check-in reminder to chat_id {chat_id}: {e}")

def schedule_checkin_reminder(chat_id: int, checkin_date: datetime, bot, stay_location: str = "Goa Hotel & Resort"):
    """
    Schedules check-in reminder job 1 day before checkin_date.
    If checkin_date - 1 day is already past, schedules it 5 seconds from now.
    """
    reminder_time = checkin_date - timedelta(days=1)
    now = datetime.now()

    if reminder_time <= now:
        reminder_time = now + timedelta(seconds=5)

    job_id = f"checkin_{chat_id}_{int(reminder_time.timestamp())}"
    scheduler.add_job(
        send_checkin_reminder_job,
        'date',
        run_date=reminder_time,
        args=[bot, chat_id, stay_location],
        id=job_id,
        replace_existing=True
    )
    logger.info(f"Check-in reminder scheduled for chat_id {chat_id} at {reminder_time}")
    return reminder_time

async def daily_weather_check(bot, active_users: set):
    """
    Fetches OpenWeatherMap API data for Goa.
    If rain/drizzle is detected, sends indoor activity suggestions to active users.
    """
    if not active_users:
        return

    api_key = config.WEATHER_API_KEY
    is_rainy = False
    weather_desc = "Rain / Showers"

    if api_key and api_key != "your_weather_api_key_here":
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q=Goa,IN&appid={api_key}&units=metric"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    weather_main = data.get("weather", [{}])[0].get("main", "").lower()
                    weather_desc = data.get("weather", [{}])[0].get("description", "Rain")
                    if any(term in weather_main for term in ["rain", "drizzle", "thunderstorm", "clouds"]):
                        is_rainy = True
        except Exception as e:
            logger.error(f"Error checking OpenWeatherMap API: {e}")

    # Send rain alert if rainy or as fallback demonstration
    if is_rainy or not api_key or api_key == "your_weather_api_key_here":
        alert_msg = (
            f"🌧️ *Goa Daily Weather Alert*\n\n"
            f"Weather update: *{weather_desc.capitalize()}* expected today in Goa!\n\n"
            "💡 *Indoor Activity Suggestion*: Baarish mein outdoor beach ke bajaye "
            "**Fontainhas Latin Quarter Heritage Walk**, **Old Goa Churches Tour**, ya **Tropical Spice Plantation Visit** explore karein! 🏛️🎨"
        )
        for chat_id in list(active_users):
            try:
                await bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending weather alert to chat {chat_id}: {e}")

def setup_scheduler(bot, active_users: set):
    """
    Initializes and starts APScheduler background jobs.
    """
    if not scheduler.running:
        # Schedule daily weather check at 08:00 AM every day
        scheduler.add_job(
            daily_weather_check,
            'cron',
            hour=8,
            minute=0,
            args=[bot, active_users],
            id="daily_weather_check",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler initialized and running.")
