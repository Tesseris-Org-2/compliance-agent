import os
from dotenv import load_dotenv

load_dotenv()

# Attempt to load OpenAI Key from environment, otherwise mock it.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
