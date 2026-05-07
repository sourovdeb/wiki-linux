// content.js — Activity recorder injected into Gmail, ProtonMail, LinkedIn, Medium
// Records user actions to teach the system how to interact with each platform

(function () {
  if (window.__wikiAutomatorLoaded) return;
  window.__wikiAutomatorLoaded = true;

  const platform = detectPlatform();
  if (!platform) return;

  const session = {
    platform,
    url: location.href,
    started: new Date().toISOString(),
    actions: [],
  };

  function detectPlatform() {
    const h = location.hostname;
    if (h.includes("mail.google.com")) return "gmail";
    if (h.includes("proton.me")) return "proton";
    if (h.includes("linkedin.com")) return "linkedin";
    if (h.includes("medium.com")) return "medium";
    return null;
  }

  function getCssSelector(el) {
    if (!el || el === document.body) return "body";
    const parts = [];
    while (el && el !== document.body) {
      let sel = el.tagName.toLowerCase();
      if (el.id) {
        sel += `#${el.id}`;
        parts.unshift(sel);
        break;
      }
      if (el.className) {
        const classes = Array.from(el.classList).slice(0, 2).join(".");
        if (classes) sel += `.${classes}`;
      }
      const parent = el.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter(c => c.tagName === el.tagName);
        if (siblings.length > 1) sel += `:nth-of-type(${siblings.indexOf(el) + 1})`;
      }
      parts.unshift(sel);
      el = el.parentElement;
    }
    return parts.slice(-4).join(" > ");
  }

  function record(type, el, extra = {}) {
    const action = {
      type,
      timestamp: new Date().toISOString(),
      url: location.href,
      selector: getCssSelector(el),
      tag: el?.tagName?.toLowerCase(),
      text: (el?.innerText || el?.value || "").slice(0, 100),
      ...extra,
    };
    session.actions.push(action);
  }

  // Record clicks
  document.addEventListener("click", (e) => {
    record("click", e.target);
  }, true);

  // Record form inputs (debounced)
  let inputTimer;
  document.addEventListener("input", (e) => {
    clearTimeout(inputTimer);
    inputTimer = setTimeout(() => {
      const val = e.target.value || "";
      // Don't record passwords
      if (e.target.type === "password") return;
      record("input", e.target, { value: val.slice(0, 200) });
    }, 800);
  }, true);

  // Record navigation
  const _pushState = history.pushState.bind(history);
  history.pushState = function (...args) {
    _pushState(...args);
    record("navigate", document.body, { to: args[2] });
  };

  // Save recording on page unload
  window.addEventListener("beforeunload", () => {
    if (session.actions.length === 0) return;
    session.ended = new Date().toISOString();
    chrome.runtime.sendMessage({
      type: "SAVE_RECORDING",
      recording: session,
    });
  });

  // Save recording periodically (every 60s if active)
  setInterval(() => {
    if (session.actions.length > 0) {
      chrome.runtime.sendMessage({
        type: "SAVE_RECORDING",
        recording: { ...session, partial: true },
      });
    }
  }, 60000);

  console.log(`[WikiAutomator] Recording ${platform} session`);
})();
