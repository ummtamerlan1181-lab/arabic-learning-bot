from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    streak: int = 0
    total_points: int = 0
    last_activity: Optional[str] = None
