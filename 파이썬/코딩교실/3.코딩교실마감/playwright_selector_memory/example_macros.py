from __future__ import annotations

import argparse
import os
from typing import Any

from .macro_engine import run_macro


DEFAULT_URLS = {
    "google-form": "https://docs.google.com/forms/",
    "signup": "https://example.com/signup",
    "course-registration": "https://example.com/course-registration",
}


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def google_form_actions() -> list[dict[str, Any]]:
    return [
        {
            "type": "input",
            "key": "email_input",
            "value": _env("USER_EMAIL", "student@example.com"),
            "label": "Email",
            "placeholder": "Your answer",
            "aria_label": "Email",
            "aliases": ["email address"],
        },
        {
            "type": "input",
            "key": "name_input",
            "value": _env("USER_NAME", "Kim Coding"),
            "label": "Name",
            "placeholder": "Your answer",
            "aria_label": "Name",
            "aliases": ["full name"],
        },
        {
            "type": "input",
            "key": "feedback_input",
            "value": _env("FORM_FEEDBACK", "Selector memory test submission"),
            "label": "Feedback",
            "placeholder": "Your answer",
            "aria_label": "Feedback",
            "aliases": ["comments", "response"],
        },
        {
            "type": "click",
            "key": "submit_button",
            "text": "Submit",
            "role": "button",
            "wait_for_load_state": "networkidle",
        },
    ]


def signup_actions() -> list[dict[str, Any]]:
    return [
        {
            "type": "input",
            "key": "full_name_input",
            "value": _env("USER_NAME", "Kim Coding"),
            "label": "Full name",
            "placeholder": "Full name",
            "aria_label": "Full name",
            "aliases": ["name"],
        },
        {
            "type": "input",
            "key": "email_input",
            "value": _env("USER_EMAIL", "student@example.com"),
            "label": "Email",
            "placeholder": "Email",
            "aria_label": "Email",
            "aliases": ["email address"],
        },
        {
            "type": "input",
            "key": "password_input",
            "value": _env("USER_PASSWORD", "ChangeMe123!"),
            "label": "Password",
            "placeholder": "Password",
            "aria_label": "Password",
            "aliases": ["new password"],
        },
        {
            "type": "click",
            "key": "signup_button",
            "text": "Create account",
            "role": "button",
            "aliases": ["sign up", "register"],
            "wait_for_load_state": "networkidle",
        },
    ]


def course_registration_actions() -> list[dict[str, Any]]:
    course_title = _env("COURSE_TITLE", "Python Basics")
    return [
        {
            "type": "input",
            "key": "student_id_input",
            "value": _env("STUDENT_ID", "20260001"),
            "label": "Student ID",
            "placeholder": "Student ID",
            "aria_label": "Student ID",
        },
        {
            "type": "input",
            "key": "course_search_input",
            "value": course_title,
            "label": "Search courses",
            "placeholder": "Search courses",
            "aria_label": "Search courses",
            "aliases": ["course search"],
        },
        {
            "type": "click",
            "key": "search_button",
            "text": "Search",
            "role": "button",
            "wait_ms": 750,
        },
        {
            "type": "click",
            "key": "course_result_card",
            "text": course_title,
            "role": "link",
            "aliases": ["course result", "course card"],
            "wait_for_load_state": "domcontentloaded",
        },
        {
            "type": "click",
            "key": "register_button",
            "text": "Register",
            "role": "button",
            "aliases": ["enroll"],
            "wait_for_load_state": "networkidle",
        },
    ]


SCENARIOS = {
    "google-form": google_form_actions,
    "signup": signup_actions,
    "course-registration": course_registration_actions,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run selector-memory Playwright macro examples."
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        required=True,
        help="Example macro to run.",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Override the example URL for the selected scenario.",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Launch the browser in headed mode.",
    )
    parser.add_argument(
        "--memory-file",
        default=None,
        help="Optional custom selector memory JSON path.",
    )
    args = parser.parse_args()

    actions = SCENARIOS[args.scenario]()
    site_url = args.url or DEFAULT_URLS[args.scenario]
    results = run_macro(
        site_url,
        actions,
        headless=not args.show_browser,
        memory_path=args.memory_file,
    )

    for result in results:
        print(
            f"{result.key}: {result.source} -> {result.selector} "
            f"({result.strategy})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
