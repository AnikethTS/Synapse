type Theme = 'light' | 'dark';

function createThemeStore() {
	const getStored = (): Theme => {
		if (typeof localStorage === 'undefined') return 'dark';
		return (localStorage.getItem('synapse-theme') as Theme) ?? 'dark';
	};

	let theme = $state<Theme>(getStored());

	function apply(t: Theme) {
		if (typeof document === 'undefined') return;
		document.documentElement.classList.toggle('dark', t === 'dark');
	}

	function setTheme(t: Theme) {
		theme = t;
		if (typeof localStorage !== 'undefined') localStorage.setItem('synapse-theme', t);
		apply(t);
	}

	// Apply immediately on module load (client only)
	if (typeof document !== 'undefined') apply(getStored());

	return {
		get theme() { return theme; },
		setTheme,
		toggle: () => setTheme(theme === 'dark' ? 'light' : 'dark')
	};
}

export const themeStore = createThemeStore();
