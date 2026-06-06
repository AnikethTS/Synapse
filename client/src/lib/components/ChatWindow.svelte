<script lang="ts">
	import { tick } from 'svelte';
	import { chat } from '$lib/stores/chat.svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Compass, PanelLeftOpen } from '@lucide/svelte';
	import ChatInput from './ChatInput.svelte';
	import MessageBubble from './MessageBubble.svelte';
	import WelcomeScreen from './WelcomeScreen.svelte';
	import TypingIndicator from './TypingIndicator.svelte';

	let { sidebarOpen = $bindable(true) }: { sidebarOpen?: boolean } = $props();

	const apiUrl = PUBLIC_API_URL ?? 'http://localhost:8000';

	let scrollEl = $state<HTMLDivElement>();

	// Auto-scroll when messages or typing state changes
	$effect(() => {
		void chat.activeSession?.messages;
		void chat.isTyping;
		scrollToBottom();
	});

	async function scrollToBottom() {
		await tick();
		if (scrollEl) scrollEl.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' });
	}

	async function handleSend(content: string) {
		await chat.sendMessage(content, apiUrl);
	}

	const hasMessages = $derived(
		(chat.activeSession?.messages?.length ?? 0) > 0 || chat.isTyping
	);
</script>

<div class="relative flex h-dvh min-w-0 flex-1 flex-col">
	<!-- Top bar — only shown when sidebar is collapsed -->
	{#if !sidebarOpen}
		<div class="absolute inset-x-0 top-0 z-10 flex items-center gap-3 border-b border-border/50 bg-background/90 px-4 py-3 backdrop-blur-sm">
			<button
				onclick={() => (sidebarOpen = true)}
				aria-label="Open sidebar"
				class="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
			>
				<PanelLeftOpen class="h-4 w-4" />
			</button>
			<div class="flex items-center gap-2 text-sm font-semibold text-foreground">
				<div class="flex h-5 w-5 items-center justify-center rounded-md bg-primary">
					<Compass class="h-3 w-3 text-primary-foreground" strokeWidth={2} />
				</div>
				Synapse
			</div>
		</div>
	{/if}

	<!-- Error banner -->
	{#if chat.error}
		<div class="mx-4 mt-14 flex items-start gap-3 rounded-xl border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive-foreground">
			<svg class="mt-0.5 h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
			</svg>
			<span class="flex-1">{chat.error}</span>
			<button onclick={chat.dismissError} class="text-muted-foreground hover:text-foreground">✕</button>
		</div>
	{/if}

	<!-- Scroll area -->
	<div
		bind:this={scrollEl}
		class={['flex-1 overflow-y-auto', !sidebarOpen ? 'pt-12' : 'pt-4'].join(' ')}
	>
		{#if !hasMessages}
			<WelcomeScreen onSelectPrompt={handleSend} />
		{:else}
			<div class="flex flex-col pb-6 pt-2">
				{#each chat.activeSession?.messages ?? [] as message (message.id)}
					<MessageBubble {message} />
				{/each}

				<!-- Typing indicator — shown while waiting for first token -->
				{#if chat.isTyping}
					<div class="mx-auto flex w-full max-w-3xl items-center gap-3.5 px-5 py-4 md:px-8">
						<div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary shadow-[0_0_12px_hsl(var(--primary)/0.3)]">
							<Compass class="h-3.5 w-3.5 text-primary-foreground" strokeWidth={2} />
						</div>
						<div class="flex h-7 items-center text-muted-foreground">
							<TypingIndicator />
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Input bar with gradient fade -->
	<div class="w-full bg-gradient-to-t from-background via-background/98 to-transparent pt-5">
		<ChatInput onsubmit={handleSend} disabled={chat.streaming} />
	</div>
</div>
