export function getSessionId(accountId, chatId) {
  return `tg-${accountId}-${chatId}`;
}
