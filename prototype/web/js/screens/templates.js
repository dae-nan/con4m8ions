import { api } from "../api.js";
import { renderStatusChip, templateStatusChip, templateStatusLabel, APPROVAL_STATUS } from "../labels.js";
import { escapeHtml, formatDateTimeUtc, navigate } from "../util.js";

const PKG = "TB-FXO-DEL-2026-001";

export async function renderTemplates(root, params) {
  const pkgId = params.get("id") || "";
  if (!pkgId) {
    await renderTemplateList(root);
    return;
  }
  await renderTemplateDetail(root, pkgId, params.get("tab") || "overview");
}

async function renderTemplateList(root) {
  const index = (await api("GET", "/templates")).data;
  const item = index.items?.[0];
  root.innerHTML = `
    <div class="cdu-page-header"><h1>Templates</h1></div>
    <div class="cdu-filter-bar"><input placeholder="Search package" disabled /></div>
    <article class="cdu-package-card" data-open="${escapeHtml(item?.packageId || PKG)}">
      <h2 style="margin:0">${escapeHtml(item?.packageName || "2026 FXO Deliverable (II-B)")} ${renderStatusChip(item?.liveVersion ? "LIVE" : "LIVE", "template")}</h2>
      <p>${escapeHtml(item?.packageId || PKG)}</p>
      <p>Draft waiting: 1.2.0 · ${renderStatusChip("APPROVED", "approval")}</p>
      <p>→ Open</p>
    </article>`;
  root.querySelector("[data-open]")?.addEventListener("click", () => {
    navigate("/templates/" + PKG);
  });
}

async function renderTemplateDetail(root, pkgId, tab) {
  const pkg = (await api("GET", `/templates/${pkgId}`)).data;
  const draft = pkg.versions?.find((v) => v.version === "1.2.0");
  const canActivate = draft?.status === "DRAFT" && draft?.approvalStatus === "APPROVED";

  const versionRows = (pkg.versions || [])
    .map((v) => {
      const iib =
        v.version === "1.2.0" && v.productTemplateVersionId === "TV-IIB-2026-1.1.0"
          ? "II-B unchanged (1.1.0)"
          : v.productTemplateVersionId;
      return `<tr>
        <td>${escapeHtml(v.version)}</td>
        <td>${renderStatusChip(v.status, "template")} ${v.approvalStatus === "APPROVED" ? renderStatusChip("APPROVED", "approval") : ""}</td>
        <td>${escapeHtml(v.masterTemplateVersionId || "—")}</td>
        <td>${escapeHtml(iib || "—")}</td>
        <td>${v.activatedAt ? escapeHtml(formatDateTimeUtc(v.activatedAt)) : "—"}</td>
        <td>${v.retiredAt ? escapeHtml(formatDateTimeUtc(v.retiredAt)) : "—"}</td>
      </tr>`;
    })
    .join("");

  const tabs = ["overview", "versions", "bindings", "audit"];
  const tabButtons = tabs
    .map(
      (t) =>
        `<button type="button" class="${tab === t ? "active" : ""}" data-tab="${t}">${t.charAt(0).toUpperCase() + t.slice(1)}</button>`,
    )
    .join("");

  let panel = "";
  if (tab === "overview") {
    const onVersion = pkg.version;
    panel = `
      <p>Exhibit I + II-B · Defs ${escapeHtml(pkg.legalDefsYear)} · rollback target ${escapeHtml(pkg.rollbackTargetVersion)}</p>
      <p><a href="#/trades?templateVersion=${encodeURIComponent(onVersion)}">Trades on this version: view desk →</a></p>
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Template approval workflow (request / approve / reject).</div>`;
  } else if (tab === "versions") {
    panel = `
      <table class="cdu-table">
        <thead><tr><th>Version</th><th>Status</th><th>Exhibit I</th><th>II-B layer</th><th>Activated</th><th>Retired</th></tr></thead>
        <tbody>${versionRows}</tbody>
      </table>
      <div class="cdu-coming-soon" style="margin-top:16px">
        <h3>Version 1.2.0</h3>
        <p>Validation (● PASSED) · Approval ${renderStatusChip("APPROVED", "template")} u.ctrl.ng · AUD-0007</p>
        <p>Four-eyes approval mocked as given. Workflow UI is <span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span>.</p>
      </div>`;
  } else if (tab === "bindings") {
    const rules = (await api("GET", "/templates/selection-rules")).data;
    const rule = rules.items?.[0];
    panel = `
      <p>Selection rule ${escapeHtml(rule?.selectionRuleId || "PSR-FXO-DEL-2026-001")}</p>
      <p>Routing: Deliverable_FX_Option / NEW_TRADE → ${escapeHtml(pkgId)}</p>
      <div class="cdu-coming-soon"><span class="cdu-chip cdu-chip--coming-soon">◌ Coming soon</span> Full II-B field matrix (18 rows).</div>`;
  } else {
    let audit;
    try {
      audit = (await api("GET", `/templates/${pkgId}/audit`)).data;
    } catch {
      audit = { items: [] };
    }
    panel = `<table class="cdu-table"><thead><tr><th>At</th><th>Action</th><th>User</th><th>Audit</th></tr></thead><tbody>
      ${(audit.items || [])
        .slice(0, 8)
        .map(
          (a) => `<tr><td>${escapeHtml(formatDateTimeUtc(a.at))}</td><td>${escapeHtml(a.action || a.summary)}</td><td>${escapeHtml(a.actor || a.userId)}</td><td>${escapeHtml(a.auditId || "—")}</td></tr>`,
        )
        .join("")}
    </tbody></table>`;
  }

  root.innerHTML = `
    <div class="cdu-page-header">
      <p class="meta">Templates / ${escapeHtml(pkg.packageName)}</p>
      <h1>${escapeHtml(pkg.packageName)} ${renderStatusChip(pkg.status, "template")} ${escapeHtml(pkg.version)}</h1>
      <p>${escapeHtml(pkgId)} · Exhibit I + II-B · Defs ${escapeHtml(pkg.legalDefsYear)}</p>
      ${canActivate ? `<button type="button" class="cdu-btn cdu-btn--primary" id="btn-activate">Activate 1.2.0</button>` : ""}
    </div>
    <nav class="cdu-tabs">${tabButtons}</nav>
    ${panel}
    <div id="activate-modal"></div>
    <div id="toast"></div>
  `;

  root.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => navigate(`/templates/${pkgId}`, { tab: btn.getAttribute("data-tab") }));
  });

  root.querySelector("#btn-activate")?.addEventListener("click", () => {
    const host = root.querySelector("#activate-modal");
    host.innerHTML = `
      <div class="cdu-modal-backdrop" role="presentation">
        <div class="cdu-modal" role="dialog" aria-modal="true">
          <h2>Activate version 1.2.0?</h2>
          <p>1.1.0 becomes rollback target. Running assemblies stay pinned. Resend policy MANUAL — nothing is resent automatically.</p>
          <div class="cdu-modal__actions">
            <button type="button" class="cdu-btn cdu-btn--secondary" data-cancel>Cancel</button>
            <button type="button" class="cdu-btn cdu-btn--primary" data-confirm>Confirm</button>
          </div>
        </div>
      </div>`;
    host.querySelector("[data-cancel]").addEventListener("click", () => (host.innerHTML = ""));
    host.querySelector("[data-confirm]").addEventListener("click", async () => {
      await api("POST", `/templates/${pkgId}/activate`, {});
      host.innerHTML = "";
      root.querySelector("#toast").innerHTML = `<div class="cdu-notice cdu-notice--success">✓ Version 1.2.0 is LIVE. Clock advanced to activation.</div>`;
      await renderTemplateDetail(root, pkgId, tab);
    });
  });
}
