import { api, getScenarioId, runScenarioScript } from "../api.js";
import { renderStatusChip, actionSentence, tradeStatusLabel } from "../labels.js";
import { escapeHtml, formatDateTimeUtc, formatTimeShort, navigate } from "../util.js";

export async function renderTimeline(root, params) {
  let tradeId = params.get("trade") || "TR-FXO-001";
  let book;
  try {
    book = (await api("GET", "/trades")).data;
  } catch {
    root.innerHTML = `<p>Could not load trades.</p>`;
    return;
  }

  const picker = (book.items || [])
    .map((r) => {
      const mark = r.timelineAvailable ? "◷ " : "";
      return `<option value="${escapeHtml(r.tradeId)}" ${r.tradeId === tradeId ? "selected" : ""}>${mark}${escapeHtml(r.tradeId)}</option>`;
    })
    .join("");

  const row = book.items.find((x) => x.tradeId === tradeId);
  if (!row) {
    root.innerHTML = `<p>Trade not found.</p>`;
    return;
  }

  let timeline = null;
  let detail = null;
  if (row.timelineAvailable) {
    try {
      timeline = (await api("GET", `/trades/${tradeId}/timeline`)).data;
      detail = (await api("GET", `/trades/${tradeId}`)).data;
    } catch {
      timeline = null;
    }
  }

  const scenario = getScenarioId();
  const demoBar =
    scenario === "B" && tradeId === "TR-FXO-001"
      ? `<div class="cdu-notice cdu-notice--info"><button type="button" class="cdu-btn cdu-btn--primary" id="run-b-journey">Run TR-FXO-001 journey (demo)</button> Replays POST/GET steps and TPs callbacks via mock API.</div>`
      : "";

  if (!row.timelineAvailable) {
    root.innerHTML = `
      <div class="cdu-page-header">
        <h1>Timeline / ${escapeHtml(tradeId)}</h1>
        <select id="timeline-trade">${picker}</select>
        <button type="button" class="cdu-btn cdu-btn--ghost" data-back-trades>‹ Back to trades</button>
      </div>
      <p>${renderStatusChip(row.status)} ${escapeHtml(row.partyBName)} · ${escapeHtml(formatNotional(row.callCurrency, row.callCurrencyAmount))}</p>
      <div class="cdu-coming-soon">
        <span class="cdu-chip cdu-chip--coming-soon">◌ Timeline</span>
        This trade has no simulated timeline. Simulated timelines: TR-FXO-001, TR-FXO-005.
        <p><a href="#/timeline?trade=TR-FXO-001">Open TR-FXO-001 timeline</a></p>
      </div>`;
    wireCommon(root, tradeId);
    return;
  }

  const events = timeline?.events || [];
  const swim = renderSwimlanes(events, timeline?.lanes || []);
  const tableRows = events
    .map(
      (ev, i) => `<tr data-ev="${i}" class="${i === events.length - 1 ? "selected" : ""}">
      <td>${escapeHtml(ev.timelineEventId)}</td>
      <td>${escapeHtml(formatDateTimeUtc(ev.at))}</td>
      <td>${escapeHtml(ev.lane)}</td>
      <td>${escapeHtml(actionSentence(ev.action))}</td>
      <td>${renderStatusChip(ev.status)}</td>
      <td>${ev.documentId ? escapeHtml(ev.documentId) : "—"}</td>
      <td>${ev.templateVersion || "—"}</td>
      <td>${escapeHtml(ev.auditId || "—")}</td>
    </tr>`,
    )
    .join("");

  const mca =
    detail?.documentation?.masterConfirmation?.masterConfirmationId ||
    row.mcaPath ||
    "—";

  root.innerHTML = `
    ${demoBar}
    <div class="cdu-page-header">
      <h1>Timeline / ${escapeHtml(tradeId)}</h1>
      <label>Trade <select id="timeline-trade">${picker}</select></label>
      <button type="button" class="cdu-btn cdu-btn--ghost" data-back-trades>‹ Back to trades</button>
    </div>
    <p>${renderStatusChip(row.status)} ${escapeHtml(row.partyBName)} · ${escapeHtml(row.optionType || "")}</p>
    <p class="meta">TB-FXO-DEL-2026-001 v${escapeHtml(row.templateVersion || detail?.template?.templateVersion || "—")} · ${escapeHtml(detail?.documentId || row.documentId || "—")} · ${escapeHtml(mca)}</p>
    <div class="cdu-timeline-lanes">${swim}</div>
    <div class="cdu-drawer-wrap">
      <table class="cdu-table" style="flex:1">
        <thead><tr><th>#</th><th>At (UTC)</th><th>Lane</th><th>Action</th><th>Status after</th><th>Doc</th><th>Version</th><th>Audit</th></tr></thead>
        <tbody>${tableRows}</tbody>
      </table>
      <aside class="cdu-drawer" id="ev-drawer"></aside>
    </div>
  `;

  wireCommon(root, tradeId);
  root.querySelector("#run-b-journey")?.addEventListener("click", async () => {
    await runScenarioScript("B");
    renderTimeline(root, new URLSearchParams(`trade=${tradeId}`));
  });

  const drawer = root.querySelector("#ev-drawer");
  const showEv = (ev) => {
    drawer.innerHTML = `
      <h3>${escapeHtml(ev.timelineEventId)}</h3>
      <p>${escapeHtml(actionSentence(ev.action))}</p>
      ${renderStatusChip(ev.status)}
      <dl class="cdu-kv">
        <dt>At</dt><dd>${escapeHtml(ev.at)}</dd>
        <dt>Actor</dt><dd>${escapeHtml(ev.actor)}</dd>
        <dt>Lane</dt><dd>${escapeHtml(ev.lane)}</dd>
        <dt>Audit</dt><dd>${escapeHtml(ev.auditId)}</dd>
      </dl>`;
  };
  if (events.length) showEv(events[events.length - 1]);
  root.querySelectorAll("tbody tr").forEach((tr) => {
    tr.addEventListener("click", () => {
      root.querySelectorAll("tbody tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
      showEv(events[parseInt(tr.getAttribute("data-ev"), 10)]);
    });
  });
}

function formatNotional(c, a) {
  const n = Number(a);
  return n >= 1e6 ? `${c} ${(n / 1e6).toFixed(1)}m` : `${c} ${a}`;
}

function renderSwimlanes(events, lanes) {
  if (!events.length) return "<p>No events yet at this clock.</p>";
  const byLane = {};
  for (const lane of lanes) byLane[lane] = [];
  for (const ev of events) {
    if (!byLane[ev.lane]) byLane[ev.lane] = [];
    byLane[ev.lane].push(ev);
  }
  return lanes
    .map((lane) => {
      const nodes = (byLane[lane] || [])
        .map((ev) => `<span title="${escapeHtml(formatTimeShort(ev.at))}">● ${escapeHtml(actionSentence(ev.action).slice(0, 12))}</span>`)
        .join(" ");
      return `<div><strong>${escapeHtml(lane)}</strong> ${nodes || "—"}</div>`;
    })
    .join("");
}

function wireCommon(root, tradeId) {
  root.querySelector("#timeline-trade")?.addEventListener("change", (e) => {
    navigate("/timeline", { trade: e.target.value });
  });
  root.querySelector("[data-back-trades]")?.addEventListener("click", () => navigate("/trades"));
}
