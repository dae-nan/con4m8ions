import { api } from "../api.js";
import { renderStatusChip, ASSEMBLY_MODE } from "../labels.js";
import { escapeHtml, formatTimeShort, navigate } from "../util.js";

const ASSEMBLY_ID = "AR-FXO-005-01";
const TRADE_ID = "TR-FXO-005";

let draftText = "";

export async function renderManualDraft(root, params) {
  const tradeId = params.get("trade") || TRADE_ID;
  let assembly;
  let shell;
  try {
    assembly = (await api("GET", `/assemblies/${ASSEMBLY_ID}`)).data;
    shell = (await api("GET", `/assemblies/${ASSEMBLY_ID}/shell`)).data;
  } catch (e) {
    root.innerHTML = `<p>Could not load manual draft (try scenario C). ${escapeHtml(e.message)}</p>`;
    return;
  }

  draftText = draftText || shell.exhibitILetter?.blocks?.elections?.calculationAgent || "Party A";

  root.innerHTML = `
    <div class="cdu-page-header">
      <p class="meta">Trades / ${escapeHtml(tradeId)} / Manual draft</p>
      <h1>${escapeHtml(tradeId)} · ${escapeHtml(shell.exhibitILetter?.blocks?.heading?.partyBName || "Globex Holdings Ltd")}</h1>
      <p>${renderStatusChip("ManualDraft")} ${escapeHtml(ASSEMBLY_MODE[assembly.mode] || assembly.mode)} · TB-FXO-DEL-2026-001 v${escapeHtml(assembly.templateVersion || "1.1.0")} (pinned)</p>
      <button type="button" class="cdu-btn cdu-btn--ghost" data-view-tl>View timeline</button>
    </div>
    <div class="cdu-notice cdu-notice--info">Reason from TPs: ${escapeHtml(assembly.manualDraftReason || assembly.reason || "Counterparty requested bespoke Calculation Agent wording")}</div>
    <div class="cdu-split">
      <div>
        <div class="cdu-letter">
          <p class="block-locked">▸ Heading · Standard Chartered Bank Sample Desk · 🔒</p>
          <p class="block-locked">▸ Definitions · 2026 FX Definitions · 🔒</p>
          <p class="block-locked">▸ Agreement clause · 🔒</p>
          <p class="block-locked">▸ productInsert · Exhibit II-B from trade · 🔒</p>
          <div class="block-editable">
            <p>✎ Elections · Calculation Agent</p>
            <textarea id="clause-edit" aria-label="Calculation Agent clause">${escapeHtml(draftText)}</textarea>
          </div>
          <p class="block-locked">▸ Closing · 🔒</p>
        </div>
        <div class="cdu-sticky-footer">
          <button type="button" class="cdu-btn cdu-btn--ghost" data-cancel>Cancel</button>
          <button type="button" class="cdu-btn cdu-btn--secondary" id="save-draft">Save draft</button>
          <button type="button" class="cdu-btn cdu-btn--primary" id="submit-draft">Submit to SmartDX</button>
        </div>
      </div>
      <aside>
        <h3>Trade facts</h3>
        <dl class="cdu-kv">
          <dt>Option</dt><dd>${escapeHtml(assembly.trade?.economics?.optionType || "EUR Call / USD Put")}</dd>
          <dt>Call</dt><dd>${escapeHtml(assembly.trade?.economics?.callCurrency || "EUR")} ${escapeHtml(assembly.trade?.economics?.callCurrencyAmount || "2500000")}</dd>
          <dt>Strike</dt><dd>${escapeHtml(assembly.trade?.economics?.strikePrice || "1.0900")}</dd>
        </dl>
        <h3>Draft</h3>
        <dl class="cdu-kv" id="draft-meta">
          <dt>Loaded</dt><dd>${escapeHtml(formatTimeShort(assembly.loadedAt || "2027-12-01T16:40:00Z"))}</dd>
        </dl>
      </aside>
    </div>
    <div id="manual-modals"></div>
  `;

  root.querySelector("[data-view-tl]")?.addEventListener("click", () => {
    navigate("/timeline", { trade: TRADE_ID });
  });
  root.querySelector("[data-cancel]")?.addEventListener("click", () => navigate("/trades", { trade: TRADE_ID }));

  root.querySelector("#save-draft")?.addEventListener("click", async () => {
    draftText = root.querySelector("#clause-edit").value;
    const res = await api("PUT", `/assemblies/${ASSEMBLY_ID}/manual-draft`, {});
    const meta = root.querySelector("#draft-meta");
    meta.innerHTML += `<dt>Saved</dt><dd>${escapeHtml(formatTimeShort(res.data.savedAt))} · ${escapeHtml(res.data.manualDraftId || "MDC-005-01")}</dd>`;
  });

  root.querySelector("#submit-draft")?.addEventListener("click", () => {
    draftText = root.querySelector("#clause-edit").value;
    const before = shell.exhibitILetter?.blocks?.elections?.calculationAgent || "Party A";
    const after = draftText.slice(0, 60);
    const host = root.querySelector("#manual-modals");
    host.innerHTML = `
      <div class="cdu-modal-backdrop">
        <div class="cdu-modal" role="dialog">
          <h2>Submit ${escapeHtml(tradeId)} to SmartDX?</h2>
          <p>Template TB-FXO-DEL-2026-001 v1.1.0 · 1 block edited · Channel SmartDX</p>
          <p><strong>Before:</strong> ${escapeHtml(before)}…</p>
          <p><strong>After:</strong> ${escapeHtml(after)}…</p>
          <div class="cdu-modal__actions">
            <button type="button" class="cdu-btn cdu-btn--secondary" data-cancel>Cancel</button>
            <button type="button" class="cdu-btn cdu-btn--primary" data-confirm>Submit</button>
          </div>
        </div>
      </div>`;
    host.querySelector("[data-cancel]").addEventListener("click", () => (host.innerHTML = ""));
    host.querySelector("[data-confirm]").addEventListener("click", async () => {
      await api("POST", `/assemblies/${ASSEMBLY_ID}/submit`, {});
      host.innerHTML = "";
      const notice = document.createElement("div");
      notice.className = "cdu-notice cdu-notice--success";
      notice.textContent = "Submitted. DOC-105 sent to SmartDX; TPs notified.";
      root.prepend(notice);
      setTimeout(() => navigate("/trades", { trade: TRADE_ID }), 1200);
    });
  });
}
