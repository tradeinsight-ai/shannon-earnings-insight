// Company Data Store - Using Svelte 5 Runes
import type { Company, EarningsCall, FinancialData } from '$lib/types';
import * as api from '$lib/services/api';

// State
let companies = $state<Company[]>([]); // Only companies that have been selected
let searchResults = $state<Company[]>([]); // Temporary search results
let selectedTicker = $state<string | null>(null);
let selectedEarningsCallId = $state<string | null>(null);
let searchQuery = $state('');
let customAudioUrl = $state('');

// Loading and error states
let isLoadingCompanies = $state(false);
let isLoadingFinancials = $state(false);
let loadingError = $state<string | null>(null);
let financialsData = $state<FinancialData | null>(null);
let earningsCallsData = $state<EarningsCall[]>([]);

// Derived state
const selectedCompany = $derived(
    selectedTicker ? companies.find(c => c.ticker === selectedTicker) ?? null : null
);

const selectedEarningsCall = $derived(
    selectedCompany && selectedEarningsCallId
        ? selectedCompany.earningsCalls.find(e => e.id === selectedEarningsCallId) ?? null
        : null
);

const financials = $derived(
    // Use real data from API
    financialsData
);

// Actions
export function setSearchQuery(query: string) {
    searchQuery = query;
    // Clear search results when query is cleared
    if (!query || query.length < 2) {
        searchResults = [];
    }
}

export function setCustomAudioUrl(url: string) {
    customAudioUrl = url;
}

export async function selectCompany(ticker: string | null) {
    selectedTicker = ticker;
    
    if (!ticker) {
        selectedEarningsCallId = null;
        financialsData = null;
        earningsCallsData = [];
        loadingError = null;
        return;
    }
    
    // Check if company already exists with data
    const existingCompany = companies.find(c => c.ticker === ticker);
    const hasExistingData = existingCompany && existingCompany.earningsCalls.length > 0;
    
    // If re-selecting existing company with data, just restore it
    if (hasExistingData && existingCompany) {
        earningsCallsData = existingCompany.earningsCalls;
        searchQuery = ticker; // Update search to show ticker
        searchResults = []; // Clear search results
        
        // Keep existing financial data if we have it
        if (!financialsData || financialsData.ticker !== ticker) {
            // Need to reload financials
            try {
                financialsData = await api.getFinancials(ticker).catch((err) => {
                    console.warn(`No financial data for ${ticker}:`, err);
                    return null;
                });
            } catch (error) {
                console.warn('Error loading financials:', error);
            }
        }
        // Auto-select first earnings call
        selectedEarningsCallId = existingCompany.earningsCalls[0]?.id || null;
        return;
    }
    
    // Add company to permanent list if not already there
    if (!existingCompany) {
        const searchResult = searchResults.find(c => c.ticker === ticker);
        if (searchResult) {
            companies = [...companies, searchResult];
        }
    }
    
    // Clear search results after selection (keep searchQuery to show ticker)
    searchResults = [];
    searchQuery = ticker;
    
    // Load company data from API (new selection)
    financialsData = null;
    earningsCallsData = [];
    loadingError = null;
    
    try {
        isLoadingFinancials = true;
        loadingError = null;
        
        // Load earnings history and financials in parallel
        const [earnings, financials] = await Promise.all([
            api.getEarningsHistory(ticker).catch((err) => {
                console.warn(`No earnings data for ${ticker}:`, err);
                return [];
            }),
            api.getFinancials(ticker).catch((err) => {
                console.warn(`No financial data for ${ticker}:`, err);
                return null;
            })
        ]);
        
        earningsCallsData = earnings;
        financialsData = financials;
        
        // Update company in list with real earnings calls
        const companyIndex = companies.findIndex(c => c.ticker === ticker);
        if (companyIndex >= 0 && earnings.length > 0) {
            companies[companyIndex].earningsCalls = earnings;
        }
        
        // Auto-select first earnings call
        if (earnings.length > 0) {
            selectedEarningsCallId = earnings[0].id;
        } else {
            selectedEarningsCallId = null;
        }
        
        // Set error message if both earnings and financials are missing
        if (earnings.length === 0 && !financials) {
            loadingError = `No financial or earnings data available for ${ticker}`;
        } else if (!financials) {
            loadingError = `Financial data not available for ${ticker}`;
        } else if (earnings.length === 0) {
            loadingError = `No earnings history available for ${ticker}`;
        }
    } catch (error) {
        console.error('Error loading company data:', error);
        loadingError = error instanceof Error ? error.message : 'Failed to load company data';
        selectedEarningsCallId = null;
    } finally {
        isLoadingFinancials = false;
    }
}

export async function searchCompaniesAPI(query: string) {
    if (!query || query.length < 2) {
        searchResults = [];
        return;
    }
    
    try {
        isLoadingCompanies = true;
        loadingError = null;
        
        const results = await api.searchCompanies(query);
        
        // Set search results (temporary, not cached)
        searchResults = results;
    } catch (error) {
        console.error('Error searching companies:', error);
        loadingError = error instanceof Error ? error.message : 'Failed to search companies';
        searchResults = [];
    } finally {
        isLoadingCompanies = false;
    }
}

export async function selectEarningsCall(callId: string | null) {
    selectedEarningsCallId = callId;
    
    if (!callId || !selectedCompany) {
        return;
    }
    
    // Find the selected call
    const call = selectedCompany.earningsCalls.find(c => c.id === callId);
    if (!call) {
        return;
    }
    
    // Fetch quarter-specific financial data and transcript from API
    try {
        isLoadingFinancials = true;
        loadingError = null;
        
        // Load financials and transcript in parallel
        const [financials, transcript] = await Promise.all([
            api.getFinancials(
                selectedCompany.ticker,
                call.quarter,
                call.year
            ).catch((err) => {
                console.warn(`No financial data for ${selectedCompany.ticker} ${call.quarter} ${call.year}:`, err);
                return null;
            }),
            api.getTranscript(
                selectedCompany.ticker,
                call.quarter,
                call.year
            ).catch((err) => {
                console.warn(`No transcript for ${selectedCompany.ticker} ${call.quarter} ${call.year}:`, err);
                return null;
            })
        ]);
        
        financialsData = financials;
        
        // Update analysis store with transcript if available
        if (transcript && transcript.entries) {
            const { analysisStore } = await import('./analysis.svelte');
            analysisStore.setTranscript(transcript.entries);
            console.log(`Loaded ${transcript.entries.length} transcript entries`);
        }
        
        if (!financials) {
            loadingError = `Financial data not available for ${call.quarter} ${call.year}`;
        }
        if (!transcript) {
            if (loadingError) {
                loadingError += ` and transcript not available`;
            } else {
                loadingError = `Transcript not available for ${call.quarter} ${call.year}`;
            }
        }
    } catch (error) {
        console.error('Error loading quarter data:', error);
        loadingError = error instanceof Error ? error.message : 'Failed to load data';
    } finally {
        isLoadingFinancials = false;
    }
}

// Store object for components
export const companyStore = {
    get companies() { return companies; },
    get searchResults() { return searchResults; },
    get selectedTicker() { return selectedTicker; },
    get selectedCompany() { return selectedCompany; },
    get selectedEarningsCall() { return selectedEarningsCall; },
    get financials() { return financials; },
    get searchQuery() { return searchQuery; },
    get customAudioUrl() { return customAudioUrl; },
    get isLoadingCompanies() { return isLoadingCompanies; },
    get isLoadingFinancials() { return isLoadingFinancials; },
    get loadingError() { return loadingError; },
    setSearchQuery,
    selectCompany,
    selectEarningsCall,
    setCustomAudioUrl,
    searchCompaniesAPI
};
