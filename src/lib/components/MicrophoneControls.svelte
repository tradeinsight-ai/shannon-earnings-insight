<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { audioService } from '$lib/services/audio';
  import { createTranscriptionWebSocket, type TranscriptionSegment } from '$lib/services/transcriptionWebSocket';
  import { analysisStore } from '$lib/stores/analysis.svelte';
  import { Mic, MicOff, Square } from 'lucide-svelte';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  let isRecording = $state(false);
  let isInitialized = $state(false);
  let wsConnected = $state(false);
  let error = $state<string | null>(null);
  let statusMessage = $state('Ready to record');
  let transcriptCounter = 0;
  let chunkDurationMs = $state(5000); // Default, will be loaded from config
  
  const transcriptionWs = createTranscriptionWebSocket(API_URL);

  onMount(async () => {
    // Load transcription config from backend
    try {
      const response = await fetch(`${API_URL}/config/transcription`);
      if (response.ok) {
        const config = await response.json();
        chunkDurationMs = config.chunk_duration_ms;
        console.log(`[Config] Chunk duration: ${chunkDurationMs}ms, Model: ${config.whisper_model_size}`);
      }
    } catch (err) {
      console.warn('[Config] Failed to load config, using default:', err);
    }
    
    // Setup transcription WebSocket callbacks
    transcriptionWs.onSegment((segment: TranscriptionSegment) => {
      if (segment.type === 'segment' && segment.text) {
        // Add transcription to analysis store with sequential ID
        analysisStore.addTranscriptEntry({
          id: `mic-${++transcriptCounter}`,
          speaker: 'Microphone',
          text: segment.text,
          timestamp: `${segment.start?.toFixed(1)}s - ${segment.end?.toFixed(1)}s`
        });
        statusMessage = `Transcribed: ${segment.text.substring(0, 50)}...`;
      } else if (segment.type === 'error') {
        error = segment.message || 'Transcription error';
        stopRecording();
      }
    });

    transcriptionWs.onStateChange((state) => {
      wsConnected = state === 'connected';
      if (state === 'error') {
        error = 'WebSocket connection failed';
        stopRecording();
      }
    });
  });

  onDestroy(() => {
    isRecordingCycle = false;
    if (isRecording) {
      stopRecording();
    }
    audioService.dispose();
    transcriptionWs.disconnect();
  });

  async function initializeAudio() {
    try {
      statusMessage = 'Requesting microphone access...';
      await audioService.initialize();
      isInitialized = true;
      statusMessage = 'Microphone ready';
      error = null;
    } catch (err) {
      error = 'Failed to access microphone. Please grant permission.';
      console.error(err);
    }
  }

  let recordingCycleInterval: number | null = null;
  let isRecordingCycle = false;
  let cumulativeTimeSeconds = 0; // Track total recording time for timestamp offsets

  async function startRecording() {
    if (!isInitialized) {
      await initializeAudio();
      if (!isInitialized) return;
    }

    try {
      // Connect to WebSocket
      statusMessage = 'Connecting to transcription service...';
      await transcriptionWs.connect();
      
      isRecording = true;
      isRecordingCycle = true;
      cumulativeTimeSeconds = 0; // Reset cumulative time on new recording session
      error = null;
      
      // Start first recording cycle
      await startRecordingCycle();
      
    } catch (err) {
      error = 'Failed to start recording';
      console.error(err);
      isRecording = false;
      isRecordingCycle = false;
    }
  }

  async function startRecordingCycle() {
    while (isRecordingCycle) {
      try {
        console.log(`[RecordingCycle] Starting new ${chunkDurationMs}ms recording...`);
        statusMessage = 'Recording...';
        
        // Start recording (without chunk callback - we want the complete file)
        audioService.startRecording();
        
        // Stop after configured duration to get a complete, valid audio file
        await new Promise(resolve => setTimeout(resolve, chunkDurationMs));
        
        if (!isRecordingCycle) {
          console.log('[RecordingCycle] Cycle stopped by user');
          break;
        }
        
        console.log('[RecordingCycle] Stopping recording to get complete blob...');
        
        // Stop recording and get the complete audio blob
        const audioBlob = await audioService.stopRecording();
        
        console.log(`[RecordingCycle] Got blob: ${(audioBlob.size / 1024).toFixed(2)} KB`);
        
        // Send the complete audio file for transcription with time offset
        if (audioBlob.size > 0) {
          console.log(`[RecordingCycle] Sending audio to WebSocket with offset ${cumulativeTimeSeconds}s...`);
          transcriptionWs.sendAudio(audioBlob, cumulativeTimeSeconds);
          
          // Update cumulative time after sending
          cumulativeTimeSeconds += chunkDurationMs / 1000;
        } else {
          console.warn('[RecordingCycle] Empty audio blob, skipping send');
        }
        
        // Small delay before starting next cycle
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (err) {
        console.error('[RecordingCycle] Error in cycle:', err);
        error = 'Recording failed: ' + err.message;
        isRecording = false;
        isRecordingCycle = false;
        break;
      }
    }
    
    console.log('[RecordingCycle] Recording cycle ended');
  }

  async function stopRecording() {
    try {
      statusMessage = 'Stopping recording...';
      
      // Stop the recording cycle
      isRecordingCycle = false;
      
      // If currently recording, stop it
      if (audioService.getState() === 'recording') {
        try {
          const audioBlob = await audioService.stopRecording();
          // Send final audio if it has content
          if (audioBlob.size > 0) {
            transcriptionWs.sendAudio(audioBlob);
          }
        } catch (err) {
          console.log('Final audio collection error (expected):', err);
        }
      }
      
      // Small delay to let final audio send
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Disconnect WebSocket
      transcriptionWs.disconnect();
      
      isRecording = false;
      statusMessage = 'Recording stopped';
    } catch (err) {
      error = 'Failed to stop recording';
      console.error(err);
    }
  }

  function clearError() {
    error = null;
  }
</script>

<div class="card p-4">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold text-gray-100">Live Transcription</h3>
    <div class="flex items-center gap-2">
      {#if wsConnected}
        <span class="w-2 h-2 bg-primary-500 rounded-full"></span>
        <span class="text-sm text-gray-400">Connected</span>
      {:else}
        <span class="w-2 h-2 bg-gray-600 rounded-full"></span>
        <span class="text-sm text-gray-500">Disconnected</span>
      {/if}
    </div>
  </div>

  <div class="mb-4 p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg">
    <p class="text-sm text-gray-300">{statusMessage}</p>
  </div>

  {#if error}
    <div class="mb-4 p-3 bg-error-900/30 border border-error-700/50 rounded-lg flex items-start justify-between">
      <p class="text-sm text-error-400">{error}</p>
      <button onclick={clearError} class="text-error-500 hover:text-error-400">
        <Square class="w-4 h-4" />
      </button>
    </div>
  {/if}

  <div class="controls flex gap-3">
    {#if !isRecording}
      <button
        onclick={startRecording}
        class="btn btn-primary flex items-center gap-2 flex-1"
        disabled={isRecording}
      >
        <Mic class="w-5 h-5" />
        Start Recording
      </button>
    {:else}
      <button
        onclick={stopRecording}
        class="btn btn-danger flex items-center gap-2 flex-1"
      >
        <Square class="w-5 h-5" />
        Stop Recording
      </button>
    {/if}

    {#if isInitialized && !isRecording}
      <button
        onclick={() => audioService.dispose()}
        class="btn btn-secondary"
        title="Release microphone"
      >
        <MicOff class="w-5 h-5" />
      </button>
    {/if}
  </div>

  <div class="mt-4 text-xs text-gray-500">
    <p>Record audio from your microphone and see real-time transcription.</p>
    <p>Transcribed text will appear in the transcript viewer below.</p>
  </div>
</div>

<style>
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    font-weight: 500;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-danger {
    background: #ef4444;
    color: white;
  }

  .btn-danger:hover {
    background: #dc2626;
  }

  .btn-secondary {
    background: #6b7280;
    color: #e5e7eb;
  }

  .btn-secondary:hover {
    background: #4b5563;
  }
</style>
