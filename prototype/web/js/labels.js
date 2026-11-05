/** Display-label map (components §3). API keeps codes; UI uses these labels. */
export const TRADE_STATUS = {
  Received: { label: "Received", tone: "neutral", chip: "cdu-chip--received" },
  Validating: { label: "Validating", tone: "info", chip: "cdu-chip--validating" },
  Composing: { label: "Composing", tone: "info", chip: "cdu-chip--composing" },
  ManualDraft: { label: "Manual draft", tone: "attention", chip: "cdu-chip--manual-draft" },
  Sent: { label: "Sent", tone: "progress", chip: "cdu-chip--sent" },
  AffirmPending: { label: "Affirm pending", tone: "progress", chip: "cdu-chip--affirm-pending" },
  Affirmed: { label: "Affirmed", tone: "success", chip: "cdu-chip--affirmed" },
};

export const TEMPLATE_STATUS = {
  DRAFT: { label: "DRAFT", tone: "neutral", chip: "cdu-chip--draft" },
  LIVE: { label: "LIVE", tone: "success", chip: "cdu-chip--live" },
  RETIRED: { label: "RETIRED", tone: "neutral", chip: "cdu-chip--retired" },
};

export const APPROVAL_STATUS = {
  APPROVED: { label: "APPROVED", tone: "success", chip: "cdu-chip--approved" },
  PENDING: { label: "Pending approval", tone: "attention", chip: "cdu-chip--pending-approval" },
};

export const ASSEMBLY_STATUS = {
  ASSEMBLING: { label: "Assembling", tone: "info", chip: "cdu-chip--assembling" },
  PENDING_MANUAL_DRAFT: { label: "Pending manual draft", tone: "attention", chip: "cdu-chip--pending-manual-draft" },
  COMPLETED: { label: "Completed", tone: "success", chip: "cdu-chip--completed" },
};

export const MCA_PATH = {
  With_MCA: "With MCA",
  Without_MCA: "Without MCA",
};

export const ASSEMBLY_MODE = {
  AUTOMATED: "Automated",
  MANUAL_DRAFTING: "Manual drafting",
};

export const ACTION_SENTENCE = {
  "trade.received": "Trade received",
  "trade.dq_passed": "DQ passed",
  "legal.resolved": "Legal resolved",
  "package.located": "Package located",
  "assembly.completed": "Assembly completed",
  "assembly.manual_started": "Manual draft started",
  "assembly.manual_saved": "Manual draft saved",
  "assembly.manual_submitted": "Manual draft submitted",
  "document.sent": "Document sent",
  "document.created": "Document created in SmartDX",
  "callback.sent": "Callback sent to TPs",
  "affirm.affirmed": "Counterparty affirmed",
  "template.approved": "Template approved",
  "template.activated": "Template activated",
  "template.validated": "Template validated",
  "template.version_added": "Template version added",
  "template.created": "Template created",
};

export function tradeStatusLabel(code) {
  return TRADE_STATUS[code]?.label ?? code;
}

export function tradeStatusChip(code) {
  return TRADE_STATUS[code]?.chip ?? "cdu-chip--received";
}

export function templateStatusLabel(code) {
  return TEMPLATE_STATUS[code]?.label ?? code;
}

export function templateStatusChip(code) {
  return TEMPLATE_STATUS[code]?.chip ?? "cdu-chip--draft";
}

export function actionSentence(code) {
  return ACTION_SENTENCE[code] ?? code.replace(/\./g, " ");
}

export function renderStatusChip(code, kind = "trade") {
  const map = kind === "template" ? TEMPLATE_STATUS : kind === "approval" ? APPROVAL_STATUS : TRADE_STATUS;
  const row = map[code];
  if (!row) return `<span class="cdu-chip">${escapeHtml(code)}</span>`;
  const hollow = code === "DRAFT" || code === "RETIRED" || code === "Received";
  const dot = hollow ? "○" : "●";
  return `<span class="cdu-chip ${row.chip}"><span aria-hidden="true">${dot}</span> ${row.label}</span>`;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;");
}
