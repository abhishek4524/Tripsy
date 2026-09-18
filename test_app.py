"""
Quick verification script for Goa Trip Concierge.
Run this script using: python test_app.py
"""

import asyncio
import sys

# 1. Test Data Loader
print("========================================")
print("1. Testing Data Loader (goa_data.json)...")
print("========================================")
try:
    from data.data_loader import load_data, filter_by_area, filter_by_category
    
    data = load_data()
    print("[OK] Data Loaded Successfully!")
    print(f"   - Restaurants count: {len(data.get('restaurants', []))}")
    print(f"   - Beaches count    : {len(data.get('beaches', []))}")
    print(f"   - Activities count : {len(data.get('activities', []))}")
    print(f"   - Transport options: {len(data.get('transport', []))}")
    
    # Test area filter
    anjuna = filter_by_area("Anjuna")
    print(f"   - Found {len(anjuna['restaurants'])} restaurants in Anjuna.")

except Exception as e:
    print(f"[ERROR] Data Loader Exception: {e}")

print("\n========================================")
print("2. Testing OpenRouter LLM Client...")
print("========================================")

async def test_llm():
    from bot.llm_client import call_llm
    import config
    
    if not config.LLM_API_KEY or config.LLM_API_KEY == "your_openrouter_api_key_here":
        print("[WARN] LLM_API_KEY is not configured in `.env` file.")
        print("       Testing Fallback mechanism...")
    else:
        print(f"   Using OpenRouter Model: {config.LLM_MODEL}")
    
    prompt = "Suggest 2 famous beaches in North Goa in 1 short sentence."
    print(f"   Sending Prompt: '{prompt}'")
    response = await call_llm(prompt)
    print("\n   [LLM Response]:")
    print(f"   {response}")

try:
    asyncio.run(test_llm())
except Exception as e:
    print(f"[ERROR] LLM Client Exception: {e}")

print("\n========================================")
print("3. Telegram Bot Status Check...")
print("========================================")
import config
if not config.BOT_TOKEN or config.BOT_TOKEN == "your_telegram_bot_token_here":
    print("[WARN] BOT_TOKEN is missing in `.env` file.")
    print("       To run Telegram bot, set BOT_TOKEN in `.env` and run 'python main.py'.")
else:
    print("[OK] BOT_TOKEN is present in `.env`!")
    print("     You can run 'python main.py' to start the bot.")
print("========================================")
