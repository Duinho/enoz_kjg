from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from urllib.parse import urlsplit


DEFAULT_MEMORY_PATH = Path(__file__).resolve().with_name("selector_memory_store.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_domain(domain_or_url: str) -> str:
    candidate = domain_or_url.strip()
    if not candidate:
        raise ValueError("Domain or URL cannot be empty.")

    parsed = urlsplit(candidate if "://" in candidate else f"https://{candidate}")
    domain = parsed.netloc or parsed.path
    return domain.split("/")[0].lower()


@dataclass(frozen=True)
class SelectorRecord:
    selector: str
    strategy: str | None = None
    success_count: int = 0
    last_verified_at: str | None = None


class JSONSelectorMemory:
    def __init__(self, path: str | Path = DEFAULT_MEMORY_PATH) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._cache: dict[str, Any] | None = None

    def _empty_payload(self) -> dict[str, Any]:
        return {
            "version": 1,
            "updated_at": _utc_now(),
            "domains": {},
        }

    def _read_disk(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._empty_payload()

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self._empty_payload()

        if not isinstance(payload, dict):
            return self._empty_payload()

        payload.setdefault("version", 1)
        payload.setdefault("updated_at", _utc_now())
        payload.setdefault("domains", {})
        return payload

    def _ensure_loaded(self) -> dict[str, Any]:
        if self._cache is None:
            self._cache = self._read_disk()
        return self._cache

    def _write_disk(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = _utc_now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._cache = payload

    def load_selector(self, domain: str) -> dict[str, str]:
        normalized = normalize_domain(domain)
        with self._lock:
            payload = self._ensure_loaded()
            raw_domain = payload["domains"].get(normalized, {})
            return {
                key: value["selector"]
                for key, value in raw_domain.items()
                if isinstance(value, dict) and value.get("selector")
            }

    def load_records(self, domain: str) -> dict[str, SelectorRecord]:
        normalized = normalize_domain(domain)
        with self._lock:
            payload = self._ensure_loaded()
            raw_domain = payload["domains"].get(normalized, {})
            records: dict[str, SelectorRecord] = {}
            for key, value in raw_domain.items():
                if not isinstance(value, dict) or not value.get("selector"):
                    continue
                records[key] = SelectorRecord(
                    selector=str(value["selector"]),
                    strategy=value.get("strategy"),
                    success_count=int(value.get("success_count", 0)),
                    last_verified_at=value.get("last_verified_at"),
                )
            return records

    def save_selector(
        self,
        domain: str,
        key: str,
        selector: str,
        strategy: str | None = None,
    ) -> None:
        normalized = normalize_domain(domain)
        with self._lock:
            payload = self._ensure_loaded()
            domain_map = payload["domains"].setdefault(normalized, {})
            previous = domain_map.get(key, {}) if isinstance(domain_map.get(key), dict) else {}
            domain_map[key] = {
                "selector": selector,
                "strategy": strategy or previous.get("strategy"),
                "success_count": int(previous.get("success_count", 0)),
                "last_verified_at": previous.get("last_verified_at"),
                "updated_at": _utc_now(),
            }
            self._write_disk(payload)

    def mark_selector_success(self, domain: str, key: str) -> None:
        normalized = normalize_domain(domain)
        with self._lock:
            payload = self._ensure_loaded()
            domain_map = payload["domains"].setdefault(normalized, {})
            if key not in domain_map or not isinstance(domain_map[key], dict):
                return

            domain_map[key]["success_count"] = int(domain_map[key].get("success_count", 0)) + 1
            domain_map[key]["last_verified_at"] = _utc_now()
            self._write_disk(payload)

    def delete_selector(self, domain: str, key: str) -> None:
        normalized = normalize_domain(domain)
        with self._lock:
            payload = self._ensure_loaded()
            domain_map = payload["domains"].get(normalized, {})
            if key in domain_map:
                del domain_map[key]
                self._write_disk(payload)


_DEFAULT_STORE = JSONSelectorMemory()


def get_selector_store(path: str | Path | None = None) -> JSONSelectorMemory:
    return _DEFAULT_STORE if path is None else JSONSelectorMemory(path)


def load_selector(domain: str) -> dict[str, str]:
    return _DEFAULT_STORE.load_selector(domain)


def save_selector(domain: str, key: str, selector: str) -> None:
    _DEFAULT_STORE.save_selector(domain, key, selector)
