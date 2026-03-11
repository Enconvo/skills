---
name: enconvo-agent-cli
description: "Enconvo AI assistant CLI toolkit. List, inspect, configure, and invoke Enconvo commands/agents. Deep links, curl patterns, preference management, tool assignment, LLM routing, workflow inspection, and full command registry access."
version: 1.3.0
author: zanearcher
category: tools
---

# Enconvo Agent CLI Skill

Interact with the Enconvo AI assistant platform from the command line. Read, search, configure, and invoke any of the 800+ installed commands.

**Trigger on:** "enconvo", "enconvo command", "enconvo agent", "enconvo bot", "list enconvo", "enconvo deep link", "enconvo curl", "enconvo preference", "enconvo tool", "enconvo workflow"

---

## Quick Reference

| Want To... | Action |
|---|---|
| List all commands | Read `installed_commands/` directory |
| Inspect a command | Read `installed_commands/{ext}\|{cmd}.json` |
| Change a command's config | Edit `installed_preferences/{ext}\|{cmd}.json` |
| Open a deep link | `open "enconvo://{extensionName}/{commandName}"` |
| Invoke via local API | `curl -X POST http://localhost:54535/{ext}/{cmd}` |
| Switch a command's LLM | Edit `llm.commandKey` in its preference file |
| Assign tools to a command | Edit `tools` field in its preference file |
| List workflows | `ls installed_commands/workflow\|*.json` |
| Find commands by type | `grep -l '"commandType":"agent"' installed_commands/*.json` |
| Read extension API schema | Read `extension/{ext}/skills/schemas.json` |
| Search all extension APIs | Search across `extension/*/skills/schemas.json` |

---

## File System Layout

```
~/.config/enconvo/
├── installed_commands/          # ~809 command definitions (read-only registry)
│   └── {extensionName}|{commandName}.json
├── installed_preferences/       # ~91 user config overrides (read-write)
│   └── {extensionName}|{commandName}.json
├── installed_extensions/        # 92 extension manifests
│   └── {extensionName}.json
├── extension/                   # 81 extension runtime code (JS bundles)
│   ├── {extensionName}/
│   │   ├── package.json         # Extension manifest with all commands
│   │   ├── {command}.js         # Compiled command entry points
│   │   ├── assets/              # Icons, images
│   │   └── skills/              # Auto-generated skill docs (78 extensions)
│   │       ├── SKILL.md         # Human-readable command docs
│   │       ├── schemas.json     # Machine-readable API schemas (routes + params)
│   │       └── docs.md          # Command documentation (same content as SKILL.md)
│   └── node_modules/@enconvo/   # SDK: @enconvo/api, @enconvo/server
├── dropdown_list_cache/         # Cached dropdown data (models, languages, voices)
│   ├── llm/                     # anthropic_models.json, openai_models.json, etc.
│   ├── enconvo/languages.json   # 199 languages
│   └── tts_providers/           # Voice lists
├── preload/
│   ├── bin/                     # rg (ripgrep), mp3cat
│   └── node/                    # Bundled Node.js runtime
├── .db/                         # SQLite database
├── .support/                    # Per-extension runtime state (~31 dirs)
├── .macopilot.socket            # Unix IPC socket (app <-> extensions)
└── .uninstalled_extensions.json # Removed extensions list
```

---

## Command JSON Schema

Every file in `installed_commands/` follows this schema:

```json
{
  "name": "command_name",
  "title": "Display Title",
  "description": "What it does",
  "icon": "icon.png",
  "commandKey": "extensionName|command_name",
  "extensionName": "extensionName",
  "commandType": "agent|bot|tool|command|provider|...",
  "mode": "no-view|view|webview|smartbar|provider",
  "taskRuntimeType": "nodejs|action|webapp|webview",
  "targetCommand": "chat_with_ai|chat_command",
  "showInCommandList": true,
  "showInSmartBar": true,
  "sort": 2000,
  "from": "store|custom",
  "author": "ysnows",
  "parameters": {
    "type": "object",
    "properties": {
      "user_input_text": { "type": "string" },
      "input_text": { "type": "string" },
      "context_files": { "type": "array", "items": { "type": "string" } }
    }
  },
  "preferences": [
    {
      "name": "pref_name",
      "title": "Display Title",
      "type": "textfield|dropdown|checkbox|password|number|extension|tools|...",
      "default": "default_value",
      "group": "Group Name",
      "visibility": "hidden",
      "dataProxy": "llm|openai_models"
    }
  ]
}
```

### All commandType Values

| Type | Description | Count |
|---|---|---|
| `api` | Internal API endpoint | 162 |
| `application` | macOS app launcher | 111 |
| `provider` | Service provider (LLM, TTS, etc.) | 103 |
| `function_command` | Internal function | 77 |
| `agent` | AI agent with tools | 52 |
| `tool` | Callable tool (for AI agents) | 50 |
| `credentials-provider` | API key / OAuth manager | 49 |
| `variable` | Template variable provider | 15 |
| `command` | General command | 13 |
| `shortcuts` | Apple Shortcuts | 13 |
| `website` | WebView page | 10 |
| `context` | Context provider | 10 |
| `function` | Internal function (legacy) | 5 |
| `action` | Action command | 5 |
| `mcp_tool` | MCP protocol tool | 4 |
| `config` | Configuration panel | 4 |
| `workflow` | Workflow definition | 3 |
| `service` | Background service | 3 |
| `trigger` | Workflow trigger | 3 |
| `bot` | AI chatbot | 2 |
| `deprecated` | Legacy command | 2 |
| `condition` | Workflow condition | 2 |
| `control` | App state checker | 2 |
| `memory` | Memory store | 1 |
| `chat` | Chat command | 1 |
| `recordings` | Audio recordings | 1 |
| `webapp` | Web application | 1 |

### All mode Values

| Mode | Description |
|---|---|
| `no-view` | Headless execution, no UI |
| `view` | Opens in a view/window |
| `webview` | Embedded web content |
| `smartbar` | Opens in SmartBar |
| `provider` | Provider mode |

---

## Preference JSON Schema

Files in `installed_preferences/` store user overrides:

```json
{
  "preferenceKey": "extensionName|command_name",
  "execute_permission": "always_allow",
  "llm": {
    "commandKey": "llm|chat_anthropic",
    "llm|chat_anthropic": { "modelName": "claude-opus-4-6" },
    "llm|chat_open_ai": { "modelName": "gpt-5.2" },
    "llm|chat_google": { "modelName": "gemini-3-pro-preview" },
    "llm|enconvo_ai": { "modelName": "openai/gpt-5-mini" }
  },
  "tools": "[{\"tool_name\":\"file_system|read_file\"},{\"tool_name\":\"code_runner|bash\"}]",
  "prompt": "System prompt with {{ now }} and {{responseLanguage}} variables...",
  "user_prompt_1": "User prompt with {{input_text}} and {{selection_text}}...",
  "image_generation_enabled": "custom|disabled",
  "search_enabled": "auto|custom|disabled",
  "image_generation_providers": {
    "commandKey": "image_generation_providers|google_gemini"
  },
  "title": "Custom Title",
  "post_command": "writing_package|some_command",
  "hotkey": "Control+d",
  "responseLanguage": "zh-CN"
}
```

### Key Preference Fields

| Field | Type | Purpose |
|---|---|---|
| `preferenceKey` | string | Links to command via `extensionName\|commandName` |
| `execute_permission` | string | `"always_allow"` bypasses confirmation |
| `llm` | object | LLM provider + model selection |
| `llm.commandKey` | string | Active LLM provider (e.g., `llm\|chat_anthropic`) |
| `tools` | string (JSON) | JSON array of `{tool_name: "ext\|cmd"}` |
| `prompt` | string | System prompt (Jinja2 templates) |
| `user_prompt_1` | string | User prompt template |
| `image_generation_enabled` | string | `"custom"` or `"disabled"` |
| `search_enabled` | string | `"auto"`, `"custom"`, or `"disabled"` |
| `post_command` | string | Chain another command after this one |
| `credentials` | object | `{commandKey: "credentials\|provider"}` |

---

## Deep Links

**URL scheme:** `enconvo://`

**Pattern:** `enconvo://{extensionName}/{commandName}`

The deep link uses `/` (forward slash) as the separator between extension and command — NOT `|` (pipe). The `|` is only used in filenames and `commandKey` fields.

### Constructing Deep Links

Given a command with `commandKey: "extensionName|commandName"`, replace the `|` with `/`:
- `commandKey: "chat_with_ai|chat"` -> `enconvo://chat_with_ai/chat`
- `commandKey: "openclaw|OpenClaw"` -> `enconvo://openclaw/OpenClaw`
- `commandKey: "writing_package|explain"` -> `enconvo://writing_package/explain`

### Examples

```bash
# Open a specific command/bot
open "enconvo://chat_with_ai/chat"                       # Mavis (default chat)
open "enconvo://openclaw/OpenClaw"                       # OpenClaw Assistant
open "enconvo://writing_package/explain"                 # Explain command

# UI Pages (enconvo_webapp is just another extension)
open "enconvo://enconvo_webapp/store"                    # Extensions Store
open "enconvo://enconvo_webapp/new_command"               # Create New Bot
open "enconvo://enconvo_webapp/new_prompt"                # Create New Prompt
open "enconvo://enconvo_webapp/new_knowledge_base"        # Create Knowledge Base
open "enconvo://enconvo_webapp/my_profile"                # User Profile
open "enconvo://enconvo_webapp/check_extension_update"    # Check for Updates

# Install Extensions
open "enconvo://enconvo_webapp/install_dxt?file=mcp-server-fetch"
open "enconvo://enconvo_webapp/mcp_store/install_detail?id=mcp-server-fetch"
```

### Generate Deep Link from commandKey

```bash
# Convert any commandKey to a deep link
python3 -c "
key = 'chat_with_ai|chat'  # replace with any commandKey
print('enconvo://' + key.replace('|', '/'))
"
```

---

## Local API Server

Enconvo runs a local HTTP server on **port 54535** for command invocation and OAuth callbacks.

- **Command invocation:** `POST http://localhost:54535/{extensionName}/{commandName}`
- **OAuth callback:** `http://localhost:54535/callback`
- **IPC socket:** `~/.config/enconvo/.macopilot.socket`

### API Pattern

```
POST http://localhost:54535/{extensionName}/{commandName}
Content-Type: application/json

{
  "input_text": "Your message or input here",
  "message_limit": 0
}
```

- **`input_text`** (string): The user message or input to send to the command
- **`message_limit`** (number, optional): Limit on messages. `0` = no limit

The URL path uses `/` (forward slash) — same as deep links, NOT `|` (pipe).

### curl Examples

```bash
# Talk to Mavis (default chat agent)
curl -X POST http://localhost:54535/chat_with_ai/chat \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Hello, how are you?", "message_limit": 0}'

# Talk to OpenClaw Assistant
curl -X POST http://localhost:54535/openclaw/OpenClaw \
  -H "Content-Type: application/json" \
  -d '{"input_text": "What can you help me with?", "message_limit": 0}'

# Use the Explain command
curl -X POST http://localhost:54535/writing_package/explain \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Explain quantum computing", "message_limit": 0}'

```

### Known Bots Quick Reference

| Bot | curl Path | Deep Link |
|---|---|---|
| Mavis (default chat) | `/chat_with_ai/chat` | `enconvo://chat_with_ai/chat` |
| OpenClaw Assistant | `/openclaw/OpenClaw` | `enconvo://openclaw/OpenClaw` |

To find custom bots: `ls ~/.config/enconvo/installed_commands/custom_bot\|*.json`

### API Response Format

```json
{
  "type": "messages",
  "messages": [{
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Response text here"},
      {"type": "flow_step", "flowType": "tool_use", "flowName": "tool_name", "flowRunStatus": "success", ...}
    ]
  }]
}
```

- `type: "text"` — Bot's text reply
- `type: "flow_step"` — Tool call executed by the bot (includes `flowParams`, `flowResults`, `flowRunStatus`)

### Tips

- Use **absolute paths** (e.g., `/Users/zanearcher/Desktop/file.txt`) instead of `~` when asking bots to do file operations — some tools don't expand `~`
### Generate curl Command from commandKey

```bash
# Convert any commandKey to a curl command
python3 -c "
key = 'chat_with_ai|chat'  # replace with any commandKey
msg = 'Hello'  # replace with your message
ext, cmd = key.split('|')
print(f'curl -X POST http://localhost:54535/{ext}/{cmd} \\\\')
print(f'  -H \"Content-Type: application/json\" \\\\')
print(f'  -d \'{{\"input_text\": \"{msg}\", \"message_limit\": 0}}\'')
"
```

### File-Based Patterns (reading config, no API needed)

```bash
# Read command definition
python3 -c "import json; print(json.dumps(json.load(open('$HOME/.config/enconvo/installed_commands/chat_with_ai|chat.json')), indent=2))"

# Read command preference/config
python3 -c "import json; print(json.dumps(json.load(open('$HOME/.config/enconvo/installed_preferences/chat_with_ai|chat.json')), indent=2))"

# List all agent commands
grep -l '"commandType":"agent"' ~/.config/enconvo/installed_commands/*.json

# Search commands by title
grep -l '"title":".*Search.*"' ~/.config/enconvo/installed_commands/*.json
```

---

## Common Operations

### 1. List All Commands

```bash
# All commands with titles
for f in ~/.config/enconvo/installed_commands/*.json; do
  python3 -c "import json,sys; d=json.load(open('$f')); print(f'{d[\"commandKey\"]:50s} | {d.get(\"commandType\",\"?\"):20s} | {d.get(\"title\",\"?\")}')"
done

# Just command keys
ls ~/.config/enconvo/installed_commands/ | sed 's/.json$//'

# Count by extension namespace
ls ~/.config/enconvo/installed_commands/ | sed 's/|.*//' | sort | uniq -c | sort -rn
```

### 2. List Commands by Type

```bash
# All agents
grep -l '"commandType":"agent"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'

# All bots
grep -l '"commandType":"bot"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'

# All tools (callable by AI)
grep -l '"commandType":"tool"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'

# All MCP tools
grep -l '"commandType":"mcp_tool"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'

# All workflows
grep -l '"commandType":"workflow"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'

# All credential providers
grep -l '"commandType":"credentials-provider"' ~/.config/enconvo/installed_commands/*.json | sed 's|.*/||;s/.json$//'
```

### 3. Inspect a Command

```bash
# Full definition
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_commands/chat_with_ai|chat.json'))
print(json.dumps(d, indent=2))
"

# Just the key fields
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_commands/chat_with_ai|chat.json'))
for k in ['commandKey','commandType','mode','targetCommand','title','description']:
    print(f'{k}: {d.get(k, \"—\")}')
print(f'parameters: {list(d.get(\"parameters\",{}).get(\"properties\",{}).keys())}')
print(f'preferences: {[p[\"name\"] for p in d.get(\"preferences\",[])]}')
"
```

### 4. Read/Change a Command's LLM Model

```bash
# Read current model
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_preferences/chat_with_ai|chat.json'))
llm = d.get('llm', {})
provider = llm.get('commandKey', 'not set')
model = llm.get(provider, {}).get('modelName', 'not set') if provider != 'not set' else 'not set'
print(f'Provider: {provider}')
print(f'Model: {model}')
"

# Switch a command to Claude Opus
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/chat_with_ai|chat.json'
d = json.load(open(path))
if 'llm' not in d: d['llm'] = {}
d['llm']['commandKey'] = 'llm|chat_anthropic'
if 'llm|chat_anthropic' not in d['llm']: d['llm']['llm|chat_anthropic'] = {}
d['llm']['llm|chat_anthropic']['modelName'] = 'claude-opus-4-6'
json.dump(d, open(path, 'w'), indent=2)
print('Switched to claude-opus-4-6')
"

# Switch to GPT 5.2
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
if 'llm' not in d: d['llm'] = {}
d['llm']['commandKey'] = 'llm|chat_open_ai'
if 'llm|chat_open_ai' not in d['llm']: d['llm']['llm|chat_open_ai'] = {}
d['llm']['llm|chat_open_ai']['modelName'] = 'gpt-5.2'
json.dump(d, open(path, 'w'), indent=2)
print('Switched to gpt-5.2')
"
```

### 5. Assign Tools to a Command

```bash
# Read current tools
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'))
tools = json.loads(d.get('tools', '[]'))
for t in tools: print(t['tool_name'])
"

# Set tools for a command
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
d['tools'] = json.dumps([
    {'tool_name': 'file_system|read_file'},
    {'tool_name': 'file_system|write_file'},
    {'tool_name': 'code_runner|bash'},
    {'tool_name': 'internet_browsing|web_search'},
    {'tool_name': 'image_generation|image_generation'}
])
json.dump(d, open(path, 'w'), indent=2)
print('Tools updated')
"
```

### 6. Change System Prompt

```bash
# Read current prompt
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'))
print(d.get('prompt', 'No prompt set'))
"

# Set system prompt
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
d['prompt'] = '''You are a helpful coding assistant.
Current time: {{ now }}
Response language: {{responseLanguage}}
'''
json.dump(d, open(path, 'w'), indent=2)
print('Prompt updated')
"
```

### 7. Enable/Disable Features

```bash
# Enable web search for a command
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
d['search_enabled'] = 'auto'  # 'auto', 'custom', or 'disabled'
json.dump(d, open(path, 'w'), indent=2)
"

# Enable image generation
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
d['image_generation_enabled'] = 'custom'  # 'custom' or 'disabled'
json.dump(d, open(path, 'w'), indent=2)
"

# Set execute permission (auto-approve tool calls)
python3 -c "
import json
path = '$HOME/.config/enconvo/installed_preferences/COMMAND_KEY_HERE.json'
d = json.load(open(path))
d['execute_permission'] = 'always_allow'
json.dump(d, open(path, 'w'), indent=2)
"
```

### 8. List Available Models (from cache)

Model cache files are dicts keyed by model name, with rich metadata per entry:

```bash
# Anthropic models
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/dropdown_list_cache/llm/anthropic_models.json'))
for name, info in d.items():
    title = info.get('title', name) if isinstance(info, dict) else name
    print(f'{name:45s} {title}')
"

# OpenAI models
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/dropdown_list_cache/llm/openai_models.json'))
for name, info in d.items():
    title = info.get('title', name) if isinstance(info, dict) else name
    print(f'{name:45s} {title}')
"

# All cached model lists
ls ~/.config/enconvo/dropdown_list_cache/llm/
# anthropic_models.json, enconvo_models.json, gemini_models.json,
# groq_models.json, openai_models.json
```

### 9. Search Commands

```bash
# By title keyword
python3 -c "
import json, glob, sys
q = sys.argv[1].lower()
for f in glob.glob('$HOME/.config/enconvo/installed_commands/*.json'):
    d = json.load(open(f))
    if q in d.get('title','').lower() or q in d.get('description','').lower():
        print(f'{d[\"commandKey\"]:50s} | {d.get(\"title\",\"\")}')
" "search_term"

# By extension namespace
ls ~/.config/enconvo/installed_commands/ | grep '^llm|'

# Commands with a specific tool assigned
python3 -c "
import json, glob
for f in glob.glob('$HOME/.config/enconvo/installed_preferences/*.json'):
    d = json.load(open(f))
    tools = d.get('tools', '')
    if 'code_runner|bash' in tools:
        print(d['preferenceKey'])
"
```

### 10. Inspect Workflows

```bash
# List all workflows
grep -l '"commandType":"workflow"' ~/.config/enconvo/installed_commands/*.json | while read f; do
    python3 -c "import json; d=json.load(open('$f')); print(d.get('title','?'),' — ',d['commandKey'])"
done

# Read workflow node graph
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/installed_commands/WORKFLOW_KEY_HERE.json'))
for p in d.get('preferences', []):
    if p.get('type') == 'workflow' and p.get('default'):
        wf = json.loads(p['default']) if isinstance(p['default'], str) else p['default']
        print('Nodes:')
        for n in wf.get('nodes', []):
            print(f'  {n[\"id\"][:8]}... type={n[\"type\"]} cmd={n.get(\"data\",{}).get(\"command\",\"\")}')
        print('Connections:')
        for src, conns in wf.get('connections', {}).items():
            for chain in conns.get('main', []):
                for c in chain:
                    print(f'  {src[:8]}... -> {c[\"node\"][:8]}...')
"
```

### 11. List Credentials

```bash
# All credential providers
grep -l '"commandType":"credentials-provider"' ~/.config/enconvo/installed_commands/*.json | while read f; do
    python3 -c "import json; d=json.load(open('$f')); print(d['commandKey'],' — ',d.get('title',''))"
done

# Check which credentials have tokens stored
for f in ~/.config/enconvo/installed_preferences/credentials|*.json; do
    python3 -c "
import json
d = json.load(open('$f'))
has_token = 'access_token' in d or 'apiKey' in d
print(f'{d[\"preferenceKey\"]:40s} | authenticated: {has_token}')
" 2>/dev/null
done
```

### 12. Bulk Operations

```bash
# Switch ALL agents/bots to Claude Opus
python3 -c "
import json, glob
count = 0
for f in glob.glob('$HOME/.config/enconvo/installed_preferences/chat_with_ai|*.json'):
    d = json.load(open(f))
    if 'llm' in d:
        d['llm']['commandKey'] = 'llm|chat_anthropic'
        if 'llm|chat_anthropic' not in d['llm']: d['llm']['llm|chat_anthropic'] = {}
        d['llm']['llm|chat_anthropic']['modelName'] = 'claude-opus-4-6'
        json.dump(d, open(f, 'w'), indent=2)
        count += 1
print(f'Updated {count} commands')
"

# Add a tool to ALL agents that have tools
python3 -c "
import json, glob
new_tool = {'tool_name': 'internet_browsing|web_search'}
count = 0
for f in glob.glob('$HOME/.config/enconvo/installed_preferences/*.json'):
    d = json.load(open(f))
    if 'tools' in d:
        tools = json.loads(d['tools'])
        if not any(t['tool_name'] == new_tool['tool_name'] for t in tools):
            tools.append(new_tool)
            d['tools'] = json.dumps(tools)
            json.dump(d, open(f, 'w'), indent=2)
            count += 1
print(f'Added tool to {count} commands')
"

# Export all command summaries to CSV
python3 -c "
import json, glob, csv, sys
w = csv.writer(sys.stdout)
w.writerow(['commandKey','title','commandType','mode','extensionName','from'])
for f in sorted(glob.glob('$HOME/.config/enconvo/installed_commands/*.json')):
    d = json.load(open(f))
    w.writerow([d.get('commandKey',''),d.get('title',''),d.get('commandType',''),d.get('mode',''),d.get('extensionName',''),d.get('from','')])
" > /tmp/enconvo_commands.csv
```

---

## Extension Skills (API Schemas)

Each extension ships a `skills/` directory with machine-readable API schemas (`schemas.json`) and human-readable docs (`SKILL.md`, `docs.md`). These define the exact routes, parameters, and types for every command — the ground truth for API invocation.

### Skills Directory Structure

```
~/.config/enconvo/extension/{extensionName}/skills/
├── SKILL.md         # Extension title, version, command docs with curl examples
├── schemas.json     # JSON array of command schemas (routes + full parameter specs)
└── docs.md          # Same content as SKILL.md (command docs)
```

**Note:** Mavis (`chat_with_ai`) has a special skills dir with richer docs. 78 of 81 extensions have skills dirs.

### Schema Format

Each entry in `schemas.json` is a command:

```json
{
  "name": "command_name",
  "title": "Display Title",
  "description": "What it does",
  "route": "extensionName/command_name",
  "parameters": {
    "type": "object",
    "properties": { ... },
    "required": ["param1"]
  },
  "routes": [...]  // optional sub-routes
}
```

The `route` field maps directly to the local API path: `POST http://localhost:54535/{route}`.

### Reading Extension Skills

```bash
# Read a specific extension's API schema
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/extension/file_system/skills/schemas.json'))
for cmd in d:
    params = list(cmd.get('parameters',{}).get('properties',{}).keys())
    print(f'{cmd[\"route\"]:45s} | {cmd[\"title\"]:25s} | {params}')
"

# List all extensions that have skills
find ~/.config/enconvo/extension/ -maxdepth 2 -name schemas.json -path '*/skills/*' | \
  sed 's|.*/extension/||;s|/skills/.*||' | sort

# Search across all extensions for a command by name
python3 -c "
import json, glob, sys
q = sys.argv[1].lower()
for f in sorted(glob.glob('$HOME/.config/enconvo/extension/*/skills/schemas.json')):
    for cmd in json.load(open(f)):
        if q in cmd.get('name','').lower() or q in cmd.get('title','').lower() or q in cmd.get('description','').lower():
            params = list(cmd.get('parameters',{}).get('properties',{}).keys())
            print(f'{cmd[\"route\"]:45s} | {cmd[\"title\"]:25s} | {params}')
" "search_term"
```

### Key Extension APIs (by Category)

#### File System (`file_system`)
| Route | Title | Key Params |
|---|---|---|
| `file_system/write_file` | Write File | path, content, description |
| `file_system/read_file` | Read File | path, description |
| `file_system/edit_file` | Edit File | path, edits, description, dryRun |
| `file_system/grep` | Grep | pattern, path, include, description |
| `file_system/glob` | Glob | pattern, path, description |

#### Code Runner (`code_runner`)
| Route | Title | Key Params |
|---|---|---|
| `code_runner/bash` | Bash | command, workDir, timeout, run_in_background |

#### TTS (`tts`) — 11 commands
| Route | Title | Key Params |
|---|---|---|
| `tts/read_aloud` | Read Aloud | user_input_text, speed |
| `tts/tts` | TTS to File | user_input_text, audio_file_name, output_dir, speed |
| `tts/gemini_tts` | Gemini TTS | user_input_text, audio_file_name, output_dir |
| `tts/gemini_tts_multi_speaker` | Gemini Multi-Speaker TTS | user_input_text, audio_file_name, output_dir |
| `tts/text_to_sound_effect` | Sound Effect | text, audio_file_name, output_dir |
| `tts/play_audio_book` | Audiobook | context_files |
| `tts/convert_srt_to_audio_file` | SRT to Audio | context_files |

#### Video Generation (`video_generation` + `fal`)
| Route | Title | Key Params |
|---|---|---|
| `video_generation/text_to_video` | Text to Video | prompt, output_dir |
| `video_generation/image_to_video` | Image to Video | prompt, reference_images, output_dir |
| `fal/generate_video_veo3` | Veo3 | prompt, aspect_ratio, duration, generate_audio |
| `fal/generate_video_hailuo02` | Minimax Hailuo | prompt, duration, prompt_optimizer |
| `fal/generate_video_seedance_lite` | Seedance Lite | prompt, duration, aspect_ratio, resolution |

#### Apple Mail (`apple_mail`) — 11 commands
| Route | Title | Key Params |
|---|---|---|
| `apple_mail/compose_new_message` | Compose | from, to, cc, bcc, subject, content, attachments |
| `apple_mail/see_recent_mail` | Recent Mail | unreadonly |
| `apple_mail/get_message_content` | Get Content | account, mailbox, messageId |
| `apple_mail/move_message_to_trash` | Trash | account, mailbox, messageId |
| `apple_mail/move_message_to_archive` | Archive | account, mailbox, messageId |

#### Gmail (`gmail`) — 13 commands
| Route | Title | Key Params |
|---|---|---|
| `gmail/send_email` | Send | to, subject, body, htmlBody, cc, bcc, attachments |
| `gmail/draft_email` | Draft | to, subject, body, htmlBody |
| `gmail/read_email` | Read | messageId |
| `gmail/search_emails` | Search | query, maxResults |
| `gmail/modify_email` | Modify Labels | messageId, addLabelIds, removeLabelIds |
| `gmail/batch_modify_emails` | Batch Modify | messageIds, addLabelIds, removeLabelIds |
| `gmail/create_label` | Create Label | name |

#### Calendar (`calender`) — 5 commands
| Route | Title | Key Params |
|---|---|---|
| `calender/add_event_to_apple_calender` | Add Event | title, startDate, endDate, notes, isAllDay, location, calendarId, recurrence |
| `calender/update_calendar_event` | Update Event | eventId, title, startDate, endDate |
| `calender/get_calendar_events` | Get Events | days |
| `calender/delete_calendar_event` | Delete Event | eventId |
| `calender/get_calendar_list` | List Calendars | — |

#### Apple Reminders (`apple_reminders`) — 6 commands
| Route | Title | Key Params |
|---|---|---|
| `apple_reminders/add_event_to_apple_reminder` | Add Reminder | title, notes, dueDate, priority, listId, recurrence |
| `apple_reminders/get_apple_reminders_events` | Get All | — |
| `apple_reminders/update_reminders_item` | Update | reminderId, title, notes, dueDate |
| `apple_reminders/delete_reminders_item` | Delete | reminderId |

#### Knowledge Base (`knowledge_base`) — 20+ commands
| Route | Title | Key Params |
|---|---|---|
| `knowledge_base/add_to_knowledge_base` | Add to KB | user_input_text, context_files |
| `knowledge_base/retrieve_document_content` | Retrieve Content | query, document_files |
| `knowledge_base/create` | Create KB | title, description, knowledge_base_type |
| `knowledge_base/api_upload_knowledge_base_attachments` | Upload | attachments, knowledge_base_id |
| `knowledge_base/update_attachment_content` | Update Content | knowledge_base_id, attachment_id, content |

**Memory sub-routes** (under `knowledge_base`):
| Sub-route | Title | Key Params |
|---|---|---|
| `add` | Add Memory | content, category, importance, memory_type, tags |
| `search` | Search Memory | — |
| `list` | List Memories | query, limit, offset |
| `delete` | Delete Memory | id, ids |
| `update` | Update Memory | id, content, category, tags |
| `compress_messages` | Compress Messages | messages, conversation_id |

#### Writing Package (`writing_package`) — 22 commands
| Route | Title |
|---|---|
| `writing_package/explain` | Explain Text |
| `writing_package/summarize` | Summarize |
| `writing_package/fix_spelling_and_grammar` | Fix Spelling & Grammar |
| `writing_package/improve_writing` | Improve Writing |
| `writing_package/make_longer` | Expand |
| `writing_package/make_shorter` | Shorten |
| `writing_package/rewrite` | Rewrite |
| `writing_package/change_tone_to_professional` | Professional Tone |
| `writing_package/change_tone_to_casual` | Casual Tone |
| `writing_package/extract_key_points` | Extract Key Points |
| `writing_package/convert_to_table` | Convert to Table |

#### Translate (`translate`) — 8 commands
| Route | Title | Key Params |
|---|---|---|
| `translate/translate` | Translate | user_input_text, source_language, target_language |
| `translate/screenshot_translate` | Screenshot Translate | — |
| `translate/deepl` | DeepL | — |
| `translate/google` | Google Translate | — |

#### YouTube (`youtube`) — 5 commands
| Route | Title | Key Params |
|---|---|---|
| `youtube/youtube_transcript_loader` | Get Transcript | youtube_url, with_timestamps, language |
| `youtube/youtube_video_downloader` | Download Video | video_url, favorite_resolution, audio_only, output_dir |

#### Transcribe (`transcribe`)
| Route | Title | Key Params |
|---|---|---|
| `transcribe/transcribe_audio_video` | Transcribe | audio_files, output_format, output_dir |

#### OCR (`ocr_action`) — 4 commands
| Route | Title | Key Params |
|---|---|---|
| `ocr_action/ocr` | OCR | image_files |
| `ocr_action/screenshot_ocr` | Screenshot OCR | — |

#### Web (`link_reader` + `network_tools`)
| Route | Title | Key Params |
|---|---|---|
| `link_reader/web_fetch` | Fetch URL | link_url, format, timeout |
| `link_reader/summarize_webpage` | Summarize Page | — |
| `network_tools/http_request` | HTTP Request | url, method, headers, body |

#### Credentials (`credentials`) — 49 providers
Key providers: `enconvo_ai`, `open_ai`, `anthropic`, `gemini`, `groq`, `x_ai`, `mistral`, `openrouter`, `fal`, `elevenlabs`, `assembly_ai`, `deepgram`, `fireworks`, `replicate`, `cohere`, `perplexity`

#### Skills Manager (`skills_manager`)
| Route | Title | Key Params |
|---|---|---|
| `skills_manager/api_install_skill` | Install Skill | skillName, downloadUrl, githubUrl |
| `skills_manager/api_skills_list` | List Skills | keyword, category |
| `skills_manager/api_uninstall_skill` | Uninstall Skill | skillName |
| `skills_manager/get_all_installed_skills` | All Installed | — |

#### Webapp Management (`enconvo_webapp`)
| Route | Title | Key Params |
|---|---|---|
| `enconvo_webapp/create_new_agent` | Create Agent | **params** (wrapper object): title, commandName, description, run_mode, prompt, user_prompt_1, llm, tools, tts_providers |
| `enconvo_webapp/api_get_commands` | Get Commands | — |
| `enconvo_webapp/api_install_skill` | Install Skill | skillName, downloadUrl |
| `enconvo_webapp/get_raw_command` | Get Raw Command | commandKey |

**IMPORTANT: `create_new_agent` requires a `params` wrapper.** All fields must be nested inside `{"params": {...}}`. Without it, the API returns `Cannot read properties of undefined (reading 'run_mode')`. Also note `create_new_bot` exists but does NOT persist agents properly — always use `create_new_agent`.

```bash
# Create a custom agent (correct format)
curl -X POST http://localhost:54535/enconvo_webapp/create_new_agent \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "title": "My Agent",
      "commandName": "my_agent",
      "description": "A helpful agent",
      "run_mode": "agent",
      "prompt": "You are a helpful assistant.",
      "user_prompt_1": "{{input_text}}",
      "llm": {"isUseGlobalDefaultCommand": true},
      "tools": [{"tool_name": "file_system|read_file"}, {"tool_name": "code_runner|bash"}],
      "tts_providers": {"isUseGlobalDefaultCommand": true}
    }
  }'
# Creates: ~/.config/enconvo/installed_commands/custom_bot|my_agent.json
# Invoke:  curl -X POST http://localhost:54535/custom_bot/my_agent ...
```

#### Template Variables (`variables`) — 14 providers
Available variables for prompts: `input_text`, `active_application`, `active_application_screenshot`, `active_screen_shot`, `focused_window_content`, `latest_clipboard`, `selection_text`, `history_messages`, `finder_current_directory`, `finder_selected_files`, `browser_tab`, `now`, `opened_applications`, `opened_application_names`

#### Other Extensions
| Extension | Commands | Key Route |
|---|---|---|
| `twitter` | 1 | `twitter/twitter_video_downloader` |
| `stackoverflow` | 1 | `stackoverflow/stackoverflow` |
| `compress_image` | 1 | `compress_image/image_compress` |
| `audio_utils` | 1 | `audio_utils/compress_audio` |
| `video_utils` | 3 | `video_utils/compress_video`, `extract_audio`, `online_video_or_audio_downloader` |
| `exporter` | 1 | `exporter/export_markdown` |
| `prompt_generator` | 1 | `prompt_generator/prompt_generator_openai` |
| `text_modifier` | 4 | `text_modifier/bold`, `italic`, `strikethrough`, `undo` |
| `message_manager` | 4 | `message_manager/add_message`, `get_messages`, `delete_message` |
| `system` | 8 | `system/toggle_system_appearance`, `toggle_mute`, `toggle_hidden_files`, `toggle_full_screen`, `search`, `open_link` |
| `mcp` | 2 | `mcp/mcp_tool`, `mcp/api_list_servers` |
| `workflow` | 20 | `workflow/run`, `workflow/if`, `workflow/loop_items`, `workflow/get_run_logs` |
| `application` | 12+ | macOS app launchers (Finder, Calendar, Mail, etc.) |

---

## Available Tools (for AI agents)

Tools are assigned to commands via the `tools` preference field. All available tool references:

### File System (15)
```
file_system|read_file, file_system|write_file, file_system|edit_file,
file_system|read_multiple_files, file_system|read_document_type_file,
file_system|list_directory, file_system|directory_tree, file_system|create_directory,
file_system|create_multiple_directories, file_system|move_file,
file_system|get_file_info, file_system|search_files, file_system|glob,
file_system|grep, file_system|update_plan
```

### Code Execution (5)
```
code_runner|bash, code_runner|shell_script_executor,
code_runner|applescript_executor, code_runner|nodejs_code_runner,
code_runner|python_code_runner
```

### Browser / MCP (22)
```
playwright-mcp|browser_click, playwright-mcp|browser_close,
playwright-mcp|browser_console_messages, playwright-mcp|browser_drag,
playwright-mcp|browser_evaluate, playwright-mcp|browser_file_upload,
playwright-mcp|browser_fill_form, playwright-mcp|browser_handle_dialog,
playwright-mcp|browser_hover, playwright-mcp|browser_install,
playwright-mcp|browser_navigate, playwright-mcp|browser_navigate_back,
playwright-mcp|browser_network_requests, playwright-mcp|browser_press_key,
playwright-mcp|browser_resize, playwright-mcp|browser_run_code,
playwright-mcp|browser_select_option, playwright-mcp|browser_snapshot,
playwright-mcp|browser_tabs, playwright-mcp|browser_take_screenshot,
playwright-mcp|browser_type, playwright-mcp|browser_wait_for
```

### Web & Search
```
internet_browsing|web_search, link_reader|link_reader,
link_reader|chat_with_link, link_reader|summarize_webpage,
link_reader|web_fetch, network_tools|http_request
```

### Media
```
image_generation|image_generation, image_generation|image_edit,
tts|read_aloud, tts|text_to_sound_effect, tts|tts,
compress_image|image_compress, transcribe|transcribe_audio_video,
video_utils|online_video_or_audio_downloader
```

### Apple Notes
```
apple-notes|add_note, apple-notes|get_note_content,
apple-notes|list_notes, apple-notes|update_note_content,
sync_to_apple_notes|sync_to_apple_notes
```

### Obsidian (11)
```
obsidian|create-note, obsidian|edit-note, obsidian|read-note,
obsidian|delete-note, obsidian|move-note, obsidian|search-vault,
obsidian|list-available-vaults, obsidian|create-directory,
obsidian|add-tags, obsidian|remove-tags, obsidian|rename-tag
```

### System
```
system|toggle_full_screen, system|toggle_hidden_files,
system|toggle_mute, system|toggle_system_appearance
```

---

## Template Variables

Prompts support Jinja2/Liquid-style templates:

| Variable | Description |
|---|---|
| `{{ now }}` | Current timestamp |
| `{{ input_text }}` | User text input |
| `{{ selection_text }}` | Selected text |
| `{{ responseLanguage }}` | Response language setting |
| `{{ focused_window_content }}` | Active window content |
| `{{ active_application.bundleId }}` | Active app bundle ID |
| `{{ active_application_screenshot }}` | Screenshot of active app |
| `{{ skills.skill_name }}` | Load a skill's content |

### Conditional Blocks

```
{% if selection_text and selection_text | trim | length > 0 %}
  Working with selected text: {{selection_text}}
{% endif %}

{% if active_application.bundleId == "com.google.Chrome" %}
  Browser content: {{focused_window_content}}
{% endif %}

{% if responseLanguage.language_code != 'auto' %}
  Respond in: {{responseLanguage}}
{% endif %}
```

---

## Extension Namespaces (91 total)

### Core Platform
`enconvo` (41), `enconvo_assistant`, `enconvo_webapp` (42), `api` (3), `system` (8), `window` (3)

### AI Chat & Agents
`chat_with_ai` (51), `custom_bot` (3), `bot_emily`, `bot_latin_teacher`, `bot_spanish_teacher`, `prompt` (5), `prompt_generator`

### LLM Providers
`llm` (61), `credentials` (51)

### Tools & Actions
`file_system`, `code_runner`, `network_tools`, `internet_browsing`, `link_reader`, `search`, `ocr_action`, `screen_shot_action`, `compress_image`, `general_action`

### Media
`image_generation`, `image_generation_providers`, `video_generation`, `video_generation_providers`, `tts`, `tts_providers`, `audio_utils`, `text_to_audio`, `text_to_sound_effect_providers`, `fal`

### Productivity
`apple_mail`, `apple_reminders`, `apple-notes`, `apple_shortcuts`, `apple_shortcuts_tools`, `obsidian`, `calender`, `gmail`, `sync_to_apple_notes`

### Knowledge & Memory
`knowledge_base`, `my_memory`, `embeddings_providers`, `document_loader_providers`, `reranker_providers`

### Context Providers
`browser_context`, `clipboard_context`, `text_context`, `finder_context`, `screenshot_context`, `application_context`, `application_condition`

### Workflow
`workflow` (20), `variables` (14), `action` (4)

### External
`twitter`, `youtube`, `stackoverflow`, `openclaw`, `mcp`, `playwright-mcp`

### System
`application` (111 macOS app launchers), `macos_application_manager`, `voice_input`, `speech_recognize_providers`, `transcription_providers`, `translate`, `translate_providers`, `language_detect_providers`, `writing_package`, `text_modifier`, `skills_manager`

---

## LLM Providers & Models

### Active Providers

| Provider Key | Display | Top Models |
|---|---|---|
| `llm\|chat_anthropic` | Anthropic | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001 |
| `llm\|chat_open_ai` | OpenAI | gpt-5.4, gpt-5.3-codex, gpt-5.2, gpt-5.1 |
| `llm\|chat_google` | Google | gemini-3.1-pro-preview, gemini-3-pro-preview, gemini-2.5-pro |
| `llm\|enconvo_ai` | Enconvo AI | openai/gpt-5-mini, openai/gpt-5.2, google/gemini-3-pro-preview |
| `llm\|chat_groq` | Groq | llama-4-scout, compound-mini, kimi-k2-instruct |

### Cached Model Lists

Model cache files are **dicts keyed by model name** (not arrays). Each value contains metadata: title, context, inputPrice, outputPrice, maxTokens, speed, intelligence, toolUse, visionEnable, etc.

```bash
ls ~/.config/enconvo/dropdown_list_cache/llm/
# anthropic_models.json, enconvo_models.json, gemini_models.json,
# groq_models.json, openai_models.json
```

---

## Command Delegation (`targetCommand`)

Commands delegate execution via `targetCommand`. Key delegation targets:

| Target | What Delegates To It |
|---|---|
| `chat_with_ai\|chat_command` | Most bots, agents, application assistants |
| `workflow\|run` | All workflow definitions |
| `mcp\|mcp_tool` | All MCP protocol tools |
| `llm\|chat_open_ai` | LLM model routing |
| `llm\|fetch_models` | Model list fetching |
| `prompt\|prompt` | Prompt templates |
| `translate\|translate` | Translation commands |
| `tts\|read_aloud` | Text-to-speech commands |
| `youtube\|chat_with_youtube` | YouTube chat integrations |

---

## macOS Integration

### Registered Services (right-click menu)
1. **"Add to Enconvo"** — Send selected text/data to Enconvo context
2. **"Add to Enconvo Knowledge Base"** — Add content to a KB
3. **"Add to Enconvo Memory"** — Add content to memory

### Custom File Types
- **`.enconvoplugin`** — Legacy extension format
- **`.dxt`** — Modern extension package (`application/x-enconvo-extension`)

### Scriptable Apps (AppleScript support)
Arc, Finder, Firefox, Google Chrome, ImageEvents, iTunes, Mail

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Preference changes not taking effect | Restart Enconvo app (Cmd+Q then reopen) |
| Command not appearing in list | Check `showInCommandList: true` in command JSON |
| Tool calls being blocked | Set `execute_permission: "always_allow"` in preference |
| Wrong model being used | Check `llm.commandKey` in preference — it overrides defaults |
| Deep link not opening | Ensure Enconvo is running; check `open` command output |
| Missing model in dropdown | Check `dropdown_list_cache/llm/` for cached model lists |
| IPC socket errors | Check if `~/.config/enconvo/.macopilot.socket` exists |
| `create_new_agent` returns `run_mode` error | Wrap all fields in `{"params": {...}}` — the API expects a params wrapper |
| `create_new_bot` returns success but no file created | Use `create_new_agent` instead — `create_new_bot` doesn't persist properly |

---

## Helper Script: enconvo-cli

For convenience, Claude can run these as inline python3 one-liners. Common patterns:

```bash
# CONFIG_DIR shorthand
export ENCONVO="$HOME/.config/enconvo"

# Quick command lookup
python3 -c "
import json, glob, sys
q = sys.argv[1].lower()
for f in sorted(glob.glob('$ENCONVO/installed_commands/*.json')):
    d = json.load(open(f))
    if q in d.get('commandKey','').lower() or q in d.get('title','').lower() or q in d.get('description','').lower():
        ct = d.get('commandType','?')
        print(f'{d[\"commandKey\"]:50s} [{ct:15s}] {d.get(\"title\",\"\")}')
" "SEARCH_TERM"
```
