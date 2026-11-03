from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ClassificationResponse(BaseModel):
    label: str 

@dataclass
class ArticleData:
    title: str
    content: str
    url: str
    source: str
    scraped_at: str
    content_hash: str
    word_count: int
    reading_time_minutes: int
    metadata: Dict[str, Any]
    quality_score: float

@dataclass
class ScrapingStats:
    total_attempted: int = 0
    successful: int = 0
    failed: int = 0
    duplicate: int = 0
    low_quality: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
