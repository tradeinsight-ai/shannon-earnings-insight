// Export Service - Download transcript and insights
import type { TranscriptEntry, CategoryInsight } from '$lib/types';
import { uiStore } from '$lib/stores/ui.svelte';

export type ExportFormat = 'txt' | 'json' | 'csv';

interface ExportData {
    companyTicker: string;
    earningsCallDate: string;
    transcript: TranscriptEntry[];
    insights: CategoryInsight[];
    exportedAt: string;
}

function downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

export function exportTranscript(
    transcript: TranscriptEntry[],
    companyTicker: string,
    format: ExportFormat = 'txt'
): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${companyTicker}_transcript_${timestamp}`;

    switch (format) {
        case 'txt': {
            const content = transcript
                .map(entry => `[${entry.timestamp}]${entry.speaker ? ` ${entry.speaker}:` : ''} ${entry.text}`)
                .join('\n\n');
            downloadFile(content, `${filename}.txt`, 'text/plain');
            break;
        }
        case 'json': {
            const content = JSON.stringify(transcript, null, 2);
            downloadFile(content, `${filename}.json`, 'application/json');
            break;
        }
        case 'csv': {
            const headers = 'Timestamp,Speaker,Text\n';
            const rows = transcript
                .map(entry => `"${entry.timestamp}","${entry.speaker || ''}","${entry.text.replace(/"/g, '""')}"`)
                .join('\n');
            downloadFile(headers + rows, `${filename}.csv`, 'text/csv');
            break;
        }
    }

    uiStore.addNotification({
        type: 'success',
        message: `Transcript exported as ${format.toUpperCase()}`,
        duration: 3000
    });
}

export function exportInsights(
    insights: CategoryInsight[],
    companyTicker: string,
    format: ExportFormat = 'json'
): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${companyTicker}_insights_${timestamp}`;

    switch (format) {
        case 'json': {
            const content = JSON.stringify(insights, null, 2);
            downloadFile(content, `${filename}.json`, 'application/json');
            break;
        }
        case 'txt': {
            const content = insights
                .map(cat => {
                    const header = `## ${cat.category.replace(/_/g, ' ').toUpperCase()} (Sentiment: ${(cat.sentiment * 100).toFixed(1)}%)\n`;
                    const insightsList = cat.insights
                        .map(i => `  [${i.timestamp}] ${i.text}`)
                        .join('\n');
                    return header + (insightsList || '  No insights yet');
                })
                .join('\n\n');
            downloadFile(content, `${filename}.txt`, 'text/plain');
            break;
        }
        case 'csv': {
            const headers = 'Category,Sentiment,Timestamp,Insight\n';
            const rows = insights
                .flatMap(cat =>
                    cat.insights.map(i =>
                        `"${cat.category}","${cat.sentiment}","${i.timestamp}","${i.text.replace(/"/g, '""')}"`
                    )
                )
                .join('\n');
            downloadFile(headers + rows, `${filename}.csv`, 'text/csv');
            break;
        }
    }

    uiStore.addNotification({
        type: 'success',
        message: `Insights exported as ${format.toUpperCase()}`,
        duration: 3000
    });
}

export function exportFullAnalysis(
    data: ExportData,
    format: 'json' = 'json'
): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${data.companyTicker}_full_analysis_${timestamp}`;

    const content = JSON.stringify(data, null, 2);
    downloadFile(content, `${filename}.json`, 'application/json');

    uiStore.addNotification({
        type: 'success',
        message: 'Full analysis exported',
        duration: 3000
    });
}
