# Feature: Claude Code as a Channel Backend

Connect Telegram/Discord (and future channels) to **Claude Code CLI** (`claude`) running on your macOS, so remote users can interact with Claude Code as if they were at the terminal.

## Architecture

```
Telegram/Discord user
        |
        v
  enconvo-gw gateway
        |
        v
  ClaudeCodeClient (new)
        |
        v
  claude CLI  (spawned as child process)
        |
        v
  Claude API (Anthropic)
```

Currently the gateway routes all messages through `EnConvoClient` (`src/enconvo/client.js`), which calls the local EnConvo HTTP API. The goal is to add a **`ClaudeCodeClient`** that spawns the `claude` CLI instead.

## Key Constraint

`claude` cannot be launched inside another Claude Code session (it checks the `CLAUDECODE` env var). When spawning, you MUST unset it:

```js
const proc = spawn('claude', args, {
  env: { ...process.env, CLAUDECODE: '' }
});
```

## Implementation Plan

### 1. Create `src/claude/client.js`

```js
import { spawn } from 'node:child_process';
import { log } from '../utils.js';

const DEFAULT_TIMEOUT_MS = 120_000; // 2 minutes

export class ClaudeCodeClient {
  constructor(options = {}) {
    this.timeout = options.timeout || DEFAULT_TIMEOUT_MS;
    this.defaultModel = options.model || null; // e.g. 'sonnet' or 'opus'
    this.systemPrompt = options.systemPrompt || null;
    this.allowedTools = options.allowedTools || null; // e.g. ['Read', 'Grep', 'Bash(git:*)']
    this.disallowedTools = options.disallowedTools || null;
    this.workingDir = options.workingDir || process.env.HOME;
    this.permissionMode = options.permissionMode || 'plan'; // safe default
  }

  /**
   * Send a prompt to claude CLI and get the response.
   *
   * @param {string} inputText - The user's message
   * @param {string} sessionId - Used to maintain conversation context.
   *   Pass the same sessionId to continue a conversation.
   *   Format suggestion: "tg-<accountId>-<chatId>" or "dc-<accountId>-<channelId>"
   * @param {object} opts - Override options for this call
   * @returns {Promise<string>} Claude's response text
   */
  async call(inputText, sessionId, opts = {}) {
    const args = ['-p', inputText, '--output-format', 'text'];

    // Session resumption for multi-turn conversations
    if (sessionId) {
      args.push('--session-id', sessionId);
    }

    // Model override
    const model = opts.model || this.defaultModel;
    if (model) {
      args.push('--model', model);
    }

    // System prompt
    const systemPrompt = opts.systemPrompt || this.systemPrompt;
    if (systemPrompt) {
      args.push('--system-prompt', systemPrompt);
    }

    // Permission mode (important for security)
    const permMode = opts.permissionMode || this.permissionMode;
    if (permMode) {
      args.push('--permission-mode', permMode);
    }

    // Tool restrictions
    const allowed = opts.allowedTools || this.allowedTools;
    if (allowed) {
      args.push('--allowedTools', ...allowed);
    }
    const disallowed = opts.disallowedTools || this.disallowedTools;
    if (disallowed) {
      args.push('--disallowedTools', ...disallowed);
    }

    log('claude', `Spawning: claude ${args.slice(0, 4).join(' ')}... session=${sessionId || 'new'}`);

    return new Promise((resolve, reject) => {
      const proc = spawn('claude', args, {
        cwd: this.workingDir,
        env: { ...process.env, CLAUDECODE: '' }, // CRITICAL: unset to avoid nested session error
        timeout: this.timeout,
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (chunk) => { stdout += chunk; });
      proc.stderr.on('data', (chunk) => { stderr += chunk; });

      proc.on('error', (err) => {
        reject(new Error(`Failed to spawn claude: ${err.message}`));
      });

      proc.on('close', (code) => {
        const output = stdout.trim();
        if (code === 0 && output) {
          resolve(output);
        } else if (code === 0 && !output) {
          resolve('(No response)');
        } else {
          const errMsg = stderr.trim() || `claude exited with code ${code}`;
          reject(new Error(errMsg));
        }
      });

      // Close stdin immediately (we pass input via -p flag)
      proc.stdin.end();
    });
  }
}
```

### 2. Create `src/claude/session.js`

Session IDs for Claude Code need to be valid UUIDs. Map channel session IDs to UUIDs:

```js
import { randomUUID } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { getDataDir } from '../config.js';

const SESSION_MAP_PATH = join(getDataDir(), 'claude-sessions.json');

function loadSessionMap() {
  if (!existsSync(SESSION_MAP_PATH)) return {};
  return JSON.parse(readFileSync(SESSION_MAP_PATH, 'utf8'));
}

function saveSessionMap(map) {
  writeFileSync(SESSION_MAP_PATH, JSON.stringify(map, null, 2));
}

/**
 * Get or create a UUID session ID for a given channel session key.
 * @param {string} channelSessionKey - e.g. "tg-mybot-12345" or "dc-mybot-67890"
 * @returns {string} A stable UUID for this session
 */
export function getClaudeSessionId(channelSessionKey) {
  const map = loadSessionMap();
  if (!map[channelSessionKey]) {
    map[channelSessionKey] = randomUUID();
    saveSessionMap(map);
  }
  return map[channelSessionKey];
}

/**
 * Reset a session (for /reset command support).
 */
export function resetClaudeSession(channelSessionKey) {
  const map = loadSessionMap();
  delete map[channelSessionKey];
  saveSessionMap(map);
}
```

### 3. Modify Agent Config Schema

In `config.js`, the agent config currently only has `{ name, model }` where model is an EnConvo path like `ext/cmd`. Extend it to support a `type` field:

```js
// Agent config examples:
// EnConvo agent (current, backward-compatible):
{
  "name": "My Assistant",
  "model": "enconvo-ext/some-command",
  "type": "enconvo"   // optional, default
}

// Claude Code agent (new):
{
  "name": "Claude Code",
  "type": "claude-code",
  "model": "sonnet",                        // optional, claude model alias
  "systemPrompt": "You are a helpful assistant",  // optional
  "permissionMode": "plan",                  // optional, default "plan" (safe)
  "allowedTools": ["Read", "Grep", "Glob", "Bash(git:*)"],  // optional
  "disallowedTools": [],                     // optional
  "workingDir": "/Users/you/projects",       // optional, default $HOME
  "timeout": 120000                          // optional, ms
}
```

### 4. Modify Handler Logic

Both `src/telegram/handlers.js` and `src/discord/handlers.js` currently call:

```js
const reply = await enconvoClient.call(model, text, sessionId);
```

Change to route based on agent type:

```js
// In handlers.js — replace the enconvoClient.call() line:

let reply;
if (agentConfig.type === 'claude-code') {
  const { getClaudeSessionId } = await import('../claude/session.js');
  const claudeSessionId = getClaudeSessionId(sessionId);
  reply = await claudeClient.call(text, claudeSessionId);
} else {
  reply = await enconvoClient.call(model, text, sessionId);
}
```

### 5. Modify `gateway.js`

Import and instantiate `ClaudeCodeClient` when needed:

```js
import { ClaudeCodeClient } from './claude/client.js';

// In startGateway(), after creating enconvoClient:
// Create claude clients per agent that needs it
const claudeClients = new Map();
for (const [agentId, agentConfig] of Object.entries(agents)) {
  if (agentConfig.type === 'claude-code') {
    claudeClients.set(agentId, new ClaudeCodeClient({
      model: agentConfig.model,
      systemPrompt: agentConfig.systemPrompt,
      allowedTools: agentConfig.allowedTools,
      disallowedTools: agentConfig.disallowedTools,
      workingDir: agentConfig.workingDir,
      permissionMode: agentConfig.permissionMode,
      timeout: agentConfig.timeout,
    }));
  }
}
```

Then pass `claudeClients` to `createBot()` / `registerHandlers()`.

### 6. Modify `registerHandlers` Signature

Both Telegram and Discord handlers need to receive the claude client:

```js
// Before:
export function registerHandlers(bot, accountId, accountConfig, enconvoClient, agentConfig)

// After:
export function registerHandlers(bot, accountId, accountConfig, enconvoClient, agentConfig, claudeClient)
```

### 7. Update CLI `agents add` Command

In `src/cli.js`, update the agents add command to support claude-code type:

```js
agents.command('add')
  .description('Add an agent')
  .requiredOption('--id <id>', 'Agent identifier')
  .requiredOption('--name <name>', 'Display name')
  .option('--model <model>', 'Model (EnConvo path or claude model alias)')
  .option('--type <type>', 'Agent type: enconvo (default) or claude-code', 'enconvo')
  .option('--system-prompt <prompt>', 'System prompt (claude-code only)')
  .option('--permission-mode <mode>', 'Permission mode (claude-code only)', 'plan')
  .option('--allowed-tools <tools...>', 'Allowed tools (claude-code only)')
  .option('--working-dir <dir>', 'Working directory (claude-code only)')
  .option('--timeout <ms>', 'Timeout in ms (claude-code only)')
  .action((opts) => {
    const config = loadConfig();
    const agent = { name: opts.name, type: opts.type };
    if (opts.model) agent.model = opts.model;
    if (opts.systemPrompt) agent.systemPrompt = opts.systemPrompt;
    if (opts.permissionMode) agent.permissionMode = opts.permissionMode;
    if (opts.allowedTools) agent.allowedTools = opts.allowedTools;
    if (opts.workingDir) agent.workingDir = opts.workingDir;
    if (opts.timeout) agent.timeout = parseInt(opts.timeout);
    config.agents[opts.id] = agent;
    saveConfig(config);
    console.log(`Added ${opts.type} agent: ${opts.id} (${opts.name})`);
  });
```

### 8. Add `/reset` Command Support

Add a `/reset` command to both Telegram and Discord handlers so users can start a fresh conversation:

```js
// In telegram/handlers.js:
bot.command('reset', async (ctx) => {
  if (agentConfig.type === 'claude-code') {
    const { resetClaudeSession } = await import('../claude/session.js');
    const sessionId = getSessionId(accountId, ctx.chat.id);
    resetClaudeSession(sessionId);
    await ctx.reply('Session reset. Starting fresh conversation.');
  } else {
    await ctx.reply('Session reset is only available for Claude Code agents.');
  }
});
```

## Files to Create

| File | Purpose |
|------|---------|
| `src/claude/client.js` | Spawns `claude` CLI, collects output |
| `src/claude/session.js` | Maps channel session IDs to UUIDs |

## Files to Modify

| File | Change |
|------|--------|
| `src/gateway.js` | Import ClaudeCodeClient, instantiate per agent, pass to handlers |
| `src/telegram/handlers.js` | Route to claude or enconvo based on `agentConfig.type`, add `/reset` |
| `src/discord/handlers.js` | Same routing logic |
| `src/telegram/bot.js` | Pass claudeClient through to registerHandlers |
| `src/discord/bot.js` | Pass claudeClient through to registerDiscordHandlers |
| `src/cli.js` | Extend `agents add` with `--type`, `--system-prompt`, etc. |
| `package.json` | Update description |

## Usage Example

```bash
# 1. Add a Claude Code agent
enconvo-gw agents add \
  --id claude \
  --name "Claude Code" \
  --type claude-code \
  --model sonnet \
  --permission-mode plan \
  --working-dir /Users/you/projects

# 2. Connect a Telegram bot to it
enconvo-gw channels add \
  --channel telegram \
  --account mybot \
  --token "123456:ABC-DEF..." \
  --agent claude

# 3. Start the gateway
enconvo-gw gateway

# 4. Message the bot on Telegram — it talks to Claude Code!
```

## Security Considerations

1. **Permission mode**: Default to `plan` (read-only). Only use `bypassPermissions` or `dangerouslySkipPermissions` if you trust the remote users fully.

2. **Tool restrictions**: Use `--allowedTools` to limit what Claude Code can do. For a chat-only agent, you might restrict to just `Read` and `Grep`. For a full dev agent, leave unrestricted.

3. **Working directory**: Each agent has a `workingDir` — Claude Code will only have access to that directory tree.

4. **Pairing/allowlist**: The existing access control system (pairing codes, allowlists) protects who can talk to the bot. Keep `dmPolicy: 'pairing'`.

5. **Concurrency**: Each message spawns a separate `claude` process. Heavy use = many processes. Consider adding a per-user queue if needed.

6. **Cost**: Each Claude Code invocation uses API credits. Set `--max-budget-usd` in the agent config if you want to cap spending.

## Streaming Support (Advanced, Optional)

For real-time streaming (Claude types as it thinks), use `--output-format stream-json`:

```js
const args = ['-p', inputText, '--output-format', 'stream-json'];
// Then parse newline-delimited JSON chunks from stdout
// Each chunk has { type: 'assistant', content: [...] } etc.
// Feed these into the existing streamText/streamDiscordText functions
```

This is more complex but gives the "typing" effect. The basic implementation above waits for the full response, which is simpler and works well for most use cases.
