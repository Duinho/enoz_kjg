# tunnel_manager.py
import os
import subprocess
import atexit

# cloudflared 프로세스를 담을 전역 변수
_tunnel_proc = None


def start_tunnel():
    """
    cloudflared 터널을 백그라운드로 실행한다.
    이미 떠 있으면 또 실행하지 않는다.
    """
    global _tunnel_proc

    # 이미 실행 중이면 패스
    if _tunnel_proc is not None and _tunnel_proc.poll() is None:
        print("[tunnel] already running")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_dir, "cloudflared.exe")
    config_path = os.path.join(base_dir, "config.yml")

    # 평소에 쓰던 명령어와 동일하게 맞추기
    #   cloudflared.exe tunnel --config config.yml run kjgmacro
    cmd = [
        exe_path,
        "tunnel",
        "--config", config_path,
        "run",
        "kjgmacro",
    ]

    print("[tunnel] starting:", " ".join(cmd))

    # 새 콘솔 창 없이 백그라운드로 실행
    _tunnel_proc = subprocess.Popen(
        cmd,
        cwd=base_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # 로그를 조금만 찍고 싶으면 이 부분을 주석 처리하거나 바꾸면 됨
    def _print_some_log():
        try:
            for _ in range(5):
                line = _tunnel_proc.stdout.readline()
                if not line:
                    break
                print("[tunnel]", line.rstrip())
        except Exception:
            pass

    _print_some_log()


def stop_tunnel():
    """
    Python 프로그램이 종료될 때 터널도 같이 종료.
    """
    global _tunnel_proc
    if _tunnel_proc is None:
        return
    if _tunnel_proc.poll() is not None:
        return

    print("[tunnel] stopping...")
    _tunnel_proc.terminate()
    try:
        _tunnel_proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        print("[tunnel] kill()")
        _tunnel_proc.kill()


# 프로그램이 끝날 때 자동 호출
atexit.register(stop_tunnel)
