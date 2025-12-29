"""WebSocket endpoint for real-time audio transcription."""

import logging
from fastapi import WebSocket, WebSocketDisconnect
from app.services.local_whisper import get_whisper_service
import json

logger = logging.getLogger(__name__)


async def handle_transcription_websocket(websocket: WebSocket):
    """
    Handle WebSocket connection for audio transcription.
    
    Protocol:
    - Client sends: complete WebM audio blobs (accumulated 3-second chunks)
    - Server responds: JSON with transcription segments
    
    Message format (server -> client):
    {
        "type": "segment",
        "start": 0.0,
        "end": 2.5,
        "text": "Transcribed text"
    }
    OR
    {
        "type": "error",
        "message": "Error description"
    }
    """
    await websocket.accept()
    logger.info("Transcription WebSocket connected")
    
    whisper_service = get_whisper_service()
    
    try:
        while True:
            # Receive complete audio blob from client
            audio_data = await websocket.receive_bytes()
            
            # Skip if empty
            if len(audio_data) == 0:
                continue
            
            logger.info(f"Received audio blob: {len(audio_data)} bytes")
            
            try:
                # Transcribe the audio blob (each blob is a complete WebM file)
                segment_count = 0
                for segment in whisper_service.transcribe_stream(
                    audio_data,
                    language="en"
                ):
                    # Send each segment back to client
                    await websocket.send_json({
                        "type": "segment",
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"]
                    })
                    segment_count += 1
                
                logger.info(f"Transcribed {segment_count} segments")
                
            except Exception as e:
                logger.error(f"Transcription error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                    
    except WebSocketDisconnect:
        logger.info("Transcription WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
