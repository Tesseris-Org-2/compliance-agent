import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.fake_chat_models import FakeListChatModel
import json

logger = logging.getLogger(__name__)

load_dotenv()

def get_gemini_agent():
    """
    Returns a LangChain ChatModel that uses Gemini 2.5 Flash.
    """
    # Force reload of dotenv from explicit path to bypass Docker env masking
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path, override=True)
    
    keys = []
    
    # Check for numbered keys
    for i in range(1, 10):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            
    # Fallback to standard key if no numbered keys exist
    if not keys:
        standard_key = os.getenv("GEMINI_API_KEY")
        if standard_key:
            keys.append(standard_key)
            
    if not keys:
        logger.warning("No Gemini API keys found. The agent will likely fail.")
        return None
            
    logger.info(f"Initialized Gemini model pool with {len(keys)} API keys.")
    
    # Create the primary model
    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=keys[0],
        temperature=0
    )
    
    # If we only have 1 key, return just the primary model
    if len(keys) == 1:
        return primary_llm
        
    # If we have multiple, create fallback LLMs and attach them
    fallback_llms = [
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=key,
            temperature=0
        ) for key in keys[1:]
    ]
    
    # Langchain's with_fallbacks will automatically try the next model if the primary hits an Exception (e.g. RateLimit)
    return primary_llm.with_fallbacks(fallback_llms)
