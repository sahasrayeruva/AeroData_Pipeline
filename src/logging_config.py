
import logging
import uuid
from pathlib import Path
from datetime import datetime, timezone

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

RUN_ID = str(uuid.uuid4())

LOG_FILE = LOG_DIR / (
    f"pipeline_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.log"
)


def setup_logger():

    logger = logging.getLogger("AeroData")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        f"RUN_ID={RUN_ID} | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE, encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
