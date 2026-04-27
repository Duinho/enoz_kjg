# 코딩교실 신청현황 매크로 PC 설치 및 실행 지침

## 목적

이 폴더는 코딩교실 신청현황을 자동으로 갱신하기 위한 패키지입니다.

원하는 최종 동작은 다음과 같습니다.

1. 매크로용 PC를 켜고 Windows에 로그인합니다.
2. 작업 스케줄러가 자동으로 `start_auto_update.ps1`을 실행합니다.
3. `start_auto_update.ps1`이 10분마다 `run_update_once.ps1`을 실행합니다.
4. `run_update_once.ps1`이 신청현황을 다운로드하고 `_sincheong\코딩교실 신청 현황.xlsx`를 갱신합니다.
5. `_secrets\google_service_account.json`이 있으면 Google 스프레드시트 원문 시트도 같이 갱신합니다.
6. 대시보드는 구글시트 안의 수식으로 자동 재계산됩니다.

주의: 현재 구성은 **Windows 로그인 후** 자동 실행되는 방식입니다. 전원만 켜지고 로그인되지 않은 상태에서도 돌리려면 Windows 자동 로그인 또는 별도 관리자 권한 작업 스케줄러 설정이 필요합니다.

## 주요 파일

- `_sincheong\신청현황확인.py`
  - 신청현황 사이트에 로그인해서 포항/구미 신청자 원문을 다운로드하고 로컬 엑셀을 갱신하는 메인 코드입니다.

- `_sincheong\신청현황확인.xlsx`
  - 로그인 정보와 대상 URL이 들어 있는 설정 파일입니다.
  - 외부에 공유하지 마세요.

- `_sincheong\코딩교실 신청 현황.xlsx`
  - 로컬 결과 엑셀 파일입니다.

- `run_update_once.ps1`
  - 한 번 갱신합니다.
  - 기본 대상은 `pohang:1`, `gumi:1`입니다.
  - Google 인증 파일이 있으면 구글시트 동기화까지 시도합니다.

- `start_auto_update.ps1`
  - 10분마다 `run_update_once.ps1`을 반복 실행합니다.

- `install_startup_task.ps1`
  - Windows 로그인 시 `start_auto_update.ps1`이 자동 실행되도록 작업 스케줄러에 등록합니다.

- `uninstall_startup_task.ps1`
  - 자동 실행 작업을 제거합니다.

- `tools\sync_google_sheet.py`
  - 로컬 결과 엑셀의 `pohang1`, `gumi1` 시트를 구글 스프레드시트에 업로드합니다.

- `logs\`
  - 실행 후 자동 생성됩니다.
  - 10분마다 실행된 결과와 오류 기록이 여기에 남습니다.

## 처음 설치 순서

PowerShell을 이 폴더에서 열고 아래 순서대로 실행합니다.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
py -3 -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_update_once.ps1
```

`py` 명령이 없으면 아래처럼 실행합니다.

```powershell
python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_update_once.ps1
```

한 번 실행이 정상 동작하면 자동 시작 작업을 등록합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_startup_task.ps1
```

등록 후에는 PC를 다시 켜고 Windows에 로그인하면 자동 갱신 루프가 시작됩니다.

## Google 스프레드시트 동기화 설정

로컬 엑셀만 갱신하려면 별도 설정 없이 사용할 수 있습니다.

구글 스프레드시트까지 자동 갱신하려면 API 인증 파일이 필요합니다. 일반적인 서비스 계정 방식은 다음 순서입니다.

1. Google Cloud에서 서비스 계정을 만듭니다.
2. 서비스 계정 JSON 키를 내려받습니다.
3. 파일명을 `google_service_account.json`으로 바꿉니다.
4. 이 폴더의 `_secrets\google_service_account.json` 위치에 넣습니다.
5. JSON 안의 `client_email` 값을 확인합니다.
6. 구글 스프레드시트 `코딩교실 신청자 현황`을 그 `client_email`에게 편집자로 공유합니다.

현재 동기화 대상 스프레드시트 ID:

```text
1eG8aPnjIbI2UQiAJbii6QnCoW2kgUK4fGRwQnKz6JT4
```

동기화되는 원문 시트:

- `pohang1`
- `gumi1`

대시보드의 수식과 서식은 건드리지 않고, 원문 시트와 `대시보드!F1` 갱신 시간만 업데이트합니다.

## 대상 추가 또는 변경

기본 실행 대상은 `run_update_once.ps1` 안의 아래 줄에서 바꿉니다.

```powershell
$Targets = @("pohang:1", "gumi:1")
```

예를 들어 북구 3기를 추가하려면 다음처럼 바꿉니다.

```powershell
$Targets = @("pohang:1", "gumi:1", "bukgu:3")
```

구글시트에 업로드할 원문 시트도 추가해야 한다면 `tools\sync_google_sheet.py` 실행 인자 또는 기본값의 `pohang1,gumi1` 목록에 해당 시트를 추가합니다.

## 수동 실행

한 번만 갱신:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_update_once.ps1
```

10분 반복 루프를 현재 창에서 직접 실행:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start_auto_update.ps1
```

자동 시작 작업 등록:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_startup_task.ps1
```

자동 시작 작업 제거:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uninstall_startup_task.ps1
```

## 확인 방법

- 실행 로그: `logs` 폴더
- 로컬 결과: `_sincheong\코딩교실 신청 현황.xlsx`
- 구글시트 결과:
  - `pohang1`
  - `gumi1`
  - `대시보드!F1`

오류가 나면 가장 최근 로그 파일을 먼저 확인합니다.

## 매크로 PC에서 Codex에게 넣을 프롬프트

아래 프롬프트를 그대로 붙여 넣으면 됩니다.

```text
이 폴더는 코딩교실 신청현황 자동갱신 프로젝트입니다.

먼저 README_매크로PC_설치및실행.md를 읽고, 현재 PC 환경과 파일 구성을 점검해줘.

목표 동작은 다음과 같아.
- Windows 로그인 후 자동으로 실행
- 10분마다 신청현황 갱신
- 기본 대상은 포항 1기와 구미 1기
- 로컬 엑셀을 갱신
- _secrets\google_service_account.json이 있으면 구글 스프레드시트도 갱신
- 실행 결과는 logs 폴더에 남김

바로 실행하지 말고, 먼저 네가 이해한 업무 내용과 실행 순서를 쭉 설명해줘.
마지막에 "이대로 실행시킬까요?"라고 물어봐.

내가 "ㅇㅋ"라고 답하면 그때 실행해.
내가 수정사항을 말하면 수정한 뒤 다시 설명하고 확인받아.

실행 순서는 기본적으로 아래처럼 해줘.
1. Python 설치 여부 확인
2. requirements.txt 설치
3. run_update_once.ps1로 1회 테스트
4. 문제가 없으면 install_startup_task.ps1로 자동 시작 작업 등록
5. 마지막에 로그 위치와 다음 확인 방법 알려주기
```

## 보안 메모

이 패키지에는 신청현황 사이트 설정 파일과 신청자 데이터가 포함될 수 있습니다. 매크로 PC 외부로 공유하지 마세요.
