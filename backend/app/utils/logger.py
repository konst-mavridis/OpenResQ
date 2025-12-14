"""
Structured logging configuration for OpenResQ backend.
Provides environment-aware, consistent logging across the application.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if provided
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    settings = get_settings()
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    
    # Choose formatter based on configuration
    if settings.log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_action(
    logger: logging.Logger,
    action: str,
    status: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Log a structured action with consistent format."""
    log_data = {
        "action": action,
        "status": status,
    }
    
    if user_id:
        log_data["user_id"] = user_id
    if resource_id:
        log_data["resource_id"] = resource_id
    if details:
        log_data.update(details)
    
    # Create a LogRecord with extra fields
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "(unknown file)",
        0,
        f"{action}: {status}",
        (),
        None,
    )
    record.extra_fields = log_data
    logger.handle(record)
