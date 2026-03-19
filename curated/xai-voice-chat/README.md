# xAI Voice Chat

Real-time voice chat webapp powered by xAI's Realtime Audio API with swappable LLM backends. Talk naturally — xAI handles the voice, your chosen LLM handles the thinking.

## Features

- **Real-time voice conversation** with server-side VAD (Voice Activity Detection)
- **Multi-LLM support** — swap between Grok, OpenAI, Anthropic, and Gemini mid-session
- **Two Grok modes** — all-in-one (fastest) or custom model selection
- **Streaming TTS** via xAI WebSocket (`wss://api.x.ai/v1/tts`) with REST MP3 fallback
- **5 voice options** — Eve, Ara, Rex, Sal, Leo
- **GUI settings** — all API keys managed in-browser, no `.env` needed
- **Live model switching** — change LLM provider/model without disconnecting
- **Mic selector** — choose your input device
- **Stop button** — interrupt speech at any time

## Architecture

### Grok All-in-One Mode

```
┌──────────┐         ┌─────────────────────────────────┐         ┌──────────┐
│          │  audio   │    wss://api.x.ai/v1/realtime   │  audio  │          │
│  Browser ├────────►│                                   ├────────►│ Speaker  │
│   (mic)  │◄────────┤   ASR  +  Grok LLM  +  TTS      │◄────────┤          │
│          │         │       (single WebSocket)          │         │          │
└──────────┘         └─────────────────────────────────┘         └──────────┘
```

Everything flows through one WebSocket. Lowest latency. You cannot choose which Grok model is used — xAI controls it.

### External LLM Mode (OpenAI / Anthropic / Gemini / Grok Custom)

```
┌──────────┐         ┌─────────────────────────┐
│          │  audio   │  wss://api.x.ai/v1/     │
│  Browser ├────────►│  realtime                │
│   (mic)  │         │  (ASR + VAD only)        │
│          │         └───────────┬──────────────┘
│          │                     │ transcription
│          │                     ▼
│          │         ┌─────────────────────────┐
│          │         │  Selected LLM API       │
│          │         │  ┌───────────────────┐  │
│          │         │  │ OpenAI /v1/chat   │  │
│          │         │  │ Anthropic /v1/msg │  │
│          │         │  │ Gemini generate   │  │
│          │         │  │ xAI /v1/chat      │  │
│          │         │  └───────────────────┘  │
│          │         └───────────┬──────────────┘
│          │                     │ response text
│          │                     ▼
│          │         ┌─────────────────────────┐
│          │  audio   │  wss://api.x.ai/v1/tts │
│          │◄────────┤  (Streaming PCM TTS)    │
│          │         │  or POST /v1/tts (MP3)  │
└──────────┘         └─────────────────────────┘
```

Three xAI endpoints used:

| Endpoint | Purpose | Protocol |
|---|---|---|
| `wss://api.x.ai/v1/realtime` | ASR + VAD (always connected) | WebSocket |
| `wss://api.x.ai/v1/tts` | Streaming TTS (default) | WebSocket |
| `POST /v1/tts` | REST TTS (fallback) | HTTP |

## Project Structure

```
xai-voice-chat/
├── server.js              # Node.js backend (Express + WebSocket)
├── public/
│   └── index.html         # Single-page frontend (vanilla JS)
├── package.json
└── README.md
```

### Server (`server.js`)

```
┌─────────────────────────────────────────────────────────┐
│                    Express Server                        │
│                                                         │
│  ┌──────────────────┐   ┌────────────────────────────┐ │
│  │  REST Endpoints   │   │  WebSocket Handler         │ │
│  │                   │   │                            │ │
│  │  POST /validate   │   │  Browser ◄──► Server       │ │
│  │  Static files     │   │     │                      │ │
│  └──────────────────┘   │     ├── config / config.update│
│                          │     ├── audio passthrough   │ │
│                          │     ├── stop / cancel       │ │
│                          │     │                      │ │
│                          │  ┌──┴──────────────────┐   │ │
│                          │  │  xAI Realtime WS    │   │ │
│                          │  │  (per-session)      │   │ │
│                          │  └─────────────────────┘   │ │
│                          │  ┌─────────────────────┐   │ │
│                          │  │  xAI TTS WS         │   │ │
│                          │  │  (per-utterance)    │   │ │
│                          │  └─────────────────────┘   │ │
│                          │  ┌─────────────────────┐   │ │
│                          │  │  External LLM call  │   │ │
│                          │  │  (fetch)            │   │ │
│                          │  └─────────────────────┘   │ │
│                          └────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Key server responsibilities:**
- Proxies browser audio to xAI Realtime API (keeps API key server-side)
- In external LLM mode: cancels Grok auto-responses, intercepts transcription, routes to chosen LLM, pipes response to TTS
- Supports hot-swapping LLM provider/model via `config.update` message
- Manages per-session state (provider, model, keys, conversation history, voice)

### Client (`public/index.html`)

Single HTML file with embedded CSS and JS. No build step, no framework.

**Audio pipeline:**
1. **Capture**: `getUserMedia` → `ScriptProcessorNode` → Float32 → PCM16 → base64
2. **Send**: WebSocket `input_audio_buffer.append` events to server
3. **Receive**: PCM16 base64 chunks (`response.output_audio.delta`) or MP3 blob (`tts.audio`)
4. **Playback**: PCM → `AudioContext.createBufferSource` queue, or MP3 → `Audio` element

**State management:**
- All settings persisted in `localStorage`
- API keys stored client-side, sent to server on each connection
- No cookies, no server-side storage

## Data Flow (External LLM Mode)

```
 Browser                    Server                     xAI APIs              LLM API
   │                          │                          │                     │
   │──── audio chunks ───────►│                          │                     │
   │                          │──── audio chunks ───────►│ Realtime WS         │
   │                          │                          │ (ASR + VAD)         │
   │                          │                          │                     │
   │                          │◄─── speech_started ──────│                     │
   │◄─── speech_started ──────│                          │                     │
   │                          │                          │                     │
   │                          │◄─── speech_stopped ──────│                     │
   │◄─── speech_stopped ──────│                          │                     │
   │                          │                          │                     │
   │                          │◄─── transcription ───────│                     │
   │◄─── transcription ───────│                          │                     │
   │                          │                          │                     │
   │                          │◄─── response.created ────│                     │
   │                          │──── response.cancel ────►│ (block Grok LLM)    │
   │                          │                          │                     │
   │◄─── llm.thinking ────────│                          │                     │
   │                          │──── chat request ───────────────────────────►│
   │                          │◄─── chat response ──────────────────────────│
   │◄─── llm.response ────────│                          │                     │
   │                          │                          │                     │
   │                          │──── text.delta ─────────►│ TTS WS              │
   │                          │──── text.done ──────────►│                     │
   │                          │◄─── audio.delta ────────│                     │
   │◄─── audio delta ─────────│                          │                     │
   │                          │◄─── audio.done ─────────│                     │
   │◄─── tts.done ────────────│                          │                     │
   │                          │                          │                     │
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/Enconvo/skills.git
cd skills/curated/xai-voice-chat
npm install

# Start
npm start
# → http://localhost:3000
```

1. Open **http://localhost:3000**
2. Click the **gear icon** → set your xAI API key → Validate
3. (Optional) Add OpenAI / Anthropic / Gemini keys for external LLM
4. Click the **orb** to connect
5. **Talk** — server VAD auto-detects speech

## Configuration

All configuration is done through the in-app **Settings** panel:

| Setting | Description |
|---|---|
| **Provider** | Grok, OpenAI, Anthropic, Gemini |
| **Grok Mode** | All-in-one (fastest) or Custom model |
| **Model** | Provider-specific, fetched dynamically |
| **Voice** | Eve, Ara, Rex, Sal, Leo |
| **TTS Mode** | Realtime (Streaming WS) or REST (MP3) |
| **Microphone** | Select input device |

Settings persist in `localStorage` across sessions. API keys are sent to the server per-connection and never stored on disk.

## API Endpoints Used

### xAI
| Endpoint | Use |
|---|---|
| `wss://api.x.ai/v1/realtime` | Voice agent (ASR + VAD + LLM + TTS in all-in-one mode) |
| `wss://api.x.ai/v1/tts` | Streaming text-to-speech (external LLM mode) |
| `POST /v1/tts` | REST text-to-speech fallback |
| `POST /v1/chat/completions` | Grok custom model LLM |
| `GET /v1/models` | Model listing |

### External LLMs
| Provider | Endpoint |
|---|---|
| OpenAI | `POST /v1/chat/completions` |
| Anthropic | `POST /v1/messages` |
| Gemini | `POST /v1beta/models/{model}:generateContent` |

## Tech Stack

- **Backend**: Node.js, Express, `ws` (WebSocket)
- **Frontend**: Vanilla HTML/CSS/JS, Web Audio API
- **Voice**: xAI Realtime API, xAI TTS API
- **Audio**: PCM16 @ 24kHz mono, base64-encoded over WebSocket

## License

MIT
