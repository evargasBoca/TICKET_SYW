from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class ReportSavedView:
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    config: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
