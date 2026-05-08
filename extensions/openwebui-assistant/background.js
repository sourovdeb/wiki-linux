chrome.runtime.onInstalled.addListener(() => {
  if (chrome.sidePanel?.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

// Fallback only when setPanelBehavior is unavailable.
if (!chrome.sidePanel?.setPanelBehavior && chrome.action?.onClicked) {
  chrome.action.onClicked.addListener(async (tab) => {
    if (!chrome.sidePanel?.open || !tab?.id) return;
    await chrome.sidePanel.open({ tabId: tab.id }).catch(() => {});
  });
}
