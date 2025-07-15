# Load environment variables and expose settings
from dotenv import load_dotenv
import os

# Load .env into environment variables
load_dotenv()

class Settings:
    # Google Custom Search API credentials
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CSE_ID  = os.getenv('GOOGLE_CSE_ID')

    # OpenAI API credentials and model choice
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL   = os.getenv('OPENAI_MODEL')

# Singleton settings object for import elsewhere
settings = Settings()