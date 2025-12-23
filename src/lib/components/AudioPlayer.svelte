<script lang="ts">
    import {
        Play,
        Pause,
        RotateCcw,
        RotateCw,
        Volume2,
        VolumeX,
        Headphones,
    } from "lucide-svelte";
    import { companyStore } from "$lib/stores/company.svelte";
    import { analysisStore } from "$lib/stores/analysis.svelte";
    import { uiStore } from "$lib/stores/ui.svelte";

    let isPlaying = $state(false);
    let currentTime = $state(0);
    let duration = $state(0);
    let volume = $state(0.8);
    let isMuted = $state(false);
    let playbackSpeed = $state(1);
    let audioElement: HTMLAudioElement | null = $state(null);

    const playbackSpeeds = [0.5, 0.75, 1, 1.25, 1.5, 2];

    function formatTime(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }

    function togglePlay() {
        if (!audioElement) return;
        if (isPlaying) {
            audioElement.pause();
        } else {
            audioElement.play();
        }
        isPlaying = !isPlaying;
    }

    function seek(e: MouseEvent) {
        if (!audioElement || !duration) return;
        const target = e.currentTarget as HTMLElement;
        const rect = target.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        audioElement.currentTime = percent * duration;
    }

    function skip(seconds: number) {
        if (!audioElement) return;
        audioElement.currentTime = Math.max(
            0,
            Math.min(duration, audioElement.currentTime + seconds),
        );
    }

    function cycleSpeed() {
        const currentIndex = playbackSpeeds.indexOf(playbackSpeed);
        const nextIndex = (currentIndex + 1) % playbackSpeeds.length;
        playbackSpeed = playbackSpeeds[nextIndex];
        if (audioElement) {
            audioElement.playbackRate = playbackSpeed;
        }
    }

    function toggleMute() {
        isMuted = !isMuted;
        if (audioElement) {
            audioElement.muted = isMuted;
        }
    }

    function handleTimeUpdate() {
        if (audioElement) {
            currentTime = audioElement.currentTime;
            analysisStore.setCurrentTime(currentTime);
        }
    }

    function handleLoadedMetadata() {
        if (audioElement) {
            duration = audioElement.duration;
        }
    }

    const progressPercent = $derived(
        duration > 0 ? (currentTime / duration) * 100 : 0,
    );
    
    const currentAudioUrl = $derived(
        uiStore.audioSource === 'custom'
            ? companyStore.customAudioUrl
            : companyStore.selectedEarningsCall?.audioUrl
    );
    
    const hasAudio = $derived(
        currentAudioUrl !== undefined && currentAudioUrl !== ''
    );
</script>

<div class="card p-4">
    <div class="flex items-center justify-between mb-4">
        <div
            class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider"
        >
            <Headphones class="w-3.5 h-3.5" />
            <span>Audio Player</span>
        </div>
        <span class="text-xs text-gray-500 font-mono">
            {hasAudio
                ? `${companyStore.selectedEarningsCall?.quarter} ${companyStore.selectedEarningsCall?.year}`
                : "NO AUDIO LOADED"}
        </span>
    </div>

    {#if hasAudio}
        <audio
            bind:this={audioElement}
            src={currentAudioUrl}
            ontimeupdate={handleTimeUpdate}
            onloadedmetadata={handleLoadedMetadata}
            onended={() => (isPlaying = false)}
        ></audio>
    {/if}

    <!-- Controls -->
    <div class="flex flex-col items-center gap-4">
        <!-- Main Controls -->
        <div class="flex items-center gap-4">
            <button
                onclick={() => skip(-10)}
                disabled={!hasAudio}
                class="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                title="Back 10 seconds"
            >
                <RotateCcw class="w-5 h-5" />
            </button>

            <button
                onclick={togglePlay}
                disabled={!hasAudio}
                class="w-14 h-14 rounded-full flex items-center justify-center transition-all
          {hasAudio
                    ? 'bg-primary-600 hover:bg-primary-500 text-white glow-primary'
                    : 'bg-gray-800 text-gray-600 cursor-not-allowed'}"
            >
                {#if isPlaying}
                    <Pause class="w-6 h-6" />
                {:else}
                    <Play class="w-6 h-6 ml-1" />
                {/if}
            </button>

            <button
                onclick={() => skip(10)}
                disabled={!hasAudio}
                class="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                title="Forward 10 seconds"
            >
                <RotateCw class="w-5 h-5" />
            </button>
        </div>

        <!-- Progress Bar -->
        <div class="w-full flex items-center gap-3">
            <span class="text-xs font-mono text-gray-500 w-12 text-right"
                >{formatTime(currentTime)}</span
            >

            <button
                onclick={seek}
                disabled={!hasAudio}
                class="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden cursor-pointer group relative"
                aria-label="Seek in audio"
            >
                <div
                    class="h-full bg-primary-600 rounded-full transition-all"
                    style="width: {progressPercent}%"
                ></div>
                <div
                    class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-primary-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    style="left: calc({progressPercent}% - 6px)"
                ></div>
            </button>

            <span class="text-xs font-mono text-gray-500 w-12"
                >{formatTime(duration)}</span
            >
        </div>

        <!-- Secondary Controls -->
        <div class="flex items-center gap-4">
            <button
                onclick={cycleSpeed}
                disabled={!hasAudio}
                class="px-2 py-1 rounded text-xs font-mono text-gray-400 hover:text-gray-200 bg-gray-800 hover:bg-gray-700 transition-colors disabled:opacity-30"
            >
                {playbackSpeed}x
            </button>

            <button
                onclick={toggleMute}
                disabled={!hasAudio}
                class="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors disabled:opacity-30"
            >
                {#if isMuted}
                    <VolumeX class="w-4 h-4" />
                {:else}
                    <Volume2 class="w-4 h-4" />
                {/if}
            </button>
        </div>
    </div>
</div>
