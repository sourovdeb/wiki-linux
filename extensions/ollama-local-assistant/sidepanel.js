const chatLog = document.getElementById("chatLog");
const promptInput = document.getElementById("promptInput");
const modelInput = document.getElementById("modelInput");
const modelSelect = document.getElementById("modelSelect");

const pickFastModelBtn = document.getElementById("pickFastModelBtn");
const refreshModelsBtn = document.getElementById("refreshModelsBtn");

const sendBtn = document.getElementById("sendBtn");
const summarizeBtn = document.getElementById("summarizeBtn");
const searchBtn = document.getElementById("searchBtn");
const crawlBtn = document.getElementById("crawlBtn");
const pdfBtn = document.getElementById("pdfBtn");
const brainstormBtn = document.getElementById("brainstormBtn");
const mindfulBtn = document.getElementById("mindfulBtn");
const fillFormBtn = document.getElementById("fillFormBtn");

const OLLAMA_BASE = "http://127.0.0.1:11434";
const DEFAULT_MODEL = "llama3.2:3b";
const MODEL_REFRESH_INTERVAL_MS = 30000;

let modelRefreshInFlight = false;
let pendingModelRefresh = false;

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.textContent = text;
  chatLog.appendChild(el);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function getActiveTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs[0];
}

function isScriptablePage(url) {
  return /^https?:\/\//i.test(url || "") || /^file:\/\//i.test(url || "");
}

function isNoReceiverError(error) {
  return /Receiving end does not exist/i.test(String(error?.message || error || ""));
}

async function sendToContent(type, payload = {}) {
  const tab = await getActiveTab();
  if (!tab?.id) throw new Error("No active tab");
  const send = () => chrome.tabs.sendMessage(tab.id, { type, ...payload });

  try {
    return await send();
  } catch (error) {
    if (!isNoReceiverError(error)) {
      throw error;
    }

    const tabUrl = tab.url || "";
    if (!isScriptablePage(tabUrl)) {
      throw new Error(
        "This tab does not allow page access. Open a regular http(s) page and try again."
      );
    }

    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content.js"]
      });
    } catch (_injectError) {
      throw new Error(
        "Cannot attach page helper to this tab. Reload the page, then retry."
      );
    }

    try {
      return await send();
    } catch (_retryError) {
      throw new Error(
        "Could not connect to the page helper. Reload this tab and retry."
      );
    }
  }
}

function modelContextCharLimit(modelName) {
  const lower = (modelName || "").toLowerCase();
  if (/(^|:)(1b|1\.5b|2b|3b|4b)\b/.test(lower)) return 6000;
  if (/(^|:)(7b|8b)\b/.test(lower)) return 10000;
  return 14000;
}

function pickFastModelName(models) {
  const candidates = models
    .map((m) => ({ name: m.name, size: typeof m.size === "number" ? m.size : Number.POSITIVE_INFINITY }))
    .filter((m) => m.name && !/embed|embedding/i.test(m.name))
    .sort((a, b) => a.size - b.size);
  return candidates[0]?.name || models[0]?.name || "";
}

function flattenText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function normalizeModelName(model) {
  return String(model || "").trim();
}

function setModelInputValue(value) {
  modelInput.value = normalizeModelName(value);
}

function updateModelSelect(models, preferredValue) {
  const names = (models || [])
    .map((m) => normalizeModelName(m.name))
    .filter(Boolean);

  const keepValue = normalizeModelName(preferredValue || modelInput.value);
  modelSelect.innerHTML = "";

  if (!names.length) {
    const none = document.createElement("option");
    none.value = "";
    none.textContent = "No installed models";
    none.disabled = true;
    none.selected = true;
    modelSelect.appendChild(none);
    modelSelect.disabled = true;
    return;
  }

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = `Installed models (${names.length})`;
  placeholder.disabled = true;
  modelSelect.appendChild(placeholder);

  for (const name of names) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    modelSelect.appendChild(opt);
  }

  modelSelect.disabled = false;
  if (names.includes(keepValue)) {
    modelSelect.value = keepValue;
  } else {
    modelSelect.selectedIndex = 0;
  }
}

async function parseOllamaErrorDetail(response) {
  let raw = "";
  try {
    raw = await response.text();
  } catch (_e) {
    return "";
  }
  if (!raw) return "";

  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.error === "string") {
      return parsed.error;
    }
  } catch (_e) {
    // Not JSON; fall through to raw text.
  }
  return flattenText(raw).slice(0, 240);
}

async function ollamaFetch(path, init = {}) {
  const response = await fetch(`${OLLAMA_BASE}${path}`, init);
  if (!response.ok) {
    if (response.status === 403) {
      throw new Error(
        "Ollama returned 403 (origin blocked). Fix: set `OLLAMA_ORIGINS` to include `chrome-extension://*` (and restart Ollama)."
      );
    }
    const detail = await parseOllamaErrorDetail(response);
    const suffix = detail ? ` (${detail})` : "";
    const error = new Error(`Ollama API failed: ${response.status}${suffix}`);
    error.status = response.status;
    error.detail = detail;
    error.path = path;
    throw error;
  }
  return response.json();
}

async function listLocalModels() {
  const data = await ollamaFetch("/api/tags", { method: "GET" });
  return Array.isArray(data?.models) ? data.models : [];
}

async function refreshInstalledModels(options = {}) {
  const { announce = false } = options;
  if (modelRefreshInFlight) {
    pendingModelRefresh = true;
    return [];
  }

  modelRefreshInFlight = true;
  if (refreshModelsBtn) {
    refreshModelsBtn.disabled = true;
  }

  try {
    const models = await listLocalModels();
    updateModelSelect(models);
    if (announce) {
      addMessage("system", `Model list refreshed (${models.length} installed).`);
    }
    return models;
  } finally {
    modelRefreshInFlight = false;
    if (refreshModelsBtn) {
      refreshModelsBtn.disabled = false;
    }
    if (pendingModelRefresh) {
      pendingModelRefresh = false;
      refreshInstalledModels().catch(() => {});
    }
  }
}

function messagesToPrompt(messages) {
  return (messages || [])
    .map((msg) => {
      const role = String(msg?.role || "user").toUpperCase();
      const content = String(msg?.content || "");
      return `[${role}]\n${content}`;
    })
    .join("\n\n");
}

async function ensureUsableModel(preferredModel) {
  const models = await listLocalModels();
  updateModelSelect(models, preferredModel);
  if (!models.length) {
    throw new Error("No local Ollama models found. Pull a model first.");
  }

  const requested = (preferredModel || "").trim() || DEFAULT_MODEL;
  const names = new Set(models.map((m) => m.name));
  if (names.has(requested)) {
    return requested;
  }

  const fallback = pickFastModelName(models);
  if (!fallback) {
    throw new Error(`Requested model \`${requested}\` not found and no fallback is available.`);
  }

  if (modelInput.value.trim() !== fallback) {
    setModelInputValue(fallback);
    modelSelect.value = fallback;
    addMessage("system", `Model \`${requested}\` not found locally. Switched to \`${fallback}\`.`);
  }
  return fallback;
}

async function ollamaChat(messages) {
  let model = await ensureUsableModel(modelInput.value);
  const chatPayload = { model, stream: false, messages };

  try {
    const data = await ollamaFetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(chatPayload)
    });
    return data?.message?.content || data?.response || "No response";
  } catch (error) {
    const detail = String(error?.detail || "").toLowerCase();
    const isChatPathMissing = detail.includes("/api/chat") || detail.includes("page not found") || detail.includes("path") && detail.includes("not found");
    const isModelMissing = detail.includes("model") && detail.includes("not found");

    if (error?.status === 404 && isModelMissing) {
      model = await ensureUsableModel("");
      const retried = await ollamaFetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...chatPayload, model })
      });
      return retried?.message?.content || retried?.response || "No response";
    }

    if (error?.status === 404 && isChatPathMissing) {
      const prompt = messagesToPrompt(messages);
      const generated = await ollamaFetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          stream: false,
          prompt
        })
      });
      addMessage("system", "Using `/api/generate` fallback because `/api/chat` returned 404.");
      return generated?.response || "No response";
    }

    throw error;
  }
}

function extractJsonObject(text) {
  const fenced = text.match(/```json\s*([\s\S]*?)```/i);
  if (fenced?.[1]) {
    try {
      return JSON.parse(fenced[1]);
    } catch (_e) {}
  }

  const fallback = text.match(/\{[\s\S]*\}/);
  if (fallback?.[0]) {
    try {
      return JSON.parse(fallback[0]);
    } catch (_e) {}
  }
  return null;
}

const SYSTEM_PROMPT = [
  "You are a local browsing assistant connected to Ollama.",
  "Give concise, practical outputs.",
  "Use only the provided page snapshot as evidence; if something is missing, say so.",
  "When the user explicitly requests JSON, output JSON only."
].join(" ");

async function askWithContext(userPrompt, includeSnapshot = true) {
  const snapshot = includeSnapshot ? await sendToContent("getPageSnapshot") : null;
  const contextLimit = modelContextCharLimit(modelInput.value);
  const contextBlock = snapshot
    ? `URL: ${snapshot.url}\nTitle: ${snapshot.title}\nSelected Text: ${snapshot.selectedText || ""}\nPage Text: ${(snapshot.text || "").slice(0, contextLimit)}\n`
    : "";

  addMessage("user", userPrompt);
  const answer = await ollamaChat([
    { role: "system", content: SYSTEM_PROMPT },
    { role: "user", content: `${contextBlock}\nUser Request: ${userPrompt}` }
  ]);
  addMessage("ai", answer);
  return { answer, snapshot };
}

sendBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) return;
  promptInput.value = "";
  try {
    await askWithContext(prompt, true);
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

summarizeBtn.addEventListener("click", async () => {
  try {
    await askWithContext(
      "Summarize this website in <=10 bullet points (<=180 words). Then add 3 next actions.",
      true
    );
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

searchBtn.addEventListener("click", async () => {
  const query = promptInput.value.trim();
  if (!query) {
    addMessage("system", "Type what information you want in the input box, then click Search Specific Info.");
    return;
  }

  try {
    const pageMatches = await sendToContent("searchInPage", { query });
    const matchesText = (pageMatches?.matches || []).slice(0, 20).join("\n- ");
    const userPrompt = `Find this information: ${query}. Here are direct page matches:\n- ${matchesText || "none"}. Return concise answer with evidence.`;
    await askWithContext(userPrompt, true);
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

crawlBtn.addEventListener("click", async () => {
  try {
    const snapshot = await sendToContent("getPageSnapshot");
    const links = (snapshot?.links || []).slice(0, 120);
    addMessage("system", `Collected ${links.length} visible links. Prioritizing with local model...`);
    const answer = await ollamaChat([
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `URL: ${snapshot.url}\nTitle: ${snapshot.title}\nLinks:\n${links.join("\n")}\n\nTask: Group links by likely intent and suggest the top 10 to open next.`
      }
    ]);
    addMessage("ai", answer);
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

pdfBtn.addEventListener("click", async () => {
  try {
    const result = await sendToContent("collectPdfLinks");
    const links = result?.links || [];
    if (!links.length) {
      addMessage("system", "No PDF links found on this page.");
      return;
    }

    const downloadResult = await chrome.runtime.sendMessage({ type: "downloadLinks", links });
    addMessage("system", `PDF scan complete: ${links.length} link(s). Download attempted: ${downloadResult.success}/${downloadResult.attempted}.`);
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

fillFormBtn.addEventListener("click", async () => {
  const instruction = promptInput.value.trim();
  if (!instruction) {
    addMessage("system", "Enter a form-fill instruction first (example: fill shipping form with my company details).");
    return;
  }

  try {
    const snapshot = await sendToContent("getPageSnapshot");
    const planResponse = await ollamaChat([
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `Form fields schema:\n${JSON.stringify(snapshot.forms || [], null, 2)}\n\nInstruction: ${instruction}\n\nReturn JSON object only: {\"field key\":\"value\"}`
      }
    ]);

    const mapping = extractJsonObject(planResponse);
    if (!mapping || typeof mapping !== "object") {
      addMessage("ai", planResponse);
      addMessage("system", "Could not parse form-fill JSON plan.");
      return;
    }

    const apply = await sendToContent("applyFormData", { mapping });
    addMessage("ai", `Applied form plan. Filled fields: ${apply.filled}.`);
    if (apply.errors?.length) {
      addMessage("system", `Some fields were not found:\n- ${apply.errors.join("\n- ")}`);
    }
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

pickFastModelBtn?.addEventListener("click", async () => {
  try {
    pickFastModelBtn.disabled = true;
    const models = await refreshInstalledModels();
    if (!models.length) {
      addMessage("system", "No local Ollama models found (or Ollama is offline).");
      return;
    }
    const best = pickFastModelName(models);
    if (!best) {
      addMessage("system", "Could not select a model automatically.");
      return;
    }
    setModelInputValue(best);
    modelSelect.value = best;
    addMessage("system", `Selected fast model: ${best}`);
  } catch (e) {
    addMessage("system", `Error selecting model: ${e.message}`);
  } finally {
    pickFastModelBtn.disabled = false;
  }
});

refreshModelsBtn?.addEventListener("click", async () => {
  try {
    await refreshInstalledModels({ announce: true });
  } catch (e) {
    addMessage("system", `Model refresh failed: ${e.message}`);
  }
});

modelSelect?.addEventListener("change", () => {
  const selected = normalizeModelName(modelSelect.value);
  if (!selected) return;
  setModelInputValue(selected);
});

modelInput?.addEventListener("change", () => {
  const typed = normalizeModelName(modelInput.value);
  if (!typed) return;
  if (modelSelect && Array.from(modelSelect.options).some((o) => o.value === typed)) {
    modelSelect.value = typed;
  }
});

brainstormBtn?.addEventListener("click", async () => {
  const topic = promptInput.value.trim();
  promptInput.value = "";
  try {
    const prompt = topic
      ? `Brainstorm ideas about: ${topic}`
      : "Brainstorm practical ideas inspired by this page";
    await askWithContext(
      `${prompt}.\n\nOutput:\n- 3 themes\n- 5 ideas per theme\n- 5-minute first step\n- 3 risks + mitigations\nKeep it concise.`,
      true
    );
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

mindfulBtn?.addEventListener("click", async () => {
  const goal = promptInput.value.trim();
  promptInput.value = "";
  try {
    await askWithContext(
      `Help me be mindful and productive right now${goal ? ` for: ${goal}` : ""}.\n\nOutput:\n1) 30-second grounding\n2) 3 priorities (next 60 minutes)\n3) 1 thing to say no to\nKeep it <=180 words.`,
      false
    );
  } catch (e) {
    addMessage("system", `Error: ${e.message}`);
  }
});

addMessage("system", "Ready. This panel uses your local Ollama endpoint on 127.0.0.1:11434.");
ensureUsableModel(modelInput.value).catch((e) => {
  addMessage("system", `Model check: ${e.message}`);
});
refreshInstalledModels().catch(() => {});
setInterval(() => {
  refreshInstalledModels().catch(() => {});
}, MODEL_REFRESH_INTERVAL_MS);
