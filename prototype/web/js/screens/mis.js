import { api } from "../api.js";
import { renderStatusChip, tradeStatusLabel } from "../labels.js";
import { escapeHtml, formatTimeShort, navigate } from "../util.js";

export async function renderMis(root) {
  const [summary, aging, contagion, errors, book] = await Promise.all([
    api("GET", "/analytics/summary").then((r) => r.data),
    api("GET", "/analytics/aging").then((r) => r.data),
    api("GET", "/analytics/contagion").then((r) => r.data),
    api("GET", "/analytics/queues/errors").then((r) => r.data),
    api("GET", "/trades").then((r) => r.data),
  ]).catch(() => null);

  if (!summary) {
    root.innerHTML = `<p>Could not load MIS analytics.</p>`;
    return;
  }

  const counts = book.counts || {};
  const queueParts = [
    "Received",
    "Validating",
    "Composing",
    "ManualDraft",
    "Sent",
    "AffirmPending",
    "Affirmed",
  ]
    .map((st) => `${tradeStatusLabel(st)} ${counts[st] ?? 0}`)
    .join(" · ");

  const kpis = `
    <div class="cdu-kpi"><div class="value">${summary.volumes?.received ?? "—"}</div><div class="label">Received today</div></div>
    <div class="cdu-kpi"><div class="value">${summary.volumes?.sent ?? "—"}</div><div class="label">Letters sent today</div></div>
    <div class="cdu-kpi"><div class="value">${summary.volumes?.affirmed ?? "—"}</div><div class="label">Affirmed today</div></div>
    <div class="cdu-kpi"><div class="value">${((summary.affirmRate ?? 0) * 100).toFixed(1)} %</div><div class="label">Affirm rate (of sent)</div></div>
    <div class="cdu-kpi"><div class="value">${((summary.errorRate ?? 0) * 100).toFixed(1)} %</div><div class="label">Error rate</div></div>
    <div class="cdu-kpi"><div class="value">${summary.medianMinutesNewToAffirmed ?? "—"} min</div><div class="label">Median new → affirmed <a href="#/timeline?trade=TR-FXO-001">ⓘ</a></div></div>`;

  const affirmSeries = (aging?.series || []).find((s) => s.status === "AffirmPending");
  const agingHtml = (affirmSeries?.buckets || [])
    .map(
      (b) => `<div class="cdu-aging-row"><button type="button" data-aging="${escapeHtml(b.label)}">${escapeHtml(b.label)}</button><div class="cdu-aging-bar" style="width:${Math.max(4, (b.count || 0) * 24)}px"></div><span>${b.count ?? 0}</span></div>`,
    )
    .join("");

  const contagionRows = (contagion?.items || [])
    .map(
      (p) => `<tr data-party="${escapeHtml(p.partyBName)}">
      <td>${escapeHtml(p.partyBName)}</td>
      <td>${p.trades ?? "—"}</td>
      <td>${p.open ?? "—"}</td>
      <td>${p.unmatched ?? 0}</td>
      <td>${p.errors ?? 0}</td>
      <td>${p.flagged ? "⚑" : "—"}</td>
    </tr>`,
    )
    .join("");

  root.innerHTML = `
    <div class="cdu-page-header">
      <h1>MIS · Deliverable FX Option</h1>
      <div class="meta">${escapeHtml(formatTimeShort(summary.window?.from))} → ${escapeHtml(formatTimeShort(summary.window?.to))}</div>
      <p><span class="cdu-chip cdu-chip--coming-soon">◌ Export</span> Product FXO · Window Today</p>
    </div>
    <div class="cdu-kpi-grid">${kpis}</div>
    <p><strong>Now in status</strong> ${escapeHtml(queueParts)}</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <section>
        <h2>Aging (from sent)</h2>
        ${agingHtml}
      </section>
      <section>
        <h2>Counterparty contagion · threshold ${contagion?.threshold ?? 3} open</h2>
        <table class="cdu-table"><thead><tr><th>Party B</th><th>Trades</th><th>Open</th><th>Unm.</th><th>Err</th><th>Flag</th></tr></thead>
        <tbody>${contagionRows}</tbody></table>
      </section>
    </div>
    <section style="margin-top:16px">
      <h2>Error queue</h2>
      ${
        errors?.items?.length
          ? `<ul>${errors.items.map((e) => `<li>${escapeHtml(e.message || JSON.stringify(e))}</li>`).join("")}</ul>`
          : `<div class="cdu-notice cdu-notice--success">✓ No errors in window</div>`
      }
    </section>
    <p class="meta">As of ${escapeHtml(summary.asOf || book.asOf)} · refreshed with the book</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px">
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Explain this number — AI assistant explains KPIs from the trade book.</div>
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Anomalies & prediction — no model in this prototype.</div>
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Alerts — subscribe to contagion / aging thresholds.</div>
    </div>
  `;

  root.querySelectorAll("[data-party]").forEach((tr) => {
    tr.addEventListener("click", () => {
      navigate("/trades", { party: tr.getAttribute("data-party") });
    });
  });
  root.querySelectorAll("[data-aging]").forEach((btn) => {
    btn.addEventListener("click", () => {
      navigate("/trades", { status: "AffirmPending" });
    });
  });
}
