# 🌴 Goa Trip Concierge - Telegram Bot

An AI-powered, intelligent Telegram concierge bot for Goa travel recommendations, custom day-by-day itinerary planning, background check-in reminders, and weather notifications. Built with `python-telegram-bot`, `OpenRouter LLM API`, and `APScheduler`.

---

## ✨ Features

- 🤖 **AI-Powered Local Assistant**: Smart free-text answers for travel queries (restaurants, beaches, transport, budget). Keeps responses concise (2-4 lines) for mobile chat.
- 🏖️ **Custom Itinerary Planner (`/itinerary`)**: Interactive day-by-day trip generator that strictly uses local dataset places (*no hallucinated places*).
- 🔔 **Check-in Reminders & APScheduler**: Automated notifications scheduled 1 day prior to check-in (parking details, reception contact).
- 🌧️ **Daily Weather Alerts**: Fetches OpenWeatherMap API; if rain is expected, suggests indoor activities (Fontainhas walk, Old Goa churches, Spice plantations).
- ⏱️ **Instant Demo Mode (`/simulate_reminder`)**: Instant 3-second sample reminder trigger for quick pitches and presentations.
- 🛡️ **Robust Error Handling & Logging**: Every handler is wrapped in `try...except` to prevent crashes, with complete background logging for easy debugging.

---

## 📁 Project Structure

```text
goa-trip-concierge/
│
├── bot/
│   ├── __init__.py
│   ├── handlers.py         # Telegram command & message handlers (/start, /itinerary, /help)
│   ├── itinerary.py        # Day-by-day itinerary generator logic
│   └── llm_client.py       # OpenRouter LLM API client with fallback handling
│
├── data/
│   ├── goa_data.json       # Structured Goa travel database (restaurants, beaches, activities, transport)
│   └── data_loader.py      # Data loading and area/category filtering functions
│
├── scheduler/
│   ├── __init__.py
│   └── jobs.py             # APScheduler jobs for check-in reminders & weather alerts
│
├── .env.example            # Environment variables template
├── .gitignore              # Ignores sensitive environment & cache files
├── config.py               # Application configuration loader
├── main.py                 # Bot startup & application entry point
├── Procfile                # Render Background Worker process definition
├── render.yaml             # Render Blueprint specification file
├── requirements.txt        # Python package dependencies
└── test_app.py             # One-command verification & test suite
```

---

## 🚀 Local Setup & Running

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/goa-trip-concierge.git
cd goa-trip-concierge
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```env
BOT_TOKEN=your_telegram_bot_token_here
LLM_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-3.3-70b-instruct
WEATHER_API_KEY=your_weather_api_key_here
```

### 3. Verify Setup
Run the quick test suite to verify data loading and LLM connectivity:
```bash
python test_app.py
```

### 4. Start the Bot
```bash
python main.py
```

---

## 🌐 Deploying to Render.com

Render is an ideal hosting platform for running this Telegram Bot as a **Background Worker**.

### Step 1: Push Project to GitHub
Initialize git repository and push your project to GitHub:
```bash
git init
git add .
git commit -m "Initial commit of Goa Trip Concierge Bot"
git branch -M main
git remote add origin https://github.com/your-username/goa-trip-concierge.git
git push -u origin main
```

### Step 2: Create a Background Worker on Render
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Background Worker**.
3. Connect your GitHub repository (`goa-trip-concierge`).
4. Configure the service:
   - **Name**: `goa-trip-concierge`
   - **Environment**: `Python 3`
   - **Region**: Select closest region (e.g. Singapore or Frankfurt)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

*(Alternatively, if using Render Blueprints, select **New + -> Blueprint** and point to `render.yaml`)*.

### Step 3: Add Environment Variables in Render
In the **Environment** tab of your Render service, add the following variables:

| Key | Value / Note |
|---|---|
| `BOT_TOKEN` | Your Telegram Bot Token from `@BotFather` |
| `LLM_API_KEY` | Your OpenRouter API Key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | `meta-llama/llama-3.3-70b-instruct` |
| `WEATHER_API_KEY` | *(Optional)* OpenWeatherMap API Key |

### Step 4: Deploy & Verify Logs
1. Click **Create Background Worker** (or **Save Changes**).
2. Monitor the **Logs** tab in Render dashboard.
3. You should see log output:
   `🤖 Goa Trip Concierge Bot is running with APScheduler & Error Handling!`
4. Open Telegram and send `/start` or `/help` to test your live deployed bot!

---

## 🤖 Telegram Bot Commands

- `/start` - Welcome message & stay area setup
- `/itinerary` - Interactive day-by-day trip planner
- `/simulate_reminder` - Demo instant check-in reminder
- `/help` - View list of all available commands
- `/cancel` - Cancel current conversation flow
