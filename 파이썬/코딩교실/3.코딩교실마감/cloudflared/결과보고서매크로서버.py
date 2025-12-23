# server_enozfuture.py
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
import tunnel_manager   # cloudflared 터널 자동 실행용

# ---- 자동화 모듈들 import (같은 디렉토리에 있다고 가정) ----
try:
    import 이름O처리
except ImportError:
    이름O처리 = None

try:
    import 역량향상도평가
except ImportError:
    역량향상도평가 = None

try:
    import 만족도조사
except ImportError:
    만족도조사 = None

try:
    import 사전역량조사
except ImportError:
    사전역량조사 = None

try:
    import 이룸캠프만족도
except ImportError:
    이룸캠프만족도 = None


# ------------------------------------------------------------
# 경로 설정: 현재 파일 기준, 엑셀양식 폴더
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 같은 디렉토리에 "엑셀양식" 폴더 사용
TEMPLATE_DIR = os.path.join(BASE_DIR, "엑셀양식")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# 실제 파일명은 현재 가지고 있는 엑셀 이름에 맞춰 수정하세요.
TEMPLATE_FILES = {
    "noc":   "이름 O 처리 양식.xlsx",        # 예시: 이름 맞게 수정
    "yl":    "역량향상도 평가 양식.xlsx",
    "pre":   "사전역량조사 양식.xlsx",
    "iloom": "이룸캠프_만족도_양식.xlsx",
}


# ------------------------------------------------------------
# Flask 기본 설정
# ------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "enozfuture-secret-key"  # flash 메시지용, 아무 문자열이나 상관 없음


# ------------------------------------------------------------
# 메인 페이지 템플릿 (HTML)
#   템플릿 다운로드 버튼을 GET 링크로 변경
# ------------------------------------------------------------
TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>enozfuture 자동화 허브</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: #111;
    color: #eee;
  }
  .appbar {
    padding: 12px 20px;
    background: #181818;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .title {
    font-size: 1.2rem;
    font-weight: 600;
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
    background: #1b1b1b;
    border-radius: 16px;
    padding: 14px 16px 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.55);
  }
  .card h2 {
    margin: 0 0 4px;
    font-size: 1.05rem;
  }
  .card p.desc {
    margin: 0 0 10px;
    font-size: 0.83rem;
    color: #b3b3b3;
  }
  label {
    display: block;
    font-size: 0.8rem;
    margin-top: 6px;
    margin-bottom: 2px;
    color: #ccc;
  }
  input[type=text],
  input[type=number] {
    width: 100%;
    padding: 6px 8px;
    border-radius: 8px;
    border: 1px solid #444;
    background: #101010;
    color: #eee;
    font-size: 0.85rem;
  }
  .btn-row {
    margin-top: 10px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  button {
    border: none;
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform .08s ease, box-shadow .08s ease, background .1s ease;
  }
  button:active {
    transform: translateY(1px) scale(.98);
    box-shadow: none;
  }
  .btn-primary {
    background: linear-gradient(135deg,#ff6a3d,#ff9f43);
    color: #fff;
    box-shadow: 0 6px 14px rgba(255,106,61,0.45);
  }
  .btn-secondary {
    background: #2a2a2a;
    color: #fff;
    box-shadow: 0 6px 14px rgba(0,0,0,0.5);
  }
  /* a 태그도 버튼처럼 보이게 */
  a.link-btn {
    display: inline-block;
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
  }

  .flash-container {
    max-width: 1100px;
    margin: 10px auto 0;
    padding: 0 16px;
  }
  .flash {
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 0.85rem;
    margin-bottom: 6px;
  }
  .flash-success {
    background: #1b3c1f;
    color: #c6ffb4;
    border: 1px solid #2d8a34;
  }
  .flash-error {
    background: #3c1717;
    color: #ffc1c1;
    border: 1px solid #b33939;
  }
</style>
</head>
<body>

<div class="appbar">
  <div>
    <div class="title">enozfuture 자동화 허브</div>
    <div class="subtitle">이름O처리 · 역량향상도 · 만족도 · 사전역량 · 이룸캠프</div>
  </div>
  <div class="subtitle">서버: 5000 포트 / 도메인: kjgmacro.com</div>
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
          엑셀 B열 이름을 “O 처리” 규칙에 맞게 변환합니다.<br>
          (예: 원본 파일 경로, 저장 경로를 직접 입력)
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
             class="btn-secondary link-btn">
            이름 O 처리 양식 다운로드
          </a>
        </div>
      </div>

      <!-- 2. 역량향상도 평가 -->
      <div class="card">
        <h2>② 역량향상도 평가</h2>
        <p class="desc">
          역량향상도 엑셀을 읽어 자동으로 점수를 계산합니다.
        </p>
        <label for="yl_path">엑셀 파일 경로</label>
        <input type="text" id="yl_path" name="yl_path"
               placeholder="예: C:\작업\역량향상도.xlsx">

        <label for="yl_error_rate">문항당 오답률</label>
        <input type="number" id="yl_error_rate" name="yl_error_rate"
               step="0.001" value="0.008">

        <div class="btn-row">
          <button type="submit" name="action" value="yl_run" class="btn-primary">
            역량향상도 자동화 실행
          </button>
          <a href="{{ url_for('download_template', kind='yl') }}"
             class="btn-secondary link-btn">
            역량향상도 양식 다운로드
          </a>
        </div>
      </div>

      <!-- 3. 만족도 조사(랜덤 설문) -->
      <div class="card">
        <h2>③ 만족도 조사 자동화</h2>
        <p class="desc">
          구글폼 등 설문 링크를 받아, 지정 횟수만큼 역량·만족도 문항을 확률적으로 응답합니다.
        </p>
        <label for="mj_link">설문 링크</label>
        <input type="text" id="mj_link" name="mj_link"
               placeholder="예: https://docs.google.com/forms/...">

        <label for="mj_repeat">반복 횟수</label>
        <input type="number" id="mj_repeat" name="mj_repeat"
               min="1" value="1">

        <label for="mj_eval_cnt">역량 향상 평가 문항 수</label>
        <input type="number" id="mj_eval_cnt" name="mj_eval_cnt"
               min="0" value="0">

        <label for="mj_sat_cnt">만족도 조사 문항 수</label>
        <input type="number" id="mj_sat_cnt" name="mj_sat_cnt"
               min="0" value="0">

        <div class="btn-row">
          <button type="submit" name="action" value="mj_run" class="btn-primary">
            만족도 조사 실행
          </button>
        </div>
      </div>

      <!-- 4. 사전역량조사 -->
      <div class="card">
        <h2>④ 사전역량조사</h2>
        <p class="desc">
          사전역량조사 엑셀을 읽어 결과를 생성합니다.
        </p>
        <label for="pre_input_path">원본 엑셀 경로</label>
        <input type="text" id="pre_input_path" name="pre_input_path"
               placeholder="예: C:\작업\사전역량_raw.xlsx">

        <label for="pre_output_path">저장 엑셀 경로</label>
        <input type="text" id="pre_output_path" name="pre_output_path"
               placeholder="예: C:\작업\사전역량_결과.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="pre_run" class="btn-primary">
            사전역량조사 자동화 실행
          </button>
          <a href="{{ url_for('download_template', kind='pre') }}"
             class="btn-secondary link-btn">
            사전역량조사 양식 다운로드
          </a>
        </div>
      </div>

      <!-- 5. 이룸캠프 만족도 -->
      <div class="card">
        <h2>⑤ 이룸캠프 만족도</h2>
        <p class="desc">
          이룸캠프 만족도 설문 엑셀을 읽어 자동으로 처리합니다.
        </p>
        <label for="iloom_path">엑셀 파일 경로</label>
        <input type="text" id="iloom_path" name="iloom_path"
               placeholder="예: C:\작업\이룸캠프_만족도.xlsx">

        <div class="btn-row">
          <button type="submit" name="action" value="iloom_run" class="btn-primary">
            이룸캠프 만족도 실행
          </button>
          <a href="{{ url_for('download_template', kind='iloom') }}"
             class="btn-secondary link-btn">
            이룸캠프 양식 다운로드
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
# 유틸: 공통 실행 래퍼
# ------------------------------------------------------------
def module_required(mod, name: str):
    if mod is None:
        raise RuntimeError(
            f"모듈 '{name}' 를 import할 수 없습니다. "
            f"{name}.py 가 서버 스크립트와 같은 폴더에 있는지 확인하세요."
        )


# ------------------------------------------------------------
# 템플릿 파일 다운로드 라우트
#   /download/template/noc  등으로 접근
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
# 메인 라우트 (한 개만 사용)
# ------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def hub():
    if request.method == "POST":
        action = request.form.get("action", "")

        try:
            # 1) 이름 O 처리
            if action == "noc_run":
                module_required(이름O처리, "이름O처리")
                in_path = request.form.get("noc_input_path", "").strip()
                out_path = request.form.get("noc_output_path", "").strip()
                if not in_path or not out_path:
                    raise ValueError("원본/저장 경로를 모두 입력해 주세요.")
                이름O처리.process_names_in_excel(in_path, out_path)
                flash(f"[이름O처리] 작업 완료: {os.path.basename(out_path)}", "success")

            # 2) 역량향상도
            elif action == "yl_run":
                module_required(역량향상도평가, "역량향상도평가")
                path = request.form.get("yl_path", "").strip()
                if not path:
                    raise ValueError("엑셀 경로를 입력해 주세요.")
                error_rate = float(request.form.get("yl_error_rate", "0.008"))
                역량향상도평가.동작(path, error_rate)
                flash(f"[역량향상도평가] 작업 완료: {os.path.basename(path)}", "success")

            # 3) 만족도 조사
            elif action == "mj_run":
                module_required(만족도조사, "만족도조사")
                link = request.form.get("mj_link", "").strip()
                repeat = int(request.form.get("mj_repeat", "0"))
                eval_cnt = int(request.form.get("mj_eval_cnt", "0"))
                sat_cnt = int(request.form.get("mj_sat_cnt", "0"))
                if not link:
                    raise ValueError("설문 링크를 입력해 주세요.")
                if repeat <= 0:
                    raise ValueError("반복 횟수는 1 이상으로 입력해 주세요.")
                만족도조사.mj(link, repeat, eval_cnt, sat_cnt)
                flash(f"[만족도조사] 링크 {repeat}회 실행 완료", "success")

            # 4) 사전역량조사
            elif action == "pre_run":
                module_required(사전역량조사, "사전역량조사")
                in_path = request.form.get("pre_input_path", "").strip()
                out_path = request.form.get("pre_output_path", "").strip()
                if not in_path or not out_path:
                    raise ValueError("원본/저장 경로를 모두 입력해 주세요.")
                사전역량조사.동작(in_path, out_path)
                flash(f"[사전역량조사] 작업 완료: {os.path.basename(out_path)}", "success")

            # 5) 이룸캠프 만족도
            elif action == "iloom_run":
                module_required(이룸캠프만족도, "이룸캠프만족도")
                path = request.form.get("iloom_path", "").strip()
                if not path:
                    raise ValueError("엑셀 경로를 입력해 주세요.")
                이룸캠프만족도.run_from_excel(path)
                flash(f"[이룸캠프 만족도] 작업 완료: {os.path.basename(path)}", "success")

        except Exception as e:
            flash(f"에러: {e}", "error")

        return redirect(url_for("hub"))

    # GET 요청
    return render_template_string(TEMPLATE)


# ------------------------------------------------------------
# 실행 엔트리포인트
# ------------------------------------------------------------
if __name__ == "__main__":
    # 1) cloudflared 터널 먼저 띄우기
    try:
        tunnel_manager.start_tunnel()
    except Exception as e:
        print("[tunnel] 시작 실패:", e)

    # 2) Flask 서버 실행
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
