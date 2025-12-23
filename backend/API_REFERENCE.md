# earningsInsight API Reference

Base URL: `http://localhost:8000`

## Health & Status

### GET `/health`
Check API health and configuration status

**Response:**
```json
{
  "status": "healthy",
  "alpha_vantage": "configured",
  "openai": "configured"
}
```

---

## Companies

### GET `/api/companies/search`
Search for companies by name or ticker

**Query Parameters:**
- `q` (required): Search query

**Example:**
```bash
curl "http://localhost:8000/api/companies/search?q=Apple"
```

**Response:**
```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc",
    "type": "Equity",
    "region": "United States",
    "currency": "USD"
  }
]
```

---

### GET `/api/companies/{ticker}`
Get detailed company information

**Path Parameters:**
- `ticker`: Company ticker symbol (e.g., AAPL)

**Example:**
```bash
curl http://localhost:8000/api/companies/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc",
  "description": "...",
  "sector": "TECHNOLOGY",
  "industry": "CONSUMER ELECTRONICS",
  "market_cap": "4061369729000",
  "pe_ratio": "36.64",
  "eps": "7.47",
  "revenue_ttm": "416161006000",
  "profit_margin": "0.269",
  "dividend_yield": "0.0037",
  "fifty_two_week_high": "288.62",
  "fifty_two_week_low": "168.63"
}
```

---

### GET `/api/companies/{ticker}/earnings`
Get historical earnings reports

**Path Parameters:**
- `ticker`: Company ticker symbol

**Example:**
```bash
curl http://localhost:8000/api/companies/AAPL/earnings
```

**Response:**
```json
[
  {
    "id": "AAPL-Q3-2025",
    "ticker": "AAPL",
    "quarter": "Q3",
    "year": 2025,
    "date": "2025-10-30",
    "fiscal_date_ending": "2025-09-30",
    "reported_eps": "1.85",
    "estimated_eps": "1.76",
    "surprise": "0.09",
    "surprise_percentage": "5.1136",
    "status": "recorded"
  }
]
```

---

### GET `/api/companies/{ticker}/financials`
Get combined financial metrics

**Path Parameters:**
- `ticker`: Company ticker symbol

**Example:**
```bash
curl http://localhost:8000/api/companies/AAPL/financials
```

**Response:**
```json
{
  "ticker": "AAPL",
  "revenue": "416161006000",
  "revenue_change": null,
  "eps": "7.47",
  "eps_change": "+18.3%",
  "pe_ratio": 36.64,
  "market_cap": "4061369729000",
  "yoy_growth": "0.269",
  "guidance_vs_actual": "+5.1%"
}
```

---

### GET `/api/companies/calendar/upcoming`
Get upcoming earnings calendar

**Query Parameters:**
- `horizon` (optional): Time horizon (3month, 6month, 12month). Default: 3month

**Example:**
```bash
curl "http://localhost:8000/api/companies/calendar/upcoming?horizon=3month"
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc",
    "report_date": "2025-01-30",
    "fiscal_date_ending": "2024-12-31",
    "estimate": "2.15",
    "currency": "USD"
  }
]
```

---

## Transcripts

### GET `/api/transcript/{ticker}/{quarter}/{year}`
Get earnings call transcript

**Path Parameters:**
- `ticker`: Company ticker symbol
- `quarter`: Quarter (Q1, Q2, Q3, Q4)
- `year`: Year (e.g., 2024)

**Example:**
```bash
curl http://localhost:8000/api/transcript/AAPL/Q4/2024
```

**Response:**
```json
{
  "ticker": "AAPL",
  "quarter": "Q4",
  "year": 2024,
  "fiscal_date_ending": "2024-09-30",
  "transcript": "Full transcript text...",
  "entries": [
    {
      "id": "uuid",
      "timestamp": "00:00",
      "text": "Good afternoon...",
      "speaker": "Suhasini Chandramouli",
      "confidence": 1.0
    }
  ]
}
```

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**404 Not Found:**
```json
{
  "detail": "No data found for ticker INVALID"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error: detailed error message"
}
```

---

## Rate Limiting

Alpha Vantage API has rate limits:
- Free tier: 5 calls per minute, 500 calls per day
- Premium tier: Higher limits

The service automatically handles rate limiting with queuing.

---

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Testing

Run the test script:
```bash
./test_endpoints.sh
```

Or use the Python test:
```bash
python test_alpha_vantage.py
```
