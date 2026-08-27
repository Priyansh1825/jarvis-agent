import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# API Keys & Cloud AI Models
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Voice / TTS Settings
# "en-GB-RyanNeural" is the best authentic British JARVIS voice
JARVIS_VOICE = os.getenv("JARVIS_VOICE", "en-GB-RyanNeural")
JARVIS_SPEECH_RATE = os.getenv("JARVIS_SPEECH_RATE", "+5%")
JARVIS_PITCH = os.getenv("JARVIS_PITCH", "+0Hz")

# Personalization
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "JARVIS")
USER_NAME = os.getenv("USER_NAME", "Sir")

# Directories for runtime artifacts
DATA_DIR = BASE_DIR / "data"
NOTES_DIR = DATA_DIR / "notes"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
TEMP_AUDIO_DIR = DATA_DIR / "temp"

for directory in [DATA_DIR, NOTES_DIR, SCREENSHOTS_DIR, TEMP_AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
