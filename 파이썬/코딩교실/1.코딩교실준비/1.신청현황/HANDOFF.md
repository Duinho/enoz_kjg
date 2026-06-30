## 2026-06-29 15:10 KST 10-minute sheet update

- User requested the 10-minute sheet update to run immediately.
- This folder is the actual 10-minute auto-update workspace: `start_auto_update.ps1` says `Schedule: every 10 minutes`.
- At request time, the 15:10 scheduled run was already active, so no duplicate run was started.
- Run target: `pohang:1`, `gumi:1`.
- Run log: `logs/update_20260629-151003.log`.
- Result: update finished normally at `2026-06-29 15:12:19`.
- Google Sheets direct read verification:
  - spreadsheet title `2026 코딩교실 지역별 신청자 현황`.
  - worksheets include `대시보드`, `pohang1`, `gumi1`.
  - `pohang1` read as `549x22`, `A1=No.`.
  - `gumi1` read as `35x20`, `A1=No.`.
  - `대시보드!F1` read as `06월 29일 15시 12분 현황`.
- Do not expose names, IDs, addresses, phone numbers, or full application rows in reports.
