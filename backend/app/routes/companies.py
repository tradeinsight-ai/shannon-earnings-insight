from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.alpha_vantage import AlphaVantageService
from app.models import (
    CompanySearchResult,
    CompanyOverview,
    EarningsCall,
    FinancialData,
    EarningsCalendarItem
)
from app.config import get_settings

router = APIRouter(prefix="/api/companies", tags=["companies"])
settings = get_settings()

# Create service instance (should be dependency injected in production)
_service: AlphaVantageService | None = None

def get_service() -> AlphaVantageService:
    """Get or create Alpha Vantage service instance"""
    global _service
    if _service is None:
        _service = AlphaVantageService(
            api_key=settings.alpha_vantage_api_key,
            rate_limit=settings.alpha_vantage_rate_limit
        )
    return _service


@router.get("/search")
async def search_companies(
    q: str = Query(..., description="Search query (company name or ticker)", min_length=1)
):
    """
    Search for companies by name or ticker symbol
    
    Filters to only US-listed equities (excludes ETFs, mutual funds, foreign exchanges)
    
    Example: `/api/companies/search?q=Apple`
    """
    try:
        service = get_service()
        results = await service.search_ticker(q)
        
        # Filter for US-listed equities only (if enabled)
        if settings.filter_us_equities_only:
            filtered_results = []
            for result in results:
                # Only include if:
                # 1. Type is "Equity" (not ETF, Mutual Fund, etc.)
                # 2. Region is "United States"
                # 3. Ticker doesn't have foreign exchange suffix (., -)
                if (result.type == "Equity" and 
                    result.region == "United States" and
                    '.' not in result.ticker and
                    '-' not in result.ticker):
                    filtered_results.append(result.model_dump(by_alias=False))
            return filtered_results
        else:
            # Return all results without filtering
            return [result.model_dump(by_alias=False) for result in results]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/{ticker}")
async def get_company(ticker: str):
    """
    Get detailed company information
    
    Example: `/api/companies/AAPL`
    """
    try:
        service = get_service()
        overview = await service.get_company_overview(ticker.upper())
        return overview.model_dump(by_alias=False)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/{ticker}/earnings", response_model=List[EarningsCall])
async def get_company_earnings(ticker: str):
    """
    Get historical earnings reports for a company
    
    Example: `/api/companies/AAPL/earnings`
    """
    try:
        service = get_service()
        earnings = await service.get_earnings(ticker.upper())
        return earnings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/{ticker}/financials", response_model=FinancialData)
async def get_company_financials(
    ticker: str,
    quarter: str = Query(None, description="Quarter (e.g., 'Q1', 'Q2', 'Q3', 'Q4')"),
    year: int = Query(None, description="Year (e.g., 2024)")
):
    """
    Get financial metrics for a company for a specific quarter or latest
    
    Examples: 
    - `/api/companies/AAPL/financials` - Latest quarter
    - `/api/companies/AAPL/financials?quarter=Q4&year=2024` - Specific quarter
    
    Returns 404 if no financial data available for the ticker.
    """
    try:
        service = get_service()
        financials = await service.get_financials(ticker.upper(), quarter, year)
        return financials
    except ValueError as e:
        # Return 404 when company not found or no data available
        raise HTTPException(
            status_code=404, 
            detail=f"Financial data not available for {ticker.upper()}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/calendar/upcoming", response_model=List[EarningsCalendarItem])
async def get_earnings_calendar(
    horizon: str = Query("3month", description="Time horizon: 3month, 6month, or 12month")
):
    """
    Get upcoming earnings calendar
    
    Example: `/api/companies/calendar/upcoming?horizon=3month`
    """
    try:
        service = get_service()
        calendar = await service.get_earnings_calendar(horizon)
        return calendar
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.on_event("shutdown")
async def shutdown_event():
    """Clean up service on shutdown"""
    global _service
    if _service:
        await _service.close()
        _service = None
