<script lang="ts">
    import {
        Quote,
        TrendingUp,
        Compass,
        Target,
        AlertTriangle,
        MessageCircle,
        ChevronDown,
        ChevronUp,
    } from "lucide-svelte";
    import type { CategoryInsight, AnalysisCategory } from "$lib/types";
    import { CATEGORY_LABELS } from "$lib/types";

    interface Props {
        insight: CategoryInsight;
    }

    let { insight }: Props = $props();
    let isExpanded = $state(false);

    const categoryIcons: Record<AnalysisCategory, typeof Quote> = {
        key_statements: Quote,
        financial_performance: TrendingUp,
        forward_guidance: Compass,
        market_position: Target,
        risk_factors: AlertTriangle,
        analyst_qa: MessageCircle,
    };

    function getSentimentColor(sentiment: number): string {
        if (sentiment > 0.3) return "text-primary-500";
        if (sentiment < -0.3) return "text-error-500";
        return "text-gray-400";
    }

    function getSentimentBg(sentiment: number): string {
        if (sentiment > 0.3) return "bg-primary-900/50 border-primary-700/50";
        if (sentiment < -0.3) return "bg-error-900/50 border-error-700/50";
        return "bg-gray-800/50 border-gray-700/50";
    }

    function formatSentiment(sentiment: number): string {
        const percent = (sentiment * 100).toFixed(0);
        return sentiment >= 0 ? `+${percent}%` : `${percent}%`;
    }

    const IconComponent = $derived(categoryIcons[insight.category]);
    const label = $derived(CATEGORY_LABELS[insight.category]);
</script>

<div
    class="rounded-lg border {getSentimentBg(
        insight.sentiment,
    )} overflow-hidden"
>
    <!-- Header -->
    <button
        onclick={() => (isExpanded = !isExpanded)}
        class="w-full p-3 flex items-center justify-between hover:bg-gray-800/30 transition-colors"
    >
        <div class="flex items-center gap-2">
            <IconComponent class="w-4 h-4 text-gray-400" />
            <span class="text-sm font-medium text-gray-200">{label}</span>
            {#if insight.insights.length > 0}
                <span
                    class="text-[10px] bg-gray-700 text-gray-400 px-1.5 py-0.5 rounded"
                >
                    {insight.insights.length}
                </span>
            {/if}
        </div>

        <div class="flex items-center gap-2">
            <span
                class="text-sm font-mono font-bold {getSentimentColor(
                    insight.sentiment,
                )}"
            >
                {formatSentiment(insight.sentiment)}
            </span>
            {#if isExpanded}
                <ChevronUp class="w-4 h-4 text-gray-500" />
            {:else}
                <ChevronDown class="w-4 h-4 text-gray-500" />
            {/if}
        </div>
    </button>

    <!-- Expanded Content -->
    {#if isExpanded}
        <div
            class="border-t border-gray-700/50 p-3 space-y-2 max-h-48 overflow-y-auto"
        >
            {#if insight.insights.length === 0}
                <p class="text-xs text-gray-500 italic">No insights yet</p>
            {:else}
                {#each insight.insights as item (item.id)}
                    <div class="flex items-start gap-2">
                        <span
                            class="text-[10px] font-mono text-primary-600 bg-primary-900/30 px-1 py-0.5 rounded shrink-0"
                        >
                            {item.timestamp}
                        </span>
                        <p class="text-xs text-gray-300 leading-relaxed">
                            {item.text}
                        </p>
                    </div>
                {/each}
            {/if}
        </div>
    {/if}
</div>
