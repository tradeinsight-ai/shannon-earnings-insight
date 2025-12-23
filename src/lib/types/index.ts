// earningsInsight Type Definitions

export interface TranscriptEntry {
    id: string;
    timestamp: string;
    text: string;
    speaker?: string;
    confidence?: number;
}

export interface Insight {
    id: string;
    timestamp: string;
    text: string;
    relevance: number;
}

export interface CategoryInsight {
    id: string;
    category: AnalysisCategory;
    sentiment: number; // -1.0 to +1.0
    insights: Insight[];
    icon: string;
}

export type AnalysisCategory =
    | 'key_statements'
    | 'financial_performance'
    | 'forward_guidance'
    | 'market_position'
    | 'risk_factors'
    | 'analyst_qa';

export const CATEGORY_LABELS: Record<AnalysisCategory, string> = {
    key_statements: 'Key Statements',
    financial_performance: 'Financial Performance',
    forward_guidance: 'Forward Guidance',
    market_position: 'Market Position',
    risk_factors: 'Risk Factors',
    analyst_qa: 'Analyst Q&A'
};

export const CATEGORY_ICONS: Record<AnalysisCategory, string> = {
    key_statements: 'quote',
    financial_performance: 'trending-up',
    forward_guidance: 'compass',
    market_position: 'target',
    risk_factors: 'alert-triangle',
    analyst_qa: 'message-circle'
};

export interface SentimentDataPoint {
    timestamp: number; // seconds into call
    overallSentiment: number;
    categorySentiments: Record<AnalysisCategory, number>;
}

export interface Company {
    ticker: string;
    name: string;
    sector?: string;
    earningsCalls: EarningsCall[];
}

export interface EarningsCall {
    id: string;
    companyTicker: string;
    date: string;
    quarter: string;
    year: number;
    duration: string;
    audioUrl?: string;
    status: 'upcoming' | 'live' | 'recorded';
}

export interface FinancialData {
    revenue: string;
    revenueChange?: string;
    eps: string;
    epsChange?: string;
    pe: number | null;
    marketCap: string;
    yoyGrowth: string;
    guidanceVsActual: string;
}

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected';

export type AudioSource = 'recordings' | 'microphone' | 'custom';

export type Theme = 'dark' | 'light';

export interface Notification {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: number;
    duration?: number; // ms, if undefined = persistent
}

// WebSocket message types
export interface WSMessage {
    type: WSMessageType;
    payload: unknown;
    timestamp: number;
}

export type WSMessageType =
    | 'transcript_update'
    | 'insight_update'
    | 'sentiment_update'
    | 'analysis_complete'
    | 'error'
    | 'connection_status';

export interface TranscriptUpdatePayload {
    entries: TranscriptEntry[];
}

export interface InsightUpdatePayload {
    category: AnalysisCategory;
    insight: Insight;
    sentiment: number;
}

export interface SentimentUpdatePayload {
    dataPoint: SentimentDataPoint;
}

// Mock data helper types
export interface MockDataConfig {
    companies: Company[];
    financials: Record<string, FinancialData>;
}
