<script lang="ts">
    import {
        X,
        CheckCircle,
        AlertCircle,
        AlertTriangle,
        Info,
    } from "lucide-svelte";
    import type { Notification } from "$lib/types";
    import { uiStore } from "$lib/stores/ui.svelte";

    interface Props {
        notification: Notification;
    }

    let { notification }: Props = $props();

    const icons = {
        success: CheckCircle,
        error: AlertCircle,
        warning: AlertTriangle,
        info: Info,
    };

    const colors = {
        success: "bg-success-900 border-success-700 text-success-400",
        error: "bg-error-900 border-error-700 text-error-400",
        warning: "bg-warning-900 border-warning-700 text-warning-400",
        info: "bg-gray-800 border-gray-700 text-gray-300",
    };

    const IconComponent = $derived(icons[notification.type]);
</script>

<div
    class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-xl {colors[
        notification.type
    ]} animate-slide-in"
    role="alert"
>
    <IconComponent class="w-5 h-5 shrink-0" />
    <p class="text-sm flex-1">{notification.message}</p>
    <button
        onclick={() => uiStore.removeNotification(notification.id)}
        class="p-1 hover:bg-white/10 rounded transition-colors"
        aria-label="Dismiss notification"
    >
        <X class="w-4 h-4" />
    </button>
</div>

<style>
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
</style>
