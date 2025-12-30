from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="earningsInsight API",
    description="Backend API for AI-powered earnings call analysis",
    version="0.1.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "earningsInsight API is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "alpha_vantage": "configured" if settings.alpha_vantage_api_key else "missing",
        "transcription": "local (faster-whisper)"
    }


@app.get("/config/transcription")
async def get_transcription_config():
    """Get transcription configuration"""
    return {
        "whisper_model_size": settings.whisper_model_size,
        "chunk_duration_ms": settings.whisper_chunk_duration_ms
    }


# Import and register routes
from app.routes import companies, transcripts
from app.websockets.transcription import handle_transcription_websocket
from fastapi import WebSocket

app.include_router(companies.router)
app.include_router(transcripts.router)


# WebSocket endpoint
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time audio transcription"""
    await handle_transcription_websocket(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
