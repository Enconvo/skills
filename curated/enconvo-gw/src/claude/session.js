import { randomUUID } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { getDataDir } from '../config.js';

const SESSION_MAP_PATH = join(getDataDir(), 'claude-sessions.json');

function loadSessionMap() {
  if (!existsSync(SESSION_MAP_PATH)) return {};
  try {
    return JSON.parse(readFileSync(SESSION_MAP_PATH, 'utf8'));
  } catch {
    return {};
  }
}

function saveSessionMap(map) {
  writeFileSync(SESSION_MAP_PATH, JSON.stringify(map, null, 2));
}

/**
 * Get or create a session entry for a given channel session key.
 * @param {string} channelSessionKey - e.g. "tg-mybot-12345"
 * @returns {{ uuid: string, started: boolean }}
 */
export function getClaudeSession(channelSessionKey) {
  const map = loadSessionMap();
  const entry = map[channelSessionKey];
  if (!entry) {
    map[channelSessionKey] = { uuid: randomUUID(), started: false };
    saveSessionMap(map);
    return map[channelSessionKey];
  }
  // Migrate old format (plain string UUID) to new format
  if (typeof entry === 'string') {
    map[channelSessionKey] = { uuid: entry, started: true };
    saveSessionMap(map);
  }
  return map[channelSessionKey];
}

/**
 * Mark a session as started (first call completed successfully).
 */
export function markClaudeSessionStarted(channelSessionKey) {
  const map = loadSessionMap();
  if (map[channelSessionKey]) {
    map[channelSessionKey].started = true;
    saveSessionMap(map);
  }
}

/**
 * Reset a session — next message will start a fresh conversation.
 */
export function resetClaudeSession(channelSessionKey) {
  const map = loadSessionMap();
  if (map[channelSessionKey]) {
    delete map[channelSessionKey];
    saveSessionMap(map);
    return true;
  }
  return false;
}
