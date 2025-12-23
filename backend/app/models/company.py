from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanySearchResult(BaseModel):
    """Search result for company ticker lookup"""
    ticker: str = Field(..., alias="1. symbol")
    name: str = Field(..., alias="2. name")
    type: str = Field(..., alias="3. type")
    region: str = Field(..., alias="4. region")
    currency: str = Field(..., alias="8. currency")
    
    class Config:
        populate_by_name = True


class CompanyOverview(BaseModel):
    """Detailed company information from Alpha Vantage"""
    symbol: str = Field(..., alias="Symbol")
    name: str = Field(..., alias="Name")
    description: Optional[str] = Field(None, alias="Description")
    sector: Optional[str] = Field(None, alias="Sector")
    industry: Optional[str] = Field(None, alias="Industry")
    market_cap: Optional[str] = Field(None, alias="MarketCapitalization")
    pe_ratio: Optional[str] = Field(None, alias="PERatio")
    eps: Optional[str] = Field(None, alias="EPS")
    revenue_ttm: Optional[str] = Field(None, alias="RevenueTTM")
    profit_margin: Optional[str] = Field(None, alias="ProfitMargin")
    operating_margin_ttm: Optional[str] = Field(None, alias="OperatingMarginTTM")
    return_on_equity_ttm: Optional[str] = Field(None, alias="ReturnOnEquityTTM")
    dividend_yield: Optional[str] = Field(None, alias="DividendYield")
    fifty_two_week_high: Optional[str] = Field(None, alias="52WeekHigh")
    fifty_two_week_low: Optional[str] = Field(None, alias="52WeekLow")
    
    class Config:
        populate_by_name = True


class EarningsCall(BaseModel):
    """Earnings call information"""
    id: str
    ticker: str
    quarter: str
    year: int
    date: str
    fiscal_date_ending: Optional[str] = None
    reported_eps: Optional[str] = None
    estimated_eps: Optional[str] = None
    surprise: Optional[str] = None
    surprise_percentage: Optional[str] = None
    status: str = "recorded"  # upcoming, live, recorded


class FinancialData(BaseModel):
    """Financial metrics for a company"""
    ticker: str
    revenue: Optional[str] = None
    revenue_change: Optional[str] = None
    eps: Optional[str] = None
    eps_change: Optional[str] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[str] = None
    yoy_growth: Optional[str] = None
    guidance_vs_actual: Optional[str] = None


class EarningsCalendarItem(BaseModel):
    """Item from earnings calendar"""
    symbol: str
    name: str
    report_date: str
    fiscal_date_ending: str
    estimate: Optional[str] = None
    currency: str
