import { randomBytes } from 'node:crypto';

const SAFE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export function generateCode(length = 8) {
  const bytes = randomBytes(length);
  let code = '';
  for (let i = 0; i < length; i++) {
    code += SAFE_CHARS[bytes[i] % SAFE_CHARS.length];
  }
  return code;
}

export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function log(tag, ...args) {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${tag}]`, ...args);
}
