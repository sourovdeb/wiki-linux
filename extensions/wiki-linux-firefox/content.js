/**
 * Content Script: Page analysis and data extraction
 */

function getPageSnapshot() {
  const snapshot = {
    title: document.title,
    url: window.location.href,
    text: document.body.innerText,
    html: document.documentElement.innerHTML,
    forms: [],
    links: [],
    pdfs: [],
    selectedText: window.getSelection().toString(),
    meta: {
      description: document.querySelector('meta[name="description"]')?.content || '',
      author: document.querySelector('meta[name="author"]')?.content || '',
      keywords: document.querySelector('meta[name="keywords"]')?.content || ''
    }
  };

  // Extract forms
  document.querySelectorAll('form').forEach(form => {
    const formData = {};
    form.querySelectorAll('input, textarea, select').forEach(field => {
      if (field.name) {
        formData[field.name] = {
          type: field.type || 'text',
          value: field.value,
          placeholder: field.placeholder || ''
        };
      }
    });
    snapshot.forms.push(formData);
  });

  // Extract links
  document.querySelectorAll('a').forEach(link => {
    snapshot.links.push({
      text: link.textContent.trim(),
      href: link.href,
      title: link.title
    });
  });

  // Extract PDF links
  document.querySelectorAll('a[href$=".pdf"], a[href*="pdf"]').forEach(link => {
    snapshot.pdfs.push({
      text: link.textContent.trim(),
      href: link.href
    });
  });

  return snapshot;
}

/**
 * Search page content for specific text
 */
function searchInPage(query) {
  const text = document.body.innerText;
  const regex = new RegExp(query, 'gi');
  const matches = [];
  let match;

  while ((match = regex.exec(text)) !== null) {
    const start = Math.max(0, match.index - 50);
    const end = Math.min(text.length, match.index + query.length + 50);
    matches.push(text.substring(start, end));
  }

  return matches.slice(0, 5); // Return top 5 matches
}

/**
 * Detect all PDF links on page
 */
function collectPdfLinks() {
  return Array.from(document.querySelectorAll('a')).filter(link => {
    const href = link.href.toLowerCase();
    return href.endsWith('.pdf') || href.includes('pdf') || link.textContent.toLowerCase().includes('pdf');
  }).map(link => ({
    text: link.textContent.trim(),
    href: link.href
  }));
}

/**
 * Apply form data to form fields
 */
function applyFormData(formIndex, fieldData) {
  const form = document.querySelectorAll('form')[formIndex];
  if (!form) return { success: false, error: 'Form not found' };

  try {
    Object.entries(fieldData).forEach(([fieldName, value]) => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (field) {
        field.value = value;
        field.dispatchEvent(new Event('change', { bubbles: true }));
        field.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    return { success: true, message: 'Form fields filled' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Listen for messages from sidebar/popup
 */
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Content script received:', request.action);

  switch (request.action) {
    case 'getPageSnapshot':
      sendResponse(getPageSnapshot());
      break;

    case 'searchInPage':
      sendResponse(searchInPage(request.query));
      break;

    case 'collectPdfLinks':
      sendResponse(collectPdfLinks());
      break;

    case 'applyFormData':
      sendResponse(applyFormData(request.formIndex, request.data));
      break;

    case 'getPageText':
      sendResponse({ text: document.body.innerText });
      break;

    case 'getPageHtml':
      sendResponse({ html: document.documentElement.outerHTML });
      break;

    default:
      sendResponse({ error: 'Unknown action' });
  }
});
