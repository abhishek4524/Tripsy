import logging
import config

logger = logging.getLogger(__name__)

# Fallback message returned in case of errors
FALLBACK_MESSAGE = "Mujhe abhi response generate karne mein dikkat ho rahi hai. Kripya thodi der baad dobara try karein."

async def call_llm(prompt: str, system_prompt: str = None) -> str:
    """
    Calls OpenRouter LLM API with the provided user prompt (and optional system prompt).
    API key and base URL are fetched from config (.env).
    
    Returns response text string. Catches any exception gracefully and returns fallback text.
    """
    api_key = getattr(config, "LLM_API_KEY", None)
    base_url = getattr(config, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model_name = getattr(config, "LLM_MODEL", "meta-llama/llama-3.3-70b-instruct")

    # Validate API Key existence
    if not api_key or api_key.strip() == "" or api_key == "your_openrouter_api_key_here":
        logger.warning("call_llm failed: LLM_API_KEY is not configured in .env file.")
        return "⚠️ OpenRouter API Key missing hai. Please .env file mein LLM_API_KEY setup karein."

    try:
        from openai import AsyncOpenAI

        # Initialize AsyncOpenAI client targeting OpenRouter
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Make API request to OpenRouter
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://github.com/goa-trip-concierge",
                "X-Title": "Goa Trip Concierge Bot",
            },
            timeout=30.0  # 30 seconds timeout limit
        )

        # Extract message content safely
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()

        logger.warning("OpenRouter API returned an empty choice response.")
        return FALLBACK_MESSAGE

    except Exception as e:
        # Log exact error for debugging without breaking bot execution
        logger.error(f"Error while executing OpenRouter call_llm: {e}", exc_info=True)
        return FALLBACK_MESSAGE
