import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const DATA_DIR = join(homedir(), '.enconvo-gw');
const CONFIG_PATH = join(DATA_DIR, 'config.json');

const DEFAULT_CONFIG = {
  enconvo: { url: 'http://localhost:54535' },
  agents: {},
  channels: { telegram: { accounts: {} }, discord: { accounts: {} } }
};

export function getDataDir() {
  return DATA_DIR;
}

export function ensureDataDirs() {
  for (const sub of ['', 'pairing', 'allowlists', 'media/inbound', 'media/outbound']) {
    const dir = join(DATA_DIR, sub);
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  }
}

export function loadConfig() {
  ensureDataDirs();
  if (!existsSync(CONFIG_PATH)) {
    writeFileSync(CONFIG_PATH, JSON.stringify(DEFAULT_CONFIG, null, 2));
    return structuredClone(DEFAULT_CONFIG);
  }
  return JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
}

export function saveConfig(config) {
  ensureDataDirs();
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

export function getConfigValue(path) {
  const config = loadConfig();
  const parts = path.split('.');
  let val = config;
  for (const p of parts) {
    if (val == null || typeof val !== 'object') return undefined;
    val = val[p];
  }
  return val;
}

export function setConfigValue(path, value) {
  const config = loadConfig();
  const parts = path.split('.');
  let obj = config;
  for (let i = 0; i < parts.length - 1; i++) {
    if (obj[parts[i]] == null || typeof obj[parts[i]] !== 'object') {
      obj[parts[i]] = {};
    }
    obj = obj[parts[i]];
  }
  // Try to parse JSON values
  try {
    value = JSON.parse(value);
  } catch {}
  obj[parts[parts.length - 1]] = value;
  saveConfig(config);
}
