import json
import logging
import os
from datetime import datetime, timezone
import sys
from dotenv import load_dotenv
from typing import Any

load_dotenv()

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(
            record.created,
            tz=timezone.utc
        ).isoformat()
        payload: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": os.getenv("APP_ENV", "development")
        }
        
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(payload)

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name. Uses structured formatting suitable for ingestion pipelines.

    Args:
        name (str): The name of the module

    Returns:
        logging.Logger: Logger helper
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()
    
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger