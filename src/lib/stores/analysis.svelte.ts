// Analysis State Store - Using Svelte 5 Runes
import type {
    ConnectionStatus,
    TranscriptEntry,
    CategoryInsight,
    SentimentDataPoint,
    AnalysisCategory,
    Insight
} from '$lib/types';

// Connection state
let connectionStatus = $state<ConnectionStatus>('disconnected');

// Analysis state
let isAnalyzing = $state(false);
let analysisProgress = $state(0); // 0-100
let analysisStartTime = $state<number | null>(null);

// Transcript
let transcript = $state<TranscriptEntry[]>([]);

// Category insights
let categoryInsights = $state<CategoryInsight[]>([
    { id: 'key_statements', category: 'key_statements', sentiment: 0, insights: [], icon: 'quote' },
    { id: 'financial_performance', category: 'financial_performance', sentiment: 0, insights: [], icon: 'trending-up' },
    { id: 'forward_guidance', category: 'forward_guidance', sentiment: 0, insights: [], icon: 'compass' },
    { id: 'market_position', category: 'market_position', sentiment: 0, insights: [], icon: 'target' },
    { id: 'risk_factors', category: 'risk_factors', sentiment: 0, insights: [], icon: 'alert-triangle' },
    { id: 'analyst_qa', category: 'analyst_qa', sentiment: 0, insights: [], icon: 'message-circle' }
]);

// Sentiment history for chart
let sentimentHistory = $state<SentimentDataPoint[]>([]);

// Current playback time for syncing
let currentTime = $state(0);

// Derived overall sentiment
const overallSentiment = $derived(() => {
    if (categoryInsights.length === 0) return 0;
    const sum = categoryInsights.reduce((acc, cat) => acc + cat.sentiment, 0);
    return sum / categoryInsights.length;
});

// Getters
export function getConnectionStatus() {
    return connectionStatus;
}

export function getIsAnalyzing() {
    return isAnalyzing;
}

export function getAnalysisProgress() {
    return analysisProgress;
}

export function getTranscript() {
    return transcript;
}

export function getCategoryInsights() {
    return categoryInsights;
}

export function getSentimentHistory() {
    return sentimentHistory;
}

export function getOverallSentiment() {
    return overallSentiment();
}

export function getCurrentTime() {
    return currentTime;
}

// Actions
export function setConnectionStatus(status: ConnectionStatus) {
    connectionStatus = status;
}

export function startAnalysis() {
    isAnalyzing = true;
    analysisStartTime = Date.now();
    analysisProgress = 0;
}

export function stopAnalysis() {
    isAnalyzing = false;
}

export function setAnalysisProgress(progress: number) {
    analysisProgress = Math.min(100, Math.max(0, progress));
}

export function addTranscriptEntry(entry: TranscriptEntry) {
    transcript = [...transcript, entry];
}

export function setTranscript(entries: TranscriptEntry[]) {
    transcript = entries;
}

export function clearTranscript() {
    transcript = [];
}

export function updateCategoryInsight(category: AnalysisCategory, insight: Insight, sentiment: number) {
    categoryInsights = categoryInsights.map(cat => {
        if (cat.category === category) {
            return {
                ...cat,
                sentiment,
                insights: [...cat.insights, insight]
            };
        }
        return cat;
    });
}

export function setCategoryInsights(insights: CategoryInsight[]) {
    categoryInsights = insights;
}

export function addSentimentDataPoint(dataPoint: SentimentDataPoint) {
    sentimentHistory = [...sentimentHistory, dataPoint];
}

export function setSentimentHistory(history: SentimentDataPoint[]) {
    sentimentHistory = history;
}

export function setCurrentTime(time: number) {
    currentTime = time;
}

export function resetAnalysis() {
    isAnalyzing = false;
    analysisProgress = 0;
    analysisStartTime = null;
    transcript = [];
    categoryInsights = [
        { id: 'key_statements', category: 'key_statements', sentiment: 0, insights: [], icon: 'quote' },
        { id: 'financial_performance', category: 'financial_performance', sentiment: 0, insights: [], icon: 'trending-up' },
        { id: 'forward_guidance', category: 'forward_guidance', sentiment: 0, insights: [], icon: 'compass' },
        { id: 'market_position', category: 'market_position', sentiment: 0, insights: [], icon: 'target' },
        { id: 'risk_factors', category: 'risk_factors', sentiment: 0, insights: [], icon: 'alert-triangle' },
        { id: 'analyst_qa', category: 'analyst_qa', sentiment: 0, insights: [], icon: 'message-circle' }
    ];
    sentimentHistory = [];
    currentTime = 0;
}

// Store object for components
export const analysisStore = {
    get connectionStatus() { return connectionStatus; },
    get isAnalyzing() { return isAnalyzing; },
    get analysisProgress() { return analysisProgress; },
    get transcript() { return transcript; },
    get categoryInsights() { return categoryInsights; },
    get sentimentHistory() { return sentimentHistory; },
    get overallSentiment() { return overallSentiment(); },
    get currentTime() { return currentTime; },
    setConnectionStatus,
    startAnalysis,
    stopAnalysis,
    setAnalysisProgress,
    addTranscriptEntry,
    setTranscript,
    clearTranscript,
    updateCategoryInsight,
    setCategoryInsights,
    addSentimentDataPoint,
    setSentimentHistory,
    setCurrentTime,
    resetAnalysis
};
