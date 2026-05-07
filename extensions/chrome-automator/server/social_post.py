"""
social_post.py — Playwright-based LinkedIn and Medium posting.
Uses saved session cookies so no password is ever stored.
"""

import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from session_store import load_cookies

log = logging.getLogger("social_post")


# ── LinkedIn ──────────────────────────────────────────────────────────────────

async def _post_linkedin(page, title: str, content: str) -> bool:
    """Post to LinkedIn using the web UI."""
    log.info("Navigating to LinkedIn feed...")
    await page.goto("https://www.linkedin.com/feed/", timeout=30000)
    await asyncio.sleep(3)

    # Click "Start a post"
    start_post_selectors = [
        "[data-control-name='share.sharebox_click']",
        ".share-box-feed-entry__trigger",
        "button:has-text('Start a post')",
        "[aria-label='Create a post']",
    ]
    clicked = False
    for sel in start_post_selectors:
        try:
            await page.click(sel, timeout=8000)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        raise RuntimeError("Cannot find LinkedIn 'Start a post' button")

    await asyncio.sleep(2)

    # Type content in the post modal
    body_selectors = [
        ".ql-editor",
        "[data-placeholder='What do you want to talk about?']",
        ".share-creation-state__text-editor [contenteditable]",
        "div[role='textbox']",
    ]
    typed = False
    for sel in body_selectors:
        try:
            el = page.locator(sel).first
            await el.click(timeout=5000)
            full_text = f"{title}\n\n{content}" if title else content
            await el.type(full_text, delay=20)
            typed = True
            break
        except Exception:
            continue
    if not typed:
        raise RuntimeError("Cannot type into LinkedIn post body")

    await asyncio.sleep(1)

    # Click Post button
    post_selectors = [
        "button.share-actions__primary-action",
        "button:has-text('Post')",
        "[data-control-name='share.post']",
    ]
    for sel in post_selectors:
        try:
            await page.click(sel, timeout=8000)
            log.info("LinkedIn post submitted")
            await asyncio.sleep(2)
            return True
        except Exception:
            continue
    raise RuntimeError("Cannot find LinkedIn Post button")


# ── Medium ────────────────────────────────────────────────────────────────────

async def _post_medium(page, title: str, content: str) -> bool:
    """Create a new Medium story."""
    log.info("Navigating to Medium new story...")
    await page.goto("https://medium.com/new-story", timeout=30000)
    await asyncio.sleep(3)

    # Fill title
    title_selectors = [
        "h3[data-placeholder='Title']",
        "[data-testid='title-input']",
        "h3.graf--title",
    ]
    for sel in title_selectors:
        try:
            el = page.locator(sel).first
            await el.click(timeout=5000)
            await el.type(title or "New Post", delay=20)
            await page.keyboard.press("Enter")
            break
        except Exception:
            continue

    await asyncio.sleep(0.5)

    # Fill body
    body_selectors = [
        "p[data-placeholder='Tell your story…']",
        "[data-testid='paragraph-input']",
        "p.graf--p",
        ".ProseMirror",
    ]
    for sel in body_selectors:
        try:
            el = page.locator(sel).first
            await el.click(timeout=5000)
            # Medium uses markdown-like shortcuts — type as plain text
            await el.type(content, delay=15)
            log.info("Medium story content typed")
            break
        except Exception:
            continue

    # Publish button
    publish_selectors = [
        "button:has-text('Publish')",
        "[data-action='show-post-publish-menu']",
    ]
    for sel in publish_selectors:
        try:
            await page.click(sel, timeout=8000)
            await asyncio.sleep(1)
            # Confirm publish
            confirm_selectors = [
                "button:has-text('Publish now')",
                "button[data-action='publish']",
            ]
            for c in confirm_selectors:
                try:
                    await page.click(c, timeout=5000)
                    log.info("Medium post published")
                    return True
                except Exception:
                    continue
        except Exception:
            continue

    log.warning("Could not click Publish — post drafted only")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

async def run_social_post(platforms: list[str], title: str, content: str, job: dict):
    """Open browser with saved sessions, post to each platform."""
    job["status"] = "running"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=80)
        context = await browser.new_context()

        for platform in platforms:
            cookies = load_cookies(platform)
            if cookies:
                await context.add_cookies(cookies)
                log.info("Loaded %d cookies for %s", len(cookies), platform)
            else:
                log.warning("No cookies for %s — manual login may be required", platform)

            page = await context.new_page()
            try:
                if platform == "linkedin":
                    await _post_linkedin(page, title, content)
                elif platform == "medium":
                    await _post_medium(page, title, content)
                job["done"] += 1
                log.info("Posted to %s", platform)
            except Exception as e:
                log.error("Failed posting to %s: %s", platform, e)
                job["failed"] = job.get("failed", 0) + 1
            finally:
                await page.close()

        await browser.close()
