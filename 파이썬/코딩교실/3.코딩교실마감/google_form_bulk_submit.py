from pathlib import Path


MESSAGE = f"""
Direct Google Form POST mode is disabled.

Reason:
- This form uses branching sections.
- The HTTP shortcut can create invalid responses such as role='???'.

Use the owner-side Apps Script instead:
- {Path(__file__).with_name('google_form_owner_tools.gs')}
"""


def main() -> int:
    print(MESSAGE.strip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
