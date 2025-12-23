<script lang="ts">
    import {
        DollarSign,
        TrendingUp,
        BarChart3,
        Building,
        Percent,
        Target,
        Activity,
        AlertCircle,
    } from "lucide-svelte";
    import { companyStore } from "$lib/stores/company.svelte";
    import { formatMoneyShort, formatPercent } from "$lib/utils/formatters";

    interface FinancialCard {
        label: string;
        value: string;
        change?: string;
        icon: typeof DollarSign;
    }

    const financialCards: FinancialCard[] = $derived.by(() => {
        const f = companyStore.financials;
        if (!f) return [];

        return [
            {
                label: "Revenue",
                value: f.revenue ? formatMoneyShort(f.revenue) : "N/A",
                change: f.revenueChange,
                icon: DollarSign,
            },
            {
                label: "EPS",
                value: f.eps ? `$${f.eps}` : "N/A",
                change: f.epsChange,
                icon: TrendingUp,
            },
            {
                label: "P/E Ratio",
                value: f.pe ? f.pe.toFixed(2) : "N/A",
                icon: BarChart3,
            },
            { 
                label: "Market Cap", 
                value: f.marketCap ? formatMoneyShort(f.marketCap) : "N/A",
                icon: Building 
            },
            { 
                label: "YoY Growth", 
                value: f.yoyGrowth || "N/A",
                icon: Percent 
            },
            {
                label: "Guidance vs Actual",
                value: f.guidanceVsActual || "N/A",
                icon: Target,
            },
        ];
    });

    function getChangeColor(change?: string): string {
        if (!change) return "text-gray-400";
        if (change.startsWith("+")) return "text-primary-500";
        if (change.startsWith("-")) return "text-error-500";
        return "text-gray-400";
    }
</script>

<div class="card p-4">
    {#if companyStore.isLoadingFinancials}
        <div
            class="flex flex-col items-center justify-center py-8 text-gray-500"
        >
            <Activity class="w-8 h-8 mb-3 opacity-50 animate-pulse" />
            <p class="text-sm">Loading financial data...</p>
        </div>
    {:else if companyStore.loadingError}
        <div
            class="flex flex-col items-center justify-center py-8 text-amber-500/70"
        >
            <AlertCircle class="w-8 h-8 mb-3 opacity-50" />
            <p class="text-sm text-center px-4">{companyStore.loadingError}</p>
        </div>
    {:else if companyStore.selectedCompany && companyStore.financials}
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {#each financialCards as card}
                {@const IconComponent = card.icon}
                <div
                    class="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50"
                >
                    <div class="flex items-center gap-1.5 mb-2">
                        <IconComponent class="w-3.5 h-3.5 text-gray-500" />
                        <span
                            class="text-[10px] text-gray-500 uppercase tracking-wider"
                            >{card.label}</span
                        >
                    </div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-lg font-bold font-mono text-gray-100"
                            >{card.value}</span
                        >
                        {#if card.change}
                            <span
                                class="text-xs font-mono {getChangeColor(
                                    card.change,
                                )}">{card.change}</span
                            >
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    {:else}
        <div
            class="flex flex-col items-center justify-center py-8 text-gray-500"
        >
            <Activity class="w-8 h-8 mb-3 opacity-50" />
            <p class="text-sm">Select a company to view financials</p>
        </div>
    {/if}
</div>
