# HANDOFF

## 2026-06-15 18:05 KST BG 추가인원 매크로 노트북 다운 복구

- 증상: 노트북 다운으로 기존 BG 추가인원 가입/수강신청 백그라운드 매크로가 2026-06-15 14:26 KST 이후 중단된 상태로 확인됨.
- 복구: 2026-06-15 17:55 KST에 `추가인원 가입 수강신청.py`를 백그라운드로 재시작함. 실행 프로세스는 `python.exe` PID 9824로 확인됨.
- 설정 확인: 대시보드 기준 대상 시트 `BG`, 기수 `1`, 총 목표 `250`, 마감 `2026-06-17 21:00`, 랜덤 분산 사용 `예`, 운영시간 `09:00-21:00`.
- 상태 확인: 재시작 직전 `BG1`은 총 51명/오늘 51명이었고, 오늘 목표는 89명으로 재산정됨.
- 스케줄 복구: 남은 오늘분 38건을 2026-06-15 17:58:17부터 20:54:19까지 다시 배치함.
- 진행 확인: 17:58 예약 이후 실제 가입/수강신청이 재개되어 18:00 KST에 총 52명, 18:03 KST에 총 53명까지 `BG1` 현황 파일 반영을 확인함.
- 현재 남은 값: 18:04 KST 대시보드 기준 총 53명, 오늘 53명, 오늘 목표 89명, 오늘 남은 36건, 전체 목표까지 197명 남음.
- 로그: 상세 진행은 `signup_debug.log`, 재시작 표준 로그는 `signup_runner_bg_20260615-175509.out.log`, 오류 로그는 `signup_runner_bg_20260615-175509.err.log`를 확인하면 됨. 표준 로그는 리다이렉션 버퍼링으로 비어 있을 수 있으므로 실시간 확인은 `signup_debug.log`가 더 정확함.
- 다음 작업자 확인 포인트: 프로세스가 살아 있는지, `signup_debug.log`의 최신 시각이 갱신되는지, `추가인원 가입 현황.xlsx`의 `BG1` 행 수와 대시보드 E5/E6/E9/E11이 같이 움직이는지 확인할 것.

## 2026-06-15 21:06 KST BG 추가인원 오늘 목표 완료

- 오늘 BG1 추가인원 목표 89명을 달성함.
- 최종 확인값: `BG1` 총 89명/오늘 89명, 대시보드 E5=89, E6=89, E8=89, E9=0, E10=0.
- 대시보드 상태는 `오늘 목표 완료`, 최근 로그는 `2026-06-15 20:54:59`, 마지막 완료 기록은 total=89/today=89로 확인됨.
- 전체 목표는 250명이며, 오늘 완료 후 전체 목표까지 남은 인원은 161명으로 확인됨.
- `추가인원 가입 수강신청.py` 프로세스는 PID 9824로 계속 실행 중이며 다음 운영일 대기 상태임.
- 임시 15분 감시 heartbeat `bg`는 오늘 목표가 완료되어 종료 처리함.

## 2026-06-15 추가인원 기수별 현황 시트 분기

- `추가인원 가입 수강신청.py`에 기수별 현황 저장 시트 선택 로직을 추가했습니다.
- 설정 엑셀 `추가인원 가입 수강신청.xlsx`의 `BG` 또는 `PH` 시트에서 `기수`라고 적힌 셀을 찾고, 같은 셀/오른쪽/아래쪽/두 칸 오른쪽/두 칸 아래쪽의 숫자를 기수로 읽습니다.
- 간단 설정 위치로 `S3=기수`, `T3=<숫자>`도 지원합니다.
- 기수가 읽히면 현황 저장 시트명은 `BG1`, `PH2`처럼 `{BG|PH}{기수}`로 결정됩니다.
- 기수가 비어 있거나 읽히지 않으면 기존처럼 `BG`, `PH` 시트에 저장합니다.
- 해당 기수 현황 시트가 없으면 `추가인원 가입 현황.xlsx` 안에 자동 생성한 뒤 저장합니다.
- 실제 신청/회원가입/수강신청은 실행하지 않았고, 임시 복사본으로만 저장 테스트를 수행했습니다.
- 2026-06-15 검증: 파이썬 문법 컴파일 통과, 기수 파싱 6건 통과, 설정/현황 파일 기본 시트 확인 통과, 임시 `BG1`/`PH2` 자동 생성 및 카운트 검증 통과, 총 25개 검증 실패 0건.
- 현재 저장된 설정 엑셀 기준으로는 `BG`, `PH` 모두 기수 값이 빈 값으로 읽혔습니다. 엑셀에서 입력한 변경사항이 있다면 저장 후 매크로를 다시 시작해야 반영됩니다.

## 2026-06-15 BG 북구 추가인원 실행 전환

- `추가인원 가입 수강신청.py`의 대상 시트를 `PH`에서 `BG`로 변경했습니다.
- `URGENT_FORCE_DAY`를 빈 값으로 바꿔 월수/화목 분배 큐가 다시 동작하도록 했습니다.
- 주소 검색 검증 키워드를 시트별로 분리했습니다. `BG=북구`, `PH=포항`입니다.
- 설정 엑셀에서 기수 값이 비어 있어도 현황 파일에 단일 기수 시트가 있으면 `BG1`, `PH1`처럼 이어받도록 보강했습니다.
- BG 수강신청 과정 ID가 기존 `3_25`/`4_26`에서 현재 `3_29`/`4_30`으로 바뀐 것을 확인하고, 정확한 ID 및 접두 규칙 fallback을 추가했습니다.
- 라벨 텍스트가 비어 있거나 라벨 클릭이 실패하면 `rdIDX` 라디오를 직접 체크하도록 보강했습니다.
- 실제 제출 전 검증: 컴파일 통과, BG 설정 확인, `BG1` 현황 연결, 주소 키워드 확인, BG URL 입력 확인, 수강신청 선택 함수 synthetic 검증 통과.
- 실제 1건 통제 실행: 회원가입 및 BG 화목 수강신청 완료, `BG1` 총 1명/오늘 1명 기록 확인.
- 첫 통제 실행 1건은 회원가입 후 수강신청 선택 ID 변경 때문에 신청 저장 전 실패했습니다. 현황 파일에는 기록되지 않았고, 이후 코드 수정으로 성공 확인했습니다.
- 백그라운드 실행 시작: 2026-06-15 10:06 KST, 프로세스 ID `15840`, 출력 로그 `signup_runner_bg_20260615-100623.out.log`, 오류 로그 `signup_runner_bg_20260615-100623.err.log`.
- 2026-06-15 10:08 KST 확인: 프로세스 실행 중, `BG1` 총 3명/오늘 3명, 오류 로그 0바이트.

## 2026-06-15 BG 추가인원 200명 목표 재조정

- 기존 BG 백그라운드 매크로는 300명 목표 및 즉시 실행 설정이어서 중지했습니다.
- 중지 시점 확인: `BG1` 총 31명/오늘 31명, 기존 프로세스 ID `15840` 종료됨.
- 목표를 `TOTAL_TARGET_COUNT = 200`으로 변경했습니다.
- 마감일을 `DEADLINE_AT = 2026-06-17 21:00:00`으로 변경했습니다.
- `RUN_WITHOUT_DELAY = False`로 변경해 남은 목표를 운영시간 안에서 랜덤 분산하도록 했습니다.
- `DAILY_TARGET_MIN = 0`으로 변경해 85명 최소 강제 없이 남은 날짜와 현재 누적에 따라 가변 목표를 계산하도록 했습니다.
- 상태 파일 `signup_run_state.json`이 이전 300명/즉시실행 설정을 재사용하지 않도록 `target_sheet`, `target_total`, `deadline_at`, `run_without_delay`가 바뀌면 당일 스케줄을 다시 생성하게 했습니다.
- 2026-06-15 10:42 KST 검증: 현재 `BG1` 31명 기준 오늘 목표 72명, 남은 오늘 예약 41건, 첫 예약 10:47:12, 마지막 예약 20:54:15.
- 신청현황 추가인원 체크 유효성 확인: 실제 자동 갱신 사본은 `bukgu1,pohang2` 대상이고, `신청현황확인.py`가 `추가인원 가입 현황.xlsx`의 모든 시트에서 회원ID를 읽습니다. 현재 추가인원 ID 331개 로드, `BG1` ID 31개 포함 확인.
- Google Sheets 동기화 쪽도 `bukgu1`의 `추가` 카운트를 읽어 대시보드 `K5`에 반영하도록 되어 있습니다. 현재 로컬 `bukgu1` 추가 카운트 31 확인.
- 2026-06-15 10:42 KST 재시작: 프로세스 ID `15568`, 출력 로그 `signup_runner_bg_20260615-104256.out.log`, 오류 로그 `signup_runner_bg_20260615-104256.err.log`.
- 재시작 직후 로그: `sheet=BG total=31/200 today=31`, 다음 가입 예약 `2026-06-15 10:47:12`.

## 2026-06-15 설정/진척도 대시보드 엑셀화

- `추가인원 가입 수강신청.xlsx`에 `대시보드` 시트를 추가하고 첫 시트로 배치했습니다.
- 백업 파일 생성: `추가인원 가입 수강신청_backup_before_dashboard_20260615-104840.xlsx`.
- 유지해야 하는 입력 데이터 시트 `정보`, `BG`, `PH`는 그대로 유지했습니다.
- 구식 원본성 데이터로 보이는 `Sheet1`은 삭제하지 않고 숨김 처리했습니다.
- 대시보드 왼쪽 설정값은 매크로가 직접 읽습니다: 대상 시트, 기수, 최종 목표 인원, 마감일시, 운영 시작/종료시, 랜덤 분산 사용 여부, 일일 최소/최대/버퍼, 성공 후 대기 초.
- 대시보드 오른쪽 현황값은 매크로가 갱신합니다: 현황 시트, 현재 누적, 오늘 완료, 전체 남은 인원, 오늘 목표, 오늘 남은 인원, 남은 예약 수, 다음/마지막 예약, 마지막 갱신, 실행 상태, 최근 로그.
- 코드 변경: `apply_dashboard_settings()`로 대시보드 설정을 읽고, `update_dashboard_progress()`로 진행도를 엑셀에 씁니다.
- 엑셀 파일이 열려 있어 저장 잠금이 걸리면 매크로는 중단하지 않고 `signup_debug.log`에 대시보드 갱신 실패만 기록합니다.
- 검증 23개 통과: 대시보드 첫 시트, 필수 데이터 시트 유지, `Sheet1` 숨김, `BG/1기/200명/2026-06-17 21:00/랜덤분산` 설정, 진행률 수식, 데이터 유효성, `BG1` 현황 31명, 코드의 설정 읽기, `BG1` 해석, 대시보드 진행도 쓰기 확인.
- 컴파일 검증 통과, `git diff --check`는 CRLF 경고만 있고 오류 없음.
- 2026-06-15 10:53 KST 새 매크로 재시작: 프로세스 ID `16760`, 출력 로그 `signup_runner_bg_20260615-105309.out.log`, 오류 로그 `signup_runner_bg_20260615-105309.err.log`.
- 재시작 직후 상태: `sheet=BG total=31/200 today=31`, 대시보드 상태 `예약 대기`, 다음 예약 `2026-06-15 11:03:44`, 오류 로그 0바이트.

## 2026-06-24 PH2 추가인원 매크로 실행

- 대시보드 확인: 대상 시트 `PH`, 기수 `2`, 최종 목표 `300`, 마감 `2026-06-26 18:00`, 랜덤 분산 `예`, 운영시간 `09:00-21:00`.
- 실행 전 현황 확인: 활성 현황 파일 `추가인원 가입 현황.xlsx`에는 `BG1` 250명, `PH1` 300명이 있었고 `PH2`는 없었습니다.
- 코드 확인: 기수 2 설정으로 `PH2`가 현황 저장 시트로 해석되며, 시트가 없으면 `추가인원 가입 현황.xlsx` 안에 새로 생성해서 기록합니다.
- 2026-06-24 13:11 KST 백그라운드 실행 시작: 프로세스 ID `5108`, 출력 로그 `signup_runner_20260624-131138.out.log`, 오류 로그 `signup_runner_20260624-131138.err.log`.
- 최초 실행 직후 상태: 오늘 목표 `105`, 첫 예약 `2026-06-24 13:15:11`, 마지막 예약 `2026-06-24 20:57:05`.
- 첫 가입/수강신청 검증: 2026-06-24 13:16 KST에 첫 1건이 온라인 신청 완료 후 `PH2`에 기록되었습니다.
- 현재 확인값: `PH2` 총 1명/오늘 1명, 대시보드 E5=1, E6=1, E7=299, E8=105, E9=104, E10=104, 다음 예약 `2026-06-24 13:19:45`.
- 추가 확인: 2026-06-24 13:21 KST에 두 번째 예약도 완료되어 `PH2` 총 2명/오늘 2명, 대시보드 E5=2, E6=2, E7=298, E9=103, E10=103, 다음 예약 `2026-06-24 13:23:36`으로 갱신되었습니다.
- 오류 상태: `signup_runner_20260624-131138.err.log`는 0바이트이며, 실행 프로세스가 살아 있습니다.
- 추적 자동화: 기존 thread heartbeat `11`을 `PH2 추가인원 신청 추적`으로 변경했고, 15분 간격으로 프로세스/로그/대시보드/`PH2` 카운트를 확인하도록 했습니다.
- 남은 확인 포인트: 15분 간격으로 프로세스 생존, `signup_debug.log` 최신 갱신, `PH2` 카운트 증가, 오류 로그, 대시보드 E5/E6/E9/E10 변화를 확인하면 됩니다.

## 2026-06-24 PH2 additional signup final status

- 2026-06-24 21:10 KST check: PH2 daily target completed.
- Dashboard values: target `PH`, generation `2`, total target `300`, today target `105`, current total `105`, today done `105`, today remaining `0`, remaining schedules `0`.
- Status workbook check: `PH2` sheet total `105`, today `105`, last recorded time `2026-06-24 20:57:47`.
- Runtime check: python PID `5108` was still alive in runpy mode after completion, dashboard status was `오늘 목표 완료`, latest log was `다음 운영일 대기`.
- Error check: `signup_runner_20260624-131138.err.log` was `0` bytes; no generic errors or Traceback found in today's log. Retry-type events observed only: zipcode search retries `45`, sugang timeout retries `4`.
- Follow-up: heartbeat automation `11` was paused after final status reporting because today's PH2 target was complete.

## 2026-06-25 PH2 additional signup restore

- User requested configured automations to be restored.
- Initial state:
  - No active `python.exe` process for `추가인원 가입 수강신청.py` was found.
  - Dashboard showed PH2 was incomplete: total `114/300`, today `9/103`.
  - `signup_debug.log` had stopped after `2026-06-25 10:00:40`.
- Actions:
  - First restart attempt created `signup_runner_20260625-150546.*` but failed because the Python script filename contains spaces and was not quoted as a single argument.
  - Restarted successfully with the full script path quoted.
- Runtime after restore:
  - Active process: `python.exe` PID `14360`.
  - Output log: `signup_runner_20260625-150619.out.log`.
  - Error log: `signup_runner_20260625-150619.err.log`, length `0`.
- Verification:
  - `signup_debug.log` shows restart at `2026-06-25 15:06:29`.
  - `signup_debug.log` shows successful signup for `정우리`.
  - `추가인원 가입 현황.xlsx` PH2 rows increased to `115`.
  - Latest log reports `total=115/300 today=10/103`.

## 2026-06-29 PH2 max-speed completion recovery

- User requested PH2 remaining additional signup to be completed without waiting and to refresh the sheet immediately.
- Initial verified state: no active signup macro process; PH2 status was `203/300`, today `0`, remaining `97`.
- Settings workbook updated:
  - target sheet `PH`, generation `2`, total target `300`.
  - random schedule disabled, daily max set to `300`, daily buffer set to `0`.
  - post-success wait min/max set to `0/0` seconds.
  - dashboard progress cells refreshed before run.
- Backup created before max-speed settings update: `추가인원 가입 수강신청_backup_before_ph2_maxspeed_20260629-132812.xlsx`.
- Added launcher `run_signup_ph2_recovery_20260629.py` to avoid Windows command-line splitting issues with Korean paths and spaces.
- Failed restart attempts before launcher fix:
  - `signup_runner_ph2_recovery_20260629-132315.*`
  - `signup_runner_ph2_recovery_20260629-132358.*`
  - `signup_runner_ph2_recovery_20260629-132445.*`
- Active max-speed run:
  - PID `7276`.
  - Output log `signup_runner_ph2_maxspeed_20260629-132919.out.log`.
  - Error log `signup_runner_ph2_maxspeed_20260629-132919.err.log`.
- Verification after restart:
  - Original script reads target as `PH2`, total target `300`.
  - `RUN_WITHOUT_DELAY = true`.
  - post-success wait is `0/0`.
  - state has immediate schedule slots for remaining work.
  - error log is `0` bytes.
  - first seven records were saved; PH2 advanced to `210/300`, today `7/97`, remaining `90`.
- Remaining work: keep monitoring PID `7276`, `signup_debug.log`, error log, dashboard, and `추가인원 가입 현황.xlsx` until PH2 reaches `300/300`. Do not expose names, IDs, addresses, phone numbers, or full rows in user reports.

## 2026-06-29 PH2 max-speed completion final

- Final check time: `2026-06-29 15:05 KST`.
- PH2 completed: status workbook `300/300`, today `97/97`, remaining `0`.
- Dashboard completed: target `PH`, generation `2`, status sheet `PH2`, current total `300`, today count `97`, remaining `0`, today remaining `0`, run status `목표 달성`, latest log `목표 달성 완료`.
- State file completed: `daily_target=97`, remaining schedule slots `0`, `run_without_delay=true`, target total `300`, target sheet `PH`.
- Runtime completed: original PID `7276` was no longer alive after completion; only status-check command was visible during final process inspection.
- Runner logs: `signup_runner_ph2_maxspeed_20260629-132919.err.log` remained `0` bytes; no Traceback found in today's debug log.
- Final status timestamp in PH2 sheet: `2026-06-29 15:00:17`; final success log point: `total=300/300 today=97/97` at `2026-06-29 15:00:23`.
- Heartbeat `ph2` should be paused after this final report.
