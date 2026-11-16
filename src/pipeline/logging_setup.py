from loguru import logger
import sys

def setup_logging() -> None:
    logger.remove()

    custom_format=(
        "<green>{time: YYYY/MM/DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> |"
        "<cyan>{name}</cyan> : <cyan>{function}</cyan> : <cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,  
        format = custom_format, 
        colorize=True
    )

    logger.add(
        "logs/pipeline.log",
        format=custom_format,
        rotation= "1 day",
        retention= "5 days",
        level="INFO"
        
    )

