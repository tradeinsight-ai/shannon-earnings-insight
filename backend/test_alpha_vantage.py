"""
Test script for Alpha Vantage service
Run: uv run python test_alpha_vantage.py
"""
import asyncio
from app.services.alpha_vantage import AlphaVantageService
from app.config import get_settings

async def test_alpha_vantage():
    """Test Alpha Vantage service methods"""
    settings = get_settings()
    service = AlphaVantageService(
        api_key=settings.alpha_vantage_api_key,
        rate_limit=settings.alpha_vantage_rate_limit
    )
    
    try:
        print("=" * 60)
        print("Testing Alpha Vantage Service")
        print("=" * 60)
        
        # Test 1: Search for a company
        print("\n1. Testing search_ticker('Apple')...")
        results = await service.search_ticker("Apple")
        if results:
            print(f"   Found {len(results)} results")
            print(f"   First result: {results[0].ticker} - {results[0].name}")
        else:
            print("   No results found")
        
        # Test 2: Get company overview
        ticker = "AAPL"
        print(f"\n2. Testing get_company_overview('{ticker}')...")
        overview = await service.get_company_overview(ticker)
        print(f"   Company: {overview.name}")
        print(f"   Sector: {overview.sector}")
        print(f"   Market Cap: {overview.market_cap}")
        print(f"   P/E Ratio: {overview.pe_ratio}")
        print(f"   EPS: {overview.eps}")
        
        # Test 3: Get earnings history
        print(f"\n3. Testing get_earnings('{ticker}')...")
        earnings = await service.get_earnings(ticker)
        if earnings:
            print(f"   Found {len(earnings)} earnings reports")
            latest = earnings[0]
            print(f"   Latest: {latest.quarter} {latest.year} - {latest.date}")
            print(f"   Reported EPS: {latest.reported_eps}")
            print(f"   Estimated EPS: {latest.estimated_eps}")
            print(f"   Surprise: {latest.surprise_percentage}")
        
        # Test 4: Get financials
        print(f"\n4. Testing get_financials('{ticker}')...")
        financials = await service.get_financials(ticker)
        print(f"   Revenue: {financials.revenue}")
        print(f"   EPS: {financials.eps}")
        print(f"   P/E Ratio: {financials.pe_ratio}")
        print(f"   Market Cap: {financials.market_cap}")
        
        # Test 5: Get earnings call transcript
        print(f"\n5. Testing get_earnings_call_transcript('{ticker}', 'Q4', 2024)...")
        try:
            transcript = await service.get_earnings_call_transcript(ticker, "Q4", 2024)
            print(f"   Transcript length: {len(transcript.transcript)} characters")
            print(f"   Number of entries: {len(transcript.entries)}")
            if transcript.entries:
                print(f"   First entry speaker: {transcript.entries[0].speaker}")
                print(f"   First entry preview: {transcript.entries[0].text[:100]}...")
        except ValueError as e:
            print(f"   Error: {e}")
            print("   (This is expected if transcript is not available yet)")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(test_alpha_vantage())
