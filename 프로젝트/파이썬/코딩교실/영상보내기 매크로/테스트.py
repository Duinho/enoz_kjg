from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# 현재 스크립트 파일의 디렉토리 경로를 가져옵니다.
폴더경로 = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(폴더경로, 'auto-send-link-b97c1597bb00.json')

# Google Drive API와 상호작용하기 위한 범위 설정
SCOPES = ['https://www.googleapis.com/auth/drive']

# 서비스 계정 키 파일을 사용하여 자격 증명 생성
creds = service_account.Credentials.from_service_account_file(
        json_file_path, scopes=SCOPES)

# Google Drive API 서비스 객체 생성
service = build('drive', 'v3', credentials=creds)

def upload_folder(folder_path, parent_folder_id=None):
    folder_name = os.path.basename(folder_path)

    # 폴더 메타데이터 정의
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # 부모 폴더 ID가 지정된 경우, 메타데이터에 추가
    if parent_folder_id:
        folder_metadata['parents'] = [parent_folder_id]

    # 폴더 생성
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    folder_id = folder.get('id')

    # 폴더 내의 파일과 하위 폴더를 업로드
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            upload_folder(item_path, folder_id)
        else:
            file_metadata = {
                'name': item,
                'parents': [folder_id]
            }
            media = MediaFileUpload(item_path)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return folder_id

# 예제 사용법
folder_path = 'path/to/local/folder'  # 여기에 업로드하려는 로컬 폴더 경로를 입력하세요.
upload_folder(folder_path)
