/* panel.js — Wiki OpenWebUI Assistant extension panel logic */

const BASE    = "http://127.0.0.1:8080";
const KB_NAME = "my_wiki_knowledge";
const frame   = document.getElementById("webui-frame");
const overlay = document.getElementById("overlay");

// ── Status polling ──────────────────────────────────────────────────────────
async function ping() {
  try {
    const r = await fetch(`${BASE}/health`, { method: "GET", cache: "no-store",
      signal: AbortSignal.timeout(3000) });
    return r.ok;
  } catch { return false; }
}

async function getKbCount() {
  const key = await getStoredKey();
  if (!key) return null;
  try {
    const r = await fetch(`${BASE}/api/v1/knowledge/`, {
      headers: { "Authorization": `Bearer ${key}` },
      signal: AbortSignal.timeout(4000),
    });
    const d = await r.json();
    const items = d.items ?? (Array.isArray(d) ? d : []);
    const kb = items.find(i => i.name === KB_NAME);
    return kb ? (kb.files?.length ?? 0) : "?";
  } catch { return null; }
}

async function getModelName() {
  try {
    const r = await fetch(`${BASE}/api/tags`, { signal: AbortSignal.timeout(3000) });
    const d = await r.json();
    const models = d.models ?? [];
    return models[0]?.name?.split(":")[0] ?? "none";
  } catch { return null; }
}

async function getStoredKey() {
  return new Promise(resolve => {
    chrome.storage.local.get("api_key", d => resolve(d.api_key ?? null));
  });
}

function setDot(id, state) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `dot ${state}`;
}

async function refreshStatus() {
  const alive = await ping();
  if (alive) {
    setDot("dot-webui", "green");
    document.getElementById("s-webui").childNodes[1].textContent = "WebUI ✓";
    overlay.classList.remove("active");
  } else {
    setDot("dot-webui", "red");
    document.getElementById("s-webui").childNodes[1].textContent = "WebUI ✗";
    overlay.classList.add("active");
  }

  const kbCount = await getKbCount();
  if (kbCount !== null) {
    setDot("dot-kb", "green");
    document.getElementById("s-kb").childNodes[1].textContent = `KB ${kbCount}f`;
  } else {
    setDot("dot-kb", "yellow");
    document.getElementById("s-kb").childNodes[1].textContent = "KB -";
  }

  const model = await getModelName();
  if (model) {
    setDot("dot-model", "green");
    document.getElementById("s-model").childNodes[1].textContent = model;
  } else {
    setDot("dot-model", "yellow");
    document.getElementById("s-model").childNodes[1].textContent = "no model";
  }
}

// ── Toolbar buttons ─────────────────────────────────────────────────────────
document.getElementById("btn-reload").addEventListener("click", () => {
  frame.src = frame.src;
  refreshStatus();
});

document.getElementById("btn-open-tab").addEventListener("click", () => {
  chrome.tabs.create({ url: frame.src });
});

document.getElementById("btn-kb").addEventListener("click", () => {
  frame.src = `${BASE}/workspace/knowledge`;
});

document.getElementById("btn-retry")?.addEventListener("click", () => {
  frame.src = `${BASE}/`;
  setTimeout(refreshStatus, 1500);
});

// ── Quick-bar nav ───────────────────────────────────────────────────────────
document.querySelectorAll(".qa").forEach(el => {
  el.addEventListener("click", () => {
    const path = el.dataset.path ?? "/";
    frame.src = `${BASE}${path}`;
  });
});

// ── Init ─────────────────────────────────────────────────────────────────────
refreshStatus();
setInterval(refreshStatus, 30_000);

// Detect frame load failure (best-effort — cross-origin limited)
frame.addEventListener("load", () => {
  setTimeout(refreshStatus, 500);
});
