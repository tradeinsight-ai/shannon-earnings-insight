<script lang="ts">
  import { Download, Sun, Moon, Filter, Settings } from "lucide-svelte";
  import { uiStore } from "$lib/stores/ui.svelte";
  import { analysisStore } from "$lib/stores/analysis.svelte";

  // Get connection status for display
  const statusColors = {
    connected: "bg-primary-400",
    connecting: "bg-warning-400 animate-pulse",
    disconnected: "bg-error-400",
  };

  const statusLabels = {
    connected: "Connected",
    connecting: "Connecting...",
    disconnected: "Disconnected",
  };

  function handleExport() {
    uiStore.addNotification({
      type: "info",
      message: "Export feature coming soon",
      duration: 2000,
    });
  }
</script>

<header class="h-14 bg-transparent flex items-center justify-between px-5">
  <!-- Left: Logo and navigation -->
  <div class="flex items-center gap-4">
    <!-- Logo -->
    <div class="flex items-center gap-2.5">
      <svg
        width="28"
        height="28"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="shrink-0"
      >
        <path
          d="M13.917 19.0312C14.4056 19.0314 14.8047 19.4195 14.8047 19.9023V27.2295C14.8047 27.7123 14.4056 28.1004 13.917 28.1006C13.4283 28.1006 13.0283 27.7125 13.0283 27.2295V19.9023C13.0283 19.4193 13.4283 19.0312 13.917 19.0312ZM9.58887 11.7256C10.0773 11.7257 10.4765 12.1128 10.4766 12.5957V22.5322C10.4766 23.0152 10.0773 23.4022 9.58887 23.4023C9.10038 23.4023 8.7002 23.0154 8.7002 22.5322V12.5957L8.7041 12.5059C8.75015 12.0654 9.13108 11.7256 9.58887 11.7256ZM18.5918 12.251C19.0383 12.2956 19.3896 12.6654 19.3896 13.1182V21.4893C19.3895 21.9419 19.0381 22.311 18.5918 22.3555L18.501 22.3594C18.0125 22.3593 17.6135 21.972 17.6133 21.4893V13.1182C17.6133 12.6353 18.0123 12.2472 18.501 12.2471L18.5918 12.251ZM23.2109 3.90039C23.6992 3.90065 24.0984 4.28777 24.0986 4.77051V16.2725C24.0986 16.7554 23.6993 17.1423 23.2109 17.1426C22.7225 17.1426 22.3223 16.7557 22.3223 16.2725V4.77051L22.3262 4.68066C22.3723 4.24031 22.7532 3.90039 23.2109 3.90039Z"
          fill="#20C099"
          stroke="#20C099"
          stroke-width="0.2"
        />
      </svg>
      <span class="font-semibold text-base tracking-tight">
        <span class="text-gray-100">earnings</span><span
          class="text-primary-400">Insight</span
        >
      </span>
    </div>

    <!-- Connection Status -->
    <div
      class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800/50"
    >
      <span class="status-dot {statusColors[analysisStore.connectionStatus]}"
      ></span>
      <span class="text-xs text-gray-400 font-mono">
        {statusLabels[analysisStore.connectionStatus]}
      </span>
    </div>
  </div>

  <!-- Right: Actions -->
  <div class="flex items-center gap-2">
    <button
      onclick={handleExport}
      class="flex items-center gap-2 text-sm py-2 px-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 transition-colors"
    >
      <Download class="w-4 h-4" />
      <span>Export</span>
    </button>

    <button
      class="w-9 h-9 rounded-full bg-gray-800/50 hover:bg-gray-700/50 flex items-center justify-center transition-colors"
      aria-label="Filter"
    >
      <Filter class="w-4 h-4 text-gray-400" />
    </button>

    <button
      class="w-9 h-9 rounded-full bg-gray-800/50 hover:bg-gray-700/50 flex items-center justify-center transition-colors"
      aria-label="Settings"
    >
      <Settings class="w-4 h-4 text-gray-400" />
    </button>

    <button
      onclick={() => uiStore.toggleTheme()}
      class="w-9 h-9 rounded-full bg-gray-800/50 hover:bg-gray-700/50 flex items-center justify-center transition-colors"
      aria-label="Toggle theme"
    >
      {#if uiStore.theme === "dark"}
        <Sun class="w-4 h-4 text-gray-400" />
      {:else}
        <Moon class="w-4 h-4 text-gray-400" />
      {/if}
    </button>
  </div>
</header>
