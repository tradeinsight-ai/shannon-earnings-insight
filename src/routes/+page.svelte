<script lang="ts">
    import Header from "$lib/components/Header.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import FinancialContext from "$lib/components/FinancialContext.svelte";
    import AudioPlayer from "$lib/components/AudioPlayer.svelte";
    import TranscriptViewer from "$lib/components/TranscriptViewer.svelte";
    import AnalysisDashboard from "$lib/components/AnalysisDashboard.svelte";
    import { uiStore } from "$lib/stores/ui.svelte";
</script>

<div class="h-screen flex flex-col overflow-hidden">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar -->
        <Sidebar />

        <!-- Main Area -->
        <main
            class="flex-1 flex flex-col overflow-hidden bg-gray-950 p-4 gap-4"
        >
            <!-- Financial Context -->
            <FinancialContext />

            <!-- Audio Player (only for custom URL source) -->
            {#if uiStore.audioSource === 'custom'}
                <AudioPlayer />
            {/if}

            <!-- Bottom Section: Transcript + Analysis -->
            <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
                <!-- Transcript Viewer -->
                <TranscriptViewer />

                <!-- Analysis Dashboard -->
                <AnalysisDashboard />
            </div>
        </main>
    </div>
</div>
