from config.common_imports import *

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logging(log_file_name, console: bool = False):
    handlers = [
        logging.FileHandler(f"{LOG_DIR}/{log_file_name}", encoding='utf-8')
    ]
    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level   = LOG_LEVEL,
        format  = '%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)