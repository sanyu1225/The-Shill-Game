"""
The Shill Game - A strategy game with AI agents playing as meme coin managers.
"""

__version__ = "0.1.0"

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
