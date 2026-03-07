import { log, sleep } from '../utils.js';

const MAX_LENGTH = 1900; // Discord limit is 2000, leave margin
const MAX_RETRIES = 3;
const STREAM_CHUNK_CHARS = 60;
const STREAM_INTERVAL_MS = 50;
const EDIT_COOLDOWN_MS = 300;

/**
 * Send text as one or more Discord messages (no streaming).
 */
export async function sendDiscordText(message, text) {
  const chunks = chunkText(text, MAX_LENGTH);
  for (const chunk of chunks) {
    await sendWithRetry(message, chunk);
  }
}

/**
 * Stream text into Discord by sending a placeholder then progressively editing it.
 */
export async function streamDiscordText(message, text) {
  if (text.length <= 20) {
    return sendDiscordText(message, text);
  }

  const chunks = chunkText(text, MAX_LENGTH);

  // Stream the first chunk progressively
  await streamChunk(message, chunks[0]);

  // Send remaining chunks normally
  for (let i = 1; i < chunks.length; i++) {
    await sendWithRetry(message, chunks[i]);
  }
}

/**
 * Progressively reveal a single chunk by editing a placeholder message.
 */
async function streamChunk(message, text) {
  let sent;
  try {
    sent = await message.channel.send('\u258D');
  } catch {
    return sendWithRetry(message, text);
  }

  let pos = 0;
  let lastEditTime = 0;

  while (pos < text.length) {
    let end = Math.min(pos + STREAM_CHUNK_CHARS, text.length);
    if (end < text.length) {
      const spaceIdx = text.lastIndexOf(' ', end);
      const nlIdx = text.lastIndexOf('\n', end);
      const breakAt = Math.max(spaceIdx, nlIdx);
      if (breakAt > pos) end = breakAt + 1;
    }

    pos = end;
    const displayText = pos < text.length ? text.slice(0, pos) + ' \u258D' : text.slice(0, pos);

    const now = Date.now();
    const elapsed = now - lastEditTime;
    if (elapsed < EDIT_COOLDOWN_MS) {
      await sleep(EDIT_COOLDOWN_MS - elapsed);
    }

    try {
      await sent.edit(displayText);
      lastEditTime = Date.now();
    } catch (err) {
      // On rate limit, wait and retry once
      if (err.status === 429) {
        const retryAfter = (err.retry_after || 1) * 1000;
        log('stream', `Rate limited, waiting ${retryAfter}ms`);
        await sleep(retryAfter);
        try {
          await sent.edit(displayText);
          lastEditTime = Date.now();
        } catch {}
      }
    }

    if (pos < text.length) {
      await sleep(STREAM_INTERVAL_MS);
    }
  }

  // Final clean edit
  try {
    await sent.edit(text);
  } catch {}
}

async function sendWithRetry(message, text) {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      await message.channel.send(text);
      return;
    } catch (err) {
      if (attempt === MAX_RETRIES) throw err;
      log('send', `Discord retry ${attempt}/${MAX_RETRIES}: ${err.message}`);
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
