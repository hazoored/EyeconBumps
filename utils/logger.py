import sys
from loguru import logger

def setup_logger():
    # Remove default handler
    logger.remove()
    
    # Custom format for a "premium" look
    # <level> tag colors the whole line or parts based on level
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(sys.stdout, format=log_format, colorize=True, level="INFO")
    
    # Optional: Add file handler for persistence
    logger.add("logs/bot.log", rotation="10 MB", retention="10 days", format=log_format, level="DEBUG")

    return logger

# Initialize immediately for easy import
bot_logger = setup_logger()
