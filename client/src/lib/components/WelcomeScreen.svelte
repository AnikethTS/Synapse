<script lang="ts">
	import { Compass, Sparkles, FileText, Code2, PlaneTakeoff } from '@lucide/svelte';

	let { onSelectPrompt }: { onSelectPrompt: (prompt: string) => void } = $props();

	const suggestions = [
		{
			icon: Sparkles,
			title: 'Explain quantum computing',
			prompt: 'Explain quantum computing in simple terms for a beginner.'
		},
		{
			icon: FileText,
			title: 'Write a cover letter',
			prompt: 'Write a professional cover letter for a software engineering role.'
		},
		{
			icon: Code2,
			title: 'Debug my Python code',
			prompt: 'Can you help me debug a Python function? I have an issue with lists.'
		},
		{
			icon: PlaneTakeoff,
			title: 'Plan a trip to Tokyo',
			prompt: 'Plan a 3-day itinerary for a trip to Tokyo, focusing on culture and food.'
		}
	];
</script>

<div class="flex h-full w-full max-w-3xl mx-auto flex-col items-center justify-center px-6 md:px-10 mt-12 mb-28">
	<!-- Logo & heading -->
	<div class="mb-11 text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
		<div
			class="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-primary shadow-[0_0_24px_hsl(var(--primary)/0.28)]"
		>
			<Compass class="h-7 w-7 text-primary-foreground" strokeWidth={1.75} />
		</div>
		<h1 class="mb-2.5 text-[1.75rem] font-semibold tracking-tight text-foreground">
			How can I help you today?
		</h1>
		<p class="mx-auto max-w-sm text-sm font-light leading-relaxed text-muted-foreground">
			Synapse is built for complex reasoning, creative work, and technical problem solving.
		</p>
	</div>

	<!-- Suggestion cards -->
	<div class="grid w-full max-w-xl grid-cols-1 gap-2.5 sm:grid-cols-2">
		{#each suggestions as s, i}
			{@const Icon = s.icon}
			<button
				onclick={() => onSelectPrompt(s.prompt)}
				style="animation-delay: {i * 70 + 200}ms"
				class="group flex animate-in fade-in slide-in-from-bottom-4 fill-mode-both duration-350 flex-col items-start rounded-xl border border-border bg-card p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[0_4px_16px_hsl(var(--primary)/0.10)] active:scale-[0.98]"
			>
				<div class="mb-3 rounded-lg bg-primary/10 p-1.5 text-primary transition-colors group-hover:bg-primary/15">
					<Icon class="h-4 w-4" />
				</div>
				<span class="text-sm font-medium leading-snug text-foreground">{s.title}</span>
				<span class="mt-1 line-clamp-1 text-xs font-light text-muted-foreground">{s.prompt}</span>
			</button>
		{/each}
	</div>
</div>
