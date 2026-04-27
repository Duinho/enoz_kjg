from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from playwright.sync_api import Page, sync_playwright

from .dom_finder import DEFAULT_FIND_TIMEOUT_MS, find_best_match, resolve_selector, validate_locator
from .selector_memory import DEFAULT_MEMORY_PATH, JSONSelectorMemory, normalize_domain


@dataclass(frozen=True)
class ActionExecution:
    key: str
    action_type: str
    selector: str
    strategy: str
    source: str


def _perform_action(page: Page, action: Mapping[str, Any], selector: str) -> None:
    locator = resolve_selector(page, selector).first
    action_type = str(action.get("type", "")).lower()

    if action_type == "input":
        locator.fill(str(action.get("value", "")))
        if action.get("press_enter"):
            locator.press("Enter")
    elif action_type == "click":
        locator.click()
    else:
        raise ValueError(f"Unsupported action type: {action_type}")

    wait_ms = action.get("wait_ms")
    if wait_ms:
        page.wait_for_timeout(float(wait_ms))

    wait_text = action.get("wait_for_text")
    if wait_text:
        page.get_by_text(str(wait_text), exact=False).first.wait_for()

    load_state = action.get("wait_for_load_state")
    if load_state:
        page.wait_for_load_state(str(load_state))


def _resolve_action(
    page: Page,
    action: Mapping[str, Any],
    domain: str,
    selector_cache: dict[str, str],
    selector_store: JSONSelectorMemory,
    selector_timeout_ms: int,
) -> ActionExecution:
    key = str(action.get("key", "")).strip()
    if not key:
        raise ValueError("Every action must include a non-empty 'key'.")

    remembered_selector = selector_cache.get(key)
    if remembered_selector:
        locator = resolve_selector(page, remembered_selector)
        if validate_locator(locator, action, selector_timeout_ms):
            _perform_action(page, action, remembered_selector)
            selector_store.mark_selector_success(domain, key)
            return ActionExecution(
                key=key,
                action_type=str(action.get("type", "")),
                selector=remembered_selector,
                strategy="memory",
                source="memory",
            )
        selector_cache.pop(key, None)
        selector_store.delete_selector(domain, key)

    discovered = find_best_match(page, action, selector_timeout_ms)
    selector_store.save_selector(domain, key, discovered.selector, strategy=discovered.strategy)
    selector_cache[key] = discovered.selector
    _perform_action(page, action, discovered.selector)
    selector_store.mark_selector_success(domain, key)
    return ActionExecution(
        key=key,
        action_type=str(action.get("type", "")),
        selector=discovered.selector,
        strategy=discovered.strategy,
        source=discovered.source,
    )


def run_macro(
    site_url: str,
    actions: Sequence[Mapping[str, Any]],
    *,
    headless: bool = True,
    browser_name: str = "chromium",
    memory_path: str | Path | None = DEFAULT_MEMORY_PATH,
    selector_timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
    navigation_timeout_ms: int = 20_000,
    default_timeout_ms: int = 5_000,
    slow_mo_ms: int = 0,
) -> list[ActionExecution]:
    domain = normalize_domain(site_url)
    selector_store = JSONSelectorMemory(memory_path or DEFAULT_MEMORY_PATH)
    selector_cache = selector_store.load_selector(domain)

    with sync_playwright() as playwright:
        browser_factory = getattr(playwright, browser_name)
        browser = browser_factory.launch(headless=headless, slow_mo=slow_mo_ms)
        page = browser.new_page()
        page.set_default_timeout(default_timeout_ms)
        page.goto(site_url, wait_until="domcontentloaded", timeout=navigation_timeout_ms)

        try:
            results = [
                _resolve_action(
                    page,
                    action,
                    domain,
                    selector_cache,
                    selector_store,
                    selector_timeout_ms,
                )
                for action in actions
            ]
        finally:
            browser.close()

    return results
