export interface Message {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
	isStreaming?: boolean;
}

export interface ChatSession {
	id: string;
	title: string;
	messages: Message[];
	createdAt: number;
}
