<script lang="ts">
    import { TrendingUp } from "lucide-svelte";
    import { analysisStore } from "$lib/stores/analysis.svelte";

    // Chart dimensions
    const width = 400;
    const height = 120;
    const padding = { top: 10, right: 10, bottom: 20, left: 30 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Generate path from sentiment history
    const pathData = $derived.by(() => {
        const history = analysisStore.sentimentHistory;
        if (history.length < 2) return "";

        const xScale = chartWidth / (history.length - 1);
        const yScale = chartHeight / 2; // -1 to 1 range

        const points = history.map((point, i) => {
            const x = padding.left + i * xScale;
            const y =
                padding.top + chartHeight / 2 - point.overallSentiment * yScale;
            return `${x},${y}`;
        });

        return `M ${points.join(" L ")}`;
    });

    // Generate area path (filled area under the line)
    const areaPath = $derived.by(() => {
        const history = analysisStore.sentimentHistory;
        if (history.length < 2) return "";

        const xScale = chartWidth / (history.length - 1);
        const yScale = chartHeight / 2;
        const baseline = padding.top + chartHeight / 2;

        const points = history.map((point, i) => {
            const x = padding.left + i * xScale;
            const y =
                padding.top + chartHeight / 2 - point.overallSentiment * yScale;
            return { x, y };
        });

        let path = `M ${padding.left},${baseline}`;
        points.forEach((p) => {
            path += ` L ${p.x},${p.y}`;
        });
        path += ` L ${points[points.length - 1].x},${baseline} Z`;

        return path;
    });

    // Y-axis labels
    const yLabels = [
        { value: 1, label: "+100%" },
        { value: 0, label: "0%" },
        { value: -1, label: "-100%" },
    ];

    function formatTime(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        return `${mins}m`;
    }
</script>

<div class="bg-gray-800/30 rounded-lg p-3 border border-gray-700/50">
    <div
        class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider mb-3"
    >
        <TrendingUp class="w-3.5 h-3.5" />
        <span>Sentiment Over Time</span>
    </div>

    {#if analysisStore.sentimentHistory.length < 2}
        <div
            class="flex items-center justify-center h-24 text-gray-500 text-xs"
        >
            Sentiment data will appear as analysis progresses
        </div>
    {:else}
        <svg
            {width}
            {height}
            class="w-full h-auto"
            viewBox="0 0 {width} {height}"
        >
            <!-- Grid lines -->
            <line
                x1={padding.left}
                y1={padding.top + chartHeight / 2}
                x2={width - padding.right}
                y2={padding.top + chartHeight / 2}
                stroke="currentColor"
                class="text-gray-700"
                stroke-dasharray="4,4"
            />

            <!-- Y-axis labels -->
            {#each yLabels as { value, label }}
                <text
                    x={padding.left - 5}
                    y={padding.top +
                        chartHeight / 2 -
                        value * (chartHeight / 2) +
                        3}
                    class="text-[8px] fill-gray-500 text-right"
                    text-anchor="end"
                >
                    {label}
                </text>
            {/each}

            <!-- Gradient definition -->
            <defs>
                <linearGradient
                    id="sentimentGradient"
                    x1="0%"
                    y1="0%"
                    x2="0%"
                    y2="100%"
                >
                    <stop
                        offset="0%"
                        stop-color="rgb(45, 208, 149)"
                        stop-opacity="0.3"
                    />
                    <stop
                        offset="50%"
                        stop-color="rgb(45, 208, 149)"
                        stop-opacity="0.1"
                    />
                    <stop
                        offset="100%"
                        stop-color="rgb(45, 208, 149)"
                        stop-opacity="0"
                    />
                </linearGradient>
            </defs>

            <!-- Area fill -->
            <path d={areaPath} fill="url(#sentimentGradient)" />

            <!-- Line -->
            <path
                d={pathData}
                fill="none"
                stroke="rgb(45, 208, 149)"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
            />

            <!-- Data points -->
            {#each analysisStore.sentimentHistory as point, i}
                {@const xScale =
                    chartWidth / (analysisStore.sentimentHistory.length - 1)}
                {@const yScale = chartHeight / 2}
                {@const x = padding.left + i * xScale}
                {@const y =
                    padding.top +
                    chartHeight / 2 -
                    point.overallSentiment * yScale}
                <circle
                    cx={x}
                    cy={y}
                    r="3"
                    fill="rgb(45, 208, 149)"
                    class="hover:r-4 transition-all cursor-pointer"
                />
            {/each}
        </svg>
    {/if}
</div>
