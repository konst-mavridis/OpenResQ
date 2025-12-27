"""
Structured logging configuration for OpenResQ backend with optional Firestore.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import get_settings
from app.firebase_config import get_db

db = get_db()
class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        return json.dumps(log_data)
    
def firestore_safe(data: Dict[str, Any]) -> Dict[str, Any]:
    safe = {}
    for k, v in data.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe[k] = v
        else:
            safe[k] = str(v)  # 🔥 stringify lists, dicts, objects
    return safe


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    settings = get_settings()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    if settings.log_format.lower() == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger

def log_action(
    logger: logging.Logger,
    action: str,
    status: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    save_to_firestore: bool = True,
    details: Optional[Dict[str, Any]] = None
):
    log_data = {
        "action": action,
        "status": status,
    }

    if user_id:
        log_data["user_id"] = user_id
    if resource_id:
        log_data["resource_id"] = resource_id

    if details:
        log_data["details"] = firestore_safe(details)  # 👈 ΜΠΑΙΝΕΙ ΕΔΩ

    # Console / JSON log
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

    # Firestore (ΔΕΝ ρίχνει request)
    if save_to_firestore and db:
        try:
            db.collection("logs").add({
                "timestamp": datetime.utcnow(),
                **log_data
            })
        except Exception as e:
            logger.error(f"Firestore log failed (ignored): {e}")
