export function formatTimestamp(sqliteUtc) {
  if (!sqliteUtc) return '';
  // SQLite's CURRENT_TIMESTAMP stores "YYYY-MM-DD HH:MM:SS" in UTC with no
  // timezone marker. Make that explicit so the browser doesn't guess wrong.
  const isoUtc = sqliteUtc.replace(' ', 'T') + 'Z';
  const date = new Date(isoUtc);
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}