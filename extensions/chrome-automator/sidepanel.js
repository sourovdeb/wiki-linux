const dot = document.getElementById("status-dot");
const log = document.getElementById("log");

function addEntry(text, type = "info") {
  const el = document.createElement("div");
  el.className = `entry ${type}`;
  const t = new Date().toLocaleTimeString();
  el.innerHTML = `<time>${t}</time>${text}`;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

// Health check
async function checkServer() {
  try {
    const r = await fetch("http://127.0.0.1:7070/api/health", { signal: AbortSignal.timeout(2000) });
    if (r.ok) {
      dot.className = "online";
    } else {
      dot.className = "";
    }
  } catch {
    dot.className = "";
  }
}

// Listen for job updates from background
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "JOB_UPDATE") {
    const type = msg.status === "done" ? "ok" : msg.status === "error" ? "error" : "info";
    addEntry(`[${msg.jobId?.slice(0, 8)}] ${msg.status} — ${msg.message || ""}`, type);
  }
  if (msg.type === "SESSION_CAPTURED") {
    addEntry(`Session captured: ${msg.platform}`, "ok");
  }
  if (msg.type === "RECORDING_SAVED") {
    addEntry(`Recording saved: ${msg.platform} (${msg.count} actions)`, "info");
  }
});

document.getElementById("btn-open-popup").addEventListener("click", () => {
  chrome.action.openPopup?.();
});

document.getElementById("btn-clear").addEventListener("click", () => {
  log.innerHTML = "";
});

checkServer();
setInterval(checkServer, 10000);
addEntry("Side panel ready", "ok");
