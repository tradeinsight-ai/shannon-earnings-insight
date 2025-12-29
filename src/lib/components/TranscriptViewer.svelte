<script lang="ts">
    import { FileText, Search, ScrollText } from "lucide-svelte";
    import { analysisStore } from "$lib/stores/analysis.svelte";

    let searchQuery = $state("");
    let transcriptContainer: HTMLElement | null = $state(null);
    let autoScroll = $state(true);

    // Filter transcript based on search
    const filteredTranscript = $derived.by(() => {
        if (!searchQuery) return analysisStore.transcript;
        const query = searchQuery.toLowerCase();
        return analysisStore.transcript.filter(
            (entry) =>
                entry.text.toLowerCase().includes(query) ||
                entry.speaker?.toLowerCase().includes(query),
        );
    });

    // Auto-scroll when new entries arrive
    $effect(() => {
        if (
            autoScroll &&
            transcriptContainer &&
            analysisStore.transcript.length > 0
        ) {
            transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
        }
    });

    function handleScroll() {
        if (!transcriptContainer) return;
        const { scrollTop, scrollHeight, clientHeight } = transcriptContainer;
        // Disable auto-scroll if user scrolls up
        autoScroll = scrollTop + clientHeight >= scrollHeight - 50;
    }

    function formatTimestamp(timestamp: string): string {
        return timestamp;
    }
</script>

<div class="card flex flex-col h-full overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-800 shrink-0">
        <div
            class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider"
        >
            <FileText class="w-3.5 h-3.5" />
            <span>Transcript</span>
        </div>

        <!-- Search -->
        <div class="relative">
            <Search
                class="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-1/2 -translate-y-1/2"
            />
            <input
                type="text"
                placeholder="Search..."
                class="input py-1 pl-8 pr-3 text-xs w-40"
                bind:value={searchQuery}
            />
        </div>
    </div>

    <!-- Transcript Content -->
    <div
        bind:this={transcriptContainer}
        onscroll={handleScroll}
        class="flex-1 overflow-y-auto p-4 min-h-0"
    >
        {#if analysisStore.transcript.length === 0}
            <div
                class="flex flex-col items-center justify-center h-full text-gray-500"
            >
                <ScrollText class="w-10 h-10 mb-3 opacity-30" />
                <p class="text-sm font-medium">Transcript will appear here</p>
                <p class="text-xs text-gray-600 mt-1">
                    Start analysis to begin transcription
                </p>
            </div>
        {:else}
            <div class="space-y-3">
                {#each filteredTranscript as entry (entry.id)}
                    <div class="group">
                        <div class="flex items-start gap-3">
                            <span
                                class="text-[10px] font-mono text-primary-600 bg-primary-900/30 px-1.5 py-0.5 rounded shrink-0 mt-0.5"
                            >
                                {formatTimestamp(entry.timestamp)}
                            </span>
                            <div class="flex-1">
                                {#if entry.speaker}
                                    <span
                                        class="text-xs font-medium text-gray-400 block mb-0.5"
                                    >
                                        {entry.speaker}
                                    </span>
                                {/if}
                                <p
                                    class="text-sm text-gray-200 leading-relaxed"
                                >
                                    {entry.text}
                                </p>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <!-- Auto-scroll indicator -->
    {#if !autoScroll && analysisStore.transcript.length > 0}
        <button
            onclick={() => {
                autoScroll = true;
                if (transcriptContainer) {
                    transcriptContainer.scrollTop =
                        transcriptContainer.scrollHeight;
                }
            }}
            class="absolute bottom-4 right-4 px-3 py-1.5 bg-primary-600 text-white text-xs rounded-full shadow-lg hover:bg-primary-500 transition-colors"
        >
            Resume auto-scroll
        </button>
    {/if}
</div>
