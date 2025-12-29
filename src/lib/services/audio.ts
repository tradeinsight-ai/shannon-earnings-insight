/**
 * Audio recording service for microphone transcription.
 * Handles MediaRecorder API for capturing audio from user's microphone.
 */

export interface AudioConfig {
  sampleRate: number;
  channelCount: number;
  mimeType: string;
}

export type RecordingState = 'inactive' | 'recording' | 'paused';

export class AudioRecordingService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;
  
  readonly config: AudioConfig = {
    sampleRate: 16000, // Whisper prefers 16kHz
    channelCount: 1,   // Mono audio
    mimeType: 'audio/webm;codecs=opus' // Fallback to 'audio/webm' if not supported
  };

  /**
   * Request microphone permission and initialize audio stream.
   */
  async initialize(): Promise<void> {
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channelCount,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // Check for supported mime types
      const preferredTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/mp4'
      ];

      for (const type of preferredTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          this.config.mimeType = type;
          break;
        }
      }

      console.log('Audio service initialized with config:', this.config);
    } catch (error) {
      console.error('Failed to initialize audio:', error);
      throw new Error('Microphone access denied or not available');
    }
  }

  /**
   * Start recording audio.
   * @param onDataAvailable Callback for when audio chunks are available
   */
  startRecording(onDataAvailable?: (chunk: Blob) => void): void {
    if (!this.stream) {
      throw new Error('Audio service not initialized. Call initialize() first.');
    }

    if (this.mediaRecorder?.state === 'recording') {
      console.warn('[AudioService] Already recording');
      return;
    }

    // Clean up any previous recorder
    if (this.mediaRecorder) {
      console.log('[AudioService] Cleaning up previous MediaRecorder');
      this.mediaRecorder = null;
    }

    this.audioChunks = [];

    try {
      console.log('[AudioService] Creating new MediaRecorder');
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: this.config.mimeType
      });

      // Collect audio chunks
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
          onDataAvailable?.(event.data);
        }
      };

      // Start recording with 1-second chunks
      this.mediaRecorder.start(1000);
      console.log('[AudioService] Recording started');
    } catch (error) {
      console.error('[AudioService] Failed to start recording:', error);
      throw new Error('Failed to start audio recording');
    }
  }

  /**
   * Stop recording and return the complete audio blob.
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No active recording'));
        return;
      }

      if (this.mediaRecorder.state === 'inactive') {
        reject(new Error('Recording already stopped'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: this.config.mimeType });
        console.log(`[AudioService] Recording stopped. Size: ${(audioBlob.size / 1024).toFixed(2)} KB`);
        
        // Clean up the mediaRecorder for next cycle
        this.mediaRecorder = null;
        
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Pause the current recording.
   */
  pauseRecording(): void {
    if (this.mediaRecorder?.state === 'recording') {
      this.mediaRecorder.pause();
      console.log('Recording paused');
    }
  }

  /**
   * Resume a paused recording.
   */
  resumeRecording(): void {
    if (this.mediaRecorder?.state === 'paused') {
      this.mediaRecorder.resume();
      console.log('Recording resumed');
    }
  }

  /**
   * Get current recording state.
   */
  getState(): RecordingState {
    return (this.mediaRecorder?.state as RecordingState) || 'inactive';
  }

  /**
   * Clean up resources and release microphone.
   */
  dispose(): void {
    if (this.mediaRecorder?.state === 'recording') {
      this.mediaRecorder.stop();
    }

    this.stream?.getTracks().forEach(track => track.stop());
    this.stream = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    console.log('Audio service disposed');
  }

  /**
   * Convert audio blob to WAV format for Whisper.
   * Note: This is a simplified conversion. For production, consider using a library like audiobuffer-to-wav.
   */
  async convertToWav(blob: Blob): Promise<Blob> {
    // For now, return the original blob
    // Faster-whisper can handle WebM/Opus directly via FFmpeg
    return blob;
  }
}

// Export a singleton instance
export const audioService = new AudioRecordingService();
