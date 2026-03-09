import { checkDiscordAccess } from './access.js';
import { sendDiscordText, streamDiscordText } from './send.js';
import { getDiscordSessionId } from './session.js';
import { getClaudeSession, markClaudeSessionStarted, resetClaudeSession } from '../claude/session.js';
import { downloadDiscordAttachment, collectOutboundFiles, cleanupOutboundFiles } from '../files.js';
import { basename } from 'node:path';
import { AttachmentBuilder } from 'discord.js';
import { log } from '../utils.js';

export function registerDiscordHandlers(client, accountId, accountConfig, enconvoClient, agentConfig, claudeClient = null) {
  const model = agentConfig.model;
  const isClaudeCode = agentConfig.type === 'claude-code' && claudeClient != null;

  client.on('messageCreate', async (message) => {
    // Skip bot messages
    if (message.author.bot) return;

    const isDM = message.channel.isDMBased();
    let text = message.content || '';

    // Handle !reset command in DMs or when mentioned
    if (text.trim() === '!reset' || text.trim() === '/reset') {
      if (isClaudeCode) {
        const sessionKey = getDiscordSessionId(accountId, message.channel.id);
        const wasReset = resetClaudeSession(sessionKey);
        await message.channel.send(wasReset
          ? 'Session reset. Starting a fresh conversation.'
          : 'No active session to reset.');
      } else {
        await message.channel.send('Session reset is only available for Claude Code agents.');
      }
      return;
    }

    // Guild messages: only respond if mentioned or replied to
    if (!isDM) {
      const mentioned = message.mentions.has(client.user);
      let isReply = false;
      if (message.reference) {
        try {
          const ref = await message.channel.messages.fetch(message.reference.messageId);
          isReply = ref.author.id === client.user.id;
        } catch {}
      }
      if (!mentioned && !isReply) return;
      // Strip bot mention from text
      text = text.replace(new RegExp(`<@!?${client.user.id}>`, 'g'), '').trim();
    }

    // Download any attachments (images, videos, files)
    if (message.attachments.size > 0) {
      const filePaths = [];
      for (const [, attachment] of message.attachments) {
        try {
          const localPath = await downloadDiscordAttachment(attachment);
          filePaths.push(localPath);
        } catch (err) {
          log(accountId, `[discord] Failed to download ${attachment.name}: ${err.message}`);
        }
      }
      if (filePaths.length) {
        const fileList = filePaths.map(p => `[File downloaded to: ${p}]`).join('\n');
        text = text ? `${text}\n\n${fileList}` : `Process these files\n\n${fileList}`;
      }
    }

    if (!text) return;

    // Check access
    const access = checkDiscordAccess(accountConfig, accountId, message);
    if (!access.allowed) {
      if (access.pairingCode) {
        await message.channel.send(
          `To use this bot, share this pairing code with the bot owner:\n\n` +
          `\`${access.pairingCode}\`\n\n` +
          `They can approve you with:\n` +
          `\`enconvo-gw pairing approve discord ${access.pairingCode}\``
        );
      } else {
        await message.channel.send('Sorry, you are not authorized to use this bot.');
      }
      return;
    }

    const channelId = message.channel.id;
    const senderName = message.author.username || 'User';
    const sessionKey = getDiscordSessionId(accountId, channelId);
    log(accountId, `[discord] ${senderName}: ${text.slice(0, 80)}${text.length > 80 ? '...' : ''}`);

    const streaming = accountConfig.streaming !== false;

    const typingInterval = setInterval(() => {
      message.channel.sendTyping().catch(() => {});
    }, 8000);

    try {
      await message.channel.sendTyping();

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
      log(accountId, `[discord] Reply: ${reply.slice(0, 80)}${reply.length > 80 ? '...' : ''}`);

      // Collect output files from outbound directory
      const { filePaths } = isClaudeCode ? collectOutboundFiles(callStart) : { filePaths: [] };

      if (streaming) {
        await streamDiscordText(message, reply);
      } else {
        await sendDiscordText(message, reply);
      }

      // Upload files to channel
      for (const fp of filePaths) {
        try {
          const attachment = new AttachmentBuilder(fp, { name: basename(fp) });
          await message.channel.send({ files: [attachment] });
          log(accountId, `[discord] Uploaded: ${basename(fp)}`);
        } catch (err) {
          log(accountId, `[discord] Failed to upload ${basename(fp)}: ${err.message}`);
        }
      }
      if (filePaths.length) cleanupOutboundFiles(filePaths);
    } catch (err) {
      clearInterval(typingInterval);
      const isTimeout = err.name === 'TimeoutError' || err.message?.includes('aborted') || err.message?.includes('timed out');
      log(accountId, `[discord] Error: ${isTimeout ? 'Timeout' : err.message}`);
      await message.channel.send(isTimeout
        ? 'Sorry, the request timed out. Please try again with a shorter message.'
        : 'Sorry, I encountered an error processing your message. Please try again.');
    }
  });
}
