// background.js — Service Worker for Wiki Automator
// Handles: cookie capture, session storage, message routing to local Python server

const SERVER = "http://127.0.0.1:7070";

// ── Session cookie capture ───────────────────────────────────────────────────
// Called from popup when user clicks "Capture Session" for a platform
async function captureSessionCookies(platform) {
  const platformUrls = {
    gmail:     "https://mail.google.com",
    proton:    "https://mail.proton.me",
    linkedin:  "https://www.linkedin.com",
    medium:    "https://medium.com",
  };
  const url = platformUrls[platform];
  if (!url) return { error: `Unknown platform: ${platform}` };

  const cookies = await chrome.cookies.getAll({ url });
  const payload = { platform, cookies, captured_at: new Date().toISOString() };

  // Save to local storage
  const stored = await chrome.storage.local.get("sessions") || {};
  const sessions = stored.sessions || {};
  sessions[platform] = payload;
  await chrome.storage.local.set({ sessions });

  // Send to Python server for Playwright to use
  try {
    await fetch(`${SERVER}/api/sessions/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return { ok: true, count: cookies.length, platform };
  } catch (e) {
    return { ok: true, count: cookies.length, platform, warning: "Server offline — saved locally only" };
  }
}

// ── Relay activity recordings ────────────────────────────────────────────────
async function saveRecording(recording) {
  try {
    await fetch(`${SERVER}/api/recordings/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recording),
    });
  } catch (_) {}
  // Also save locally
  const data = await chrome.storage.local.get("recordings");
  const recordings = data.recordings || [];
  recordings.push(recording);
  // Keep last 500 recordings
  await chrome.storage.local.set({ recordings: recordings.slice(-500) });
}

// ── Server health check ───────────────────────────────────────────────────────
async function checkServer() {
  try {
    const r = await fetch(`${SERVER}/api/health`, { signal: AbortSignal.timeout(2000) });
    return (await r.json()).status === "ok";
  } catch (_) {
    return false;
  }
}

// ── Message handler ───────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    switch (msg.type) {
      case "CAPTURE_SESSION":
        sendResponse(await captureSessionCookies(msg.platform));
        break;

      case "SAVE_RECORDING":
        await saveRecording(msg.recording);
        sendResponse({ ok: true });
        break;

      case "SERVER_HEALTH":
        sendResponse({ online: await checkServer() });
        break;

      case "GET_SESSIONS": {
        const d = await chrome.storage.local.get("sessions");
        sendResponse(d.sessions || {});
        break;
      }

      case "RUN_JOB": {
        // Forward job to Python server
        try {
          const r = await fetch(`${SERVER}/api/jobs/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(msg.job),
          });
          sendResponse(await r.json());
        } catch (e) {
          sendResponse({ error: e.message });
        }
        break;
      }

      case "JOB_STATUS": {
        try {
          const r = await fetch(`${SERVER}/api/jobs/status/${msg.job_id}`);
          sendResponse(await r.json());
        } catch (e) {
          sendResponse({ error: e.message });
        }
        break;
      }

      default:
        sendResponse({ error: "Unknown message type" });
    }
  })();
  return true; // async response
});

// ── Badge updater ─────────────────────────────────────────────────────────────
setInterval(async () => {
  const online = await checkServer();
  chrome.action.setBadgeText({ text: online ? "" : "off" });
  chrome.action.setBadgeBackgroundColor({ color: online ? "#22c55e" : "#ef4444" });
}, 10000);
