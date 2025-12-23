from pydantic import BaseModel
from typing import List, Optional


class TranscriptEntry(BaseModel):
    """Single entry in an earnings call transcript"""
    id: str
    timestamp: str
    text: str
    speaker: Optional[str] = None
    confidence: Optional[float] = None


class TranscriptData(BaseModel):
    """Complete earnings call transcript"""
    ticker: str
    quarter: str
    year: int
    fiscal_date_ending: str
    transcript: str
    entries: List[TranscriptEntry] = []
    
    
class TranscriptMetadata(BaseModel):
    """Metadata about an earnings call transcript"""
    ticker: str
    quarter: str
    year: int
    fiscal_date_ending: str
    has_transcript: bool
    length: Optional[int] = None  # character count
