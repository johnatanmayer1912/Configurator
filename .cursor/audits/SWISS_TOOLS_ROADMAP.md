# Swiss Tools & Standard Map — Roadmap (updated v7.0.47)

**Status:** P0 and P1 **shipped** in v7.0.47. P2 remains backlog.

---

## Delivered in v7.0.47

| ID | Item | Status |
|----|------|--------|
| P0-1 | Port Map multi-device + API | ✅ |
| P0-2 | Node Analyze results panel | ✅ |
| P0-3 | Failed-host drill-down + `failed_hosts.txt` | ✅ |
| P0-4 | Parallel pool → VLAN/audit/backup/interfaces/ping | ✅ |
| P0-5 | G-005 IM device_type guard | ✅ |
| P1-1 | HTML report header + truncation banner | ✅ |
| P1-2 | Link inventory VLAN column + sort | ✅ |
| P1-3 | Export ZIP bundle API | ✅ |
| P1-4 | Print CSS + color-blind legend | ✅ |
| P1-5 | Discovery → Swiss Tools cross-link | ✅ |

---

## P2 — Next excellence sprint

- G-002 IM bulk multi-host deploy
- G-010 Credential API hardening beyond localhost
- G-015 Arista EOS first-class
- Live `devices_done` on port map / node analyze threads
- PNG snapshot in export bundle (headless optional)

~~G-014~~ — **N/A (web-only policy):** Tk GUI not maintained; control plane lives in web console only.

---

## Operator checklist (unchanged)

1. Confirm sidebar scope → Standard Map → Stop if wrong scope.
2. Review failed-host panel + `failed_hosts.txt` before sign-off.
3. Port Map: multi-switch runs produce index HTML in output folder.
4. Node Analyze: use inline table → “Open Standard Map” for L2 context.
5. Archive export ZIP under change ticket.

---

*Last updated: 2026-06-18 — v7.0.47 release.*
