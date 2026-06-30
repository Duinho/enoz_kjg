from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
SCRIPT_NAME = "추가인원 가입 수강신청.py"
script_path = HERE / SCRIPT_NAME

if not script_path.exists():
    raise FileNotFoundError(f"Missing main signup script: {script_path}")

runpy.run_path(str(script_path), run_name="__main__")
