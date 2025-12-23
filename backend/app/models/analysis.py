from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class AnalysisCategory(str, Enum):
    """Categories for earnings analysis"""
    KEY_STATEMENTS = "key_statements"
    FINANCIAL_PERFORMANCE = "financial_performance"
    FORWARD_GUIDANCE = "forward_guidance"
    MARKET_POSITION = "market_position"
    RISK_FACTORS = "risk_factors"
    ANALYST_QA = "analyst_qa"


class Insight(BaseModel):
    """Single insight from analysis"""
    id: str
    timestamp: str
    text: str
    relevance: float


class CategoryInsight(BaseModel):
    """Insights grouped by category"""
    id: str
    category: AnalysisCategory
    sentiment: float  # -1.0 to +1.0
    insights: List[Insight]
    icon: str


class SentimentDataPoint(BaseModel):
    """Sentiment at a specific point in time"""
    timestamp: int  # seconds into call
    overall_sentiment: float
    category_sentiments: Dict[str, float]


class AnalysisRequest(BaseModel):
    """Request to start analysis"""
    ticker: str
    quarter: str
    year: int


class AnalysisSession(BaseModel):
    """Analysis session information"""
    session_id: str
    ticker: str
    quarter: str
    year: int
    status: str  # pending, processing, completed, error
    created_at: datetime
    progress: float = 0.0


class AnalysisStatus(BaseModel):
    """Current status of an analysis"""
    session_id: str
    status: str
    progress: float
    message: Optional[str] = None


class WSMessage(BaseModel):
    """WebSocket message format"""
    type: str  # transcript_update, insight_update, sentiment_update, analysis_complete, error
    payload: dict
    timestamp: int
