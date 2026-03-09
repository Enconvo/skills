import { mkdirSync, existsSync, createWriteStream, statSync, readdirSync, unlinkSync } from 'node:fs';
import { join, extname } from 'node:path';
import { homedir } from 'node:os';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
import { getDataDir } from './config.js';
import { log } from './utils.js';

const INBOUND_DIR = join(getDataDir(), 'media/inbound');
const OUTBOUND_DIR = join(getDataDir(), 'media/outbound');

function ensureDir(dir) {
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

export function getOutboundDir() {
  ensureDir(OUTBOUND_DIR);
  return OUTBOUND_DIR;
}

/**
 * Download a file from a URL to the inbound media directory.
 */
export async function downloadFile(url, filename) {
  ensureDir(INBOUND_DIR);
  const localPath = join(INBOUND_DIR, filename);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);
  await pipeline(Readable.fromWeb(res.body), createWriteStream(localPath));
  log('files', `Downloaded: ${filename}`);
  return localPath;
}

/**
 * Download a Telegram file via bot API.
 */
export async function downloadTelegramFile(ctx, fileId, filename) {
  const file = await ctx.api.getFile(fileId);
  const url = `https://api.telegram.org/file/bot${ctx.api.token}/${file.file_path}`;
  return downloadFile(url, filename);
}

/**
 * Download a Discord attachment.
 */
export async function downloadDiscordAttachment(attachment) {
  const filename = `dc_${Date.now()}_${attachment.name}`;
  return downloadFile(attachment.url, filename);
}

// File extensions that should be uploaded back to the channel
const UPLOADABLE_EXTENSIONS = new Set([
  '.mp4', '.mov', '.avi', '.mkv', '.webm',
  '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp',
  '.pdf', '.docx', '.xlsx', '.pptx', '.csv',
  '.zip', '.tar', '.gz',
]);

/**
 * Collect output files from the outbound directory that were created/modified after startTime.
 * Removes collected files from outbound after listing them (so they aren't re-uploaded next time).
 *
 * @param {number} startTime - timestamp (ms); only files modified after this are included
 * @returns {{ filePaths: string[] }}
 */
export function collectOutboundFiles(startTime) {
  ensureDir(OUTBOUND_DIR);
  const filePaths = [];

  try {
    for (const entry of readdirSync(OUTBOUND_DIR, { withFileTypes: true })) {
      if (!entry.isFile()) continue;
      const fullPath = join(OUTBOUND_DIR, entry.name);
      try {
        const s = statSync(fullPath);
        if (s.mtimeMs >= startTime && s.size > 0) {
          filePaths.push(fullPath);
        }
      } catch {}
    }
  } catch {}

  for (const fp of filePaths) {
    const mb = (statSync(fp).size / 1024 / 1024).toFixed(1);
    log('files', `Outbound file: ${fp} (${mb}MB)`);
  }

  return { filePaths };
}

/**
 * Delete files after they've been uploaded to the channel.
 */
export function cleanupOutboundFiles(filePaths) {
  for (const fp of filePaths) {
    try { unlinkSync(fp); } catch {}
  }
}
