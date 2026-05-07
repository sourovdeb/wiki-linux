const api = chrome.sidePanel ?? chrome.action;

chrome.runtime.onInstalled.addListener(() => {
  if (chrome.sidePanel?.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

// Open side panel on toolbar click (fallback for non-sidePanel builds)
chrome.action.onClicked.addListener(async (tab) => {
  if (!chrome.sidePanel?.open) return;
  await chrome.sidePanel.open({ tabId: tab.id }).catch(() => {});
});
