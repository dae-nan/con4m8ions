import { initApi, onClockChange, getManifest, getClock, getScenarioId, setScenario } from "./api.js";
import { parseHash, navigate, formatTimeShort } from "./util.js";
import { renderTrades } from "./screens/trades.js";
import { renderTimeline } from "./screens/timeline.js";
import { renderMis } from "./screens/mis.js";
import { renderTemplates } from "./screens/templates.js";
import { renderManualDraft } from "./screens/manual-draft.js";

const app = document.getElementById("app");

async function loadShellCounts() {
  let trades = 6;
  let draftBadge = 1;
  try {
    trades = (await (await fetch("./data/outbound/api-responses/book/get-trades.200.json")).json()).count;
  } catch {
    /* */
  }
  return { trades, draftBadge };
}

function renderShellFrame(counts) {
  const manifest = getManifest();
  const scenarios = manifest?.scenarios || [];
  const sid = getScenarioId();
  const clock = getClock();

  const scenarioOptions = scenarios
    .map((s) => `<option value="${s.id}" ${s.id === sid ? "selected" : ""}>${s.label}</option>`)
    .join("");

  const { path } = parseHash();
  const navClass = (p) => (path.startsWith(p) ? "active" : "");

  app.innerHTML = `
    <div class="cdu-shell">
      <header class="cdu-shell__header">
        <span class="cdu-shell__brand">▣ CDU-PS Confirmations</span>
        <div class="cdu-shell__search"><input type="search" id="global-search" placeholder="Search trade, doc…" aria-label="Global search" /></div>
        <div class="cdu-shell__sim" aria-live="polite" id="sim-banner">
          SIMULATION ·
          <select id="scenario-picker" class="cdu-shell__scenario" aria-label="Scenario">${scenarioOptions}</select>
          · as of ${formatTimeShort(clock)}
        </div>
        <div class="cdu-shell__actions">
          <button type="button" class="cdu-btn cdu-btn--ghost" id="theme-toggle" aria-label="Toggle dark mode">◐</button>
          <span>(UT)</span>
        </div>
      </header>
      <div class="cdu-shell__body">
        <nav class="cdu-shell__nav" aria-label="Main">
          <a href="#/trades" class="${navClass("/trades")}">Trades <span class="badge">${counts.trades}</span></a>
          <a href="#/timeline" class="${navClass("/timeline")}">Timeline</a>
          <a href="#/mis" class="${navClass("/mis")}">MIS</a>
          <a href="#/templates" class="${navClass("/templates")}">Templates <span class="badge">${counts.draftBadge}</span></a>
          <a href="#" onclick="return false">? Help</a>
        </nav>
        <main class="cdu-shell__main" id="main-content" tabindex="-1"></main>
      </div>
      <nav class="cdu-shell__tabbar" aria-label="Mobile navigation">
        <a href="#/trades" class="${navClass("/trades")}">Trades<span class="badge">${counts.trades}</span></a>
        <a href="#/timeline" class="${navClass("/timeline")}">Timeline</a>
        <a href="#/mis" class="${navClass("/mis")}">MIS</a>
        <a href="#/templates" class="${navClass("/templates")}">Tmpl<span class="badge">${counts.draftBadge}</span></a>
      </nav>
    </div>`;

  document.getElementById("scenario-picker")?.addEventListener("change", (e) => {
    setScenario(e.target.value);
    route();
  });
  document.getElementById("theme-toggle")?.addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem("cdu-theme", next);
  });
  document.getElementById("global-search")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") navigate("/trades", { q: e.target.value, trade: "TR-FXO-001" });
  });
}

async function route() {
  const { path, params } = parseHash();
  const main = document.getElementById("main-content");
  if (!main) return;

  const simBanner = document.getElementById("sim-banner");
  if (simBanner) {
    simBanner.innerHTML = `SIMULATION ·
      <select id="scenario-picker" class="cdu-shell__scenario" aria-label="Scenario">${(getManifest()?.scenarios || [])
        .map((s) => `<option value="${s.id}" ${s.id === getScenarioId() ? "selected" : ""}>${s.label}</option>`)
        .join("")}</select>
      · as of ${formatTimeShort(getClock())}`;
    document.getElementById("scenario-picker")?.addEventListener("change", (e) => {
      setScenario(e.target.value);
      route();
    });
  }

  if (path === "/trades" || path === "/") {
    await renderTrades(main, params);
  } else if (path === "/timeline") {
    await renderTimeline(main, params);
  } else if (path === "/mis") {
    await renderMis(main);
  } else if (path.startsWith("/templates")) {
    const parts = path.split("/").filter(Boolean);
    if (parts[1]) params.set("id", parts[1]);
    await renderTemplates(main, params);
  } else if (path === "/manual-draft") {
    await renderManualDraft(main, params);
  } else {
    main.innerHTML = `<p>Unknown route ${path}</p>`;
  }
}

async function boot() {
  const savedTheme = localStorage.getItem("cdu-theme");
  if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
  await initApi();
  const urlScenario = new URLSearchParams(window.location.search).get("scenario");
  if (urlScenario) setScenario(urlScenario);
  const counts = await loadShellCounts();
  renderShellFrame(counts);
  onClockChange(() => {
    route();
  });
  window.addEventListener("hashchange", () => route());
  await route();
}

boot();
