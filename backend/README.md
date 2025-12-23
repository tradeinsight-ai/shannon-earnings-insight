# earningsInsight Backend

FastAPI backend for AI-powered earnings call analysis.

## Setup

1. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the server**
```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Test the API**
```bash
# Health check
curl http://localhost:8000/health

# API docs (Swagger UI)
open http://localhost:8000/docs
```

## API Endpoints

### Health
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Companies (Coming soon)
- `GET /api/companies/search?q={query}` - Search companies
- `GET /api/companies/{ticker}` - Get company details
- `GET /api/companies/{ticker}/financials` - Get financial data
- `GET /api/companies/{ticker}/earnings` - Get earnings history

### Transcripts (Coming soon)
- `GET /api/transcript/{ticker}/{quarter}` - Get earnings call transcript

### Analysis (Coming soon)
- `POST /api/analysis/start` - Start AI analysis
- `GET /api/analysis/{session_id}/status` - Get analysis status
- `WS /ws/analysis/{session_id}` - WebSocket for real-time updates

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration and settings
│   ├── models/              # Pydantic data models
│   ├── services/            # Business logic
│   │   ├── alpha_vantage.py # Alpha Vantage API client
│   │   └── ai_analysis.py   # AI analysis service
│   ├── routes/              # API endpoints
│   │   ├── companies.py
│   │   ├── transcripts.py
│   │   └── analysis.py
│   └── websockets/          # WebSocket handlers
│       └── analysis_stream.py
├── requirements.txt
├── .env.example
└── README.md
```

## Development

- FastAPI auto-generates API documentation at `/docs` (Swagger UI)
- Alternative docs at `/redoc` (ReDoc)
- Debug mode enables auto-reload on code changes

## Environment Variables

See `.env.example` for required configuration.
