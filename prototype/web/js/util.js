export function escapeHtml(s) {
  if (s == null) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function formatNotional(currency, amount) {
  const n = Number(amount);
  if (!Number.isFinite(n)) return `${currency} ${amount}`;
  if (n >= 1_000_000) return `${currency} ${(n / 1_000_000).toFixed(1)}m`;
  if (n >= 1_000) return `${currency} ${(n / 1_000).toFixed(1)}k`;
  return `${currency} ${n.toLocaleString()}`;
}

export function formatTimeShort(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const hh = String(d.getUTCHours()).padStart(2, "0");
  const mm = String(d.getUTCMinutes()).padStart(2, "0");
  const ss = String(d.getUTCSeconds()).padStart(2, "0");
  if (ss === "00") return `${hh}:${mm}Z`;
  return `${hh}:${mm}:${ss}Z`;
}

export function formatDateTimeUtc(iso) {
  if (!iso) return "—";
  return iso.replace("T", " ").replace("Z", "Z");
}

export function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "/trades";
  const [path, query = ""] = raw.split("?");
  const params = new URLSearchParams(query);
  return { path, params };
}

export function navigate(path, params = {}) {
  const q = new URLSearchParams(params);
  const qs = q.toString();
  location.hash = qs ? `#${path}?${qs}` : `#${path}`;
}
