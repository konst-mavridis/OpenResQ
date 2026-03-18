# models/dispatch_priority.py

from pydantic import BaseModel
from typing import Dict

# In-memory store (βάλε DB στη θέση του)
SERVICE_PRIORITIES: Dict[str, Dict[str, int]] = {}


class ServicePriorityConfig(BaseModel):
    service_id: str
    priorities: Dict[str, int]  # π.χ. {"fire": 1, "hazard": 2, ...}
