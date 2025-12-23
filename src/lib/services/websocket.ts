// WebSocket Service Stub for Python Backend Connection
import type { WSMessage, WSMessageType } from '$lib/types';
import { analysisStore } from '$lib/stores/analysis.svelte';

export interface WebSocketConfig {
    url: string;
    reconnectAttempts?: number;
    reconnectDelay?: number;
}

class WebSocketService {
    private ws: WebSocket | null = null;
    private config: WebSocketConfig | null = null;
    private reconnectCount = 0;
    private messageHandlers: Map<WSMessageType, ((payload: unknown) => void)[]> = new Map();

    connect(config: WebSocketConfig): Promise<void> {
        this.config = config;
        this.reconnectCount = 0;

        return new Promise((resolve, reject) => {
            try {
                analysisStore.setConnectionStatus('connecting');

                this.ws = new WebSocket(config.url);

                this.ws.onopen = () => {
                    console.log('[WebSocket] Connected to', config.url);
                    analysisStore.setConnectionStatus('connected');
                    this.reconnectCount = 0;
                    resolve();
                };

                this.ws.onclose = (event) => {
                    console.log('[WebSocket] Disconnected', event.code, event.reason);
                    analysisStore.setConnectionStatus('disconnected');
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('[WebSocket] Error:', error);
                    reject(error);
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
            } catch (error) {
                analysisStore.setConnectionStatus('disconnected');
                reject(error);
            }
        });
    }

    disconnect(): void {
        if (this.ws) {
            this.ws.close(1000, 'Client disconnected');
            this.ws = null;
        }
        analysisStore.setConnectionStatus('disconnected');
    }

    send(type: WSMessageType, payload: unknown): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('[WebSocket] Cannot send - not connected');
            return;
        }

        const message: WSMessage = {
            type,
            payload,
            timestamp: Date.now()
        };

        this.ws.send(JSON.stringify(message));
    }

    on(type: WSMessageType, handler: (payload: unknown) => void): () => void {
        if (!this.messageHandlers.has(type)) {
            this.messageHandlers.set(type, []);
        }
        this.messageHandlers.get(type)!.push(handler);

        // Return unsubscribe function
        return () => {
            const handlers = this.messageHandlers.get(type);
            if (handlers) {
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            }
        };
    }

    private handleMessage(data: string): void {
        try {
            const message: WSMessage = JSON.parse(data);
            const handlers = this.messageHandlers.get(message.type);

            if (handlers) {
                handlers.forEach(handler => handler(message.payload));
            }

            // Built-in handling for common message types
            switch (message.type) {
                case 'transcript_update':
                    // Handle transcript updates
                    break;
                case 'insight_update':
                    // Handle insight updates
                    break;
                case 'sentiment_update':
                    // Handle sentiment updates
                    break;
                case 'analysis_complete':
                    analysisStore.stopAnalysis();
                    break;
                case 'error':
                    console.error('[WebSocket] Server error:', message.payload);
                    break;
            }
        } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
        }
    }

    private attemptReconnect(): void {
        if (!this.config) return;

        const maxAttempts = this.config.reconnectAttempts ?? 5;
        const delay = this.config.reconnectDelay ?? 3000;

        if (this.reconnectCount < maxAttempts) {
            this.reconnectCount++;
            console.log(`[WebSocket] Attempting reconnect ${this.reconnectCount}/${maxAttempts} in ${delay}ms`);

            setTimeout(() => {
                this.connect(this.config!).catch(() => {
                    // Reconnection failed, will try again via onclose
                });
            }, delay);
        } else {
            console.log('[WebSocket] Max reconnect attempts reached');
        }
    }

    get isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}

// Singleton instance
export const websocketService = new WebSocketService();

// Convenience functions
export function connectWebSocket(url: string): Promise<void> {
    return websocketService.connect({ url, reconnectAttempts: 5, reconnectDelay: 3000 });
}

export function disconnectWebSocket(): void {
    websocketService.disconnect();
}

export function sendMessage(type: WSMessageType, payload: unknown): void {
    websocketService.send(type, payload);
}

export function onMessage(type: WSMessageType, handler: (payload: unknown) => void): () => void {
    return websocketService.on(type, handler);
}
