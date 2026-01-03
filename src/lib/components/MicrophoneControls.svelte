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
    disposeAudio();
    transcriptionWs.disconnect();
  });

  async function initializeAudio() {
    try {
      statusMessage = 'Requesting microphone access...';
      await audioService.initialize();
      isInitialized = true;
      error = null;
    } catch (err) {
      error = 'Failed to access microphone. Please grant permission.';
      console.error(err);
    }
  }

  function disposeAudio() {
    audioService.dispose();
    isInitialized = false;
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
    <div
      class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider"
    >
      <Mic class="w-3.5 h-3.5" />
      <span>Microphone</span>
    </div>
    <span class="text-xs text-gray-500 font-mono">
      {#if isRecording}
        RECORDING
      {:else if wsConnected}
        CONNECTED
      {:else}
        READY
      {/if}
    </span>
  </div>

  {#if error}
    <div class="mb-4 p-3 bg-error-900/30 border border-error-700/50 rounded-lg flex items-start justify-between">
      <p class="text-sm text-error-400">{error}</p>
      <button onclick={clearError} class="text-error-500 hover:text-error-400">
        <Square class="w-4 h-4" />
      </button>
    </div>
  {/if}

  <!-- Controls -->
  <div class="flex flex-col items-center gap-4">
    <div class="flex items-center gap-4">
      {#if !isRecording}
        <button
          onclick={startRecording}
          class="w-14 h-14 rounded-full flex items-center justify-center transition-all bg-primary-600 hover:bg-primary-500 text-white glow-primary"
        >
          <Mic class="w-6 h-6" />
        </button>
      {:else}
        <button
          onclick={stopRecording}
          class="w-14 h-14 rounded-full flex items-center justify-center transition-all bg-error-600 hover:bg-error-500 text-white"
        >
          <Square class="w-6 h-6" />
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .glow-primary {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  }
</style>
