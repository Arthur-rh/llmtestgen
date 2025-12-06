from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
