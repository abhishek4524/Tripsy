import logging
import json
from data.data_loader import filter_by_area, load_data
from bot.llm_client import call_llm

logger = logging.getLogger("GoaConcierge.Itinerary")

async def generate_itinerary(area: str, num_days: int, preferences: str = "") -> str:
    """
    Generates a day-by-day Goa travel itinerary using filtered local dataset and OpenRouter LLM.
    Wrapped in try/except to prevent unhandled crashes.
    """
    try:
        logger.info(f"generate_itinerary called for area '{area}', days={num_days}, prefs='{preferences}'")
        
        # 1. Filter local dataset for specified area
        area_data = filter_by_area(area)

        # Fallback to full dataset if no specific area matches
        has_matches = any(area_data.get(cat) for cat in ["restaurants", "beaches", "activities"])
        if not has_matches:
            logger.info(f"No specific area matches found for '{area}'. Falling back to full Goa dataset.")
            all_data = load_data()
            area_data = {
                "restaurants": all_data.get("restaurants", []),
                "beaches": all_data.get("beaches", []),
                "activities": all_data.get("activities", []),
                "transport": all_data.get("transport", [])
            }

        dataset_json = json.dumps(area_data, indent=2)

        # 2. Construct system prompt enforcing strict use of provided data
        system_prompt = f"""You are 'Goa Trip Concierge', an expert AI travel planner.

CRITICAL INSTRUCTION: You MUST strictly use ONLY the places, restaurants, beaches, and activities listed in the provided JSON dataset below. DO NOT invent, hallucinate, or fabricate any new place names.

Available Goa Dataset:
{dataset_json}
"""

        # 3. Construct user prompt
        pref_text = preferences if preferences and preferences.strip().lower() != "skip" else "General sightseeing, beach chill & local food"

        prompt = f"""Create a clean, well-formatted {num_days}-day trip itinerary for '{area}'.
User Preference: {pref_text}

Format Requirements:
1. Divide into clear sections using headings: 'Day 1:', 'Day 2:', etc.
2. For EVERY day, include:
   - 🌅 Morning Activity (from available activities)
   - 🏖️ Afternoon / Lunch Spot (from available beaches & restaurants)
   - 🌙 Evening / Dinner & Nightlife (from available restaurants & activities)
3. Include a small '💡 Travel Tip' at the bottom using available transport options.
4. Write in a friendly, conversational Hinglish style (Hindi + English).
5. Remember: STRICTLY use place names from the dataset.
"""

        logger.info(f"Sending LLM request for {num_days}-day itinerary ({area})...")
        itinerary_result = await call_llm(prompt=prompt, system_prompt=system_prompt)
        return itinerary_result

    except Exception as e:
        logger.error(f"Error generating itinerary for area '{area}': {e}", exc_info=True)
        return "⚠️ Itinerary generate karne mein issue aaya. Please dobara try karein."
