<script lang="ts">
	import { ArrowUp, Paperclip, Mic, ChevronDown } from '@lucide/svelte';

	let {
		onsubmit,
		disabled = false
	}: { onsubmit: (message: string) => void; disabled?: boolean } = $props();

	let value = $state('');
	let textarea = $state<HTMLTextAreaElement>();
	let modelOpen = $state(false);
	let selectedModel = $state('Llama 3.3 70B');

	const models = ['Llama 3.3 70B', 'Llama 3.1 8B', 'Mixtral 8×7B'];
	const canSend = $derived(value.trim().length > 0 && !disabled);

	function submit() {
		if (!canSend) return;
		onsubmit(value.trim());
		value = '';
		if (textarea) textarea.style.height = 'auto';
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}

	function autoResize() {
		if (!textarea) return;
		textarea.style.height = 'auto';
		textarea.style.height = Math.min(textarea.scrollHeight, 130) + 'px';
	}
</script>

<!-- Close model dropdown on outside click -->
<svelte:window onclick={(e) => { if (!(e.target as Element)?.closest('.model-select')) modelOpen = false; }} />

<div class="w-full max-w-3xl mx-auto px-5 md:px-8 pb-5">
	<div
		class={[
			'relative overflow-hidden rounded-2xl border bg-card shadow-sm transition-all duration-200',
			canSend
				? 'border-primary/40 shadow-[0_0_0_1px_hsl(var(--primary)/0.15),0_4px_20px_hsl(0_0%_0%/0.25)]'
				: 'border-border focus-within:border-border/80'
		].join(' ')}
	>
		<textarea
			bind:this={textarea}
			bind:value
			oninput={autoResize}
			onkeydown={handleKeydown}
			{disabled}
			placeholder="Message Synapse…"
			rows={1}
			class="min-h-[52px] max-h-[130px] w-full resize-none bg-transparent px-4 pb-2 pt-4 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground/50 disabled:opacity-50"
		></textarea>

		<div class="flex items-center justify-between px-3 pb-2.5">
			<!-- Left: model picker + attach + mic -->
			<div class="flex items-center gap-1">
				<!-- Model selector -->
				<div class="model-select relative">
					<button
						onclick={() => (modelOpen = !modelOpen)}
						class="flex h-7 items-center gap-1 rounded-md px-2 text-[11px] font-medium text-muted-foreground/70 transition-colors hover:bg-secondary hover:text-muted-foreground"
					>
						{selectedModel}
						<ChevronDown class="h-3 w-3 opacity-60" />
					</button>
					{#if modelOpen}
						<div class="absolute bottom-full left-0 mb-1 min-w-[160px] rounded-lg border border-border bg-popover py-1 shadow-lg">
							{#each models as model}
								<button
									onclick={() => { selectedModel = model; modelOpen = false; }}
									class={[
										'flex w-full items-center px-3 py-1.5 text-left text-xs transition-colors hover:bg-secondary',
										model === selectedModel ? 'text-primary' : 'text-foreground'
									].join(' ')}
								>
									{model}
								</button>
							{/each}
						</div>
					{/if}
				</div>

				<div class="mx-0.5 h-3.5 w-px bg-border"></div>

				<button
					class="rounded-md p-1.5 text-muted-foreground/50 transition-colors hover:bg-secondary hover:text-muted-foreground"
					title="Attach file"
					aria-label="Attach file"
				>
					<Paperclip class="h-3.5 w-3.5" />
				</button>
				<button
					class="rounded-md p-1.5 text-muted-foreground/50 transition-colors hover:bg-secondary hover:text-muted-foreground"
					title="Voice input"
					aria-label="Voice input"
				>
					<Mic class="h-3.5 w-3.5" />
				</button>
			</div>

			<!-- Right: hint + send -->
			<div class="flex items-center gap-3">
				<span class="hidden font-mono text-[10px] tracking-wide text-muted-foreground/40 sm:inline">
					⏎ send · ⇧⏎ newline
				</span>
				<button
					onclick={submit}
					{disabled}
					class={[
						'flex h-8 w-8 items-center justify-center rounded-full transition-all duration-200 active:scale-[0.92]',
						canSend
							? 'bg-primary text-primary-foreground shadow-[0_0_12px_hsl(var(--primary)/0.4)] hover:brightness-110'
							: 'bg-secondary text-muted-foreground/40'
					].join(' ')}
					aria-label="Send message"
				>
					<ArrowUp class="h-4 w-4" strokeWidth={2.5} />
				</button>
			</div>
		</div>
	</div>

	<p class="mt-2.5 text-center text-[11px] tracking-wide text-muted-foreground/40">
		Synapse can make mistakes — verify important information.
	</p>
</div>
