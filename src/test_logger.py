
from src.logging_config import setup_logger

logger = setup_logger()

logger.info("AeroData Pipeline started")
logger.info("Airport data processing completed")
logger.warning("Some records require review")
logger.error("Example error message")

logger.info("AeroData Pipeline finished")
