from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from playwright.sync_api import Locator, Page
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


DEFAULT_FIND_TIMEOUT_MS = 1_500
_ID_TOKEN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_SPLIT_RE = re.compile(r"[_\-\s]+")
_IGNORED_TERMS = {
    "button",
    "click",
    "field",
    "form",
    "input",
    "link",
    "page",
    "submit",
    "textbox",
}
_DATA_ATTRIBUTE_PRIORITY = (
    "data-testid",
    "data-test-id",
    "data-test",
    "data-qa",
    "data-cy",
    "data-id",
    "data-name",
)


@dataclass(frozen=True)
class ResolvedElement:
    locator: Locator
    selector: str
    strategy: str
    source: str


def _ordered_unique(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value:
            continue
        cleaned = " ".join(str(value).split()).strip()
        if not cleaned:
            continue
        normalized = cleaned.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(cleaned)
    return ordered


def _candidate_terms(action: Mapping[str, Any]) -> list[str]:
    values: list[str | None] = [
        action.get("text"),
        action.get("label"),
        action.get("aria_label"),
        action.get("placeholder"),
        action.get("name"),
    ]

    aliases = action.get("aliases", [])
    if isinstance(aliases, list):
        values.extend(str(value) for value in aliases)

    key = str(action.get("key", ""))
    if key:
        key_phrase = key.replace("_", " ").replace("-", " ")
        values.append(key_phrase)
        for token in _SPLIT_RE.split(key_phrase):
            lowered = token.strip().lower()
            if lowered and lowered not in _IGNORED_TERMS:
                values.append(token)

    return _ordered_unique(values)


def _quote_css_attribute(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _css_id_selector(value: str) -> str:
    if _ID_TOKEN_RE.match(value):
        return f"#{value}"
    return f'[id="{_quote_css_attribute(value)}"]'


def _css_attribute_selector(name: str, value: str) -> str:
    return f'[{name}="{_quote_css_attribute(value)}"]'


def resolve_selector(page: Page, selector: str) -> Locator:
    raw = selector.strip()

    if raw.startswith("css="):
        return page.locator(raw[4:])
    if raw.startswith("aria="):
        value = raw[5:].strip()
        return page.locator(f'[aria-label="{_quote_css_attribute(value)}"]')
    if raw.startswith("placeholder="):
        return page.get_by_placeholder(raw[12:].strip(), exact=True)
    if raw.startswith("text="):
        return page.get_by_text(raw[5:].strip(), exact=True)
    if raw.startswith("xpath="):
        return page.locator(f"xpath={raw[6:]}")
    return page.locator(raw)


def _is_action_compatible(locator: Locator, action: Mapping[str, Any]) -> bool:
    meta = locator.evaluate(
        """(element) => {
            const role = (element.getAttribute("role") || "").toLowerCase();
            const tag = element.tagName.toLowerCase();
            const contentEditable = element.isContentEditable;
            const disabled =
                Boolean(element.disabled) ||
                element.getAttribute("aria-disabled") === "true";
            return { role, tag, contentEditable, disabled };
        }"""
    )

    action_type = str(action.get("type", "")).lower()
    if action_type == "input":
        return (
            meta["tag"] in {"input", "textarea", "select"}
            or meta["contentEditable"]
            or meta["role"] in {"textbox", "combobox", "spinbutton", "searchbox"}
        )
    if action_type == "click":
        return not meta["disabled"]
    return True


def validate_locator(
    locator: Locator,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> bool:
    candidate = locator.first
    try:
        candidate.wait_for(state="visible", timeout=timeout_ms)
        return _is_action_compatible(candidate, action)
    except (PlaywrightTimeoutError, PlaywrightError):
        return False


def _promote_locator(
    page: Page,
    locator: Locator,
    source: str,
    action: Mapping[str, Any],
    timeout_ms: int,
) -> ResolvedElement:
    candidate = locator.first
    promoted = candidate.evaluate(
        """(element) => {
            const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();
            const cssValue = (value) =>
                String(value).replace(/\\\\/g, "\\\\\\\\").replace(/"/g, '\\"');
            const cssEscape = (value) => {
                if (window.CSS && typeof window.CSS.escape === "function") {
                    return window.CSS.escape(value);
                }
                return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\\\$&");
            };
            const uniqueCss = (selector) => {
                try {
                    return document.querySelectorAll(selector).length === 1;
                } catch (error) {
                    return false;
                }
            };
            const uniqueText = (text) => {
                if (!text) {
                    return false;
                }
                const target = normalize(text);
                const matches = Array.from(document.querySelectorAll("*")).filter((node) => {
                    const rect = node.getBoundingClientRect();
                    const style = window.getComputedStyle(node);
                    if (style.display === "none" || style.visibility === "hidden") {
                        return false;
                    }
                    if (rect.width <= 0 || rect.height <= 0) {
                        return false;
                    }
                    return normalize(node.innerText || node.textContent || "") === target;
                });
                return matches.length === 1;
            };
            const textContent = normalize(
                element.innerText || element.textContent || element.value || ""
            );
            const dataAttributes = Array.from(element.attributes)
                .filter((attribute) => attribute.name.startsWith("data-") && normalize(attribute.value))
                .sort((left, right) => {
                    const preferred = [
                        "data-testid",
                        "data-test-id",
                        "data-test",
                        "data-qa",
                        "data-cy",
                        "data-id",
                        "data-name",
                    ];
                    const leftIndex = preferred.indexOf(left.name);
                    const rightIndex = preferred.indexOf(right.name);
                    return (leftIndex === -1 ? preferred.length : leftIndex)
                        - (rightIndex === -1 ? preferred.length : rightIndex);
                });

            if (element.id) {
                const idSelector = `#${cssEscape(element.id)}`;
                if (uniqueCss(idSelector)) {
                    return { selector: `css=${idSelector}`, strategy: "css_id" };
                }
                const attrSelector = `[id="${cssValue(element.id)}"]`;
                if (uniqueCss(attrSelector)) {
                    return { selector: `css=${attrSelector}`, strategy: "css_id" };
                }
            }

            for (const attribute of dataAttributes) {
                const selector = `[${attribute.name}="${cssValue(attribute.value)}"]`;
                if (uniqueCss(selector)) {
                    return { selector: `css=${selector}`, strategy: "data_attribute" };
                }
            }

            const ariaLabel = normalize(element.getAttribute("aria-label"));
            const ariaSelector = `[aria-label="${cssValue(ariaLabel)}"]`;
            if (ariaLabel && uniqueCss(ariaSelector)) {
                return { selector: `aria=${ariaLabel}`, strategy: "aria_label" };
            }

            const placeholder = normalize(element.getAttribute("placeholder"));
            const placeholderSelector = `[placeholder="${cssValue(placeholder)}"]`;
            if (placeholder && uniqueCss(placeholderSelector)) {
                return { selector: `placeholder=${placeholder}`, strategy: "placeholder" };
            }

            if (textContent && textContent.length <= 80 && uniqueText(textContent)) {
                return { selector: `text=${textContent}`, strategy: "text" };
            }

            const xpath = (() => {
                const parts = [];
                let current = element;
                while (current && current.nodeType === Node.ELEMENT_NODE) {
                    let index = 1;
                    let sibling = current.previousElementSibling;
                    while (sibling) {
                        if (sibling.tagName === current.tagName) {
                            index += 1;
                        }
                        sibling = sibling.previousElementSibling;
                    }
                    parts.unshift(`${current.tagName.toLowerCase()}[${index}]`);
                    current = current.parentElement;
                }
                return `/${parts.join("/")}`;
            })();

            return { selector: `xpath=${xpath}`, strategy: "xpath" };
        }"""
    )

    selector = str(promoted["selector"])
    strategy = str(promoted["strategy"])
    promoted_locator = resolve_selector(page, selector)
    if validate_locator(promoted_locator, action, timeout_ms):
        return ResolvedElement(promoted_locator.first, selector, strategy, source)
    return ResolvedElement(candidate, selector, strategy, source)


def search_by_placeholder(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> ResolvedElement | None:
    hints = _ordered_unique([action.get("placeholder")] + _candidate_terms(action))
    for hint in hints:
        locator = page.get_by_placeholder(hint, exact=False)
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "placeholder-search", action, timeout_ms)
    return None


def search_by_aria_label(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> ResolvedElement | None:
    hints = _ordered_unique(
        [action.get("aria_label"), action.get("label")] + _candidate_terms(action)
    )
    for hint in hints:
        locator = page.locator(f'[aria-label*="{_quote_css_attribute(hint)}" i]')
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "aria-label-search", action, timeout_ms)
    return None


def search_by_role(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> ResolvedElement | None:
    action_type = str(action.get("type", "")).lower()
    explicit_role = action.get("role")
    roles = [str(explicit_role)] if explicit_role else []

    if not roles:
        if action_type == "input":
            roles = ["textbox", "combobox", "spinbutton", "searchbox"]
        elif action_type == "click":
            roles = ["button", "link", "tab", "option"]

    names = _candidate_terms(action) or [None]
    for role in roles:
        for name in names:
            locator = (
                page.get_by_role(role, name=re.compile(re.escape(name), re.IGNORECASE))
                if name
                else page.get_by_role(role)
            )
            if validate_locator(locator, action, timeout_ms):
                return _promote_locator(page, locator, "role-search", action, timeout_ms)
    return None


def search_by_text(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> ResolvedElement | None:
    hints = _ordered_unique([action.get("text"), action.get("label")] + _candidate_terms(action))
    for hint in hints:
        locator = page.get_by_text(hint, exact=False)
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "text-search", action, timeout_ms)
    return None


def _search_by_label(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int,
) -> ResolvedElement | None:
    if str(action.get("type", "")).lower() != "input":
        return None

    hints = _ordered_unique([action.get("label")] + _candidate_terms(action))
    for hint in hints:
        locator = page.get_by_label(hint, exact=False)
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "label-search", action, timeout_ms)
    return None


def _search_by_explicit_selector(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int,
) -> ResolvedElement | None:
    explicit_selector = action.get("selector")
    if explicit_selector:
        locator = resolve_selector(page, str(explicit_selector))
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "explicit-selector", action, timeout_ms)

    explicit_id = action.get("id")
    if explicit_id:
        locator = resolve_selector(page, f"css={_css_id_selector(str(explicit_id))}")
        if validate_locator(locator, action, timeout_ms):
            return _promote_locator(page, locator, "id-search", action, timeout_ms)

    data_attrs = action.get("data_attrs", {})
    if isinstance(data_attrs, dict):
        for name, value in data_attrs.items():
            locator = resolve_selector(
                page,
                f"css={_css_attribute_selector(str(name), str(value))}",
            )
            if validate_locator(locator, action, timeout_ms):
                return _promote_locator(page, locator, "data-attribute-search", action, timeout_ms)

    return None


def _search_by_data_attributes(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int,
) -> ResolvedElement | None:
    for term in _candidate_terms(action):
        for attribute in _DATA_ATTRIBUTE_PRIORITY:
            locator = page.locator(f'[{attribute}*="{_quote_css_attribute(term)}" i]')
            if validate_locator(locator, action, timeout_ms):
                return _promote_locator(page, locator, "data-attribute-search", action, timeout_ms)
    return None


def _search_dom_fallback(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int,
) -> ResolvedElement | None:
    payload = {
        "type": str(action.get("type", "")),
        "key": str(action.get("key", "")),
        "role": str(action.get("role", "")),
        "text": str(action.get("text", "")),
        "label": str(action.get("label", "")),
        "placeholder": str(action.get("placeholder", "")),
        "ariaLabel": str(action.get("aria_label", "")),
        "terms": _candidate_terms(action),
    }

    result = page.evaluate(
        """(payload) => {
            const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();
            const lower = (value) => normalize(value).toLowerCase();
            const cssValue = (value) =>
                String(value).replace(/\\\\/g, "\\\\\\\\").replace(/"/g, '\\"');
            const cssEscape = (value) => {
                if (window.CSS && typeof window.CSS.escape === "function") {
                    return window.CSS.escape(value);
                }
                return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\\\$&");
            };
            const isVisible = (element) => {
                const style = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return (
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    rect.width > 0 &&
                    rect.height > 0
                );
            };
            const labelText = (element) => {
                const values = [];
                if (element.id) {
                    for (const label of document.querySelectorAll(`label[for="${cssValue(element.id)}"]`)) {
                        values.push(normalize(label.innerText || label.textContent || ""));
                    }
                }
                const wrapper = element.closest("label");
                if (wrapper) {
                    values.push(normalize(wrapper.innerText || wrapper.textContent || ""));
                }
                return normalize(values.join(" "));
            };
            const textContent = (element) =>
                normalize(element.innerText || element.textContent || element.value || "");
            const roleOf = (element) => {
                const explicit = lower(element.getAttribute("role"));
                if (explicit) {
                    return explicit;
                }
                const tag = lower(element.tagName);
                const type = lower(element.getAttribute("type"));
                if (tag === "button") {
                    return "button";
                }
                if (tag === "a") {
                    return "link";
                }
                if (tag === "input" && ["button", "submit"].includes(type)) {
                    return "button";
                }
                if (tag === "input" || tag === "textarea") {
                    return "textbox";
                }
                return "";
            };
            const uniqueCss = (selector) => {
                try {
                    return document.querySelectorAll(selector).length === 1;
                } catch (error) {
                    return false;
                }
            };
            const uniqueText = (text) => {
                if (!text) {
                    return false;
                }
                const target = normalize(text);
                const matches = Array.from(document.querySelectorAll("*")).filter((node) => {
                    if (!isVisible(node)) {
                        return false;
                    }
                    return textContent(node) === target;
                });
                return matches.length === 1;
            };
            const preferredDataAttributes = [
                "data-testid",
                "data-test-id",
                "data-test",
                "data-qa",
                "data-cy",
                "data-id",
                "data-name",
            ];
            const selectorFor = (element) => {
                if (element.id) {
                    const idSelector = `#${cssEscape(element.id)}`;
                    if (uniqueCss(idSelector)) {
                        return { selector: `css=${idSelector}`, strategy: "css_id" };
                    }
                    const attrSelector = `[id="${cssValue(element.id)}"]`;
                    if (uniqueCss(attrSelector)) {
                        return { selector: `css=${attrSelector}`, strategy: "css_id" };
                    }
                }

                const dataAttributes = Array.from(element.attributes)
                    .filter((attribute) => attribute.name.startsWith("data-") && normalize(attribute.value))
                    .sort((left, right) => {
                        const leftIndex = preferredDataAttributes.indexOf(left.name);
                        const rightIndex = preferredDataAttributes.indexOf(right.name);
                        return (leftIndex === -1 ? preferredDataAttributes.length : leftIndex)
                            - (rightIndex === -1 ? preferredDataAttributes.length : rightIndex);
                    });

                for (const attribute of dataAttributes) {
                    const selector = `[${attribute.name}="${cssValue(attribute.value)}"]`;
                    if (uniqueCss(selector)) {
                        return { selector: `css=${selector}`, strategy: "data_attribute" };
                    }
                }

                const ariaLabel = normalize(element.getAttribute("aria-label"));
                const ariaSelector = `[aria-label="${cssValue(ariaLabel)}"]`;
                if (ariaLabel && uniqueCss(ariaSelector)) {
                    return { selector: `aria=${ariaLabel}`, strategy: "aria_label" };
                }

                const placeholder = normalize(element.getAttribute("placeholder"));
                const placeholderSelector = `[placeholder="${cssValue(placeholder)}"]`;
                if (placeholder && uniqueCss(placeholderSelector)) {
                    return { selector: `placeholder=${placeholder}`, strategy: "placeholder" };
                }

                const text = textContent(element);
                if (text && text.length <= 80 && uniqueText(text)) {
                    return { selector: `text=${text}`, strategy: "text" };
                }

                const parts = [];
                let current = element;
                while (current && current.nodeType === Node.ELEMENT_NODE) {
                    let index = 1;
                    let sibling = current.previousElementSibling;
                    while (sibling) {
                        if (sibling.tagName === current.tagName) {
                            index += 1;
                        }
                        sibling = sibling.previousElementSibling;
                    }
                    parts.unshift(`${current.tagName.toLowerCase()}[${index}]`);
                    current = current.parentElement;
                }
                return { selector: `xpath=/${parts.join("/")}`, strategy: "xpath" };
            };
            const terms = payload.terms
                .map((term) => lower(term))
                .filter(Boolean);
            const desiredRole = lower(payload.role);
            const actionType = lower(payload.type);

            const selectors =
                actionType === "input"
                    ? [
                          "input",
                          "textarea",
                          "select",
                          "[contenteditable='true']",
                          "[role='textbox']",
                          "[role='combobox']",
                          "[role='spinbutton']",
                          "[role='searchbox']",
                      ]
                    : [
                          "button",
                          "a",
                          "[role='button']",
                          "[role='link']",
                          "[role='tab']",
                          "[role='option']",
                          "input[type='button']",
                          "input[type='submit']",
                      ];

            const candidates = Array.from(document.querySelectorAll(selectors.join(",")))
                .filter((element) => isVisible(element));
            const scored = candidates.map((element) => {
                const attributes = [
                    lower(element.id),
                    lower(element.getAttribute("name")),
                    lower(element.getAttribute("placeholder")),
                    lower(element.getAttribute("aria-label")),
                    lower(labelText(element)),
                    lower(textContent(element)),
                    lower(
                        Array.from(element.attributes)
                            .filter((attribute) => attribute.name.startsWith("data-"))
                            .map((attribute) => `${attribute.name}:${attribute.value}`)
                            .join(" ")
                    ),
                ];
                let score = 0;
                if (actionType === "input") {
                    score += 25;
                } else if (["button", "link", "tab", "option"].includes(roleOf(element))) {
                    score += 20;
                }
                if (desiredRole && roleOf(element) === desiredRole) {
                    score += 20;
                }
                for (const term of terms) {
                    for (const field of attributes) {
                        if (!field) {
                            continue;
                        }
                        if (field === term) {
                            score += 35;
                        } else if (field.includes(term)) {
                            score += 14;
                        }
                    }
                }
                return { element, score };
            });

            scored.sort((left, right) => right.score - left.score);
            if (!scored.length || scored[0].score < 30) {
                return null;
            }
            return selectorFor(scored[0].element);
        }""",
        payload,
    )

    if not result:
        return None

    locator = resolve_selector(page, str(result["selector"]))
    if validate_locator(locator, action, timeout_ms):
        return ResolvedElement(
            locator.first,
            str(result["selector"]),
            str(result["strategy"]),
            "dom-scan",
        )
    return None


def find_best_match(
    page: Page,
    action: Mapping[str, Any],
    timeout_ms: int = DEFAULT_FIND_TIMEOUT_MS,
) -> ResolvedElement:
    searchers = (
        _search_by_explicit_selector,
        _search_by_data_attributes,
        _search_by_label,
        search_by_aria_label,
        search_by_placeholder,
        search_by_role,
        search_by_text,
        _search_dom_fallback,
    )

    for searcher in searchers:
        match = searcher(page, action, timeout_ms)
        if match is not None:
            return match

    raise LookupError(f"Unable to find a selector for action key={action.get('key')!r}.")
