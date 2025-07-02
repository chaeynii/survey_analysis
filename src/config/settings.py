from config.common_imports import *
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DEF_PATH = BASE_DIR / os.getenv("DEF_PATH")
RAW_PATH = BASE_DIR / os.getenv("RAW_PATH")
PROCESSED = BASE_DIR / os.getenv("PROCESSED_PATH")

EXCLUDE_COLUMNS = [
    'user_name',
    'user_number',
]

ORG_NAME = os.getenv("ORG_NAME")
BASE_DATE = os.getenv("BASE_DATE")