// popup.js

const SERVER = "http://127.0.0.1:7070";
let csvData = null;
let activePlatforms = new Set();
let modelsLoadedOnce = false;

// ── Helpers ───────────────────────────────────────────────────────────────────
function setStatus(msg, type = "info") {
  const el = document.getElementById("statusBar");
  el.textContent = msg;
  el.style.color = type === "error" ? "#f87171" : type === "ok" ? "#86efac" : "#94a3b8";
}

async function sendMsg(type, data = {}) {
  return new Promise(resolve => chrome.runtime.sendMessage({ type, ...data }, resolve));
}

async function apiPost(path, body) {
  const r = await fetch(`${SERVER}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

function parseCsvLine(line) {
  const out = [];
  let cell = "";
  let inQuotes = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === "\"") {
      if (inQuotes && line[index + 1] === "\"") {
        cell += "\"";
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === "," && !inQuotes) {
      out.push(cell.trim());
      cell = "";
      continue;
    }
    cell += char;
  }
  out.push(cell.trim());
  return out;
}

function normalizeHeader(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, "_").trim();
}

function parseCsvText(text) {
  const rows = [];
  const lines = String(text || "").split(/\r?\n/);
  for (const rawLine of lines) {
    const trimmed = rawLine.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    rows.push(parseCsvLine(rawLine));
  }
  if (rows.length < 2) {
    return { error: "CSV needs a header row plus at least one data row." };
  }

  const headers = rows[0].map(normalizeHeader);
  if (!headers.includes("recipient")) {
    return { error: "CSV header must include `recipient`." };
  }

  const indexOf = (name) => headers.indexOf(name);
  const cell = (arr, name) => {
    const index = indexOf(name);
    return index >= 0 ? String(arr[index] || "").trim() : "";
  };

  const parsed = rows.slice(1).map((entry) => ({
    recipient: cell(entry, "recipient"),
    subject: cell(entry, "subject"),
    body_file: cell(entry, "body_file"),
    body: cell(entry, "body"),
    attachments: cell(entry, "attachments"),
    provider: cell(entry, "provider"),
    delay: Number.parseInt(cell(entry, "delay"), 10) || 3
  })).filter((entry) => entry.recipient);

  if (!parsed.length) {
    return { error: "No valid recipient rows found in CSV." };
  }

  return { rows: parsed };
}

async function loadAiModels() {
  const select = document.getElementById("aiModel");
  const previousValue = select.value;
  const noneOption = '<option value="none">None (use body as-is)</option>';

  try {
    const response = await fetch(`${SERVER}/api/ollama/models`, { signal: AbortSignal.timeout(3000) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const models = Array.isArray(payload?.models) ? payload.models : [];

    select.innerHTML = noneOption;
    for (const model of models) {
      const name = String(model || "").trim();
      if (!name) continue;
      const option = document.createElement("option");
      option.value = name;
      option.textContent = `Ollama ${name}`;
      select.appendChild(option);
    }

    if (previousValue && Array.from(select.options).some((opt) => opt.value === previousValue)) {
      select.value = previousValue;
    } else if (models.length) {
      select.value = models[0];
    } else {
      select.value = "none";
    }
    modelsLoadedOnce = true;
  } catch (_e) {
    if (!modelsLoadedOnce) {
      select.innerHTML = `${noneOption}<option value="mistral:latest">Ollama mistral:latest</option><option value="llama3.2:3b">Ollama llama3.2:3b</option>`;
    }
  }
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
  });
});

// ── Server health ─────────────────────────────────────────────────────────────
async function checkHealth() {
  const res = await sendMsg("SERVER_HEALTH");
  const dot = document.getElementById("serverDot");
  const label = document.getElementById("serverLabel");
  if (res?.online) {
    dot.className = "dot online";
    label.textContent = "server online";
    document.getElementById("runEmailBtn").disabled = !csvData;
    document.getElementById("postBtn").disabled = !activePlatforms.size;
    if (!modelsLoadedOnce) {
      loadAiModels().catch(() => {});
    }
  } else {
    dot.className = "dot";
    label.textContent = "server offline";
    document.getElementById("runEmailBtn").disabled = true;
    document.getElementById("postBtn").disabled = true;
    setStatus("Start the Python server: cd server && python server.py", "error");
  }
}
checkHealth();
setInterval(checkHealth, 10000);
setInterval(() => {
  loadAiModels().catch(() => {});
}, 30000);

// ── CSV loading ───────────────────────────────────────────────────────────────
document.getElementById("csvFile").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  const parsed = parseCsvText(text);
  if (parsed.error) {
    setStatus(parsed.error, "error");
    document.getElementById("csvInfo").textContent = parsed.error;
    document.getElementById("csvInfo").style.display = "block";
    document.getElementById("csvInfo").style.color = "#fca5a5";
    csvData = null;
    document.getElementById("runEmailBtn").disabled = true;
    return;
  }

  const rows = parsed.rows;
  csvData = { file: file.name, rows };
  document.getElementById("csvInfo").textContent = `Loaded ${rows.length} emails from ${file.name}`;
  document.getElementById("csvInfo").style.display = "block";
  document.getElementById("csvInfo").style.color = "#22c55e";
  document.getElementById("runEmailBtn").disabled = false;
  setStatus(`CSV loaded: ${rows.length} emails`);
});

// File drop zone
const dropZone = document.getElementById("csvDrop");
dropZone.addEventListener("dragover", e => e.preventDefault());
dropZone.addEventListener("drop", async (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) {
    // Trigger same handler
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById("csvFile").files = dt.files;
    document.getElementById("csvFile").dispatchEvent(new Event("change"));
  }
});

// ── Email batch run ───────────────────────────────────────────────────────────
document.getElementById("runEmailBtn").addEventListener("click", async () => {
  if (!csvData) return;
  const job = {
    type: "email_batch",
    provider: document.getElementById("emailProvider").value,
    ai_model: document.getElementById("aiModel").value,
    dry_run: document.getElementById("dryRun").checked,
    rows: csvData.rows,
  };
  setStatus(`Submitting ${csvData.rows.length} emails...`);
  document.getElementById("emailProgress").style.display = "block";
  document.getElementById("emailProgressFill").style.width = "5%";

  const res = await sendMsg("RUN_JOB", { job });
  if (res?.error) {
    setStatus(`Error: ${res.error}`, "error");
    return;
  }
  if (res?.job_id) {
    pollJobStatus(res.job_id, "email");
  }
});

async function pollJobStatus(job_id, jobType) {
  const fill = document.getElementById(`${jobType}ProgressFill`);
  const interval = setInterval(async () => {
    const res = await sendMsg("JOB_STATUS", { job_id });
    if (!res || res.error) { clearInterval(interval); return; }
    const pct = Math.round((res.done / Math.max(res.total, 1)) * 100);
    fill.style.width = `${pct}%`;
    setStatus(`${jobType}: ${res.done}/${res.total} — ${res.status}`);
    if (res.status === "done" || res.status === "error") {
      clearInterval(interval);
      setStatus(`Done: ${res.done} sent, ${res.failed || 0} failed`, res.status === "error" ? "error" : "ok");
    }
  }, 2000);
}

// ── Social posting ────────────────────────────────────────────────────────────
document.querySelectorAll("[data-platform]").forEach(btn => {
  btn.addEventListener("click", () => {
    const p = btn.dataset.platform;
    if (activePlatforms.has(p)) {
      activePlatforms.delete(p);
      btn.classList.remove("captured");
    } else {
      activePlatforms.add(p);
      btn.classList.add("captured");
    }
    document.getElementById("postBtn").disabled = activePlatforms.size === 0;
  });
});

document.getElementById("loadMdBtn").addEventListener("click", () => {
  document.getElementById("mdFile").click();
});
document.getElementById("mdFile").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  // Extract title from first # heading
  const titleMatch = text.match(/^#\s+(.+)/m);
  if (titleMatch) document.getElementById("postTitle").value = titleMatch[1];
  document.getElementById("postContent").value = text;
});

document.getElementById("postBtn").addEventListener("click", async () => {
  const platforms = Array.from(activePlatforms);
  const socialDryRun = document.getElementById("socialDryRun").checked;
  const job = {
    type: "social_post",
    platforms,
    title: document.getElementById("postTitle").value,
    content: document.getElementById("postContent").value,
    ai_rewrite: document.getElementById("aiRewrite").checked,
    dry_run: socialDryRun,
  };
  setStatus(`${socialDryRun ? "Dry-run validating" : "Posting"} to ${platforms.join(", ")}...`);
  const res = await sendMsg("RUN_JOB", { job });
  if (res?.error) setStatus(`Error: ${res.error}`, "error");
  else if (res?.job_id) pollJobStatus(res.job_id, "social");
});

// ── Session capture ───────────────────────────────────────────────────────────
document.querySelectorAll("[data-capture]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const platform = btn.dataset.capture;
    setStatus(`Capturing ${platform} session...`);
    const res = await sendMsg("CAPTURE_SESSION", { platform });
    if (res?.ok) {
      btn.classList.add("captured");
      setStatus(`${platform}: ${res.count} cookies captured`, "ok");
      loadSessionStatus();
    } else {
      setStatus(`Failed: ${res?.error || "unknown error"}`, "error");
    }
  });
});

async function loadSessionStatus() {
  const sessions = await sendMsg("GET_SESSIONS");
  const el = document.getElementById("sessionList");
  if (!sessions || Object.keys(sessions).length === 0) {
    el.textContent = "No sessions captured yet.";
    return;
  }
  el.innerHTML = Object.entries(sessions).map(([platform, data]) => {
    const age = Math.round((Date.now() - new Date(data.captured_at)) / 3600000);
    const badge = age < 24 ? "badge-green" : age < 72 ? "badge-yellow" : "badge-red";
    return `<div class="job-row">
      <span>${platform}</span>
      <span class="badge ${badge}">${data.cookies.length} cookies</span>
      <span style="color:#64748b;font-size:10px">${age}h ago</span>
    </div>`;
  }).join("");
}
loadSessionStatus();

// ── Learn panel ───────────────────────────────────────────────────────────────
chrome.storage.local.get("recordings", (data) => {
  const recordings = data.recordings || [];
  const byPlatform = recordings.reduce((acc, r) => {
    acc[r.platform] = (acc[r.platform] || 0) + 1;
    return acc;
  }, {});
  document.getElementById("recordingStats").innerHTML =
    Object.entries(byPlatform).length
      ? Object.entries(byPlatform).map(([p, n]) => `${p}: <strong>${n}</strong> sessions`).join(" · ")
      : "No recordings yet. Browse the target sites to record activity.";
});

document.getElementById("trainBtn").addEventListener("click", async () => {
  const data = await new Promise(resolve => chrome.storage.local.get("recordings", resolve));
  const recordings = (data.recordings || []).slice(-20);
  if (!recordings.length) { setStatus("No recordings to analyse."); return; }
  setStatus("Sending recordings to Ollama...");
  try {
    const res = await apiPost("/api/learn/analyse", { recordings });
    const out = document.getElementById("trainOutput");
    out.textContent = res.insights || res.error || JSON.stringify(res, null, 2);
    out.style.display = "block";
    setStatus("Analysis complete", "ok");
  } catch (e) {
    setStatus(`Failed: ${e.message}`, "error");
  }
});
