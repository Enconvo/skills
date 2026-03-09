export function getDiscordSessionId(accountId, channelId) {
  return `dc-${accountId}-${channelId}`;
}
