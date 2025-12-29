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
    - Client sends: audio chunks as binary data
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
    audio_buffer = bytearray()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # Process when we have enough data (e.g., every 30KB ~= 2-3 seconds at 16kHz)
            if len(audio_buffer) >= 30000:
                try:
                    # Transcribe the accumulated audio (sync generator)
                    for segment in whisper_service.transcribe_stream(
                        bytes(audio_buffer),
                        language="en"
                    ):
                        # Send each segment back to client
                        await websocket.send_json({
                            "type": "segment",
                            "start": segment["start"],
                            "end": segment["end"],
                            "text": segment["text"]
                        })
                    
                    # Clear buffer after processing
                    audio_buffer.clear()
                    
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
    finally:
        # Process any remaining audio in buffer
        if len(audio_buffer) > 0:
            try:
                for segment in whisper_service.transcribe_stream(
                    bytes(audio_buffer),
                    language="en"
                ):
                    await websocket.send_json({
                        "type": "segment",
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"]
                    })
            except Exception as e:
                logger.error(f"Final transcription error: {e}")
