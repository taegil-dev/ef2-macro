from pathlib import Path
import sys
import os

from dotenv import load_dotenv

BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip('/')
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_EMAIL = os.environ["SUPABASE_EMAIL"]
SUPABASE_PASSWORD = os.environ["SUPABASE_PASSWORD"]

CLIENT_URL = os.environ['API_BASE_URL'].rstrip('/')
DEVICE = os.environ['DEVICE_ID']
DEVICE_TOKEN = os.environ['DEVICE_TOKEN']
POLL = float(os.environ['POLL'])
HEARTBEAT = float(os.environ['HEARTBEAT'])

GAME_TITLE = os.environ['GAME_TITLE']
GAME_TARGET_CLASS = os.environ['GAME_TARGET_CLASS']

MACRO_DELAY = float(os.environ['MACRO_DELAY'])
SEQUENCE_DELAY = float(os.environ['SEQUENCE_DELAY'])

__all__ = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_EMAIL",
    "SUPABASE_PASSWORD",

    "CLIENT_URL",
    "DEVICE",
    "DEVICE_TOKEN",
    "POLL",
    "HEARTBEAT",

    "GAME_TITLE",
    "GAME_TARGET_CLASS",

    "MACRO_DELAY",
    "SEQUENCE_DELAY",
]