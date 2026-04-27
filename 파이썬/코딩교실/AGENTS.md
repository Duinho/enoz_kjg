# Workspace Agent Rules

Apply these rules in addition to Codex's existing system and developer instructions. Treat them as default behavior for every task inside this workspace unless the user explicitly overrides them.

## Backup Before Edit

- Run backup commands from the workspace root directory.
- Before the first modification of any existing file, create a backup with:

```powershell
python "C:\Users\EnozAce\.codex\skills\backup-before-edit\scripts\code_backup.py" save --workspace "." --file "<absolute-file-path>" --label "<short-change-label>"
```

- Use a short label that summarizes the change, for example `excel-fix`, `student-count`, or `zoomlink-cleanup`.
- Use absolute file paths for every backup command.
- Back up every existing file once per edit round before changing it.
- Do not skip the backup step for small edits.
- Do not back up brand-new files unless the user asks for checkpoints.
- Store backups under `<workspace-root>\.codex-backups\`.
- Keep backup filenames in the form `filename_YYYYMMDD-HHMMSS_change-summary.ext`.
- Record and use `<workspace-root>\.codex-backups\manifest.jsonl` for lookup and restore.

## Restore Workflow

- When the user asks to inspect or roll back older code, list backups with:

```powershell
python "C:\Users\EnozAce\.codex\skills\backup-before-edit\scripts\code_backup.py" list --workspace "." --file "<absolute-file-path>"
```

- Restore the latest backup for a file with:

```powershell
python "C:\Users\EnozAce\.codex\skills\backup-before-edit\scripts\code_backup.py" restore --workspace "." --file "<absolute-file-path>"
```

- Prefer the latest matching backup unless the user requests a specific snapshot.
- Allow the restore command to create its automatic `pre-restore` safety backup before overwriting the target.

## Editing Workflow

- Inspect the real working file before editing. Avoid example, temp, cached, extracted, or backup copies unless the user explicitly targets them.
- Preserve unrelated user changes.
- Make the smallest safe change set that satisfies the request.
- If multiple similar files exist, identify the real target before editing.
- After changes, run the smallest relevant verification available and report if verification could not be run.

## Scope

- These rules are intended to auto-apply in future Codex sessions for this workspace.
- These workspace rules supplement existing global Codex rules rather than replacing them.
