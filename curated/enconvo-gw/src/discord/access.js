import { isAllowed, createPairing } from '../pairing/pairing.js';
import { log } from '../utils.js';

/**
 * Check if a Discord message should be processed based on DM/group policy.
 * Returns { allowed: boolean, pairingCode?: string }
 */
export function checkDiscordAccess(accountConfig, accountId, message) {
  const isDM = message.channel.isDMBased();
  const senderId = message.author.id;
  const senderName = message.author.username || 'Unknown';

  // Guild (server) messages
  if (!isDM) {
    const policy = accountConfig.groupPolicy || 'open';
    if (policy === 'open') return { allowed: true };
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
    log('access', `Denied ${senderName} (${senderId}) on ${accountId} [discord] — not in allowlist`);
    return { allowed: false };
  }

  if (policy === 'pairing') {
    const code = createPairing(accountId, senderId, senderName);
    log('access', `Pairing code ${code} for ${senderName} (${senderId}) on ${accountId} [discord]`);
    return { allowed: false, pairingCode: code };
  }

  return { allowed: false };
}
