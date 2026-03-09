import { writeFileSync, readFileSync, unlinkSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { loadConfig, getDataDir } from './config.js';
import { EnConvoClient } from './enconvo/client.js';
import { ClaudeCodeClient } from './claude/client.js';
import { createBot, startBot, stopBot } from './telegram/bot.js';
import { createDiscordBot, startDiscordBot, stopDiscordBot } from './discord/bot.js';
import { log, sleep } from './utils.js';

const PID_FILE = join(getDataDir(), 'gateway.pid');
const MAX_BACKOFF = 5 * 60 * 1000; // 5 min

export function getPidFile() {
  return PID_FILE;
}

export function isRunning() {
  if (!existsSync(PID_FILE)) return false;
  const pid = parseInt(readFileSync(PID_FILE, 'utf8').trim());
  try {
    process.kill(pid, 0);
    return pid;
  } catch {
    // Stale PID file
    try { unlinkSync(PID_FILE); } catch {}
    return false;
  }
}

export function killExisting() {
  const pid = isRunning();
  if (pid) {
    log('gateway', `Killing existing gateway (PID ${pid})`);
    try { process.kill(pid, 'SIGTERM'); } catch {}
    try { unlinkSync(PID_FILE); } catch {}
    return true;
  }
  return false;
}

export async function startGateway(opts = {}) {
  if (opts.force) {
    killExisting();
    await sleep(1000);
  }

  const existingPid = isRunning();
  if (existingPid) {
    log('gateway', `Already running (PID ${existingPid}). Use --force to restart.`);
    process.exit(1);
  }

  // Write PID
  writeFileSync(PID_FILE, String(process.pid));

  const config = loadConfig();
  const enconvoClient = new EnConvoClient(config.enconvo?.url);
  const accounts = config.channels?.telegram?.accounts || {};
  const agents = config.agents || {};
  const bots = new Map();

  // Build a ClaudeCodeClient for each claude-code agent
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
      log('gateway', `Claude Code agent: ${agentId} (model=${agentConfig.model || 'default'})`);
    }
  }

  log('gateway', `Starting gateway (PID ${process.pid})`);

  const discordClients = new Map();

  // Graceful shutdown
  const shutdown = () => {
    log('gateway', 'Shutting down...');
    for (const [id, bot] of bots) {
      stopBot(bot, id);
    }
    for (const [id, client] of discordClients) {
      stopDiscordBot(client, id);
    }
    try { unlinkSync(PID_FILE); } catch {}
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  // Start each enabled account
  for (const [accountId, accountConfig] of Object.entries(accounts)) {
    if (!accountConfig.enabled) {
      log('gateway', `Skipping disabled account: ${accountId}`);
      continue;
    }

    const agentId = accountConfig.agentId;
    const agentConfig = agents[agentId];
    if (!agentConfig) {
      log('gateway', `No agent config for ${agentId}, skipping ${accountId}`);
      continue;
    }

    const claudeClient = claudeClients.get(accountConfig.agentId) || null;
    startBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, bots, claudeClient);
  }

  // Start Discord bots
  const discordAccounts = config.channels?.discord?.accounts || {};
  for (const [accountId, accountConfig] of Object.entries(discordAccounts)) {
    if (!accountConfig.enabled) {
      log('gateway', `Skipping disabled Discord account: ${accountId}`);
      continue;
    }

    const agentId = accountConfig.agentId;
    const agentConfig = agents[agentId];
    if (!agentConfig) {
      log('gateway', `No agent config for ${agentId}, skipping Discord ${accountId}`);
      continue;
    }

    const claudeClient = claudeClients.get(agentId) || null;
    startDiscordBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, discordClients, claudeClient);
  }

  if (bots.size === 0 && discordClients.size === 0) {
    log('gateway', 'No bots to start. Add channels with: enconvo-gw channels add');
    try { unlinkSync(PID_FILE); } catch {}
    process.exit(1);
  }
}

async function startBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, bots, claudeClient = null, backoff = 5000) {
  try {
    const bot = createBot(accountId, accountConfig, enconvoClient, agentConfig, claudeClient);
    bots.set(accountId, bot);
    await startBot(bot, accountId);
  } catch (err) {
    log(accountId, `Failed to start: ${err.message}`);
    const nextBackoff = Math.min(backoff * 2, MAX_BACKOFF);
    log(accountId, `Retrying in ${backoff / 1000}s...`);
    await sleep(backoff);
    return startBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, bots, claudeClient, nextBackoff);
  }
}

async function startDiscordBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, discordClients, claudeClient = null, backoff = 5000) {
  try {
    const client = createDiscordBot(accountId, accountConfig, enconvoClient, agentConfig, claudeClient);
    discordClients.set(`dc:${accountId}`, client);
    await startDiscordBot(client, accountConfig, accountId);
  } catch (err) {
    log(accountId, `[discord] Failed to start: ${err.message}`);
    const nextBackoff = Math.min(backoff * 2, MAX_BACKOFF);
    log(accountId, `[discord] Retrying in ${backoff / 1000}s...`);
    await sleep(backoff);
    return startDiscordBotWithRetry(accountId, accountConfig, enconvoClient, agentConfig, discordClients, claudeClient, nextBackoff);
  }
}

export function stopGateway() {
  const pid = isRunning();
  if (!pid) {
    console.log('Gateway is not running.');
    return;
  }
  try {
    process.kill(pid, 'SIGTERM');
    console.log(`Sent SIGTERM to gateway (PID ${pid})`);
    try { unlinkSync(PID_FILE); } catch {}
  } catch (err) {
    console.error(`Failed to stop gateway: ${err.message}`);
  }
}

export function gatewayStatus() {
  const pid = isRunning();
  if (pid) {
    console.log(`Gateway is running (PID ${pid})`);
  } else {
    console.log('Gateway is not running.');
  }
}
