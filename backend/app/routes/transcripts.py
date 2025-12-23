from fastapi import APIRouter, HTTPException, Path, Query
from app.services.alpha_vantage import AlphaVantageService
from app.models import TranscriptData
from app.config import get_settings

router = APIRouter(prefix="/api/transcript", tags=["transcripts"])
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


@router.get("/{ticker}/{quarter}", response_model=TranscriptData)
async def get_transcript(
    ticker: str = Path(..., description="Company ticker symbol (e.g., AAPL)"),
    quarter: str = Path(..., description="Quarter (e.g., Q4-2024 or Q4)"),
):
    """
    Get earnings call transcript for a specific quarter
    
    Examples:
    - `/api/transcript/AAPL/Q4-2024`
    - `/api/transcript/AAPL/Q4?year=2024`
    """
    try:
        # Parse quarter format: "Q4-2024" or "Q4" with year param
        if "-" in quarter:
            quarter_part, year_part = quarter.split("-")
            year = int(year_part)
        else:
            # If no year in path, require it as query param
            raise HTTPException(
                status_code=400,
                detail="Quarter must be in format 'Q1-2024' or provide year as query parameter"
            )
        
        service = get_service()
        transcript = await service.get_earnings_call_transcript(
            ticker.upper(),
            quarter_part,
            year
        )
        return transcript
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/{ticker}/{quarter}/{year}", response_model=TranscriptData)
async def get_transcript_with_year(
    ticker: str = Path(..., description="Company ticker symbol (e.g., AAPL)"),
    quarter: str = Path(..., description="Quarter (e.g., Q4)"),
    year: int = Path(..., description="Year (e.g., 2024)")
):
    """
    Get earnings call transcript for a specific quarter and year
    
    Example: `/api/transcript/AAPL/Q4/2024`
    """
    try:
        service = get_service()
        transcript = await service.get_earnings_call_transcript(
            ticker.upper(),
            quarter,
            year
        )
        return transcript
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.on_event("shutdown")
async def shutdown_event():
    """Clean up service on shutdown"""
    global _service
    if _service:
        await _service.close()
        _service = None
