chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) return;
  await chrome.sidePanel.open({ tabId: tab.id }).catch(() => {});
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
