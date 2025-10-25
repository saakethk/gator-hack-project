# Schema Defintion for Topic

# Dependencies
from datetime import datetime, timezone
import uuid
from difflib import SequenceMatcher
from dataclasses import dataclass, field

# Helper Functions
def parse_date(utc_timestamp: float) -> datetime:
        return datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    
def get_utc_timestamp() -> datetime:
    return datetime.now(timezone.utc)



# Topic data class
@dataclass(slots=True)
class Topic:
    date_added: datetime
    date_created: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    summary: str = ""
    url: str = ""
    source: str = ""
    is_active: bool = False
    is_archived: bool = False
    exercises: list[str] = field(default_factory=lambda: [])
    relevance_score: int = 0
    internal_relevance_score: int = 0
    pros: list[str] = field(default_factory=lambda: [])
    cons: list[str] = field(default_factory=lambda: [])
    
    def __eq__(self, other) -> bool:
        # Other param must be a story object
        es = SequenceMatcher(None, self.name, other.name).ratio()
        threshold = 0.8 # Threshold for similarity to prevent duplicates
        if es > threshold:
            return True
        else:
            return False
        
    def __str__(self) -> str:
        return self.name
    
    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "date_added": self.date_added.isoformat(),
            "date_created": self.date_created.isoformat(),
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "exercises": self.exercises,
            "relevance_score": self.relevance_score,
            "internal_relevance_score": self.internal_relevance_score,
            "pros": self.pros,
            "cons": self.cons
        }