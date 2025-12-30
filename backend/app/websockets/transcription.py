"""WebSocket endpoint for real-time audio transcription."""

import logging
from fastapi import WebSocket, WebSocketDisconnect
from app.services.local_whisper import get_whisper_service
from app.config import get_settings
import json

logger = logging.getLogger(__name__)
settings = get_settings()


async def handle_transcription_websocket(websocket: WebSocket):
    """
    Handle WebSocket connection for audio transcription.
    
    Protocol:
    - Client sends: JSON metadata with timeOffsetSeconds, then binary audio data
    - Server responds: JSON with transcription segments (timestamps adjusted by offset)
    
    Message format (client -> server):
    1. JSON: {"type": "metadata", "timeOffsetSeconds": 5.0}
    2. Binary: WebM audio blob
    
    Message format (server -> client):
    {
        "type": "segment",
        "start": 5.0,
        "end": 7.5,
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
    
    whisper_service = get_whisper_service(model_size=settings.whisper_model_size)
    time_offset = 0.0  # Default offset
    
    try:
        while True:
            # First, try to receive metadata (JSON)
            try:
                message = await websocket.receive_text()
                metadata = json.loads(message)
                if metadata.get("type") == "metadata":
                    time_offset = metadata.get("timeOffsetSeconds", 0.0)
                    logger.info(f"Received metadata: time_offset={time_offset}s")
                    # Now receive the audio data
                    audio_data = await websocket.receive_bytes()
                else:
                    logger.warning(f"Unexpected message type: {metadata.get('type')}")
                    continue
            except json.JSONDecodeError:
                # If not JSON, might be old protocol with just audio
                logger.warning("Received non-JSON message, assuming binary audio")
                audio_data = await websocket.receive_bytes()
                time_offset = 0.0
            
            # Skip if empty
            if len(audio_data) == 0:
                continue
            
            logger.info(f"Received audio blob: {len(audio_data)} bytes, offset: {time_offset}s")
            
            try:
                # Transcribe the audio blob with time offset
                segment_count = 0
                for segment in whisper_service.transcribe_stream(
                    audio_data,
                    language="en",
                    time_offset=time_offset
                ):
                    # Send each segment back to client (timestamps already adjusted)
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
