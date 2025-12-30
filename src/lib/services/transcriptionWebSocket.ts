/**
 * WebSocket service specifically for audio transcription streaming.
 * Handles binary audio data and receives JSON transcription segments.
 */

export interface TranscriptionSegment {
  type: 'segment' | 'error';
  start?: number;
  end?: number;
  text?: string;
  message?: string;
}

export type TranscriptionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export class TranscriptionWebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private onSegmentCallback?: (segment: TranscriptionSegment) => void;
  private onStateChangeCallback?: (state: TranscriptionState) => void;
  private state: TranscriptionState = 'disconnected';

  constructor(url: string) {
    this.url = url;
  }

  /**
   * Connect to the transcription WebSocket server.
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.setState('connecting');
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[TranscriptionWS] Connected');
          this.setState('connected');
          resolve();
        };

        this.ws.onclose = () => {
          console.log('[TranscriptionWS] Disconnected');
          this.setState('disconnected');
        };

        this.ws.onerror = (error) => {
          console.error('[TranscriptionWS] Error:', error);
          this.setState('error');
          reject(error);
        };

        this.ws.onmessage = (event) => {
          try {
            const segment: TranscriptionSegment = JSON.parse(event.data);
            console.log('[TranscriptionWS] Received segment:', segment);
            this.onSegmentCallback?.(segment);
          } catch (error) {
            console.error('[TranscriptionWS] Failed to parse message:', error);
          }
        };
      } catch (error) {
        this.setState('error');
        reject(error);
      }
    });
  }

  /**
   * Send audio data to the server for transcription.
   * @param audioData Audio blob or array buffer
   * @param timeOffsetSeconds Cumulative time offset in seconds for timestamp adjustment
   */
  async sendAudio(audioData: Blob | ArrayBuffer, timeOffsetSeconds: number = 0): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[TranscriptionWS] Cannot send audio - not connected. State:', this.ws?.readyState);
      return;
    }

    const size = audioData instanceof Blob ? audioData.size : audioData.byteLength;
    console.log(`[TranscriptionWS] Sending audio: ${(size / 1024).toFixed(2)} KB with offset ${timeOffsetSeconds}s`);

    // Send metadata first
    const metadata = {
      type: 'metadata',
      timeOffsetSeconds: timeOffsetSeconds
    };
    this.ws.send(JSON.stringify(metadata));

    // Convert to ArrayBuffer if needed and send audio data
    if (audioData instanceof Blob) {
      const buffer = await audioData.arrayBuffer();
      console.log(`[TranscriptionWS] Converted blob to buffer: ${(buffer.byteLength / 1024).toFixed(2)} KB`);
      this.ws.send(buffer);
    } else {
      this.ws.send(audioData);
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected');
      this.ws = null;
    }
    this.setState('disconnected');
  }

  /**
   * Register callback for transcription segments.
   */
  onSegment(callback: (segment: TranscriptionSegment) => void): void {
    this.onSegmentCallback = callback;
  }

  /**
   * Register callback for connection state changes.
   */
  onStateChange(callback: (state: TranscriptionState) => void): void {
    this.onStateChangeCallback = callback;
  }

  /**
   * Get current connection state.
   */
  getState(): TranscriptionState {
    return this.state;
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.state === 'connected' && this.ws?.readyState === WebSocket.OPEN;
  }

  private setState(state: TranscriptionState): void {
    this.state = state;
    this.onStateChangeCallback?.(state);
  }
}

/**
 * Create a transcription WebSocket instance.
 * @param backendUrl Base URL of the backend (e.g., 'http://localhost:8000')
 */
export function createTranscriptionWebSocket(backendUrl: string): TranscriptionWebSocketService {
  // Convert http(s) to ws(s)
  const wsUrl = backendUrl.replace(/^http/, 'ws') + '/ws/transcribe';
  return new TranscriptionWebSocketService(wsUrl);
}
