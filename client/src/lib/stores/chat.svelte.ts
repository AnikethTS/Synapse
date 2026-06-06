import type { ChatSession, Message } from '$lib/types';

const STORAGE_KEY = 'synapse_history';

function generateId(): string {
	return crypto.randomUUID();
}

function deriveTitle(firstMessage: string): string {
	return firstMessage.slice(0, 40) + (firstMessage.length > 40 ? '…' : '');
}

function loadFromStorage(): ChatSession[] {
	if (typeof localStorage === 'undefined') return [];
	try {
		const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]') as ChatSession[];
		// Revive Date objects that were serialized as strings
		return raw.map((s) => ({
			...s,
			messages: s.messages.map((m) => ({ ...m, timestamp: new Date(m.timestamp) }))
		}));
	} catch {
		return [];
	}
}

function saveToStorage(sessions: ChatSession[]): void {
	if (typeof localStorage === 'undefined') return;
	localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

function createChatStore() {
	const initialSessions = loadFromStorage();
	let sessions = $state<ChatSession[]>(initialSessions);
	let activeId = $state<string | null>(initialSessions[0]?.id ?? null);
	let streaming = $state(false);
	let isTyping = $state(false);
	let error = $state<string | null>(null);

	const activeSession = $derived(sessions.find((s) => s.id === activeId) ?? null);

	function newSession(): void {
		const session: ChatSession = {
			id: generateId(),
			title: 'New chat',
			messages: [],
			createdAt: Date.now()
		};
		sessions = [session, ...sessions];
		activeId = session.id;
		saveToStorage(sessions);
	}

	function selectSession(id: string): void {
		activeId = id;
	}

	function deleteSession(id: string): void {
		sessions = sessions.filter((s) => s.id !== id);
		if (activeId === id) activeId = sessions[0]?.id ?? null;
		saveToStorage(sessions);
	}

	function clearActiveSession(): void {
		if (!activeId) return;
		sessions = sessions.map((s) => (s.id === activeId ? { ...s, messages: [] } : s));
		saveToStorage(sessions);
	}

	function _updateSession(id: string, updater: (s: ChatSession) => ChatSession): void {
		sessions = sessions.map((s) => (s.id === id ? updater(s) : s));
		saveToStorage(sessions);
	}

	async function sendMessage(content: string, apiUrl: string): Promise<void> {
		if (streaming || !content.trim()) return;

		if (!activeId) newSession();
		const sessionId = activeId!;

		const userMsg: Message = {
			id: generateId(),
			role: 'user',
			content: content.trim(),
			timestamp: new Date()
		};

		_updateSession(sessionId, (s) => ({
			...s,
			title: s.messages.length === 0 ? deriveTitle(content) : s.title,
			messages: [...s.messages, userMsg]
		}));

		// Snapshot the outgoing history AFTER adding the user message
		const outgoing = (sessions.find((s) => s.id === sessionId)?.messages ?? []).map((m) => ({
			role: m.role,
			content: m.content
		}));

		streaming = true;
		isTyping = true;
		error = null;

		let assistantMsgId: string | null = null;
		let firstToken = true;

		try {
			const response = await fetch(`${apiUrl}/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ messages: outgoing })
			});

			if (!response.ok) throw new Error(`Server error: ${response.status} ${response.statusText}`);

			const reader = response.body?.getReader();
			if (!reader) throw new Error('No response body');

			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() ?? '';

				for (const line of lines) {
					if (!line.startsWith('data: ')) continue;
					const data = line.slice(6);
					if (data === '[DONE]') break;

					// Restore escaped newlines from backend
					const chunk = data.replace(/\\n/g, '\n');

					if (firstToken) {
						firstToken = false;
						isTyping = false;
						assistantMsgId = generateId();

						_updateSession(sessionId, (s) => ({
							...s,
							messages: [
								...s.messages,
								{
									id: assistantMsgId!,
									role: 'assistant',
									content: chunk,
									timestamp: new Date(),
									isStreaming: true
								}
							]
						}));
					} else {
						_updateSession(sessionId, (s) => {
							const msgs = [...s.messages];
							const last = msgs[msgs.length - 1];
							msgs[msgs.length - 1] = { ...last, content: last.content + chunk };
							return { ...s, messages: msgs };
						});
					}
				}
			}

			// Mark assistant message as done
			if (assistantMsgId) {
				_updateSession(sessionId, (s) => ({
					...s,
					messages: s.messages.map((m) =>
						m.id === assistantMsgId ? { ...m, isStreaming: false } : m
					)
				}));
			}
		} catch (err) {
			error =
				err instanceof Error
					? err.message === 'Failed to fetch'
						? 'Cannot reach the backend. Is it running on ' + apiUrl + '?'
						: err.message
					: 'An unexpected error occurred';
		} finally {
			isTyping = false;
			streaming = false;
		}
	}

	return {
		get sessions() { return sessions; },
		get activeSession() { return activeSession; },
		get activeId() { return activeId; },
		get streaming() { return streaming; },
		get isTyping() { return isTyping; },
		get error() { return error; },
		newSession,
		selectSession,
		deleteSession,
		clearActiveSession,
		sendMessage,
		dismissError: () => { error = null; }
	};
}

export const chat = createChatStore();
