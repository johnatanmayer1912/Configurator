# Disaster Recovery / Offline Runbook

**When shit hits the fan — use this page.**

## Symptom: Exe won't start

1. Check `logs/startup_bootstrap.log` (next to exe or in project `logs/`)
2. **Port 9000 in use** — stop the prior instance:
   ```powershell
   .\scripts\stop_configurator.ps1
   ```
   Or: `NXOS_Configurator_Web_*.exe --stop`  
   Or upgrade in place: `NXOS_Configurator_Web_*.exe --replace`
3. **Missing assets** — rebuild: `python utils/build_exe.py` (after `python scripts/enterprise_qa_gate.py`)
4. Antivirus quarantine — whitelist the exe; PyInstaller one-files are often flagged

## Symptom: Can't stop / old version keeps running

1. Click **Stop** in the web UI (works without `?token=` in the URL on v3.7.1+)
2. Close the console window or press **Ctrl+C**
3. `.\scripts\stop_configurator.ps1` or `exe --stop`
4. PID file: `logs/nxos_configurator.pid`

## Symptom: Browser shows blank / 404

1. Confirm console shows `Starting Production Server`
2. Open `http://127.0.0.1:9000/?token=...` from console URL if auto-open failed
3. Frozen exe: templates/static/data must be bundled — verify `utils/build_exe.py` datas list

## Symptom: Config generation fails

1. Use **Validate Scenario** before **Build**
2. Read validation errors in output panel
3. Check hostname format (no spaces)
4. Mgmt IP must include `/24` (or other prefix)
5. vPC: local and remote keepalive IPs must differ

## Symptom: Wrong NX-OS syntax on device

1. Verify NX-OS version selected matches switch `show version`
2. Legacy 7.x → select **7.0.x** for simplified template
3. Lab-test before production paste

## Recover previous configs

Artifacts: `configs/history/` (or `dist/configs/history/` when run from exe folder)

Checkpoints: `configs/checkpoints/*.json`

## Full project backup

```powershell
python -c "from utils.dr_backup import create_backup; create_backup()"
```

Or zip the entire Configurator folder including `docs/`, `data/`, `VERSION`.

## Rebuild from scratch

See `docs/REBUILD_GUIDE.md` and `docs/04-technical/ARCHITECTURE.md`.

## Truth sources (single source of truth)

| What | Where |
|------|-------|
| App version | `VERSION` |
| Hardware ports | `hardware_profiles.yaml` |
| Scenarios | `data/scenario_templates.yaml` |
| NX-OS versions | `data/nxos_versions.yaml` |
| CLI template | `templates/nxos_base.j2` |
| Changelog | `CHANGELOG.md` |
