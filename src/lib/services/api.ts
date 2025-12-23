// Backend API service for earningsInsight
import type {
    Company,
    EarningsCall,
    FinancialData,
    TranscriptEntry
} from '$lib/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Error handling helper
class APIError extends Error {
    constructor(
        message: string,
        public status: number,
        public detail?: string
    ) {
        super(message);
        this.name = 'APIError';
    }
}

async function fetchAPI<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
            `API request failed: ${response.status}`,
            response.status,
            errorData.detail || response.statusText
        );
    }
    
    return response.json();
}

// Types matching backend models
interface CompanySearchResult {
    ticker: string;
    name: string;
    type: string;
    region: string;
    currency: string;
}

interface CompanyOverview {
    symbol: string;
    name: string;
    description?: string;
    sector?: string;
    industry?: string;
    market_cap?: string;
    pe_ratio?: string;
    eps?: string;
    revenue_ttm?: string;
    profit_margin?: string;
    operating_margin_ttm?: string;
    return_on_equity_ttm?: string;
    dividend_yield?: string;
    fifty_two_week_high?: string;
    fifty_two_week_low?: string;
}

interface BackendEarningsCall {
    id: string;
    ticker: string;
    quarter: string;
    year: number;
    date: string;
    fiscal_date_ending?: string;
    reported_eps?: string;
    estimated_eps?: string;
    surprise?: string;
    surprise_percentage?: string;
    status: string;
}

interface BackendFinancialData {
    ticker: string;
    revenue?: string;
    revenue_change?: string;
    eps?: string;
    eps_change?: string;
    pe_ratio?: number;
    market_cap?: string;
    yoy_growth?: string;
    guidance_vs_actual?: string;
}

interface TranscriptData {
    ticker: string;
    quarter: string;
    year: number;
    fiscal_date_ending: string;
    transcript: string;
    entries: TranscriptEntry[];
}

/**
 * Search for companies by name or ticker
 */
export async function searchCompanies(query: string): Promise<Company[]> {
    const results = await fetchAPI<CompanySearchResult[]>(
        `/api/companies/search?q=${encodeURIComponent(query)}`
    );
    
    // Convert to frontend Company type
    return results.map(result => ({
        ticker: result.ticker,
        name: result.name,
        sector: result.type,
        earningsCalls: [] // Will be loaded separately
    }));
}

/**
 * Get detailed company information
 */
export async function getCompany(ticker: string): Promise<CompanyOverview> {
    return fetchAPI<CompanyOverview>(`/api/companies/${ticker}`);
}

/**
 * Get earnings history for a company
 */
export async function getEarningsHistory(ticker: string): Promise<EarningsCall[]> {
    const earnings = await fetchAPI<BackendEarningsCall[]>(
        `/api/companies/${ticker}/earnings`
    );
    
    // Convert to frontend EarningsCall type
    return earnings.map(e => ({
        id: e.id,
        companyTicker: e.ticker,
        date: e.date,
        quarter: e.quarter,
        year: e.year,
        duration: 'N/A', // Not provided by backend yet
        status: e.status as 'upcoming' | 'live' | 'recorded'
    }));
}

/**
 * Get financial data for a company for a specific quarter or latest
 */
export async function getFinancials(
    ticker: string,
    quarter?: string,
    year?: number
): Promise<FinancialData> {
    let url = `/api/companies/${ticker}/financials`;
    const params = new URLSearchParams();
    
    if (quarter) params.append('quarter', quarter);
    if (year) params.append('year', year.toString());
    
    if (params.toString()) {
        url += `?${params.toString()}`;
    }
    
    const data = await fetchAPI<BackendFinancialData>(url);
    
    // Convert to frontend FinancialData type
    return {
        revenue: data.revenue || 'N/A',
        revenueChange: data.revenue_change,
        eps: data.eps || 'N/A',
        epsChange: data.eps_change,
        pe: data.pe_ratio || null,
        marketCap: data.market_cap || 'N/A',
        yoyGrowth: data.yoy_growth || 'N/A',
        guidanceVsActual: data.guidance_vs_actual || 'N/A'
    };
}

/**
 * Get earnings call transcript
 */
export async function getTranscript(
    ticker: string,
    quarter: string,
    year: number
): Promise<TranscriptData> {
    return fetchAPI<TranscriptData>(
        `/api/transcript/${ticker}/${quarter}/${year}`
    );
}

/**
 * Get upcoming earnings calendar
 */
export async function getEarningsCalendar(
    horizon: '3month' | '6month' | '12month' = '3month'
): Promise<any[]> {
    return fetchAPI<any[]>(
        `/api/companies/calendar/upcoming?horizon=${horizon}`
    );
}

// Export error class
export { APIError };
