import { checkAccess } from './access.js';
import { sendText, streamText } from './send.js';
import { getSessionId } from './session.js';
import { getClaudeSession, markClaudeSessionStarted, resetClaudeSession } from '../claude/session.js';
import { downloadTelegramFile, collectOutboundFiles, cleanupOutboundFiles } from '../files.js';
import { createReadStream } from 'node:fs';
import { basename, extname } from 'node:path';
import { InputFile } from 'grammy';
import { log } from '../utils.js';

export function registerHandlers(bot, accountId, accountConfig, enconvoClient, agentConfig, claudeClient = null) {
  const model = agentConfig.model;
  const isClaudeCode = agentConfig.type === 'claude-code' && claudeClient != null;

  // /start command
  bot.command('start', async (ctx) => {
    await ctx.reply(`Hello! I'm ${agentConfig.name}. Send me a message and I'll respond.`);
  });

  // /help command
  bot.command('help', async (ctx) => {
    const backend = isClaudeCode ? 'Claude Code' : 'EnConvo';
    await ctx.reply(`I'm ${agentConfig.name}, powered by ${backend}.\nJust send me a message!\n\n/reset — start a fresh conversation`);
  });

  // /reset command — clears conversation session
  bot.command('reset', async (ctx) => {
    if (isClaudeCode) {
      const sessionKey = getSessionId(accountId, ctx.chat.id);
      const wasReset = resetClaudeSession(sessionKey);
      await ctx.reply(wasReset
        ? 'Session reset. Starting a fresh conversation.'
        : 'No active session to reset.');
    } else {
      await ctx.reply('Session reset is only available for Claude Code agents.');
    }
  });

  // Handle text messages
  bot.on('message:text', async (ctx) => {
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, ctx.message.text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle photos
  bot.on('message:photo', async (ctx) => {
    const caption = ctx.message.caption || 'Describe this image';
    const photo = ctx.message.photo.at(-1); // highest resolution
    const filePath = await downloadTelegramFile(ctx, photo.file_id, `tg_${Date.now()}_photo.jpg`).catch(() => null);
    const text = filePath ? `${caption}\n\n[File downloaded to: ${filePath}]` : caption;
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle videos
  bot.on('message:video', async (ctx) => {
    const caption = ctx.message.caption || 'Process this video';
    const video = ctx.message.video;
    const ext = video.mime_type?.split('/')[1] || 'mp4';
    const filePath = await downloadTelegramFile(ctx, video.file_id, `tg_${Date.now()}_video.${ext}`).catch(() => null);
    const text = filePath ? `${caption}\n\n[File downloaded to: ${filePath}]` : caption;
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle documents
  bot.on('message:document', async (ctx) => {
    const caption = ctx.message.caption || 'Process this file';
    const doc = ctx.message.document;
    const filename = doc.file_name || `tg_${Date.now()}_file`;
    const filePath = await downloadTelegramFile(ctx, doc.file_id, `tg_${Date.now()}_${filename}`).catch(() => null);
    const text = filePath ? `${caption}\n\n[File downloaded to: ${filePath}]` : caption;
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle voice/audio
  bot.on('message:voice', async (ctx) => {
    const voice = ctx.message.voice;
    const filePath = await downloadTelegramFile(ctx, voice.file_id, `tg_${Date.now()}_voice.ogg`).catch(() => null);
    const text = filePath
      ? `[Voice message downloaded to: ${filePath}]`
      : '[Voice message received]';
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle audio files
  bot.on('message:audio', async (ctx) => {
    const audio = ctx.message.audio;
    const filename = audio.file_name || `tg_${Date.now()}_audio.mp3`;
    const filePath = await downloadTelegramFile(ctx, audio.file_id, `tg_${Date.now()}_${filename}`).catch(() => null);
    const caption = ctx.message.caption || 'Process this audio';
    const text = filePath ? `${caption}\n\n[File downloaded to: ${filePath}]` : caption;
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle video notes (round videos)
  bot.on('message:video_note', async (ctx) => {
    const vn = ctx.message.video_note;
    const filePath = await downloadTelegramFile(ctx, vn.file_id, `tg_${Date.now()}_videonote.mp4`).catch(() => null);
    const text = filePath
      ? `[Video note downloaded to: ${filePath}]`
      : '[Video note received]';
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig);
  });

  // Handle stickers
  bot.on('message:sticker', async (ctx) => {
    const emoji = ctx.message.sticker.emoji || '';
    await handleMessage(ctx, accountId, accountConfig, enconvoClient, model, `[Sticker: ${emoji}]`, isClaudeCode, claudeClient, agentConfig);
  });
}

async function handleMessage(ctx, accountId, accountConfig, enconvoClient, model, text, isClaudeCode, claudeClient, agentConfig) {
  const chatId = ctx.chat.id;
  const senderName = ctx.from?.first_name || 'User';

  // Check access
  const access = checkAccess(accountConfig, accountId, ctx);
  if (!access.allowed) {
    if (access.pairingCode) {
      await ctx.reply(
        `🔑 To use this bot, please share this pairing code with the bot owner:\n\n` +
        `<code>${access.pairingCode}</code>\n\n` +
        `They can approve you with:\n` +
        `<code>enconvo-gw pairing approve telegram ${access.pairingCode}</code>`,
        { parse_mode: 'HTML' }
      );
    } else {
      await ctx.reply('Sorry, you are not authorized to use this bot.');
    }
    return;
  }

  // For group messages, only respond if mentioned or replied to
  const isGroup = ctx.chat.type === 'group' || ctx.chat.type === 'supergroup';
  if (isGroup) {
    const botInfo = ctx.me;
    const mentioned = text.includes(`@${botInfo.username}`);
    const isReply = ctx.message.reply_to_message?.from?.id === botInfo.id;
    if (!mentioned && !isReply) return;
    text = text.replace(`@${botInfo.username}`, '').trim();
  }

  if (!text) return;

  const sessionKey = getSessionId(accountId, chatId);
  log(accountId, `${senderName}: ${text.slice(0, 80)}${text.length > 80 ? '...' : ''}`);

  const streaming = accountConfig.streaming !== false; // default: on

  const typingInterval = setInterval(() => {
    ctx.api.sendChatAction(chatId, 'typing').catch(() => {});
  }, 4000);

  try {
    await ctx.api.sendChatAction(chatId, 'typing');

    const callStart = Date.now();
    let reply;
    if (isClaudeCode) {
      const session = getClaudeSession(sessionKey);
      reply = await claudeClient.call(text, session.uuid, { resume: session.started });
      if (!session.started) markClaudeSessionStarted(sessionKey);
    } else {
      reply = await enconvoClient.call(model, text, sessionKey);
    }

    clearInterval(typingInterval);
    log(accountId, `Reply: ${reply.slice(0, 80)}${reply.length > 80 ? '...' : ''}`);

    // Collect output files from outbound directory
    const { filePaths } = isClaudeCode ? collectOutboundFiles(callStart) : { filePaths: [] };

    if (streaming) {
      await streamText(ctx, reply);
    } else {
      await sendText(ctx, reply);
    }

    // Upload files to channel
    for (const fp of filePaths) {
      try {
        const ext = extname(fp).toLowerCase();
        const file = new InputFile(createReadStream(fp), basename(fp));
        if (['.mp4', '.mov', '.avi', '.mkv', '.webm'].includes(ext)) {
          await ctx.replyWithVideo(file);
        } else if (['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'].includes(ext)) {
          await ctx.replyWithAudio(file);
        } else if (['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'].includes(ext)) {
          await ctx.replyWithPhoto(file);
        } else {
          await ctx.replyWithDocument(file);
        }
        log(accountId, `Uploaded: ${basename(fp)}`);
      } catch (err) {
        log(accountId, `Failed to upload ${basename(fp)}: ${err.message}`);
      }
    }
    if (filePaths.length) cleanupOutboundFiles(filePaths);
  } catch (err) {
    clearInterval(typingInterval);
    const isTimeout = err.name === 'TimeoutError' || err.message?.includes('aborted') || err.message?.includes('timed out');
    log(accountId, `Error: ${isTimeout ? 'Timeout' : err.message}`);
    await ctx.reply(isTimeout
      ? 'Sorry, the request timed out. Please try again with a shorter message.'
      : 'Sorry, I encountered an error processing your message. Please try again.');
  }
}
