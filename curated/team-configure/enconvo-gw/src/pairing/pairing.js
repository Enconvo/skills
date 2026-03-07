import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { getDataDir } from '../config.js';
import { generateCode, log } from '../utils.js';

const TTL_MS = 60 * 60 * 1000; // 60 minutes
const MAX_PENDING = 3;

function pairingPath(accountId) {
  return join(getDataDir(), 'pairing', `${accountId}.json`);
}

function allowlistPath(accountId) {
  return join(getDataDir(), 'allowlists', `${accountId}.json`);
}

function loadPairings(accountId) {
  const path = pairingPath(accountId);
  if (!existsSync(path)) return [];
  const data = JSON.parse(readFileSync(path, 'utf8'));
  const now = Date.now();
  // Filter expired
  return data.filter(p => now - p.createdAt < TTL_MS);
}

function savePairings(accountId, pairings) {
  writeFileSync(pairingPath(accountId), JSON.stringify(pairings, null, 2));
}

export function loadAllowlist(accountId) {
  const path = allowlistPath(accountId);
  if (!existsSync(path)) return [];
  return JSON.parse(readFileSync(path, 'utf8'));
}

function saveAllowlist(accountId, list) {
  writeFileSync(allowlistPath(accountId), JSON.stringify(list, null, 2));
}

export function isAllowed(accountId, senderId) {
  const list = loadAllowlist(accountId);
  return list.includes(String(senderId));
}

export function createPairing(accountId, senderId, senderName) {
  const pairings = loadPairings(accountId);

  // Already has pending?
  const existing = pairings.find(p => String(p.senderId) === String(senderId));
  if (existing) return existing.code;

  if (pairings.length >= MAX_PENDING) {
    // Remove oldest
    pairings.shift();
  }

  const code = generateCode(8);
  pairings.push({
    code,
    senderId: String(senderId),
    senderName: senderName || 'Unknown',
    createdAt: Date.now()
  });
  savePairings(accountId, pairings);
  log('pairing', `Created code ${code} for ${senderName} (${senderId}) on ${accountId}`);
  return code;
}

export function listPairings(accountId) {
  return loadPairings(accountId);
}

export function approvePairing(accountId, code) {
  const pairings = loadPairings(accountId);
  const idx = pairings.findIndex(p => p.code.toUpperCase() === code.toUpperCase());
  if (idx === -1) return null;

  const pairing = pairings[idx];
  pairings.splice(idx, 1);
  savePairings(accountId, pairings);

  // Add to allowlist
  const list = loadAllowlist(accountId);
  if (!list.includes(pairing.senderId)) {
    list.push(pairing.senderId);
    saveAllowlist(accountId, list);
  }

  log('pairing', `Approved ${pairing.senderName} (${pairing.senderId}) for ${accountId}`);
  return pairing;
}
