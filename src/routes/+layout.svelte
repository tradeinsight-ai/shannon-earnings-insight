<script lang="ts">
	import "../app.css";
	import { uiStore } from "$lib/stores/ui.svelte";
	import Notification from "$lib/components/Notification.svelte";

	let { children } = $props();

	// Initialize theme on mount
	$effect(() => {
		if (typeof document !== "undefined") {
			document.documentElement.classList.remove("dark", "light");
			document.documentElement.classList.add(uiStore.theme);
		}
	});
</script>

<svelte:head>
	<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
</svelte:head>

<div class="min-h-screen bg-gray-950 text-gray-100 font-mono">
	{@render children()}
</div>

<!-- Notifications -->
<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
	{#each uiStore.notifications as notification (notification.id)}
		<Notification {notification} />
	{/each}
</div>
