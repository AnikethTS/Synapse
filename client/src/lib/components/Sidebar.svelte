<script lang="ts">
	import { fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { chat } from '$lib/stores/chat.svelte';
	import { themeStore } from '$lib/stores/theme.svelte';
	import {
		Compass,
		Plus,
		MessageSquare,
		Settings,
		Moon,
		Sun,
		PanelLeftClose,
		PanelLeftOpen
	} from '@lucide/svelte';

	let {
		isOpen = $bindable(true),
		onclose
	}: { isOpen?: boolean; onclose?: () => void } = $props();

	// Group sessions by recency
	const grouped = $derived(() => {
		const now = Date.now();
		const ms = (days: number) => days * 86_400_000;

		const today: typeof chat.sessions = [];
		const yesterday: typeof chat.sessions = [];
		const last7: typeof chat.sessions = [];
		const older: typeof chat.sessions = [];

		for (const s of chat.sessions) {
			const age = now - s.createdAt;
			if (age < ms(1)) today.push(s);
			else if (age < ms(2)) yesterday.push(s);
			else if (age < ms(7)) last7.push(s);
			else older.push(s);
		}

		return [
			{ label: 'Today', key: 'today', items: today },
			{ label: 'Yesterday', key: 'yesterday', items: yesterday },
			{ label: 'Last 7 days', key: 'last7', items: last7 },
			{ label: 'Older', key: 'older', items: older }
		].filter((g) => g.items.length > 0);
	});

	function handleNewChat() {
		chat.newSession();
		onclose?.();
	}

	function handleSelect(id: string) {
		chat.selectSession(id);
		onclose?.();
	}
</script>

{#if isOpen}
	<aside
		transition:fly={{ x: -16, duration: 220, easing: cubicOut }}
		class="flex h-dvh w-[240px] flex-shrink-0 flex-col border-r border-sidebar-border bg-sidebar"
	>
		<!-- Header -->
		<div class="flex items-center justify-between px-4 py-4">
			<div class="flex select-none items-center gap-2.5">
				<div
					class="flex h-6 w-6 items-center justify-center rounded-md bg-sidebar-primary shadow-sm"
				>
					<Compass class="h-3.5 w-3.5 text-sidebar-primary-foreground" strokeWidth={2} />
				</div>
				<span class="text-sm font-semibold tracking-tight text-sidebar-foreground">Synapse</span>
			</div>
			<button
				onclick={() => { isOpen = false; onclose?.(); }}
				class="rounded-md p-1.5 text-sidebar-foreground/40 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground md:hidden"
				aria-label="Close sidebar"
			>
				<PanelLeftClose class="h-4 w-4" />
			</button>
		</div>

		<!-- New Chat -->
		<div class="px-3 pb-3">
			<button
				onclick={handleNewChat}
				class="flex w-full items-center gap-2 rounded-lg border border-sidebar-border bg-sidebar-accent px-3 py-2 text-sm font-medium text-sidebar-accent-foreground transition-all hover:border-primary/30 hover:bg-sidebar-accent/80"
			>
				<Plus class="h-4 w-4 text-primary" strokeWidth={2.5} />
				New Chat
			</button>
		</div>

		<!-- History -->
		<nav class="flex-1 space-y-5 overflow-y-auto px-2 py-1">
			{#if chat.sessions.length === 0}
				<p class="mt-4 px-2 text-center text-xs text-sidebar-foreground/40">No chats yet</p>
			{:else}
				{#each grouped() as group (group.key)}
					<div class="space-y-0.5">
						<p class="px-2 pb-1 text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/35">
							{group.label}
						</p>
						{#each group.items as session (session.id)}
							<div class="group/item relative flex items-center">
								<button
									onclick={() => handleSelect(session.id)}
									class={[
										'flex w-full items-center gap-2.5 rounded-md px-2 py-1.5 text-left text-xs transition-colors',
										chat.activeId === session.id
											? 'bg-sidebar-accent text-sidebar-foreground'
											: 'text-sidebar-foreground/65 hover:bg-sidebar-accent hover:text-sidebar-foreground'
									].join(' ')}
								>
									<MessageSquare
										class="h-3 w-3 shrink-0 opacity-40 transition-opacity group-hover/item:opacity-70"
									/>
									<span class="truncate">{session.title}</span>
								</button>
								<button
									onclick={() => chat.deleteSession(session.id)}
									class="absolute right-1 hidden rounded p-1 text-sidebar-foreground/30 transition-colors hover:text-red-400 group-hover/item:block"
									aria-label="Delete chat"
								>
									<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>
						{/each}
					</div>
				{/each}
			{/if}
		</nav>

		<!-- Footer -->
		<div class="flex items-center justify-between gap-2 border-t border-sidebar-border p-3">
			<!-- User profile -->
			<button class="-ml-0.5 flex min-w-0 flex-1 items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-sidebar-accent">
				<div
					class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-sidebar-border bg-sidebar-primary text-[10px] font-bold text-sidebar-primary-foreground"
				>
					U
				</div>
				<div class="flex min-w-0 flex-col items-start">
					<span class="truncate text-xs font-medium text-sidebar-foreground">User</span>
					<span class="text-[10px] text-sidebar-foreground/45">Free plan</span>
				</div>
			</button>

			<!-- Theme toggle + settings -->
			<div class="flex shrink-0 items-center gap-0.5">
				<button
					onclick={themeStore.toggle}
					title="Toggle theme"
					class="rounded-md p-1.5 text-sidebar-foreground/45 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground"
				>
					{#if themeStore.theme === 'dark'}
						<Sun class="h-3.5 w-3.5" />
					{:else}
						<Moon class="h-3.5 w-3.5" />
					{/if}
				</button>
				<button
					class="rounded-md p-1.5 text-sidebar-foreground/45 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground"
					aria-label="Settings"
				>
					<Settings class="h-3.5 w-3.5" />
				</button>
			</div>
		</div>
	</aside>
{:else}
	<!-- Collapsed — floating open button -->
	<button
		onclick={() => { isOpen = true; }}
		class="fixed left-4 top-4 z-50 rounded-md border border-border bg-background p-2 text-muted-foreground shadow-sm transition-colors hover:bg-secondary hover:text-foreground"
		aria-label="Open sidebar"
	>
		<PanelLeftOpen class="h-4 w-4" />
	</button>
{/if}
