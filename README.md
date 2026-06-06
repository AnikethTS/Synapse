# Synapse

![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A blazing-fast AI chat assistant built for developers. Synapse streams responses in real time from **Llama 3.3 70B** via **Groq**, renders Markdown with syntax-highlighted code blocks, and persists your chat history locally.

---

## Features

- **Streaming responses** — tokens appear as they are generated, no waiting for full replies
- **Markdown + syntax highlighting** — code blocks rendered with highlight.js (10+ languages)
- **Chat history** — sessions persisted in `localStorage`, survive page refreshes
- **Multi-session sidebar** — create, switch, and delete chat sessions
- **Mobile responsive** — collapsible sidebar, works on any screen size
- **Dark theme** — easy on the eyes for long coding sessions
- **Error handling** — clear messages when the backend is unreachable

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | SvelteKit 2 + TypeScript + Tailwind CSS v4 |
| Backend | FastAPI + Uvicorn |
| LLM | Llama 3.3 70B Versatile via Groq SDK |
| Package managers | pnpm (frontend) · uv (backend) |

---

## Prerequisites

- **Node.js** 18+ and **pnpm** (`npm install -g pnpm`)
- **Python** 3.11+ and **uv** (`pip install uv` or via [uv docs](https://docs.astral.sh/uv/))
- A free **Groq API key** → [console.groq.com](https://console.groq.com)

---

## Setup

### 1 · Backend

```bash
cd devmind/backend

# Copy and fill in your Groq API key
cp .env.example .env
# Edit .env and set GROQ_API_KEY=<your_key>

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Health check: `curl http://localhost:8000/health`

### 2 · Frontend

```bash
cd devmind/frontend

# Install dependencies
pnpm install

# Start the dev server
pnpm dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Getting a Groq API Key

1. Visit [console.groq.com](https://console.groq.com) and sign up (free)
2. Navigate to **API Keys** and create a new key
3. Paste it into `backend/.env` as `GROQ_API_KEY=<your_key>`

Groq's free tier is generous — Llama 3.3 70B runs at thousands of tokens per second.

---

## Project Structure

```
devmind/
├── backend/
│   ├── main.py            # FastAPI app — /chat streaming endpoint, /health
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # GROQ_API_KEY (git-ignored)
│   └── .env.example       # Template for .env
│
├── frontend/
│   ├── src/
│   │   ├── app.html        # HTML shell — CDN imports for marked.js & highlight.js
│   │   ├── app.css         # Tailwind CSS v4 entry point
│   │   ├── lib/
│   │   │   ├── types.ts              # Shared TypeScript interfaces
│   │   │   ├── stores/
│   │   │   │   └── chat.svelte.ts    # Reactive chat store (Svelte 5 runes)
│   │   │   └── components/
│   │   │       ├── Sidebar.svelte    # Session list + new chat button
│   │   │       ├── ChatWindow.svelte # Message list + empty state
│   │   │       ├── MessageBubble.svelte # Individual message with Markdown
│   │   │       └── ChatInput.svelte  # Auto-resizing textarea + send button
│   │   └── routes/
│   │       ├── +layout.svelte # Root layout
│   │       └── +page.svelte   # Main page — responsive shell
│   ├── .env               # PUBLIC_API_URL (git-ignored)
│   └── .env.example       # Template for .env
│
└── README.md
```

---

## API Reference

### `POST /chat`

Stream a chat completion.

**Request body:**
```json
{
  "messages": [
    { "role": "user", "content": "Explain closures in JavaScript" }
  ]
}
```

**Response:** `text/event-stream`

```
data: Sure\n
data: !\n
data:  A closure\n
...
data: [DONE]
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## License

MIT © 2025 — see [LICENSE](LICENSE) for details.
