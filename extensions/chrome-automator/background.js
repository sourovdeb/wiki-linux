// background.js — Service Worker for Wiki Automator
// Handles: cookie capture, session storage, message routing to local Python server

const SERVER = "http://127.0.0.1:7070";
const BADGE_ALARM = "server_health_badge";

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
    const result = { ok: true, count: cookies.length, platform };
    broadcast({ type: "SESSION_CAPTURED", platform, count: cookies.length });
    return result;
  } catch (e) {
    const result = { ok: true, count: cookies.length, platform, warning: "Server offline — saved locally only" };
    broadcast({ type: "SESSION_CAPTURED", platform, count: cookies.length });
    return result;
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
  broadcast({
    type: "RECORDING_SAVED",
    platform: recording?.platform || "unknown",
    count: Array.isArray(recording?.actions) ? recording.actions.length : 0
  });
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

function broadcast(message) {
  chrome.runtime.sendMessage(message).catch(() => {});
}

async function updateBadge() {
  const online = await checkServer();
  await chrome.action.setBadgeText({ text: online ? "" : "off" });
  await chrome.action.setBadgeBackgroundColor({ color: online ? "#22c55e" : "#ef4444" });
}

async function ensureBadgeAlarm() {
  const existing = await chrome.alarms.get(BADGE_ALARM);
  if (existing) return;
  await chrome.alarms.create(BADGE_ALARM, { periodInMinutes: 0.5 });
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
          const payload = await r.json();
          if (payload?.job_id) {
            broadcast({ type: "JOB_UPDATE", jobId: payload.job_id, status: "queued", message: "Job queued" });
          }
          sendResponse(payload);
        } catch (e) {
          sendResponse({ error: e.message });
        }
        break;
      }

      case "JOB_STATUS": {
        try {
          const r = await fetch(`${SERVER}/api/jobs/status/${msg.job_id}`);
          const status = await r.json();
          if (!status?.error) {
            broadcast({
              type: "JOB_UPDATE",
              jobId: msg.job_id,
              status: status.status,
              message: `${status.done || 0}/${status.total || 0}${status.failed ? `, failed ${status.failed}` : ""}`
            });
          }
          sendResponse(status);
        } catch (e) {
          sendResponse({ error: e.message });
        }
        break;
      }

      case "JOB_UPDATE":
      case "SESSION_CAPTURED":
      case "RECORDING_SAVED":
        // Internal broadcast message types are ignored by background listener.
        sendResponse({ ok: true });
        break;

      default:
        sendResponse({ error: "Unknown message type" });
    }
  })();
  return true; // async response
});

chrome.runtime.onInstalled.addListener(async () => {
  await ensureBadgeAlarm();
  await updateBadge();
});

chrome.runtime.onStartup.addListener(async () => {
  await ensureBadgeAlarm();
  await updateBadge();
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== BADGE_ALARM) return;
  await updateBadge();
});
