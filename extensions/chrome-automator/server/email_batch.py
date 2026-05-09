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

from playwright.async_api import async_playwright

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


def _resolve_provider(row: dict, default_provider: str) -> str:
    candidate = str(row.get("provider", "")).strip().lower()
    if candidate in SELECTORS:
        return candidate
    fallback = str(default_provider or "").strip().lower()
    if fallback in SELECTORS:
        return fallback
    return "gmail"


def _resolve_model_name(ai_model: str) -> str:
    raw = str(ai_model or "").strip()
    if not raw or raw == "none":
        return "none"
    if raw.startswith("ollama-"):
        raw = raw.replace("ollama-", "", 1)
    aliases = {
        "mistral": "mistral:latest",
        "llama3": "llama3.2:3b",
        "llama3.2": "llama3.2:3b",
    }
    return aliases.get(raw, raw)


def _load_body_text(row: dict) -> str:
    body_text = str(row.get("body", "") or "")
    body_file = str(row.get("body_file", "") or "").strip()
    if not body_file:
        return body_text

    body_path = Path(body_file)
    if not body_path.is_absolute():
        body_path = TEMPLATES_DIR / body_path
    if body_path.exists():
        return body_path.read_text(encoding="utf-8")

    log.warning("Body file not found: %s", body_path)
    return body_text


def _resolve_attachment_paths(row: dict) -> list[Path]:
    attachments = [a.strip() for a in str(row.get("attachments", "") or "").split(";") if a.strip()]
    resolved: list[Path] = []
    for attachment in attachments:
        att_path = Path(attachment)
        if not att_path.is_absolute():
            att_path = TEMPLATES_DIR / att_path
        resolved.append(att_path)
    return resolved


async def _prepare_email_row(row: dict, provider: str, ai_model: str, dry_run: bool) -> dict:
    recipient = str(row.get("recipient", "")).strip()
    if not recipient:
        raise RuntimeError("Missing recipient in row")

    prepared = dict(row)
    prepared["provider"] = provider
    prepared["recipient"] = recipient
    prepared["subject"] = str(row.get("subject", "") or "")
    prepared["_body_text"] = _load_body_text(row)
    prepared["_attachment_paths"] = _resolve_attachment_paths(row)

    model = _resolve_model_name(ai_model)
    if model != "none" and prepared["_body_text"] and not dry_run:
        prepared["_body_text"] = await personalise_email_body(
            prepared["_body_text"],
            recipient=recipient,
            model=model,
        )

    return prepared


async def _send_single_email(page, row: dict, provider: str, ai_model: str, dry_run: bool) -> bool:
    sel = SELECTORS[provider]
    prepared = await _prepare_email_row(row, provider, ai_model, dry_run=dry_run)
    body_text = prepared["_body_text"]

    log.info("  → %s | %s%s", prepared["recipient"], prepared.get("subject", ""), " [DRY RUN]" if dry_run else "")

    if dry_run:
        return True

    # Click compose
    if not await _try_click(page, sel["compose"]):
        raise RuntimeError("Cannot find compose button")
    await asyncio.sleep(1.5)

    # Fill To
    if not await _try_fill(page, sel["to"], prepared["recipient"]):
        raise RuntimeError(f"Cannot fill To field for {prepared['recipient']}")
    await page.keyboard.press("Tab")

    # Fill Subject
    if prepared.get("subject"):
        if not await _try_fill(page, sel["subject"], prepared["subject"]):
            log.warning("Cannot fill Subject for %s", prepared["recipient"])

    # Fill Body
    if body_text:
        if not await _try_type_body(page, sel["body"], body_text):
            log.warning("Cannot fill body for %s", prepared["recipient"])

    # Attach files
    for att_path in prepared["_attachment_paths"]:
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
        raise RuntimeError(f"Cannot click Send for {prepared['recipient']}")

    await asyncio.sleep(2)
    return True


async def run_email_batch(
    rows: list[dict],
    provider: str,
    ai_model: str,
    dry_run: bool,
    job: dict,
):
    """Main entry: send emails (or validate inputs when dry_run is enabled)."""
    job["status"] = "running"
    if not rows:
        return

    # True dry-run: validate rows and resolve files without launching browser.
    if dry_run:
        for i, row in enumerate(rows):
            try:
                resolved_provider = _resolve_provider(row, provider)
                prepared = await _prepare_email_row(row, resolved_provider, ai_model, dry_run=True)
                missing_attachments = [str(p) for p in prepared["_attachment_paths"] if not p.exists()]
                if missing_attachments:
                    log.warning(
                        "Dry run row %d missing attachments: %s",
                        i + 1,
                        "; ".join(missing_attachments),
                    )
                job["done"] += 1
                log.info("[DRY %d/%d] Validated %s via %s", i + 1, len(rows), prepared["recipient"], resolved_provider)
            except Exception as e:
                log.error("Dry run failed row %d (%s): %s", i + 1, row.get("recipient", "?"), e)
                job["failed"] = job.get("failed", 0) + 1
        return

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()
        page = await context.new_page()
        loaded_cookie_platforms: set[str] = set()
        current_provider = ""

        for i, row in enumerate(rows):
            try:
                resolved_provider = _resolve_provider(row, provider)
                if resolved_provider != current_provider:
                    cookies = load_cookies(resolved_provider)
                    if cookies and resolved_provider not in loaded_cookie_platforms:
                        await context.add_cookies(cookies)
                        loaded_cookie_platforms.add(resolved_provider)
                        log.info("Loaded %d saved cookies for %s", len(cookies), resolved_provider)
                    elif not cookies:
                        log.warning("No saved cookies for %s — manual login required", resolved_provider)
                    await page.goto(PLATFORM_URL[resolved_provider], timeout=30000)
                    await asyncio.sleep(3)
                    current_provider = resolved_provider

                delay = int(row.get("delay", 3))
                await _send_single_email(page, row, resolved_provider, ai_model, dry_run=False)
                job["done"] += 1
                log.info("[%d/%d] Sent to %s via %s", i + 1, len(rows), row.get("recipient", "?"), resolved_provider)
                if i < len(rows) - 1:
                    await asyncio.sleep(delay)
            except Exception as e:
                log.error("Failed row %d (%s): %s", i + 1, row.get("recipient", "?"), e)
                job["failed"] = job.get("failed", 0) + 1

        await browser.close()
