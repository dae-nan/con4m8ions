import { api } from "../api.js";
import {
  renderStatusChip,
  MCA_PATH,
  ASSEMBLY_MODE,
  actionSentence,
  tradeStatusChip,
  tradeStatusLabel,
} from "../labels.js";
import {
  escapeHtml,
  formatNotional,
  formatTimeShort,
  navigate,
} from "../util.js";

const STATUS_ORDER = [
  "Received",
  "Validating",
  "Composing",
  "ManualDraft",
  "Sent",
  "AffirmPending",
  "Affirmed",
];

function inStatusLabel(row, bookAsOf) {
  const t = row.receivedAt || row.sentAt;
  if (!t || !bookAsOf) return "—";
  const ms = new Date(bookAsOf) - new Date(t);
  const h = Math.floor(ms / 3600000);
  if (h < 1) return "<1h";
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export async function renderTrades(root, params) {
  const filterStatus = params.get("status") || "";
  const filterParty = params.get("party") || "";
  const filterTpl = params.get("templateVersion") || "";
  const selected = params.get("trade") || "";
  const search = params.get("q") || "";

  let book;
  try {
    book = (await api("GET", "/trades")).data;
  } catch {
    root.innerHTML = `<p class="cdu-coming-soon">Could not load trade book.</p>`;
    return;
  }

  const counts = book.counts || {};
  const asOf = book.asOf;

  const chips = [];
  if (filterStatus) chips.push({ k: "status", v: filterStatus, label: tradeStatusLabel(filterStatus) });
  if (filterParty) chips.push({ k: "party", v: filterParty, label: filterParty });
  if (filterTpl) chips.push({ k: "templateVersion", v: filterTpl, label: `Pkg ${filterTpl}` });

  let items = [...(book.items || [])];
  if (filterStatus) items = items.filter((r) => r.status === filterStatus);
  if (filterParty) items = items.filter((r) => r.partyBName === filterParty);
  if (filterTpl) items = items.filter((r) => r.templateVersion === filterTpl);
  if (search) {
    const q = search.toLowerCase();
    items = items.filter(
      (r) =>
        r.tradeId.toLowerCase().includes(q) ||
        (r.partyBName || "").toLowerCase().includes(q) ||
        (r.documentId || "").toLowerCase().includes(q),
    );
  }

  const strip = STATUS_ORDER.map(
    (st) => `
    <button type="button" data-filter-status="${st}" class="${filterStatus === st ? "active" : ""}">
      <span class="label">${escapeHtml(tradeStatusLabel(st))}</span>
      <span class="count">${counts[st] ?? 0}</span>
    </button>`,
  ).join("");

  const rows = items
    .map((r) => {
      const tl = r.timelineAvailable
        ? `<span title="Timeline available" aria-label="Timeline available">◷</span>`
        : "";
      return `<tr class="${selected === r.tradeId ? "selected" : ""}" data-trade="${escapeHtml(r.tradeId)}">
        <td><a href="#/trades?trade=${encodeURIComponent(r.tradeId)}">${escapeHtml(r.tradeId)}</a></td>
        <td>${escapeHtml(r.partyBName)}</td>
        <td>${escapeHtml(MCA_PATH[r.mcaPath] || r.mcaPath || "—")}</td>
        <td>${escapeHtml(r.optionType || "—")}</td>
        <td>${escapeHtml(formatNotional(r.callCurrency, r.callCurrencyAmount))}</td>
        <td class="col-status">${renderStatusChip(r.status)}</td>
        <td>${r.documentId ? `<a href="#">${escapeHtml(r.documentId)}</a>` : "—"}</td>
        <td>${inStatusLabel(r, asOf)}</td>
        <td>${tl}</td>
      </tr>`;
    })
    .join("");

  const cards = items
    .map(
      (r) => `
    <div class="cdu-package-card" data-trade="${escapeHtml(r.tradeId)}">
      <strong>${escapeHtml(r.tradeId)}</strong> ${renderStatusChip(r.status)}
      <div>${escapeHtml(r.partyBName)} · ${escapeHtml(formatNotional(r.callCurrency, r.callCurrencyAmount))}</div>
      <div>${r.documentId ? escapeHtml(r.documentId) : "—"} · ${escapeHtml(formatTimeShort(r.affirmedAt || r.receivedAt))}</div>
      ${r.timelineAvailable ? `<div aria-label="Timeline available">◷ Timeline</div>` : ""}
    </div>`,
    )
    .join("");

  root.innerHTML = `
    <div class="cdu-page-header">
      <h1>Trades · Deliverable FX Options</h1>
      <div class="meta">as of ${escapeHtml(formatTimeShort(asOf))}</div>
    </div>
    <div class="cdu-queue-strip" role="group" aria-label="Queue by status">${strip}
      <button type="button" class="cdu-btn--ghost" data-nav-mis>View MIS →</button>
    </div>
    ${
      chips.length
        ? `<div class="cdu-filter-chips">${chips
            .map(
              (c) =>
                `<button type="button" data-clear-filter="${escapeHtml(c.k)}">${escapeHtml(c.label)} ✕</button>`,
            )
            .join("")}</div>`
        : ""
    }
    <div class="cdu-filter-bar">
      <input type="search" placeholder="Search trade, doc, counterparty" value="${escapeHtml(search)}" id="trade-search" />
      <select id="filter-status"><option value="">Status: All</option>${STATUS_ORDER.map((s) => `<option value="${s}" ${filterStatus === s ? "selected" : ""}>${tradeStatusLabel(s)}</option>`).join("")}</select>
    </div>
    <div class="cdu-drawer-wrap">
      <div style="flex:1;min-width:0">
        <table class="cdu-table cdu-table-desktop">
          <thead><tr>
            <th>Trade ID</th><th>Counterparty</th><th>MCA</th><th>Option</th><th>Notional</th>
            <th class="col-status">Status</th><th>Doc</th><th>In status</th><th scope="col"><abbr title="Simulated timeline available">Timeline</abbr></th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
        <div class="cdu-trade-cards">${cards}</div>
        <p style="font-size:0.875rem;color:var(--cdu-text-secondary)">1–${items.length} of ${book.count}</p>
      </div>
      <aside class="cdu-drawer" id="trade-drawer" hidden></aside>
    </div>
  `;

  root.querySelector("[data-nav-mis]")?.addEventListener("click", () => navigate("/mis"));
  root.querySelectorAll("[data-filter-status]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const st = btn.getAttribute("data-filter-status");
      navigate("/trades", { status: st, trade: selected });
    });
  });
  root.querySelectorAll("[data-clear-filter]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const k = btn.getAttribute("data-clear-filter");
      const p = { trade: selected };
      if (k !== "status") p.status = filterStatus;
      if (k !== "party") p.party = filterParty;
      if (k !== "templateVersion") p.templateVersion = filterTpl;
      navigate("/trades", p);
    });
  });
  root.querySelector("#filter-status")?.addEventListener("change", (e) => {
    navigate("/trades", { status: e.target.value, trade: selected, party: filterParty, templateVersion: filterTpl });
  });
  root.querySelector("#trade-search")?.addEventListener("change", (e) => {
    navigate("/trades", { q: e.target.value, trade: selected, status: filterStatus });
  });

  const openTrade = async (tradeId) => {
    navigate("/trades", {
      trade: tradeId,
      status: filterStatus,
      party: filterParty,
      templateVersion: filterTpl,
      q: search,
    });
    const drawer = root.querySelector("#trade-drawer");
    drawer.hidden = false;
    drawer.innerHTML = "<p>Loading…</p>";
    const row = book.items.find((x) => x.tradeId === tradeId);
    let detail = null;
    let doc = null;
    let timeline = null;
    try {
      detail = (await api("GET", `/trades/${tradeId}`)).data;
    } catch {
      detail = null;
    }
    if (detail?.documentId) {
      try {
        doc = (await api("GET", `/documents/${detail.documentId}`)).data;
      } catch {
        /* no doc file */
      }
    }
    if (row?.timelineAvailable) {
      try {
        timeline = (await api("GET", `/trades/${tradeId}/timeline`)).data;
      } catch {
        /* */
      }
    }
    drawer.innerHTML = await buildDrawer(tradeId, row, detail, doc, timeline);
    wireDrawer(drawer, tradeId, row);
  };

  root.querySelectorAll("[data-trade]").forEach((el) => {
    el.addEventListener("click", () => openTrade(el.getAttribute("data-trade")));
  });

  if (selected) openTrade(selected);
}

async function buildDrawer(tradeId, row, detail, doc, timeline) {
  const status = detail?.status || row?.status;
  const chip = renderStatusChip(status);
  const isManual = status === "ManualDraft";
  const hasTimeline = row?.timelineAvailable;

  let body = "";
  if (detail) {
    const tpl = detail.template || {};
    const mca =
      detail.documentation?.masterConfirmation?.masterConfirmationId ||
      "None (long-form ISDA 2002)";
    body = `
      <dl class="cdu-kv">
        <dt>Package</dt><dd><a href="#/templates/TB-FXO-DEL-2026-001">${escapeHtml(tpl.templateBundleId || "—")} v${escapeHtml(tpl.templateVersion || row?.templateVersion || "—")}</a></dd>
        <dt>Assembly</dt><dd>${escapeHtml(detail.assemblyRunId || row?.assemblyRunId || "—")} · ${escapeHtml(ASSEMBLY_MODE[detail.assemblyMode || row?.assemblyMode] || "—")}</dd>
        <dt>Document</dt><dd>${doc ? `${escapeHtml(doc.documentId)} · SmartDX ${escapeHtml(doc.smartdxDocumentId || "")}` : "—"}</dd>
        <dt>MCA</dt><dd>${escapeHtml(mca)}</dd>
        <dt>Economics</dt><dd>Strike ${escapeHtml(detail.economics?.strikePrice || row?.strikePrice || "—")} · Premium ${escapeHtml(detail.economics?.premiumAmount || "—")}</dd>
      </dl>`;
  } else if (row) {
    body = `
      <dl class="cdu-kv">
        <dt>Counterparty</dt><dd>${escapeHtml(row.partyBName)}</dd>
        <dt>MCA path</dt><dd>${escapeHtml(MCA_PATH[row.mcaPath] || row.mcaPath)}</dd>
        <dt>Template</dt><dd>${escapeHtml(row.templateVersion || "—")}</dd>
      </dl>
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Full trade detail from book fields only.</div>`;
  }

  let journey = "";
  if (hasTimeline && timeline?.events?.length) {
    const sent = timeline.events.find((e) => e.action === "document.sent");
    const aff = timeline.events.find((e) => e.action === "affirm.affirmed");
    journey = `
      <div class="cdu-journey-rail" aria-label="Journey milestones">
        <span class="dot"></span> Received
        →
        <span class="dot"></span> Sent ${sent ? formatTimeShort(sent.at) : ""}
        →
        <span class="dot"></span> Affirmed ${aff ? formatTimeShort(aff.at) : ""}
      </div>`;
  } else if (!hasTimeline) {
    journey = `<div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Timeline</span> No simulated timeline for this trade.</div>`;
  }

  const primaryBtn = isManual
    ? `<button type="button" class="cdu-btn cdu-btn--primary" data-open-draft>Open draft</button>`
    : hasTimeline
      ? `<button type="button" class="cdu-btn cdu-btn--primary" data-open-timeline>Open timeline</button>`
      : "";

  return `
    <div style="display:flex;justify-content:space-between;align-items:start">
      <h2 style="margin:0;font-size:1rem">${escapeHtml(tradeId)}</h2>
      <button type="button" class="cdu-btn--ghost" data-close-drawer aria-label="Close">✕</button>
    </div>
    <p>${escapeHtml(row?.partyBName || detail?.parties?.find((p) => p.id === "partyB")?.partyName || "")}</p>
    <p>${chip}</p>
    ${body}
    ${journey}
    <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
      ${doc ? `<button type="button" class="cdu-btn cdu-btn--secondary" data-view-letter>View letter</button>` : hasTimeline ? "" : `<span class="cdu-chip cdu-chip--coming-soon">◌ View letter</span>`}
      ${primaryBtn}
    </div>
  `;
}

function wireDrawer(drawer, tradeId, row) {
  drawer.querySelector("[data-close-drawer]")?.addEventListener("click", () => {
    drawer.hidden = true;
    navigate("/trades");
  });
  drawer.querySelector("[data-open-timeline]")?.addEventListener("click", () => {
    navigate("/timeline", { trade: tradeId });
  });
  drawer.querySelector("[data-open-draft]")?.addEventListener("click", () => {
    navigate("/manual-draft", { trade: tradeId });
  });
  drawer.querySelector("[data-view-letter]")?.addEventListener("click", async () => {
    const detail = (await api("GET", `/trades/${tradeId}`)).data;
    const doc = (await api("GET", `/documents/${detail.documentId}`)).data;
    const blocks = doc.exhibitILetter?.blocks;
    const text = blocks
      ? JSON.stringify(blocks, null, 2)
      : doc.renderedHtml || doc.bodyText || "Letter content";
    showLetterModal(doc.documentId, text);
  });
}

function showLetterModal(docId, text) {
  const backdrop = document.createElement("div");
  backdrop.className = "cdu-modal-backdrop";
  backdrop.innerHTML = `
    <div class="cdu-modal" role="dialog" aria-modal="true">
      <h2>Letter ${escapeHtml(docId)}</h2>
      <div class="cdu-letter"><pre style="white-space:pre-wrap;font-family:var(--cdu-font-mono);font-size:0.75rem">${escapeHtml(text)}</pre></div>
      <div class="cdu-modal__actions"><button type="button" class="cdu-btn cdu-btn--primary" data-close>Close</button></div>
    </div>`;
  backdrop.querySelector("[data-close]").addEventListener("click", () => backdrop.remove());
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) backdrop.remove();
  });
  document.body.appendChild(backdrop);
}

export { showLetterModal };
