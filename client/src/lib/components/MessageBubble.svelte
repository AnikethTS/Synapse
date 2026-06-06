<script lang="ts">
	import type { Message } from '$lib/types';
	import { tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { Compass, Copy, ThumbsUp, ThumbsDown } from '@lucide/svelte';

	let { message }: { message: Message } = $props();

	const isUser = $derived(message.role === 'user');

	let el = $state<HTMLDivElement>();
	let copied = $state(false);

	function formatTime(date: Date) {
		return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
	}

	async function copyMessage() {
		await navigator.clipboard.writeText(message.content);
		copied = true;
		setTimeout(() => (copied = false), 1800);
	}

	// Re-render markdown whenever content changes
	$effect(() => {
		void message.content;
		renderMarkdown();
	});

	async function renderMarkdown() {
		if (!el || message.role !== 'assistant') return;
		await tick();

		// @ts-expect-error CDN globals
		const marked = window.marked;
		// @ts-expect-error CDN globals
		const hljs = window.hljs;
		if (!marked || !hljs) return;

		const renderer = new marked.Renderer();

		// Custom code block with language label + copy button
		renderer.code = (code: string, lang: string) => {
			const validLang = lang && hljs.getLanguage(lang) ? lang : '';
			const highlighted = validLang
				? hljs.highlight(code, { language: validLang }).value
				: hljs.highlightAuto(code).value;
			// Escape quotes for the data attribute
			const safeCode = code.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
			return `<div class="code-block relative rounded-lg overflow-hidden my-3 border border-[hsl(var(--border))]">
  <div class="flex items-center justify-between px-4 py-1.5 bg-[hsl(0_0%_8%)] border-b border-[hsl(0_0%_12%)]">
    <span class="text-[10px] font-semibold uppercase tracking-widest opacity-50 font-mono">${validLang || 'text'}</span>
    <button class="copy-code-btn flex items-center gap-1 text-[10px] text-muted-foreground/60 hover:text-muted-foreground transition-colors" data-code="${safeCode}">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      Copy
    </button>
  </div>
  <pre class="!m-0 !rounded-none overflow-x-auto bg-[hsl(0_0%_6%)] p-4"><code class="hljs${validLang ? ' language-' + validLang : ''} !bg-transparent">${highlighted}</code></pre>
</div>`;
		};

		marked.use({ renderer, breaks: true, gfm: true });
		el.innerHTML = marked.parse(message.content || '');

		// Wire up in-DOM copy buttons after render
		el.querySelectorAll<HTMLButtonElement>('.copy-code-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				const raw = btn.dataset.code ?? '';
				// Unescape HTML entities
				const txt = raw
					.replace(/&quot;/g, '"')
					.replace(/&amp;/g, '&')
					.replace(/&#39;/g, "'");
				navigator.clipboard.writeText(txt);
				btn.textContent = 'Copied!';
				setTimeout(() => {
					btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy`;
				}, 1500);
			});
		});
	}
</script>

<div
	in:fly={{ y: 8, duration: 280, easing: cubicOut }}
	class={['group flex w-full max-w-3xl mx-auto px-5 md:px-8 py-5 gap-3.5', isUser ? 'flex-row-reverse' : 'flex-row'].join(' ')}
>
	<!-- Avatar -->
	<div class="mt-0.5 shrink-0">
		{#if isUser}
			<div class="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-secondary text-[10px] font-semibold text-secondary-foreground">
				ME
			</div>
		{:else}
			<div class="flex h-7 w-7 items-center justify-center rounded-lg bg-primary shadow-[0_0_12px_hsl(var(--primary)/0.3)]">
				<Compass class="h-3.5 w-3.5 text-primary-foreground" strokeWidth={2} />
			</div>
		{/if}
	</div>

	<!-- Content -->
	<div class={['flex max-w-[88%] flex-col gap-1.5', isUser ? 'items-end' : 'items-start'].join(' ')}>
		<!-- Timestamp — visible on group hover -->
		<div class="flex items-center gap-1.5 text-[11px] text-muted-foreground/0 transition-colors duration-150 group-hover:text-muted-foreground/70">
			<span class="font-medium">{isUser ? 'You' : 'Synapse'}</span>
			<span class="opacity-50">·</span>
			<span>{formatTime(message.timestamp)}</span>
		</div>

		<!-- Message body -->
		{#if isUser}
			<div class="max-w-full rounded-2xl rounded-tr-md border border-border bg-secondary px-4 py-2.5 text-sm leading-relaxed text-secondary-foreground">
				<p class="m-0 whitespace-pre-wrap">{message.content}</p>
			</div>
		{:else}
			<div
				bind:this={el}
				class="prose prose-sm dark:prose-invert max-w-none leading-relaxed text-foreground
					prose-p:my-1.5 prose-ul:my-1.5 prose-li:my-0.5
					prose-code:rounded prose-code:border prose-code:border-border prose-code:bg-secondary prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[0.82em]
					[&_pre]:!p-0 [&_pre_code]:block"
			></div>
			<!-- Streaming cursor -->
			{#if message.isStreaming}
				<span class="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-primary"></span>
			{/if}
		{/if}

		<!-- Action buttons — assistant only, shown on hover after streaming -->
		{#if !isUser && !message.isStreaming}
			<div class="mt-1 flex items-center gap-0.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
				<button
					onclick={copyMessage}
					title={copied ? 'Copied!' : 'Copy'}
					class="rounded-md p-1.5 text-muted-foreground/60 transition-colors hover:bg-secondary hover:text-foreground"
				>
					<Copy class="h-3.5 w-3.5" />
				</button>
				<button
					title="Good response"
					class="rounded-md p-1.5 text-muted-foreground/60 transition-colors hover:bg-secondary hover:text-foreground"
				>
					<ThumbsUp class="h-3.5 w-3.5" />
				</button>
				<button
					title="Bad response"
					class="rounded-md p-1.5 text-muted-foreground/60 transition-colors hover:bg-secondary hover:text-foreground"
				>
					<ThumbsDown class="h-3.5 w-3.5" />
				</button>
			</div>
		{/if}
	</div>
</div>
