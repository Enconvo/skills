import { isAllowed, createPairing } from '../pairing/pairing.js';
import { log } from '../utils.js';

/**
 * Check if a message should be processed based on DM/group policy.
 * Returns { allowed: boolean, pairingCode?: string }
 */
export function checkAccess(accountConfig, accountId, ctx) {
  const chatType = ctx.chat?.type;
  const isGroup = chatType === 'group' || chatType === 'supergroup';
  const senderId = String(ctx.from?.id);
  const senderName = [ctx.from?.first_name, ctx.from?.last_name].filter(Boolean).join(' ') || ctx.from?.username || 'Unknown';

  // Group messages
  if (isGroup) {
    const policy = accountConfig.groupPolicy || 'open';
    if (policy === 'open') return { allowed: true };
    // Could add more group policies later
    return { allowed: true };
  }

  // DM messages
  const policy = accountConfig.dmPolicy || 'pairing';

  if (policy === 'open') return { allowed: true };

  // Check static allowFrom in config
  if (accountConfig.allowFrom?.includes(senderId)) return { allowed: true };

  // Check dynamic allowlist file
  if (isAllowed(accountId, senderId)) return { allowed: true };

  if (policy === 'allowlist') {
    log('access', `Denied ${senderName} (${senderId}) on ${accountId} — not in allowlist`);
    return { allowed: false };
  }

  if (policy === 'pairing') {
    const code = createPairing(accountId, senderId, senderName);
    log('access', `Pairing code ${code} for ${senderName} (${senderId}) on ${accountId}`);
    return { allowed: false, pairingCode: code };
  }

  return { allowed: false };
}
