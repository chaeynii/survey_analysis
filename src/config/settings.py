from src.config.common_imports import *

BASE_DIR = Path(__file__).resolve().parent.parent
DEF_PATH = BASE_DIR / 'data/raw/설문조사 문항 정의서.xlsx'
RAW_PATH = BASE_DIR / './data/raw/수요조사 결과 원본.xlsx'
PROCESSED = BASE_DIR / 'data/processed/preprocessed_survey.xlsx'

EXCLUDE_COLUMNS = [
    'user_name',
    'user_number',
]
