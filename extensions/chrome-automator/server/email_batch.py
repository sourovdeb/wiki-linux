"""
email_batch.py — Playwright-based batch email sender.
Builds on patterns from github.com/sourovdeb/email_automation.

Supports:
- Gmail (web UI)
- ProtonMail (web UI)
- Different recipient/subject/body/attachments per row
- Ollama SLM body personalisation
- Dry-run mode
- Per-email delay to avoid spam detection
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from session_store import load_cookies
from llm_helper import personalise_email_body

log = logging.getLogger("email_batch")

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
RECORDINGS_DIR = Path(__file__).parent.parent / "recordings"


# ── Platform-specific selectors (learned from recordings + email_automation repo) ──

GMAIL_SELECTORS = {
    "compose":   ["[data-tooltip='Compose']", ".T-I.T-I-KE.L3", "[gh='cm']"],
    "to":        ["[name='to']", "input[aria-label='To']"],
    "subject":   ["[name='subjectbox']", "input[name='subject']"],
    "body":      ["[aria-label='Message Body']", ".Am.Al.editable"],
    "attach":    ["[data-tooltip='Attach files']", "input[type='file']"],
    "send":      ["[data-tooltip='Send']", "[aria-label='Send']"],
}

PROTON_SELECTORS = {
    "compose":   ["[data-testid='compose-button']", ".compose-button", "button:has-text('New message')"],
    "to":        ["[data-testid='composer:to']", "input[placeholder*='recipient']"],
    "subject":   ["[data-testid='composer:subject']", "input[placeholder*='Subject']"],
    "body":      [".composer-content [contenteditable]", "[data-testid='rooster-editor']"],
    "attach":    ["[data-testid='composer:attachment-button']", "input[type='file']"],
    "send":      ["[data-testid='composer:send-button']", "button:has-text('Send')"],
}

SELECTORS = {"gmail": GMAIL_SELECTORS, "proton": PROTON_SELECTORS}
PLATFORM_URL = {"gmail": "https://mail.google.com", "proton": "https://mail.proton.me"}


async def _try_click(page, selectors: list[str]) -> bool:
    for sel in selectors:
        try:
            await page.click(sel, timeout=5000)
            return True
        except Exception:
            continue
    return False


async def _try_fill(page, selectors: list[str], value: str) -> bool:
    for sel in selectors:
        try:
            await page.fill(sel, value, timeout=5000)
            return True
        except Exception:
            continue
    return False


async def _try_type_body(page, selectors: list[str], text: str) -> bool:
    """Click into body and type (for contenteditable divs)."""
    for sel in selectors:
        try:
            el = page.locator(sel).first
            await el.click(timeout=5000)
            await el.type(text, delay=30)
            return True
        except Exception:
            continue
    return False


async def _send_single_email(page, row: dict, provider: str, ai_model: str, dry_run: bool) -> bool:
    sel = SELECTORS[provider]
    body_text = row.get("body", "")

    # Load body from file if body_file specified
    body_file = row.get("body_file", "")
    if body_file:
        body_path = Path(body_file) if Path(body_file).is_absolute() else TEMPLATES_DIR / body_file
        if body_path.exists():
            body_text = body_path.read_text(encoding="utf-8")
        else:
            log.warning("Body file not found: %s", body_path)

    # Personalise with Ollama if requested
    if ai_model != "none" and body_text:
        model = ai_model.replace("ollama-", "")
        body_text = await personalise_email_body(
            body_text,
            recipient=row.get("recipient", ""),
            model=model,
        )

    log.info("  → %s | %s%s", row["recipient"], row.get("subject", ""), " [DRY RUN]" if dry_run else "")

    if dry_run:
        return True

    # Click compose
    if not await _try_click(page, sel["compose"]):
        raise RuntimeError("Cannot find compose button")
    await asyncio.sleep(1.5)

    # Fill To
    if not await _try_fill(page, sel["to"], row["recipient"]):
        raise RuntimeError(f"Cannot fill To field for {row['recipient']}")
    await page.keyboard.press("Tab")

    # Fill Subject
    if row.get("subject"):
        if not await _try_fill(page, sel["subject"], row["subject"]):
            log.warning("Cannot fill Subject for %s", row["recipient"])

    # Fill Body
    if body_text:
        if not await _try_type_body(page, sel["body"], body_text):
            log.warning("Cannot fill body for %s", row["recipient"])

    # Attach files
    attachments = [a.strip() for a in row.get("attachments", "").split(";") if a.strip()]
    for attachment in attachments:
        att_path = Path(attachment) if Path(attachment).is_absolute() else Path(attachment)
        if not att_path.exists():
            log.warning("Attachment not found: %s", att_path)
            continue
        try:
            async with page.expect_file_chooser() as fc_info:
                await _try_click(page, sel["attach"])
            file_chooser = await fc_info.value
            await file_chooser.set_files(str(att_path))
            await asyncio.sleep(1)
        except Exception as e:
            log.warning("Attachment failed for %s: %s", att_path, e)

    # Send
    await asyncio.sleep(0.5)
    if not await _try_click(page, sel["send"]):
        raise RuntimeError(f"Cannot click Send for {row['recipient']}")

    await asyncio.sleep(2)
    return True


async def run_email_batch(
    rows: list[dict],
    provider: str,
    ai_model: str,
    dry_run: bool,
    job: dict,
):
    """Main entry: open browser with saved session, send all emails."""
    job["status"] = "running"
    platform_url = PLATFORM_URL.get(provider, "https://mail.google.com")
    cookies = load_cookies(provider)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()

        if cookies:
            await context.add_cookies(cookies)
            log.info("Loaded %d saved cookies for %s", len(cookies), provider)
        else:
            log.warning("No saved cookies for %s — manual login required", provider)

        page = await context.new_page()
        await page.goto(platform_url, timeout=30000)
        await asyncio.sleep(3)

        for i, row in enumerate(rows):
            try:
                delay = int(row.get("delay", 3))
                await _send_single_email(page, row, provider, ai_model, dry_run)
                job["done"] += 1
                log.info("[%d/%d] Sent to %s", i + 1, len(rows), row["recipient"])
                if i < len(rows) - 1:
                    await asyncio.sleep(delay)
            except Exception as e:
                log.error("Failed row %d (%s): %s", i + 1, row.get("recipient", "?"), e)
                job["failed"] = job.get("failed", 0) + 1

        await browser.close()
