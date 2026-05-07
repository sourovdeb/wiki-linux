const chatLog = document.getElementById("chatLog");
const promptInput = document.getElementById("promptInput");
const modelInput = document.getElementById("modelInput");

const sendBtn = document.getElementById("sendBtn");
const summarizeBtn = document.getElementById("summarizeBtn");
const searchBtn = document.getElementById("searchBtn");
const crawlBtn = document.getElementById("crawlBtn");
const pdfBtn = document.getElementById("pdfBtn");
const fillFormBtn = document.getElementById("fillFormBtn");

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

async function sendToContent(type, payload = {}) {
  const tab = await getActiveTab();
  if (!tab?.id) throw new Error("No active tab");
  return chrome.tabs.sendMessage(tab.id, { type, ...payload });
}

async function ollamaChat(messages) {
  const model = modelInput.value.trim() || "qwen2.5-coder:3b";
  const response = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      messages
    })
  });

  if (!response.ok) {
    throw new Error(`Ollama API failed: ${response.status}`);
  }

  const data = await response.json();
  return data?.message?.content || "No response";
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
  "If producing a form fill plan, output valid JSON object only with key:value pairs."
].join(" ");

async function askWithContext(userPrompt, includeSnapshot = true) {
  const snapshot = includeSnapshot ? await sendToContent("getPageSnapshot") : null;
  const contextBlock = snapshot
    ? `URL: ${snapshot.url}\nTitle: ${snapshot.title}\nSelected Text: ${snapshot.selectedText || ""}\nPage Text: ${(snapshot.text || "").slice(0, 12000)}\n`
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
    await askWithContext("Summarize this website in bullet points. Include key facts and actions.", true);
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

addMessage("system", "Ready. This panel uses your local Ollama endpoint on 127.0.0.1:11434.");
