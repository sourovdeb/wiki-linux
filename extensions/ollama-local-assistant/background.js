chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => {
    console.error("Failed to set panel behavior:", error);
  });
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) {
    console.error("No active tab found.");
    return;
  }

  try {
    await chrome.sidePanel.open({ tabId: tab.id });
    console.log("Side panel opened successfully.");
  } catch (error) {
    console.error("Failed to open side panel:", error);
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "downloadLinks") {
    (async () => {
      const links = Array.isArray(msg.links) ? msg.links : [];
      let success = 0;
      for (const url of links) {
        try {
          await chrome.downloads.download({ url, saveAs: false });
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
