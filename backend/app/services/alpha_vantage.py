import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.company import (
    CompanySearchResult,
    CompanyOverview,
    EarningsCall,
    FinancialData,
    EarningsCalendarItem
)
from app.models.transcript import TranscriptData, TranscriptEntry, TranscriptMetadata
import uuid
import re


class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, calls_per_minute: int = 5):
        self.calls_per_minute = calls_per_minute
        self.calls: List[datetime] = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until we can make another API call"""
        # If rate limit is 0, skip rate limiting entirely
        if self.calls_per_minute == 0:
            return
            
        async with self.lock:
            now = datetime.now()
            # Remove calls older than 1 minute
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < timedelta(minutes=1)]
            
            # If we've hit the limit, wait
            if len(self.calls) >= self.calls_per_minute:
                oldest_call = self.calls[0]
                wait_time = 60 - (now - oldest_call).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Remove old calls after waiting
                    now = datetime.now()
                    self.calls = [call_time for call_time in self.calls 
                                 if now - call_time < timedelta(minutes=1)]
            
            # Record this call
            self.calls.append(datetime.now())


class AlphaVantageService:
    """Service for interacting with Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str, rate_limit: int = 5):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    
    async def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Store data in cache"""
        self.cache[key] = (data, datetime.now())
    
    async def _make_request(self, params: dict) -> dict:
        """Make API request with rate limiting and error handling"""
        await self.rate_limiter.acquire()
        
        params["apikey"] = self.api_key
        
        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
            if "Note" in data:
                raise ValueError(f"Alpha Vantage rate limit: {data['Note']}")
            
            return data
        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error calling Alpha Vantage: {str(e)}")
    
    async def search_ticker(self, keywords: str) -> List[CompanySearchResult]:
        """Search for companies by keywords"""
        cache_key = f"search:{keywords}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords
        }
        
        data = await self._make_request(params)
        
        if "bestMatches" not in data:
            return []
        
        results = [
            CompanySearchResult(**match)
            for match in data["bestMatches"]
        ]
        
        self._set_cache(cache_key, results)
        return results
    
    async def get_company_overview(self, ticker: str) -> CompanyOverview:
        """Get detailed company information"""
        cache_key = f"overview:{ticker}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "OVERVIEW",
            "symbol": ticker
        }
        
        data = await self._make_request(params)
        
        if not data or "Symbol" not in data:
            raise ValueError(f"No data found for ticker {ticker}")
        
        overview = CompanyOverview(**data)
        self._set_cache(cache_key, overview)
        return overview
    
    async def get_earnings(self, ticker: str) -> List[EarningsCall]:
        """Get earnings history for a company"""
        cache_key = f"earnings:{ticker}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "EARNINGS",
            "symbol": ticker
        }
        
        data = await self._make_request(params)
        
        if "quarterlyEarnings" not in data:
            return []
        
        earnings_calls = []
        for earning in data["quarterlyEarnings"][:20]:  # Last 5 years (20 quarters)
            fiscal_date = earning.get("fiscalDateEnding", "")
            reported_date = earning.get("reportedDate", fiscal_date)
            
            # Parse quarter and year
            if fiscal_date:
                year = int(fiscal_date[:4])
                month = int(fiscal_date[5:7])
                quarter = f"Q{(month - 1) // 3 + 1}"
            else:
                continue
            
            call = EarningsCall(
                id=f"{ticker}-{quarter}-{year}",
                ticker=ticker,
                quarter=quarter,
                year=year,
                date=reported_date,
                fiscal_date_ending=fiscal_date,
                reported_eps=earning.get("reportedEPS"),
                estimated_eps=earning.get("estimatedEPS"),
                surprise=earning.get("surprise"),
                surprise_percentage=earning.get("surprisePercentage"),
                status="recorded"
            )
            earnings_calls.append(call)
        
        self._set_cache(cache_key, earnings_calls)
        return earnings_calls
    
    async def get_earnings_calendar(self, horizon: str = "3month") -> List[EarningsCalendarItem]:
        """Get upcoming earnings calendar"""
        cache_key = f"calendar:{horizon}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "EARNINGS_CALENDAR",
            "horizon": horizon
        }
        
        # Note: This returns CSV format, need to parse
        response = await self.client.get(self.BASE_URL, params={**params, "apikey": self.api_key})
        response.raise_for_status()
        
        # Parse CSV
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(',')
        calendar_items = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) >= 4:
                item = EarningsCalendarItem(
                    symbol=values[0],
                    name=values[1],
                    report_date=values[2],
                    fiscal_date_ending=values[3],
                    estimate=values[4] if len(values) > 4 else None,
                    currency=values[5] if len(values) > 5 else "USD"
                )
                calendar_items.append(item)
        
        self._set_cache(cache_key, calendar_items)
        return calendar_items
    
    async def get_earnings_call_transcript(
        self, 
        ticker: str, 
        quarter: str,
        year: int
    ) -> TranscriptData:
        """Get earnings call transcript"""
        cache_key = f"transcript:{ticker}:{quarter}:{year}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        # Format: 2024Q4, 2024Q3, etc.
        quarter_param = f"{year}{quarter}"
        
        params = {
            "function": "EARNINGS_CALL_TRANSCRIPT",
            "symbol": ticker,
            "quarter": quarter_param
        }
        
        data = await self._make_request(params)
        
        if "transcript" not in data:
            raise ValueError(f"No transcript found for {ticker} {quarter} {year}")
        
        # Transcript can be either a string or a list of dicts
        transcript_raw = data["transcript"]
        if isinstance(transcript_raw, list):
            # List of dicts with 'speaker' and 'content' fields
            transcript_parts = []
            for item in transcript_raw:
                if isinstance(item, dict):
                    speaker = item.get("speaker", "")
                    content = item.get("content", "")
                    if speaker and content:
                        transcript_parts.append(f"{speaker}: {content}")
                    elif content:
                        transcript_parts.append(content)
                else:
                    transcript_parts.append(str(item))
            transcript_text = "\n\n".join(transcript_parts)
        else:
            transcript_text = str(transcript_raw)
        
        fiscal_date = data.get("fiscalDateEnding", f"{year}-{int(quarter[1])*3:02d}-01")
        
        # Parse transcript into entries (simple splitting by speaker)
        entries = self._parse_transcript(transcript_text)
        
        transcript_data = TranscriptData(
            ticker=ticker,
            quarter=quarter,
            year=year,
            fiscal_date_ending=fiscal_date,
            transcript=transcript_text,
            entries=entries
        )
        
        self._set_cache(cache_key, transcript_data)
        return transcript_data
    
    def _parse_transcript(self, transcript_text: str) -> List[TranscriptEntry]:
        """Parse transcript text into structured entries"""
        entries = []
        
        # Simple parsing: split by paragraphs and detect speaker patterns
        # Pattern: "Speaker Name:" or "Operator:" at start of paragraph
        paragraphs = transcript_text.split('\n\n')
        
        current_time = 0
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Try to detect speaker
            speaker_match = re.match(r'^([A-Za-z\s\.]+):\s*', para)
            speaker = None
            text = para
            
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = para[speaker_match.end():].strip()
            
            if text:
                entry = TranscriptEntry(
                    id=str(uuid.uuid4()),
                    timestamp=f"{current_time // 60:02d}:{current_time % 60:02d}",
                    text=text,
                    speaker=speaker,
                    confidence=1.0
                )
                entries.append(entry)
                
                # Estimate time (roughly 150 words per minute speaking rate)
                word_count = len(text.split())
                current_time += int((word_count / 150) * 60)
        
        return entries
    
    async def get_income_statement(self, ticker: str) -> dict:
        """Get quarterly income statement data"""
        cache_key = f"income_statement:{ticker}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": ticker
        }
        
        data = await self._make_request(params)
        self._set_cache(cache_key, data)
        return data
    
    async def get_daily_prices(self, ticker: str, outputsize: str = "full") -> dict:
        """Get daily price history"""
        cache_key = f"daily_prices:{ticker}:{outputsize}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": outputsize  # "compact" = 100 days, "full" = 20+ years
        }
        
        data = await self._make_request(params)
        self._set_cache(cache_key, data)
        return data
    
    async def get_financials(self, ticker: str, quarter: str = None, year: int = None) -> FinancialData:
        """Get financial data combining overview and earnings for a specific quarter or latest"""
        overview = await self.get_company_overview(ticker)
        earnings_list = await self.get_earnings(ticker)
        
        # Find the specific earnings call if quarter/year provided
        target_call = None
        if quarter and year:
            target_call = next(
                (e for e in earnings_list if e.quarter == quarter and e.year == year),
                None
            )
        else:
            # Default to most recent
            target_call = earnings_list[0] if earnings_list else None
        
        if not target_call:
            raise ValueError(f"No earnings data found for {ticker} {quarter} {year}")
        
        # Find previous quarter for comparison
        call_index = earnings_list.index(target_call)
        previous_call = earnings_list[call_index + 1] if call_index + 1 < len(earnings_list) else None
        
        # Calculate changes
        revenue_change = None
        eps_change = None
        yoy_growth = None
        
        # QoQ EPS change (previous quarter)
        if previous_call and target_call.reported_eps and previous_call.reported_eps:
            try:
                current_eps = float(target_call.reported_eps)
                prev_eps = float(previous_call.reported_eps)
                if prev_eps != 0:
                    eps_change_pct = ((current_eps - prev_eps) / abs(prev_eps)) * 100
                    eps_change = f"{'+' if eps_change_pct > 0 else ''}{eps_change_pct:.1f}%"
            except (ValueError, ZeroDivisionError):
                pass
        
        # YoY EPS growth (same quarter last year)
        same_quarter_last_year = next(
            (e for e in earnings_list if e.quarter == target_call.quarter and e.year == target_call.year - 1),
            None
        )
        if same_quarter_last_year and target_call.reported_eps and same_quarter_last_year.reported_eps:
            try:
                current_eps = float(target_call.reported_eps)
                last_year_eps = float(same_quarter_last_year.reported_eps)
                if last_year_eps != 0:
                    yoy_pct = ((current_eps - last_year_eps) / abs(last_year_eps)) * 100
                    yoy_growth = f"{'+' if yoy_pct > 0 else ''}{yoy_pct:.1f}%"
            except (ValueError, ZeroDivisionError):
                pass
        
        # Calculate guidance vs actual from surprise percentage
        guidance_vs_actual = None
        if target_call.surprise_percentage:
            try:
                surprise_pct = float(target_call.surprise_percentage)
                guidance_vs_actual = f"{'+' if surprise_pct > 0 else ''}{surprise_pct:.1f}%"
            except ValueError:
                pass
        
        # Try to get quarterly revenue from income statement
        revenue = overview.revenue_ttm
        try:
            income_stmt = await self.get_income_statement(ticker)
            if "quarterlyReports" in income_stmt:
                # Match quarter by fiscal date
                for report in income_stmt["quarterlyReports"]:
                    report_date = report.get("fiscalDateEnding", "")
                    if target_call.fiscal_date_ending and report_date == target_call.fiscal_date_ending:
                        revenue = report.get("totalRevenue", revenue)
                        break
        except Exception as e:
            # Fallback to TTM revenue if quarterly data not available
            pass
        
        # Get historical stock price for market cap and P/E calculation
        historical_pe = None
        historical_market_cap = None
        
        try:
            # Get stock price around the earnings call date
            daily_prices = await self.get_daily_prices(ticker, outputsize="full")
            time_series = daily_prices.get("Time Series (Daily)", {})
            
            # Try to find price within 7 days of earnings date
            from datetime import datetime, timedelta
            earnings_date = datetime.strptime(target_call.date, "%Y-%m-%d")
            
            # Search for price within a week of earnings date
            for days_offset in range(0, 8):
                for direction in [0, 1, -1]:  # same day, after, before
                    check_date = earnings_date + timedelta(days=days_offset * direction)
                    date_str = check_date.strftime("%Y-%m-%d")
                    
                    if date_str in time_series:
                        price_data = time_series[date_str]
                        close_price = float(price_data.get("4. close", 0))
                        
                        if close_price > 0:
                            # Calculate historical P/E ratio
                            if target_call.reported_eps:
                                try:
                                    eps_value = float(target_call.reported_eps)
                                    if eps_value > 0:
                                        historical_pe = close_price / eps_value
                                except (ValueError, ZeroDivisionError):
                                    pass
                            
                            # Calculate historical market cap
                            # Use current shares outstanding (approximation)
                            if overview.market_cap:
                                try:
                                    current_market_cap = float(overview.market_cap)
                                    current_price = float(overview.fifty_two_week_high) if overview.fifty_two_week_high else None
                                    
                                    if current_price and current_price > 0:
                                        # Estimate shares outstanding
                                        shares_outstanding = current_market_cap / current_price
                                        historical_market_cap = str(int(close_price * shares_outstanding))
                                except (ValueError, ZeroDivisionError, TypeError):
                                    pass
                            
                            break
                    
                    if historical_pe or historical_market_cap:
                        break
                
                if historical_pe or historical_market_cap:
                    break
        except Exception as e:
            # Fallback to current values if historical data not available
            pass
        
        return FinancialData(
            ticker=ticker,
            revenue=revenue,
            revenue_change=revenue_change,
            eps=target_call.reported_eps or overview.eps,
            eps_change=eps_change,
            pe_ratio=historical_pe if historical_pe else (float(overview.pe_ratio) if overview.pe_ratio else None),
            market_cap=historical_market_cap if historical_market_cap else overview.market_cap,
            yoy_growth=yoy_growth or overview.profit_margin,  # Quarter YoY growth or fallback to profit margin
            guidance_vs_actual=guidance_vs_actual
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
