// background.js — robust side-panel handler for Chromium and fallback behavior.
const api = (typeof browser !== "undefined") ? browser : chrome;

if (api.sidePanel && api.sidePanel.setPanelBehavior) {
  api.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(err => console.warn("sidePanel.setPanelBehavior failed:", err));
}

(function setupSidePanel() {
  const hasSidePanel = !!api.sidePanel;

  api.action.onClicked.addListener(async () => {
    try {
      if (hasSidePanel && typeof api.sidePanel.open === "function") {
        const attempts = [
          async () => api.sidePanel.open({ path: "sidepanel.html" }),
          async () => api.sidePanel.open(),
          async () => api.sidePanel.open({ url: api.runtime.getURL("sidepanel.html") })
        ];

        for (const a of attempts) {
          try { await a(); console.log("sidePanel.open succeeded"); return; } catch (e) { /* try next */ }
        }
      }

      await api.tabs.create({ url: api.runtime.getURL("sidepanel.html") });
      console.log("Opened sidepanel.html in a new tab as fallback");
    } catch (err) {
      console.error("Failed to open side panel or fallback tab:", err);
    }
  });
})();

// Keep previous message handler behavior for other features (e.g., downloads).
api.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "downloadLinks") {
    (async () => {
      const links = Array.isArray(msg.links) ? msg.links : [];
      let success = 0;
      for (const url of links) {
        try {
          await api.downloads.download({ url, saveAs: false });
          success += 1;
        } catch (_e) {
          // Continue trying remaining links.
        }
      }
      sendResponse({ ok: true, attempted: links.length, success });
    })();
    return true;
  }
  return false;
});
