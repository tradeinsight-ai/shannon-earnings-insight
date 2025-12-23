/**
 * Utility functions for formatting data display
 */

/**
 * Format ISO date string to "Month DD, YYYY" format
 * @example "2025-10-22" → "October 22, 2025"
 */
export function formatDate(dateString: string): string {
    try {
        const date = new Date(dateString);
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return dateString; // Return original if invalid
        }
        
        const options: Intl.DateTimeFormatOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        
        return date.toLocaleDateString('en-US', options);
    } catch (error) {
        return dateString; // Return original on error
    }
}

/**
 * Format ISO date string to short format "Mon DD, YYYY"
 * @example "2025-10-22" → "Oct 22, 2025"
 */
export function formatDateShort(dateString: string): string {
    try {
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
            return dateString;
        }
        
        const options: Intl.DateTimeFormatOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        return date.toLocaleDateString('en-US', options);
    } catch (error) {
        return dateString;
    }
}

/**
 * Format large numbers with commas
 * @example 1000000 → "1,000,000"
 */
export function formatNumber(num: number | string): string {
    const numValue = typeof num === 'string' ? parseFloat(num) : num;
    if (isNaN(numValue)) return num.toString();
    return numValue.toLocaleString('en-US');
}

/**
 * Format currency values
 * @example 1234.56 → "$1,234.56"
 */
export function formatCurrency(amount: number | string, currency = 'USD'): string {
    const numValue = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(numValue)) return amount.toString();
    
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numValue);
}

/**
 * Format percentage values
 * @example 0.1234 → "12.34%"
 */
export function formatPercent(value: number | string, decimals = 2): string {
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return value.toString();
    
    return `${(numValue * 100).toFixed(decimals)}%`;
}

/**
 * Format large monetary values with abbreviations
 * @example 1500000000 → "$1.5B"
 */
export function formatMoneyShort(value: number | string): string {
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return value.toString();
    
    const absValue = Math.abs(numValue);
    const sign = numValue < 0 ? '-' : '';
    
    if (absValue >= 1e12) {
        return `${sign}$${(absValue / 1e12).toFixed(2)}T`;
    } else if (absValue >= 1e9) {
        return `${sign}$${(absValue / 1e9).toFixed(2)}B`;
    } else if (absValue >= 1e6) {
        return `${sign}$${(absValue / 1e6).toFixed(2)}M`;
    } else if (absValue >= 1e3) {
        return `${sign}$${(absValue / 1e3).toFixed(2)}K`;
    } else {
        return `${sign}$${absValue.toFixed(2)}`;
    }
}
