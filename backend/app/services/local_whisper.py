"""Local Whisper transcription service using faster-whisper."""

import logging
from pathlib import Path
from typing import Optional, Iterator
from faster_whisper import WhisperModel
import tempfile

logger = logging.getLogger(__name__)


class LocalWhisperService:
    """Service for local audio transcription using faster-whisper."""

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize the Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to run on (cpu, cuda)
            compute_type: Computation type (int8, int16, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None
        logger.info(f"LocalWhisperService initialized with model={model_size}, device={device}")

    def _ensure_model_loaded(self) -> WhisperModel:
        """Lazy load the model on first use."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded successfully")
        return self._model

    def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = None,
        beam_size: int = 5
    ) -> Iterator[dict]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en'), None for auto-detect
            beam_size: Beam size for decoding (higher = more accurate but slower)
            
        Yields:
            Segment dictionaries with 'start', 'end', 'text' keys
        """
        model = self._ensure_model_loaded()
        
        logger.info(f"Transcribing file: {audio_path}")
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        for segment in segments:
            yield {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }

    def transcribe_stream(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        beam_size: int = 5
    ) -> Iterator[dict]:
        """
        Transcribe audio from bytes (for WebSocket streaming).
        
        Args:
            audio_data: Raw audio bytes (WebM format from MediaRecorder)
            language: Language code (e.g., 'en'), None for auto-detect
            beam_size: Beam size for decoding
            
        Yields:
            Segment dictionaries with 'start', 'end', 'text' keys
        """
        # Write audio data to temporary file with correct extension
        # MediaRecorder sends WebM/Opus format, not WAV
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe the temporary file
            for segment in self.transcribe_file(tmp_path, language, beam_size):
                yield segment
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)


# Global instance
_whisper_service: Optional[LocalWhisperService] = None


def get_whisper_service() -> LocalWhisperService:
    """Get or create the global Whisper service instance."""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = LocalWhisperService()
    return _whisper_service
