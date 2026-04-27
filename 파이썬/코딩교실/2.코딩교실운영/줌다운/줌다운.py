import json
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from threading import Lock

import openpyxl
import requests
from playwright.sync_api import sync_playwright
from requests.auth import HTTPBasicAuth


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")
excel_file_path = os.path.join(script_dir, "영상보내기.xlsx")
BASE_DIR = os.path.join(script_dir, "녹화영상")

priority_types = [
    "shared_screen_with_gallery_view",
    "shared_screen_with_speaker_view",
    "shared_screen",
    "speaker_view",
    "gallery_view",
]

processed_meetings = set()
processed_meetings_lock = Lock()


@dataclass(frozen=True)
class Zoom설정:
    client_id: str
    client_secret: str
    account_id: str
    start_date: str
    end_date: str
    delete_after_download: bool
    max_workers: int


def text_or_empty(value):
    if value is None:
        return ""
    return str(value).strip()


def parse_bool(value, default):
    if value is None:
        return default
    if isinstance(value, bool):
        return value

    value_text = str(value).strip().lower()
    if value_text in {"1", "true", "yes", "y", "on"}:
        return True
    if value_text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def load_local_config():
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_zoom_config():
    config = load_local_config()
    zoom_section = config.get("Zoom", {})
    recordings_section = config.get("Recordings", {})

    settings = Zoom설정(
        client_id=os.getenv("ZOOM_CLIENT_ID", text_or_empty(zoom_section.get("client_id"))),
        client_secret=os.getenv("ZOOM_CLIENT_SECRET", text_or_empty(zoom_section.get("client_secret"))),
        account_id=os.getenv("ZOOM_ACCOUNT_ID", text_or_empty(zoom_section.get("account_id"))),
        start_date=os.getenv("ZOOM_RECORDINGS_START_DATE", text_or_empty(recordings_section.get("start_date"))),
        end_date=os.getenv("ZOOM_RECORDINGS_END_DATE", text_or_empty(recordings_section.get("end_date"))),
        delete_after_download=parse_bool(
            os.getenv("ZOOM_DELETE_AFTER_DOWNLOAD", recordings_section.get("delete_after_download")),
            True,
        ),
        max_workers=max(
            1,
            int(os.getenv("ZOOM_MAX_WORKERS", recordings_section.get("max_workers", 4))),
        ),
    )

    missing = []
    if not settings.client_id:
        missing.append("ZOOM_CLIENT_ID")
    if not settings.client_secret:
        missing.append("ZOOM_CLIENT_SECRET")
    if not settings.account_id:
        missing.append("ZOOM_ACCOUNT_ID")
    if not settings.start_date:
        missing.append("ZOOM_RECORDINGS_START_DATE")
    if not settings.end_date:
        missing.append("ZOOM_RECORDINGS_END_DATE")

    if missing:
        raise ValueError(
            "Zoom 설정이 부족합니다. config.json 또는 환경변수를 확인하세요: "
            + ", ".join(missing)
        )

    return settings


def get_access_token(session, settings):
    response = session.post(
        "https://zoom.us/oauth/token",
        params={
            "grant_type": "account_credentials",
            "account_id": settings.account_id,
        },
        auth=HTTPBasicAuth(settings.client_id, settings.client_secret),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_all_users(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 100}
    users = []

    while True:
        response = session.get(
            "https://api.zoom.us/v2/users",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        users.extend(data.get("users", []))
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            return users
        params["next_page_token"] = next_page_token


def list_recordings(session, token, user_id, settings):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "from": settings.start_date,
        "to": settings.end_date,
        "page_size": 50,
    }
    meetings = []

    while True:
        response = session.get(
            f"https://api.zoom.us/v2/users/{user_id}/recordings",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        meetings.extend(data.get("meetings", []))
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            return meetings
        params["next_page_token"] = next_page_token


def mark_meeting_processed(meeting_id):
    with processed_meetings_lock:
        if meeting_id in processed_meetings:
            return False
        processed_meetings.add(meeting_id)
        return True


def sanitize_filename(name):
    sanitized = re.sub(r'[<>:"/\\|?*]+', "_", text_or_empty(name))
    sanitized = sanitized.rstrip(". ")
    return sanitized or "NoTopic"


def get_region(topic):
    if "경산" in topic:
        return "경산"
    if "포항" in topic:
        return "포항"
    if "구미" in topic:
        return "구미"
    if "온라인SW" in topic:
        return "대구"
    return "기타"


def select_recording_file(files):
    for recording_type in priority_types:
        for file_info in files:
            if file_info.get("recording_type") == recording_type and file_info.get("file_type") == "MP4":
                return file_info
    return None


def download_and_delete(meeting, token, user_email, settings):
    meeting_id = meeting["id"]
    if not mark_meeting_processed(meeting_id):
        print(f"⏭️ 이미 처리된 회의 스킵: {meeting_id}")
        return

    topic = text_or_empty(meeting.get("topic")) or "NoTopic"
    safe_topic = sanitize_filename(topic)
    start_time = text_or_empty(meeting.get("start_time"))
    dt = datetime.fromisoformat(start_time.rstrip("Z"))
    date_str = f"{dt.year}년 {dt.month}월 {dt.day}일"
    region = get_region(topic)

    folder_path = os.path.join(BASE_DIR, region, date_str, f"{safe_topic} _{date_str}")
    os.makedirs(folder_path, exist_ok=True)

    with requests.Session() as session:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(
            f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        files = response.json().get("recording_files", [])

        selected = select_recording_file(files)
        if not selected:
            print(f"⚠️ MP4 파일 없음: {topic} ({meeting_id})")
            return

        download_url = selected["download_url"] + f"?access_token={token}"
        base_filename = f"{safe_topic} _{date_str}.mp4"
        file_path = os.path.join(folder_path, base_filename)

        counter = 1
        name, ext = os.path.splitext(base_filename)
        while os.path.exists(file_path):
            file_path = os.path.join(folder_path, f"{name}_{counter}{ext}")
            counter += 1

        print(f"🔽 {user_email} 회의 → 다운로드: {os.path.basename(file_path)}")
        with session.get(download_url, stream=True, timeout=120) as download_response:
            download_response.raise_for_status()
            with open(file_path, "wb") as output_file:
                shutil.copyfileobj(download_response.raw, output_file)

        if not settings.delete_after_download:
            print(f"🗂️ 다운로드 완료, 삭제는 건너뜀: {topic} ({meeting_id})")
            return

        delete_response = session.delete(
            f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings",
            headers=headers,
            timeout=30,
        )
        if delete_response.status_code == 204:
            print(f"🧹 삭제 완료: {topic} ({meeting_id})")
        else:
            print(f"❌ 삭제 실패 ({delete_response.status_code}): {delete_response.text}")


def get_sms_config_from_excel():
    workbook = openpyxl.load_workbook(excel_file_path, data_only=True)
    worksheet = workbook.active
    문자박스링크 = text_or_empty(worksheet.cell(row=8, column=15).value)
    문자박스아이디 = text_or_empty(worksheet.cell(row=9, column=15).value)
    문자박스비번 = text_or_empty(worksheet.cell(row=10, column=15).value)
    회신번호 = "010" + text_or_empty(worksheet.cell(row=6, column=17).value)
    알람받을번호 = text_or_empty(worksheet.cell(row=5, column=15).value)
    workbook.close()
    return 문자박스링크, 문자박스아이디, 문자박스비번, 회신번호, 알람받을번호


def send_sms_via_playwright(link, user_id, user_pwd, recv_number, callback_number):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        page = browser.new_page()
        page.goto(link)
        page.fill("input[name='id']", user_id)
        page.fill("input[name='pwd']", user_pwd)
        page.press("input[name='pwd']", "Enter")
        time.sleep(1)
        try:
            page.click("button[onclick*='contentsLayerClose']")
        except Exception:
            pass

        page.fill("textarea#recvList", recv_number)
        page.fill("textarea#msg", "영상 발송 완료")
        page.locator("a.hand.openLayer", has_text="선택").click()
        frame = page.frame(name="callbackFrame")
        frame.wait_for_selector("span:has-text('전체 회신번호')", timeout=5000)
        frame.locator("span:has-text('전체 회신번호')").click()
        frame.wait_for_selector("#bulkCallbackNum", timeout=3000)
        frame.fill("#bulkCallbackNum", callback_number)
        frame.click("button[onclick*='callbackCheckForm']")
        time.sleep(0.3)
        page.locator("a.hand.openLayer", has_text="전송하기").click()
        time.sleep(0.3)
        page.keyboard.press("Enter")
        time.sleep(0.3)
        page.keyboard.press("Enter")
        print("📨 영상 발송 완료 메시지 전송 완료")
        browser.close()


def main():
    try:
        settings = load_zoom_config()
    except Exception as error:
        print(f"설정 로드 실패: {error}")
        return

    with requests.Session() as session:
        print("🔐 Access Token 발급 중...")
        token = get_access_token(session, settings)

        print("👥 사용자 목록 조회 중...")
        users = get_all_users(session, token)
        print(f"총 사용자 수: {len(users)}")

        download_tasks = []
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            for user in users:
                user_id = user["id"]
                user_email = user["email"]
                print(f"\n📁 [{user_email}] 회의 목록 조회 중...")

                try:
                    meetings = list_recordings(session, token, user_id, settings)
                    print(f"📋 회의 수: {len(meetings)}")
                    for meeting in meetings:
                        download_tasks.append(
                            executor.submit(download_and_delete, meeting, token, user_email, settings)
                        )
                except Exception as error:
                    print(f"⚠️ 사용자 {user_email} 오류: {error}")

            for future in as_completed(download_tasks):
                try:
                    future.result()
                except Exception as error:
                    print(f"❌ 병렬 다운로드 오류: {error}")

    print("\n🎉 모든 병렬 다운로드 완료")
    문자박스링크, 문자박스아이디, 문자박스비번, 회신번호, 알람받을번호 = get_sms_config_from_excel()
    send_sms_via_playwright(
        문자박스링크,
        문자박스아이디,
        문자박스비번,
        알람받을번호,
        회신번호,
    )


if __name__ == "__main__":
    main()
