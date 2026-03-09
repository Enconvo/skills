import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { registerDiscordHandlers } from './handlers.js';
import { log } from '../utils.js';

export function createDiscordBot(accountId, accountConfig, enconvoClient, agentConfig, claudeClient = null) {
  const client = new Client({
    intents: [
      GatewayIntentBits.Guilds,
      GatewayIntentBits.GuildMessages,
      GatewayIntentBits.DirectMessages,
      // MessageContent is a privileged intent — only add if enabled in Developer Portal.
      // DMs and @mentions work without it.
      ...(accountConfig.messageContentIntent ? [GatewayIntentBits.MessageContent] : []),
    ],
    partials: [Partials.Channel],
  });

  registerDiscordHandlers(client, accountId, accountConfig, enconvoClient, agentConfig, claudeClient);

  client.on('error', (err) => {
    log(accountId, `[discord] Client error: ${err.message}`);
  });

  return client;
}

export async function startDiscordBot(client, accountConfig, accountId) {
  return new Promise((resolve, reject) => {
    client.once('clientReady', () => {
      log(accountId, `Discord @${client.user.tag} connected`);
      resolve();
    });

    client.login(accountConfig.botToken).catch(reject);
  });
}

export function stopDiscordBot(client, accountId) {
  try {
    client.destroy();
    log(accountId, '[discord] Bot stopped');
  } catch {}
}
