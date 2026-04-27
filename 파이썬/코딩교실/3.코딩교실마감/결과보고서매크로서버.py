"""
업무자동화 도구.py 기능을 서버(Flask)용으로 노출하는 스크립트.
"""
import os
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
import tunnel_manager  # cloudflared 터널 자동 실행용

# ---- 자동화 모듈 import ----
try:
    import 이름O처리
except ImportError:
    이름O처리 = None

try:
    import 구글폼응답_대상
except ImportError:
    구글폼응답_대상 = None

try:
    import 구글폼응답_폼
except ImportError:
    구글폼응답_폼 = None

try:
    import 학교알리미
except ImportError:
    학교알리미 = None


# ------------------------------------------------------------
# 경로 설정
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "엑셀양식")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

TEMPLATE_FILES = {
    "noc": "이름 O 처리 양식.xlsx",
    "target": "구글폼응답(대상) 양식.xlsx",
    "form": "구글폼응답(폼) 양식.xlsx",
    "school": "학교알리미 양식.xlsx",
}


# ------------------------------------------------------------
# Flask 기본 설정
# ------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "enozfuture-secret-key"  # flash 메시지용


# ------------------------------------------------------------
# 메인 페이지 템플릿
# ------------------------------------------------------------
TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>업무자동화 도구 (서버)</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: #0f0f10;
    color: #f2f2f2;
  }
  .appbar {
    padding: 14px 20px;
    background: #16171a;
    border-bottom: 1px solid #25262b;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .title {
    font-size: 1.2rem;
    font-weight: 700;
  }
  .subtitle {
    font-size: 0.85rem;
    color: #aaa;
  }
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 16px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
  }
  .card {
    background: #17181d;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.55);
    border: 1px solid #202128;
  }
  .card h2 {
    margin: 0 0 6px;
    font-size: 1.05rem;
  }
  .card p.desc {
    margin: 0 0 12px;
    font-size: 0.84rem;
    color: #c2c2c2;
    line-height: 1.45;
  }
  label {
    display: block;
    font-size: 0.8rem;
    margin-top: 6px;
    margin-bottom: 2px;
    color: #cfd0d5;
  }
  input[type=text] {
    width: 100%;
    padding: 7px 10px;
    border-radius: 10px;
    border: 1px solid #2a2b31;
    background: #0e0f12;
    color: #f2f2f2;
    font-size: 0.9rem;
  }
  .btn-row {
    margin-top: 12px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  button {
    border: none;
    border-radius: 999px;
    padding: 9px 14px;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform .08s ease, box-shadow .08s ease, background .1s ease;
  }
  button:active {
    transform: translateY(1px) scale(.98);
    box-shadow: none;
  }
  .btn-primary {
    background: linear-gradient(135deg,#ff7a3d,#ffb347);
    color: #1a0d00;
    box-shadow: 0 6px 14px rgba(255,122,61,0.4);
  }
  .btn-secondary {
    background: #25262d;
    color: #f2f2f2;
    box-shadow: 0 6px 14px rgba(0,0,0,0.45);
    text-decoration: none;
    display: inline-block;
  }
  .flash-container {
    max-width: 1100px;
    margin: 10px auto 0;
    padding: 0 16px;
  }
  .flash {
    padding: 9px 12px;
    border-radius: 10px;
    font-size: 0.85rem;
    margin-bottom: 6px;
  }
  .flash-success {
    background: #1c3620;
    color: #c6ffb4;
    border: 1px solid #2a8c34;
  }
  .flash-error {
    background: #3b1a1a;
    color: #ffc1c1;
    border: 1px solid #b33939;
  }
</style>
</head>
<body>

<div class="appbar">
  <div>
    <div class="title">업무자동화 도구 (서버)</div>
    <div class="subtitle">이름 O 처리 · 구글폼 응답(대상/폼) · 학교알리미</div>
  </div>
  <div class="subtitle">포트 5000 / cloudflared 터널 사용</div>
</div>

<div class="flash-container">
  {% with msgs = get_flashed_messages(with_categories=true) %}
    {% if msgs %}
      {% for category, msg in msgs %}
        <div class="flash {{ 'flash-' + category }}">{{ msg }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
</div>

<div class="container">
  <form method="post">
    <div class="grid">

      <!-- 1. 이름 O 처리 -->
      <div class="card">
        <h2>① 이름 O 처리</h2>
        <p class="desc">
          엑셀 B열 이름을 “O 처리” 규칙에 맞게 변환합니다.
        </p>
        <label for="noc_input_path">원본 엑셀 경로</label>
        <input type="text" id="noc_input_path" name="noc_input_path"
               placeholder="예: C:\작업\이름목록.xlsx">

        <label for="noc_output_path">저장 엑셀 경로</label>
        <input type="text" id="noc_output_path" name="noc_output_path"
               placeholder="예: C:\작업\이름O처리_결과.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="noc_run" class="btn-primary">
            이름 O 처리 실행
          </button>
          <a href="{{ url_for('download_template', kind='noc') }}"
             class="btn-secondary">
            양식 다운로드
          </a>
        </div>
      </div>

      <!-- 2. 구글폼 응답(대상) -->
      <div class="card">
        <h2>② 구글폼 응답(대상)</h2>
        <p class="desc">
          엑셀 분포대로 만족도 응답을 자동 제출합니다. (동작 시트 AB2 딜레이 적용)
        </p>
        <label for="target_excel_path">엑셀 경로</label>
        <input type="text" id="target_excel_path" name="target_excel_path"
               placeholder="예: C:\작업\구글폼응답_대상.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="target_run" class="btn-primary">
            자동화 실행
          </button>
          <a href="{{ url_for('download_template', kind='target') }}"
             class="btn-secondary">
            양식 다운로드
          </a>
        </div>
      </div>

      <!-- 3. 구글폼 응답(폼) -->
      <div class="card">
        <h2>③ 구글폼 응답(폼)</h2>
        <p class="desc">
          하나의 설문 안에서 여러 폼 블록을 순서대로 자동 제출합니다.
        </p>
        <label for="form_excel_path">엑셀 경로</label>
        <input type="text" id="form_excel_path" name="form_excel_path"
               placeholder="예: C:\작업\구글폼응답_폼.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="form_run" class="btn-primary">
            자동화 실행
          </button>
          <a href="{{ url_for('download_template', kind='form') }}"
             class="btn-secondary">
            양식 다운로드
          </a>
        </div>
      </div>

      <!-- 4. 학교알리미 -->
      <div class="card">
        <h2>④ 학교알리미</h2>
        <p class="desc">
          학교알리미 사이트에서 학생/반 정보를 가져와 엑셀에 채웁니다.
        </p>
        <label for="school_excel_path">엑셀 경로</label>
        <input type="text" id="school_excel_path" name="school_excel_path"
               placeholder="예: C:\작업\학교알리미.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="school_run" class="btn-primary">
            자동화 실행
          </button>
          <a href="{{ url_for('download_template', kind='school') }}"
             class="btn-secondary">
            양식 다운로드
          </a>
        </div>
      </div>

    </div>
  </form>
</div>

</body>
</html>
"""


# ------------------------------------------------------------
# 유틸
# ------------------------------------------------------------
def module_required(mod, name: str):
    if mod is None:
        raise RuntimeError(
            f"모듈 '{name}' 를 import할 수 없습니다. "
            f"{name}.py 가 서버 스크립트와 같은 폴더에 있는지 확인하세요."
        )


def require_path(path: str, label: str):
    if not path:
        raise ValueError(f"{label} 경로를 입력해 주세요.")
    if not os.path.exists(path):
        raise ValueError(f"{label} 경로를 확인해 주세요: {path}")


# ------------------------------------------------------------
# 템플릿 다운로드
# ------------------------------------------------------------
@app.route("/download/template/<kind>")
def download_template(kind: str):
    filename = TEMPLATE_FILES.get(kind)
    if not filename:
        flash("알 수 없는 템플릿 종류입니다.", "error")
        return redirect(url_for("hub"))

    path = os.path.join(TEMPLATE_DIR, filename)
    if not os.path.exists(path):
        flash(f"서버에 템플릿 파일이 없습니다: {filename}", "error")
        return redirect(url_for("hub"))

    return send_from_directory(
        TEMPLATE_DIR,
        filename,
        as_attachment=True,
        download_name=filename,
    )


# ------------------------------------------------------------
# 메인 라우트
# ------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def hub():
    if request.method == "POST":
        action = request.form.get("action", "")

        try:
            if action == "noc_run":
                module_required(이름O처리, "이름O처리")
                in_path = request.form.get("noc_input_path", "").strip()
                out_path = request.form.get("noc_output_path", "").strip()
                require_path(in_path, "원본 엑셀")
                if not out_path:
                    raise ValueError("저장 경로를 입력해 주세요.")
                이름O처리.process_names_in_excel(in_path, out_path)
                flash(f"[이름 O 처리] 완료: {os.path.basename(out_path)}", "success")

            elif action == "target_run":
                module_required(구글폼응답_대상, "구글폼응답_대상")
                path = request.form.get("target_excel_path", "").strip()
                require_path(path, "엑셀")
                구글폼응답_대상.run_from_excel(path)
                flash(f"[구글폼 응답(대상)] 완료: {os.path.basename(path)}", "success")

            elif action == "form_run":
                module_required(구글폼응답_폼, "구글폼응답_폼")
                path = request.form.get("form_excel_path", "").strip()
                require_path(path, "엑셀")
                구글폼응답_폼.run_from_excel_form(path)
                flash(f"[구글폼 응답(폼)] 완료: {os.path.basename(path)}", "success")

            elif action == "school_run":
                module_required(학교알리미, "학교알리미")
                path = request.form.get("school_excel_path", "").strip()
                require_path(path, "엑셀")
                학교알리미.run_from_excel(path)
                flash(f"[학교알리미] 완료: {os.path.basename(path)}", "success")

        except Exception as e:
            flash(f"에러: {e}", "error")

        return redirect(url_for("hub"))

    return render_template_string(TEMPLATE)


# ------------------------------------------------------------
# 실행 엔트리포인트
# ------------------------------------------------------------
if __name__ == "__main__":
    try:
        tunnel_manager.start_tunnel()
    except Exception as e:
        print("[tunnel] 시작 실패:", e)

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
