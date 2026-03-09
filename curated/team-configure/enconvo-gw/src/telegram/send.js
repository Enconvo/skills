import { log, sleep } from '../utils.js';

const MAX_LENGTH = 4000;
const MAX_RETRIES = 3;
const STREAM_CHUNK_CHARS = 60;   // characters per edit tick
const STREAM_INTERVAL_MS = 50;   // ms between edits
const EDIT_COOLDOWN_MS = 300;    // min ms between Telegram editMessage calls (rate limit)

/**
 * Send text as a single message (no streaming).
 */
export async function sendText(ctx, text) {
  const chunks = chunkText(text, MAX_LENGTH);
  for (const chunk of chunks) {
    await sendWithRetry(ctx, chunk);
  }
}

/**
 * Stream text into Telegram by sending a placeholder then progressively editing it.
 * For long responses (>4000 chars), streams the first chunk then sends the rest normally.
 */
export async function streamText(ctx, text) {
  if (text.length <= 20) {
    // Too short to bother streaming
    return sendText(ctx, text);
  }

  const chunks = chunkText(text, MAX_LENGTH);

  // Stream the first chunk progressively
  await streamChunk(ctx, chunks[0]);

  // Send remaining chunks normally
  for (let i = 1; i < chunks.length; i++) {
    await sendWithRetry(ctx, chunks[i]);
  }
}

/**
 * Progressively reveal a single chunk by editing a placeholder message.
 */
async function streamChunk(ctx, text) {
  // Send initial placeholder
  let sent;
  try {
    sent = await ctx.reply('▍', { parse_mode: undefined });
  } catch {
    // Fallback: just send the full text
    return sendWithRetry(ctx, text);
  }

  const chatId = sent.chat.id;
  const messageId = sent.message_id;
  let displayed = '';
  let pos = 0;
  let lastEditTime = 0;

  while (pos < text.length) {
    // Advance by STREAM_CHUNK_CHARS, but try to break at word boundary
    let end = Math.min(pos + STREAM_CHUNK_CHARS, text.length);
    if (end < text.length) {
      // Try to break at space/newline within the chunk
      const spaceIdx = text.lastIndexOf(' ', end);
      const nlIdx = text.lastIndexOf('\n', end);
      const breakAt = Math.max(spaceIdx, nlIdx);
      if (breakAt > pos) end = breakAt + 1;
    }

    displayed = text.slice(0, end);
    pos = end;

    // Add cursor if not finished
    const displayText = pos < text.length ? displayed + ' ▍' : displayed;

    // Respect rate limits
    const now = Date.now();
    const elapsed = now - lastEditTime;
    if (elapsed < EDIT_COOLDOWN_MS) {
      await sleep(EDIT_COOLDOWN_MS - elapsed);
    }

    try {
      await ctx.api.editMessageText(chatId, messageId, displayText);
      lastEditTime = Date.now();
    } catch (err) {
      // "message is not modified" is fine (same text)
      if (!err.description?.includes('not modified')) {
        // On rate limit (429), wait and retry
        if (err.error_code === 429) {
          const retryAfter = (err.parameters?.retry_after || 1) * 1000;
          log('stream', `Rate limited, waiting ${retryAfter}ms`);
          await sleep(retryAfter);
          try {
            await ctx.api.editMessageText(chatId, messageId, displayText);
            lastEditTime = Date.now();
          } catch {}
        }
      }
    }

    if (pos < text.length) {
      await sleep(STREAM_INTERVAL_MS);
    }
  }

  // Final edit to clean text (remove cursor, no parse mode issues)
  try {
    await ctx.api.editMessageText(chatId, messageId, text);
  } catch {}
}

async function sendWithRetry(ctx, text) {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      await ctx.reply(text, { parse_mode: 'HTML' });
      return;
    } catch (err) {
      if (err.description?.includes('parse')) {
        try {
          await ctx.reply(text);
          return;
        } catch (plainErr) {
          if (attempt === MAX_RETRIES) throw plainErr;
        }
      }
      if (attempt === MAX_RETRIES) throw err;
      log('send', `Retry ${attempt}/${MAX_RETRIES}: ${err.message}`);
      await sleep(1000 * attempt);
    }
  }
}

function chunkText(text, maxLen) {
  if (text.length <= maxLen) return [text];
  const chunks = [];
  let remaining = text;
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) {
      chunks.push(remaining);
      break;
    }
    let breakAt = remaining.lastIndexOf('\n', maxLen);
    if (breakAt < maxLen * 0.3) breakAt = maxLen;
    chunks.push(remaining.slice(0, breakAt));
    remaining = remaining.slice(breakAt).trimStart();
  }
  return chunks;
}
