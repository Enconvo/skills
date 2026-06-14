# EnConvo Settings Docs Map

Use this module when the user wants a live walkthrough of EnConvo setup or the EnConvo Settings User Guide v3. Canonical guide: `https://enconvo-settings-guide-v3.vercel.app/`. Local fallback when the deployed guide is unavailable: `file:///Users/zanearcher/Documents/Codex/2026-05-25/use-ai-tutor-skill-to-help/enconvo-settings-guide-v3/index.html`.

## Contents

- Access Boundaries
- Core URLs And Anchors
- Feature Inventory
- Domain Concepts
- Vocabulary Bridge
- Privacy And Safety
- Deep-Link And Synchronization Notes
- EnConvo Setup Coverage
- Default Teaching Paths

## Access Boundaries

- **Public/no login:** the Vercel guide, its screenshots, and non-secret setup instructions.
- **Native app/user account:** live EnConvo Settings panes, provider account state, installed agents, tools, skills, shortcuts, dictation history, recordings, memory, logs, and credentials.
- Never expose API keys, OAuth codes, tokens, callback URLs, logs, recordings, memory contents, private knowledge sources, personal email addresses, or account identifiers. If a screenshot or visible pane contains sensitive data, describe the path and ask the user before proceeding.
- Do not click destructive controls, validate credentials, reconnect OAuth, enable scheduled jobs, submit broker/live actions, delete memory, reset settings, or change provider defaults unless the user explicitly asks for that exact action.

## Opening EnConvo

- Preferred live-walkthrough entry: press `Cmd+Shift+D` to bring EnConvo/Smart Bar to the front. Once Smart Bar or EnConvo is active, press `Cmd+,` to open EnConvo's global Settings UI.
- Settings fallback: with EnConvo active, click the macOS menu bar path EnConvo -> Settings.
- If Settings does not appear, bring Smart Bar forward again with `Cmd+Shift+D`, wait for EnConvo to be active, then press `Cmd+,` once more. Verify the visible front window is Settings before teaching or changing anything.

## Core URLs And Anchors

- Guide home: `https://enconvo-settings-guide-v3.vercel.app/`
- Local fallback: `file:///Users/zanearcher/Documents/Codex/2026-05-25/use-ai-tutor-skill-to-help/enconvo-settings-guide-v3/index.html`
- Global Providers: `#global-providers`
- Global AI Model: `#global-providers-ai-model`
- Global AI Model OpenAI setup: `#global-ai-model-openai-global-provider-setup`
- OpenAI OAuth2: `#global-ai-model-openai-oauth2-connect-or-reconnect`
- OpenAI ApiKey: `#global-ai-model-openai-apikey-setup`
- Text-to-Speech: `#global-providers-text-to-speech`
- Agent List: `#agents-agent-list`
- Create New Agent: `#agent-list-create-create-new-agent-menu`
- Mavis agent overview: `#agent-mavis`
- Agent AI Model override: `#agent-mavis-ai-model-override`
- Agent Tools manager: `#agent-mavis-tools-manager`
- Agent More runtime settings: `#agent-mavis-more-runtime-settings`
- Credential Management: `#credential-management-credential-management`
- Dictation models: `#dictation-transcription-dictation-models`
- Dictation behavior: `#dictation-transcription-dictation`
- KnowledgeBase: `#knowledgebase-knowledgebase`
- Shortcut Settings: `#general-shortcut-settings`
- Developer Tools: `#developer-developer-tools`
- Logging: `#developer-logging`
- APIs: `#developer-apis`

## Feature Inventory

| Feature | Access | What it shows | Teaching use |
| --- | --- | --- | --- |
| Global Providers | guide + app | app-wide AI model, TTS, web search, image/video, web fetch, OCR defaults | Teach what new agents inherit |
| Credential sheets | app, sensitive | OAuth2/API-key setup, provider account state, validation controls | Teach credential branches without exposing secrets |
| Agents > Agent List | guide + app | create/select agents and edit tabs | Teach agent-level overrides and structure |
| Agent Definition | guide + app | instruction, user message, working folder, prompt files | Teach behavior shaping and prompt leaves |
| Agent AI Model | guide + app | global provider inheritance or per-agent provider override | Teach when to override app defaults |
| Agent Tools / Skills | guide + app | enabled tools, tool settings, skill access | Teach capability boundaries |
| Text to Speech | guide + app | global or agent voice provider/voice settings | Teach spoken-output setup when needed |
| More runtime settings | guide + app | dynamic context, live screen, tutor mode, run mode, language, memory | Teach runtime behavior carefully |
| Shortcuts | guide + app | keyboard triggers for Smart Bar, Chat Window, Sidebar, Dictation, Voice Command | Teach conflict-safe shortcut setup |
| Dictation & Transcription | guide + app, sensitive | STT/ASR providers, dictation behavior, recordings/history | Teach voice input while protecting recordings |
| KnowledgeBase | guide + app, sensitive | knowledge sources and indexing | Teach source setup without exposing private files |
| Developer panes | guide + app, sensitive | diagnostics, logs, APIs, CLI, reset controls | Teach diagnostics; avoid destructive actions |

## Domain Concepts

- **Global Providers** are app-level defaults. New agents inherit these unless an agent overrides them.
- **Agent override** means a specific agent uses its own model, TTS, tools, or runtime behavior instead of the global default.
- **Credential Provider** is the account/key route a provider uses. The pencil usually edits local provider setup; the gear usually opens central Credential Management.
- **OAuth2** means browser account authorization. **ApiKey** means direct provider key setup.
- **EnConvo Cloud Plan** means EnConvo-managed provider access through the user's subscription; direct providers use the user's own credential.
- **Tools and Skills** define what an agent can do; enable only what the agent needs.
- **Dynamic Context, Live Screen, Tutor Mode, Run Mode, and Memory** affect runtime behavior and privacy footprint.

## Vocabulary Bridge

| EnConvo term | Plain meaning | Teaching note |
| --- | --- | --- |
| Global Provider | App-wide default provider | Start here before per-agent overrides |
| Agent AI Model | Agent-specific model route | Use when one agent needs different behavior |
| Credential pencil | Edit selected credential/provider setup | Sensitive; do not reveal keys/codes |
| Credential gear | Open central Credential Management | Useful for inventory and reuse |
| OAuth2 | Browser login/authorization | Codes/callback URLs are temporary secrets |
| ApiKey | Provider key setup | Keys are secrets; validate only on request |
| Tools | Callable capabilities | Capability surface, not personality |
| Skills | Specialized workflows | Defines what the agent can invoke |
| KnowledgeBase | User-provided knowledge sources | Paths/content may be private |

## Privacy And Safety

- For credentials, OAuth, logs, recordings, memory, APIs, and knowledge sources, remind the user to keep secrets private.
- Ask before clicking `Connect`, `Reconnect`, `Validate`, `Set as Default Provider`, `Enable`, `Delete`, `Reset`, `Factory Reset`, `Run`, `Schedule`, or any switch that changes state.
- Prefer explaining from the guide or current visible state. When the user wants live setup, make one change at a time and confirm before moving.
- When operating the native app, first bring EnConvo/Smart Bar front with `Cmd+Shift+D`, then press `Cmd+,` while Smart Bar or EnConvo is active to open global Settings. Use the menu bar path EnConvo -> Settings as a fallback.

## Deep-Link And Synchronization Notes

- Prefer exact guide anchors from the list above. Render source URLs visibly, for example `https://enconvo-settings-guide-v3.vercel.app/#global-providers-ai-model`.
- In live tutoring, keep the guide page or Settings pane matched to the current explanation. Do not explain a hidden tab, lower panel, or credential branch while another section is visible.
- For native EnConvo Settings, use Computer Use when needed. Keep tool chatter silent; the user should see the Settings pane and concise tutoring beat, not automation debugging.
- Before teaching native Settings, verify the Settings window is actually frontmost. Do not explain stale screenshots or a hidden Settings window.
- For credential sheets, teach the visible branch (`OAuth2` or `ApiKey`) only after the branch is visible. If a secret field is visible, avoid reading it aloud.

## EnConvo Setup Coverage

For setup walkthroughs, check only the relevant path:

- Goal identified: app-wide default, one agent override, credential repair, tools/skills, voice/dictation, shortcuts, knowledgebase, or diagnostics.
- Correct entry point shown: guide page, Settings sidebar path, or native pane.
- Inheritance explained: global default vs agent override.
- Credential branch identified: Cloud Plan, OAuth2, ApiKey, local provider, or no-key provider.
- Sensitive controls named but not clicked without confirmation.
- Source anchor shared for the current step.
- Final recap lists what changed, what was only inspected, and what still needs user action.

Do not apply options coverage ledgers, GEX/DEX drill-downs, market-data freshness rules, or ticker conclusions to EnConvo setup walkthroughs.

## Default Teaching Paths

### Global AI Model Setup

1. Open the guide at `#global-providers-ai-model` or bring Smart Bar forward with `Cmd+Shift+D`, press `Cmd+,`, then open native Settings -> `Global Providers Settings > AI Model`.
2. Viewport 1: explain provider column and global inheritance.
3. Viewport 2: show Credential Provider, pencil/gear, and model settings.
4. Viewport 3: show the provider-specific branch (Cloud Plan, OAuth2, or ApiKey).
5. Stop before Connect/Reconnect/Validate/Set as Default unless the user explicitly confirms.

### Create Or Configure An Agent

1. Open `#agents-agent-list` or Settings -> `Agents > Agent List`.
2. Viewport 1: agent list and create/select controls.
3. Viewport 2: Agent Definition basics.
4. Viewport 3: AI Model override vs Global Provider.
5. Viewport 4: Tools, Text to Speech, or More depending on the user's goal.

### Credential Setup

1. Identify whether the setup is global or agent-specific.
2. Show the Credential Provider row and explain pencil vs gear.
3. Show OAuth2 or ApiKey branch.
4. For OAuth2, stop before browser authorization unless the user confirms.
5. For ApiKey, never read or store the key; stop before Validate unless the user confirms.

### Shortcuts, Dictation, And KnowledgeBase

1. Open the exact guide anchor or Settings sidebar path.
2. Explain the visible controls and privacy implications.
3. For shortcuts, check for conflicts before changing.
4. For dictation/knowledgebase, treat recordings, transcripts, paths, and indexed content as private.
