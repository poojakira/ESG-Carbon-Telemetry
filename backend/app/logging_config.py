import os
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """ Custom JSON formatter for industrial observability. """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(level=logging.INFO):
    """ Configures structured logging. """
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Console Handler (JSON)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    # Also log to file for audit persistence
    file_handler = logging.FileHandler("audit.log")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    logging.info("📟 Observability Engine: STRUCTURED LOGGING ACTIVE")
