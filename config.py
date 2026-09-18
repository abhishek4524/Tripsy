import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# OpenRouter LLM API Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# Default to active OpenRouter model slug (meta-llama/llama-3.3-70b-instruct or openai/gpt-4o-mini)
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct")

# Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
