import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
BASE_DIR = Path(__file__).parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Paths for data and images
DATA_FILE = BASE_DIR / "times.json"
TRACKIMGS_DIR = BASE_DIR / "trackimgs"

# Set token
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN ist nicht gesetzt. Bitte .env prüfen.")
