/**
 * In-browser mock API (architecture §5). Loads routes.json + prototype/data.
 */
const listeners = new Set();

let manifest = null;
let clock = null;
let scenarioId = "D";

function normalizeUrl(url) {
  let u = (url || "").split("?")[0];
  if (!u.startsWith("/")) u = `/${u}`;
  return u;
}

function isResponseContract(contract) {
  return contract && contract.startsWith("response");
}

function compareIso(a, b) {
  return a.localeCompare(b);
}

export async function initApi() {
  const res = await fetch("routes.json");
  if (!res.ok) throw new Error("Failed to load routes.json");
  manifest = await res.json();
  setScenario(manifest.defaultScenario || "D");
  return manifest;
}

export function onClockChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function notify() {
  for (const fn of listeners) fn({ clock, scenarioId });
}

export function getManifest() {
  return manifest;
}

export function getClock() {
  return clock;
}

export function getScenarioId() {
  return scenarioId;
}

export function setScenario(id) {
  if (!manifest) return;
  const s = manifest.scenarios.find((x) => x.id === id);
  if (!s) return;
  scenarioId = id;
  clock = s.clock;
  notify();
}

export function setClock(iso) {
  clock = iso;
  notify();
}

function findGetRoute(method, url) {
  const norm = normalizeUrl(url);
  const candidates = manifest.items.filter(
    (it) =>
      it.method === method &&
      normalizeUrl(it.url) === norm &&
      isResponseContract(it.contract) &&
      compareIso(it.at, clock) <= 0,
  );
  if (!candidates.length) return null;
  candidates.sort((a, b) => compareIso(a.at, b.at));
  return candidates[candidates.length - 1];
}

function findWriteRoute(method, url) {
  const norm = normalizeUrl(url);
  const matches = manifest.items.filter(
    (it) =>
      it.method === method &&
      normalizeUrl(it.url) === norm &&
      isResponseContract(it.contract),
  );
  if (!matches.length) return null;
  matches.sort((a, b) => compareIso(a.at, b.at));
  return matches[matches.length - 1];
}

async function loadData(file) {
  const res = await fetch(`data/${file}`);
  if (!res.ok) throw new Error(`Missing data file: ${file}`);
  return res.json();
}

function applyListFilter(data, listFilter) {
  if (!listFilter || !data) return data;
  const arr = data[listFilter];
  if (!Array.isArray(arr)) return data;
  const filtered = arr.filter((el) => el.at && compareIso(el.at, clock) <= 0);
  const out = { ...data, [listFilter]: filtered };
  if (typeof out.count === "number") out.count = filtered.length;
  const latest = filtered.reduce((m, el) => (el.at > m ? el.at : m), "");
  if (latest) out.asOf = latest;
  return out;
}

function statusFromContract(contract) {
  const m = contract && contract.match(/response-(\d+)/);
  return m ? parseInt(m[1], 10) : 200;
}

export async function api(method, url, _body) {
  if (!manifest) await initApi();
  method = method.toUpperCase();
  const base = manifest.basePath || "/v1";
  let path = normalizeUrl(url);
  if (path.startsWith(base)) path = path.slice(base.length) || "/";

  if (method === "GET") {
    const route = findGetRoute(method, path);
    if (!route) {
      const err = { code: "NOT_FOUND", message: `No recorded response for GET ${path}` };
      throw Object.assign(new Error(err.message), { status: 404, body: err });
    }
    let data = await loadData(route.file);
    data = applyListFilter(data, route.listFilter);
    return { ok: true, status: 200, data, route: route.step };
  }

  const route = findWriteRoute(method, path);
  if (!route) {
    const err = { code: "NOT_FOUND", message: `No recorded response for ${method} ${path}` };
    throw Object.assign(new Error(err.message), { status: 404, body: err });
  }
  clock = route.at;
  notify();
  const data = await loadData(route.file);
  return { ok: true, status: statusFromContract(route.contract), data, route: route.step };
}

export async function runScenarioScript(scenario) {
  const steps = [...manifest.items]
    .filter((it) => it.scenario === scenario)
    .sort((a, b) => a.step.localeCompare(b.step, undefined, { numeric: true }));
  const results = [];
  for (const step of steps) {
    if (!isResponseContract(step.contract)) continue;
    if (step.method === "GET") {
      setClock(step.at);
    }
    const r = await api(step.method, step.url);
    results.push({ step: step.step, ...r });
  }
  return results;
}

export function apiPath(path) {
  const base = manifest?.basePath || "/v1";
  return `${base}${normalizeUrl(path)}`;
}
