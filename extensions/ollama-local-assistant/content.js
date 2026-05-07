function safeText(input) {
  return (input || "").replace(/\s+/g, " ").trim();
}

function getFormSchema() {
  const fields = [];
  const controls = document.querySelectorAll("input, textarea, select");
  controls.forEach((el, idx) => {
    const label =
      el.getAttribute("aria-label") ||
      el.getAttribute("placeholder") ||
      el.getAttribute("name") ||
      el.getAttribute("id") ||
      `field_${idx + 1}`;
    fields.push({
      label: safeText(label),
      name: el.getAttribute("name") || "",
      id: el.id || "",
      type: el.type || el.tagName.toLowerCase(),
      tag: el.tagName.toLowerCase(),
      selector: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}[name=\"${(el.getAttribute("name") || "").replace(/"/g, "\\\"")}\"]`
    });
  });
  return fields;
}

function findFieldByKey(key) {
  const normalized = String(key).toLowerCase();
  if (normalized.startsWith("#") || normalized.startsWith(".") || normalized.startsWith("[")) {
    return document.querySelector(key);
  }

  const controls = document.querySelectorAll("input, textarea, select");
  for (const el of controls) {
    const candidates = [
      el.getAttribute("name"),
      el.getAttribute("id"),
      el.getAttribute("placeholder"),
      el.getAttribute("aria-label")
    ]
      .filter(Boolean)
      .map((v) => String(v).toLowerCase());
    if (candidates.some((v) => v.includes(normalized) || normalized.includes(v))) {
      return el;
    }
  }
  return null;
}

function setFieldValue(el, value) {
  if (!el) return false;
  const tag = el.tagName.toLowerCase();
  const type = (el.type || "").toLowerCase();

  if (type === "checkbox") {
    el.checked = Boolean(value);
  } else if (type === "radio") {
    if (el.value === String(value)) {
      el.checked = true;
    }
  } else if (tag === "select") {
    el.value = String(value);
  } else {
    el.value = String(value ?? "");
  }

  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
  return true;
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "getPageSnapshot") {
    const text = safeText(document.body?.innerText || "").slice(0, 20000);
    const links = Array.from(document.querySelectorAll("a[href]"))
      .map((a) => a.href)
      .filter(Boolean)
      .slice(0, 300);

    const pdfLinks = links.filter((l) => /\.pdf($|\?)/i.test(l));
    sendResponse({
      title: document.title || "",
      url: location.href,
      text,
      forms: getFormSchema(),
      links,
      pdfLinks,
      selectedText: safeText(window.getSelection?.().toString() || "").slice(0, 6000)
    });
    return true;
  }

  if (msg?.type === "searchInPage") {
    const query = String(msg.query || "").toLowerCase().trim();
    const body = safeText(document.body?.innerText || "");
    if (!query) {
      sendResponse({ matches: [] });
      return true;
    }

    const lines = body.split(/(?<=[.!?])\s+/).slice(0, 1000);
    const matches = lines.filter((l) => l.toLowerCase().includes(query)).slice(0, 30);
    sendResponse({ matches });
    return true;
  }

  if (msg?.type === "collectPdfLinks") {
    const links = Array.from(document.querySelectorAll("a[href]"))
      .map((a) => a.href)
      .filter((l) => /\.pdf($|\?)/i.test(l));
    sendResponse({ links: Array.from(new Set(links)).slice(0, 100) });
    return true;
  }

  if (msg?.type === "applyFormData") {
    const mapping = msg.mapping && typeof msg.mapping === "object" ? msg.mapping : {};
    let filled = 0;
    const errors = [];

    for (const [key, value] of Object.entries(mapping)) {
      const field = findFieldByKey(key);
      if (!field) {
        errors.push(`Missing field for key: ${key}`);
        continue;
      }
      if (setFieldValue(field, value)) {
        filled += 1;
      }
    }

    sendResponse({ ok: true, filled, errors });
    return true;
  }

  return false;
});
