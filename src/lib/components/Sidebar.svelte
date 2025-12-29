<script lang="ts">
    import {
        Building2,
        Radio,
        Mic,
        Play,
        Square,
        ChevronDown,
        Search,
        ChevronLeft,
        Link,
    } from "lucide-svelte";
    import { uiStore } from "$lib/stores/ui.svelte";
    import { companyStore } from "$lib/stores/company.svelte";
    import { analysisStore } from "$lib/stores/analysis.svelte";
    import { formatDateShort } from "$lib/utils/formatters";

    let searchInput = $state("");
    let showCompanyDropdown = $state(false);
    let showEarningsDropdown = $state(false);
    let customUrlInput = $state("");

    let searchTimeout: number | null = null;

    function handleSearch(e: Event) {
        const target = e.target as HTMLInputElement;
        searchInput = target.value;
        companyStore.setSearchQuery(target.value);
        
        // Only show dropdown if user has typed at least 2 characters
        if (target.value.length >= 2) {
            showCompanyDropdown = true;
        } else {
            showCompanyDropdown = false;
        }
        
        // Debounce API search
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        if (target.value.length >= 2) {
            searchTimeout = setTimeout(() => {
                companyStore.searchCompaniesAPI(target.value);
            }, 500);
        }
    }

    function selectCompany(ticker: string) {
        companyStore.selectCompany(ticker);
        searchInput = ticker; // Keep ticker in search bar
        showCompanyDropdown = false;
    }

    function handleSearchKeydown(e: KeyboardEvent) {
        if (e.key === "Enter" && companyStore.searchResults.length > 0) {
            e.preventDefault();
            // Select first result
            selectCompany(companyStore.searchResults[0].ticker);
        } else if (e.key === "Escape") {
            // Close dropdown and clear search
            showCompanyDropdown = false;
        }
    }

    function handleStartAnalysis() {
        if (analysisStore.isAnalyzing) {
            analysisStore.stopAnalysis();
            uiStore.addNotification({
                type: "info",
                message: "Analysis stopped",
                duration: 2000,
            });
        } else {
            analysisStore.startAnalysis();
            uiStore.addNotification({
                type: "success",
                message: "Analysis started",
                duration: 2000,
            });
        }
    }
</script>

<aside class="w-56 bg-transparent flex flex-col h-full">
    <!-- Company Section -->
    <div class="p-4 border-b border-gray-800/30">
        <div
            class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider mb-3"
        >
            <Building2 class="w-3.5 h-3.5" />
            <span>Company</span>
        </div>

        <!-- Ticker Search -->
        <div class="mb-3">
            <label
                for="ticker-search"
                class="text-[10px] text-gray-500 uppercase tracking-wider mb-1 block"
            >
                Ticker Symbol
            </label>
            <div class="relative">
                <Search
                    class="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                    id="ticker-search"
                    type="search"
                    placeholder="Search..."
                    spellcheck="false"
                    autocorrect="off"
                    autocomplete="off"
                    autocapitalize="off"
                    class="input w-full pl-10 pr-3 py-2 text-sm"
                    value={searchInput}
                    oninput={handleSearch}
                    onkeydown={handleSearchKeydown}
                    onfocus={(e) => (e.target as HTMLInputElement).select()}
                    onclick={(e) => e.stopPropagation()}
                />

                {#if showCompanyDropdown && searchInput.length >= 2}
                    <div
                        role="listbox"
                        tabindex="-1"
                        aria-label="Company search results"
                        class="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-48 overflow-y-auto"
                        onclick={(e) => e.stopPropagation()}
                        onkeydown={(e) => e.stopPropagation()}
                    >
                        {#if companyStore.isLoadingCompanies}
                            <div class="px-3 py-4 text-center text-sm text-gray-400">
                                <div class="animate-pulse">Searching...</div>
                            </div>
                        {:else if companyStore.searchResults.length === 0}
                            <div class="px-3 py-4 text-center text-sm text-gray-400">
                                No companies found
                            </div>
                        {:else}
                            {#each companyStore.searchResults as company}
                                <button
                                    type="button"
                                    role="option"
                                    aria-selected={companyStore.selectedTicker === company.ticker}
                                    class="w-full px-3 py-2 text-left hover:bg-gray-700 flex items-center justify-between transition-colors"
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        selectCompany(company.ticker);
                                    }}
                                >
                                    <span class="font-mono text-sm text-gray-100"
                                        >{company.ticker}</span
                                    >
                                    <span class="text-xs text-gray-500 truncate max-w-37.5"
                                        >{company.name}</span
                                    >
                                </button>
                            {/each}
                        {/if}
                    </div>
                {/if}
            </div>
        </div>

        <!-- Earnings Call Dropdown -->
        <div>
            <label
                for="earnings-call-button"
                class="text-[10px] text-gray-500 uppercase tracking-wider mb-1 block"
            >
                Earnings Call
            </label>
            <div class="relative">
                <button
                    id="earnings-call-button"
                    type="button"
                    class="input w-full pl-3 pr-3 py-2 text-sm text-left flex items-center justify-between gap-2 transition-colors
                        {!companyStore.selectedCompany || companyStore.selectedCompany.earningsCalls.length === 0
                        ? 'cursor-not-allowed opacity-60'
                        : 'cursor-pointer hover:bg-gray-700/50'}"
                    disabled={!companyStore.selectedCompany || companyStore.selectedCompany.earningsCalls.length === 0}
                    onclick={(e) => {
                        e.stopPropagation();
                        if (companyStore.selectedCompany && companyStore.selectedCompany.earningsCalls.length > 0) {
                            showEarningsDropdown = !showEarningsDropdown;
                        }
                    }}
                >
                    <span class="truncate">
                        {#if !companyStore.selectedCompany}
                            QX YYYY
                        {:else if companyStore.selectedCompany.earningsCalls.length === 0}
                            N/A
                        {:else if companyStore.selectedEarningsCall}
                            {companyStore.selectedEarningsCall.quarter} {companyStore.selectedEarningsCall.year}
                        {:else}
                            Select call
                        {/if}
                    </span>
                    <ChevronDown
                        class="w-4 h-4 text-gray-500 shrink-0 transition-transform {showEarningsDropdown ? 'rotate-180' : ''}"
                    />
                </button>

                {#if showEarningsDropdown && companyStore.selectedCompany && companyStore.selectedCompany.earningsCalls.length > 0}
                    <div
                        role="listbox"
                        tabindex="-1"
                        aria-label="Earnings calls list"
                        class="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-48 overflow-y-auto"
                        onclick={(e) => e.stopPropagation()}
                        onkeydown={(e) => e.stopPropagation()}
                    >
                        {#each companyStore.selectedCompany.earningsCalls as call}
                            <button
                                type="button"
                                role="option"
                                aria-selected={call.id === companyStore.selectedEarningsCall?.id}
                                class="w-full px-3 py-2 text-left hover:bg-gray-700 transition-colors
                                    {call.id === companyStore.selectedEarningsCall?.id ? 'bg-gray-700/70' : ''}"
                                onclick={(e) => {
                                    e.stopPropagation();
                                    companyStore.selectEarningsCall(call.id);
                                    showEarningsDropdown = false;
                                }}
                            >
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-100">
                                        {call.quarter} {call.year}
                                    </span>
                                    <span class="text-xs text-gray-500">
                                        {formatDateShort(call.date)}
                                    </span>
                                </div>
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <!-- Source Section -->
    <div class="p-4 border-b border-gray-800/30">
        <div
            class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider mb-3"
        >
            <Radio class="w-3.5 h-3.5" />
            <span>Source</span>
        </div>

        <div class="grid grid-cols-3 rounded-lg overflow-hidden border border-gray-700 mb-3">
            <button
                type="button"
                class="py-2 px-2 text-xs font-medium flex items-center justify-center gap-1 transition-colors
          {uiStore.audioSource === 'recordings'
                    ? 'bg-primary-900 text-primary-400 border-r border-primary-700'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border-r border-gray-700'}"
                onclick={() => uiStore.setAudioSource("recordings")}
            >
                <Radio class="w-3.5 h-3.5" />
                <span>Rec</span>
            </button>
            <button
                type="button"
                class="py-2 px-2 text-xs font-medium flex items-center justify-center gap-1 transition-colors
          {uiStore.audioSource === 'microphone'
                    ? 'bg-primary-900 text-primary-400 border-r border-primary-700'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border-r border-gray-700'}"
                onclick={() => uiStore.setAudioSource("microphone")}
            >
                <Mic class="w-3.5 h-3.5" />
                <span>Mic</span>
            </button>
            <button
                type="button"
                class="py-2 px-2 text-xs font-medium flex items-center justify-center gap-1 transition-colors
          {uiStore.audioSource === 'custom'
                    ? 'bg-primary-900 text-primary-400'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
                onclick={() => uiStore.setAudioSource("custom")}
            >
                <Link class="w-3.5 h-3.5" />
                <span>URL</span>
            </button>
        </div>

        {#if uiStore.audioSource === 'custom'}
            <div>
                <label
                    for="custom-audio-url"
                    class="text-[10px] text-gray-500 uppercase tracking-wider mb-1 block"
                >
                    Audio URL
                </label>
                <input
                    id="custom-audio-url"
                    type="url"
                    placeholder="https://example.com/audio.mp3"
                    class="input w-full px-3 py-2 text-xs"
                    value={customUrlInput}
                    oninput={(e) => {
                        customUrlInput = (e.target as HTMLInputElement).value;
                        companyStore.setCustomAudioUrl(customUrlInput);
                    }}
                />
            </div>
        {/if}
    </div>

    <!-- Selected Companies -->
    <div class="flex-1 overflow-y-auto">
        {#if companyStore.companies.length === 0}
            <div class="flex flex-col items-center justify-center h-full text-gray-500 p-4">
                <Search class="w-8 h-8 mb-2 opacity-30" />
                <p class="text-xs text-center">Search for a company to get started</p>
            </div>
        {:else}
            {#each companyStore.companies as company}
                {@const isSelectedCompany = companyStore.selectedTicker === company.ticker}
                {@const displayCall = isSelectedCompany && companyStore.selectedEarningsCall
                    ? companyStore.selectedEarningsCall
                    : company.earningsCalls[0]}
                {#if displayCall}
                    <button
                        type="button"
                        class="w-full p-3 text-left border-b border-gray-800/30 hover:bg-gray-800/50 transition-colors
                {companyStore.selectedEarningsCall?.id === displayCall.id
                            ? 'bg-gray-800/70'
                            : ''}"
                        onclick={() => {
                            companyStore.selectCompany(company.ticker);
                            companyStore.selectEarningsCall(displayCall.id);
                        }}
                    >
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-mono font-bold text-sm text-gray-100"
                                >{company.ticker}</span
                            >
                            <span class="badge badge-primary text-[10px]"
                                >{displayCall.quarter} {displayCall.year}</span
                            >
                        </div>
                        <div class="text-xs text-gray-500">
                            <span>{formatDateShort(displayCall.date)}</span>
                        </div>
                    </button>
                {/if}
            {/each}
        {/if}
    </div>

    <!-- Analysis Section -->
    <div class="p-4 border-t border-gray-800/30">
        <div
            class="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider mb-3"
        >
            <ChevronLeft class="w-3.5 h-3.5" />
            <span>Analysis</span>
        </div>

        <button
            type="button"
            onclick={handleStartAnalysis}
            disabled={!companyStore.selectedEarningsCall}
            class="w-full py-3 px-4 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-all
        {analysisStore.isAnalyzing
                ? 'bg-error-900 hover:bg-error-800 text-error-400 border border-error-700'
                : 'bg-primary-600 hover:bg-primary-500 text-white'}
        {!companyStore.selectedEarningsCall
                ? 'opacity-50 cursor-not-allowed'
                : ''}"
        >
            {#if analysisStore.isAnalyzing}
                <Square class="w-4 h-4" />
                <span>Stop Analysis</span>
            {:else}
                <Play class="w-4 h-4" />
                <span>Start Analysis</span>
            {/if}
        </button>
    </div>
</aside>

<svelte:window 
    onclick={() => {
        showCompanyDropdown = false;
        showEarningsDropdown = false;
    }}
    onkeydown={(e) => {
        if (e.key === "Escape") {
            showCompanyDropdown = false;
            showEarningsDropdown = false;
        }
    }}
/>
