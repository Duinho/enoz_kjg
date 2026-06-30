import runpy
import sys
import traceback
from pathlib import Path


def main():
    candidates = [
        path
        for path in Path.cwd().glob("*.py")
        if path.name not in {"run_lms_assignment.py"} and 6000 <= path.stat().st_size <= 9000
    ]
    if not candidates:
        raise FileNotFoundError("LMS assignment script not found")
    script = max(candidates, key=lambda path: path.stat().st_size)
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(1)
