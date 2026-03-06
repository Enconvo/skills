import { Bot } from 'grammy';
import { registerHandlers } from './handlers.js';
import { log } from '../utils.js';

export function createBot(accountId, accountConfig, enconvoClient, agentConfig, claudeClient = null) {
  const bot = new Bot(accountConfig.botToken);

  // Dedup middleware — skip already-processed updates
  const seen = new Set();
  bot.use(async (ctx, next) => {
    const updateId = ctx.update.update_id;
    if (seen.has(updateId)) return;
    seen.add(updateId);
    // Keep set bounded
    if (seen.size > 1000) {
      const arr = [...seen];
      for (let i = 0; i < 500; i++) seen.delete(arr[i]);
    }
    await next();
  });

  // Sequentialize per chat — process messages in order per chat
  bot.use(async (ctx, next) => {
    await next();
  });

  // Register message handlers
  registerHandlers(bot, accountId, accountConfig, enconvoClient, agentConfig, claudeClient);

  // Error handler
  bot.catch((err) => {
    log(accountId, `Bot error: ${err.message}`);
  });

  return bot;
}

export async function startBot(bot, accountId, signal) {
  const me = await bot.api.getMe();
  log(accountId, `Bot @${me.username} connected (${me.first_name})`);

  await bot.start({
    drop_pending_updates: true,
    onStart: () => log(accountId, 'Polling started'),
    allowed_updates: ['message', 'callback_query'],
  });
}

export function stopBot(bot, accountId) {
  try {
    bot.stop();
    log(accountId, 'Bot stopped');
  } catch {}
}
