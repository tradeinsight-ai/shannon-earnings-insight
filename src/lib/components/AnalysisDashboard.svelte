<script lang="ts">
    import { Sparkles, ArrowRight } from "lucide-svelte";
    import { analysisStore } from "$lib/stores/analysis.svelte";
    import CategoryCard from "./CategoryCard.svelte";
    import SentimentChart from "./SentimentChart.svelte";

    function formatSentiment(sentiment: number): string {
        const percent = (sentiment * 100).toFixed(0);
        return sentiment >= 0 ? `+${percent}%` : `${percent}%`;
    }

    function getSentimentColor(sentiment: number): string {
        if (sentiment > 0.1) return "text-primary-500";
        if (sentiment < -0.1) return "text-error-500";
        return "text-gray-400";
    }
</script>

<div class="card flex flex-col h-full overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-800">
        <div class="flex items-center gap-2">
            <Sparkles class="w-4 h-4 text-warning-400" />
            <span class="text-sm font-medium text-gray-200">AI Analysis</span>
        </div>

        <!-- Overall Sentiment -->
        <div class="flex items-center gap-2">
            <span class="text-[10px] text-gray-500 uppercase tracking-wider"
                >Overall Sentiment</span
            >
            <div class="flex items-center gap-1">
                <span
                    class="text-lg font-mono font-bold {getSentimentColor(
                        analysisStore.overallSentiment,
                    )}"
                >
                    {formatSentiment(analysisStore.overallSentiment)}
                </span>
                <ArrowRight class="w-3 h-3 text-gray-500" />
            </div>
        </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <!-- Sentiment Chart -->
        <SentimentChart />

        <!-- Category Cards Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {#each analysisStore.categoryInsights as insight (insight.id)}
                <CategoryCard {insight} />
            {/each}
        </div>
    </div>
</div>
