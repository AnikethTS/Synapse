<script lang="ts">
	import { chat } from '$lib/stores/chat.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import ChatWindow from '$lib/components/ChatWindow.svelte';

	let sidebarOpen = $state(true);

	// Start with an active session
	if (chat.sessions.length === 0) chat.newSession();
</script>

<svelte:head>
	<title>Synapse — AI for Developers</title>
</svelte:head>

<div class="flex h-dvh w-full overflow-hidden bg-background text-foreground">
	<!-- Mobile overlay -->
	{#if sidebarOpen}
		<button
			aria-label="Close sidebar"
			class="fixed inset-0 z-40 w-full cursor-default bg-background/70 backdrop-blur-sm md:hidden"
			onclick={() => (sidebarOpen = false)}
		></button>
	{/if}

	<!-- Sidebar -->
	<div class="fixed inset-y-0 left-0 z-50 md:static md:block">
		<Sidebar bind:isOpen={sidebarOpen} onclose={() => (sidebarOpen = false)} />
	</div>

	<!-- Main chat area -->
	<ChatWindow bind:sidebarOpen />
</div>
