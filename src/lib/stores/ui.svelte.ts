// UI State Store - Using Svelte 5 Runes
import type { Theme, AudioSource, Notification } from '$lib/types';

// Theme state
let theme = $state<Theme>('dark');

// Source toggle
let audioSource = $state<AudioSource>('recordings');

// Notifications
let notifications = $state<Notification[]>([]);

// Sidebar collapsed state
let sidebarCollapsed = $state(false);

// Export reactive getters and setters
export function getTheme() {
    return theme;
}

export function setTheme(newTheme: Theme) {
    theme = newTheme;
    // Update HTML class for theme
    if (typeof document !== 'undefined') {
        document.documentElement.classList.remove('dark', 'light');
        document.documentElement.classList.add(newTheme);
    }
}

export function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark');
}

export function getAudioSource() {
    return audioSource;
}

export function setAudioSource(source: AudioSource) {
    audioSource = source;
}

export function getNotifications() {
    return notifications;
}

export function addNotification(notification: Omit<Notification, 'id' | 'timestamp'>) {
    const id = crypto.randomUUID();
    const newNotification: Notification = {
        ...notification,
        id,
        timestamp: Date.now()
    };
    notifications = [...notifications, newNotification];

    // Auto-remove after duration if specified
    if (notification.duration) {
        setTimeout(() => {
            removeNotification(id);
        }, notification.duration);
    }

    return id;
}

export function removeNotification(id: string) {
    notifications = notifications.filter(n => n.id !== id);
}

export function clearNotifications() {
    notifications = [];
}

export function getSidebarCollapsed() {
    return sidebarCollapsed;
}

export function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
}

// Create a reactive store object for use in components
export const uiStore = {
    get theme() { return theme; },
    get audioSource() { return audioSource; },
    get notifications() { return notifications; },
    get sidebarCollapsed() { return sidebarCollapsed; },
    setTheme,
    toggleTheme,
    setAudioSource,
    addNotification,
    removeNotification,
    clearNotifications,
    toggleSidebar
};
