# Standard Map — Network Engineering Redesign Plan

**Version baseline:** v7.0.48  
**Audience:** NOC / NetOps / field engineers  
**Status:** Implemented v7.0.49 — Tier default + Focus toggle + Schematic export style; matrix excluded.  
**Demos:** `docs/06-ui-ux/mockups/standard-map-demo-index.html`

---

## Executive diagnosis (why it feels “vague” today)

| Problem | NetEng impact | Root cause in product |
|---------|---------------|------------------------|
| **No “so what?” header** | Engineer opens HTML and must infer scope, freshness, gaps | Header is node/edge counts only; truncation/failures buried |
| **Graph-first, story-second** | Answers “what connects?” only after clicking around | Vis.js box diagram dominates; link inventory is secondary tab |
| **Rich data collected, thin data shown** | CDP platform, speed, VLAN, MAC, Po detail exist in JSON but not in default view | Side panel requires click; many fields never surface in infographic |
| **Physical vs logical collapsed** | Cannot see *port* vs *bundle* vs *domain* without mental mapping | Po/vPC edges styled but not explained in operator language |
| **No WHO / HOW / WHAT columns** | Handoff to shift or vendor needs re-export | Table lacks: remote hostname, local port, protocol, VLAN, role, confidence |
| **Swiss Tools UI ≠ map UX** | Run flow is OK; result is a separate dark-themed page with different mental model | Web tab promises “infographic”; output feels like dev diagnostic |
| **No path or dependency view** | “How is AP-12 reachable from core?” requires external tools | No BFS path, no upstream/downstream summary per node |

**NetEng verdict:** Current Standard Map is a **topology renderer**, not an **L2 operations briefing**. Data plumbing is strong (Phase 1 collection, manifest, parallel SSH); **presentation and information architecture** are the gap.

---

## Design principles ( council: NetOps + UI/UX )

1. **Briefing first** — First screen answers: site, time, scope, health, anomalies.  
2. **Connection index is first-class** — Sortable table = primary artifact; graph = lens.  
3. **Layer toggles** — Physical (ports/members) | Logical (adjacency) | Identity (CDP/LLDP/platform) — same selection, synced.  
4. **Progressive disclosure** — Summary → link row → port detail → MAC list (never empty graph).  
5. **Handoff-ready** — Print/PDF/ZIP with legend, truncation banner, failed hosts.  
6. **Same language in app and export** — Swiss Tools status text matches HTML header verbatim.

---

## Data enrichment (what to collect per device — Phase 1.5)

Already partially collected; **surface and normalize** in manifest + HTML:

| Field | Source command | Use in UI |
|-------|----------------|-----------|
| Hostname, role heuristic | prompt + `_detect_device_role` | Swimlane placement |
| Platform, serial, OS | `show version` (short) | Node card, export header |
| Mgmt IP | CDP/LLDP | SSH link, search |
| Per-port: status, desc, VLAN, speed, duplex | `show interface status` | Edge + port panel |
| MAC count / top MACs | `show mac address-table` (truncated) | Edge “endpoints” badge |
| Po members, LACP | `show etherchannel` / `show lacp` | Physical layer view |
| STP role per VLAN (optional) | existing STP plugin cross-link | Risk badge on blocked ports |
| Collection status | parallel pool | Failed host strip |

**New normalized object:** `ConnectionRecord` — one row per logical adjacency (or per member for unbundled):

```json
{
  "local_device", "local_port", "remote_device", "remote_port",
  "protocol": "cdp|lldp", "vlan", "speed", "bundle": "Po1|null",
  "local_role", "remote_role", "confidence", "endpoint_mac_count"
}
```

---

## Layer model (physical + OS in one product)

```
┌─────────────────────────────────────────────────────────┐
│  L3 (future / optional)  — SVI, routed interfaces       │
├─────────────────────────────────────────────────────────┤
│  L2 Logical  — CDP/LLDP adjacency, VLAN, STP state      │
├─────────────────────────────────────────────────────────┤
│  L1 Physical — port, speed, Po members, optics (future) │
├─────────────────────────────────────────────────────────┤
│  Identity    — platform, OS, mgmt IP, serial            │
└─────────────────────────────────────────────────────────┘
```

**Single-pane mode:** stacked cards on one node (Identity header → L2 neighbors → L1 ports).  
**Twin-pane mode:** left = physical port list for selected device; right = logical graph highlighting those ports’ edges.

---

## Four demo directions (open in browser)

| ID | Name | Best for | Tradeoff |
|----|------|----------|----------|
| **A** | NOC Briefing Board | Daily ops, shift handoff | More UI chrome; less “pure graph” |
| **B** | Physical + Logical Twin | Troubleshooting port issues | Wider layout; power users |
| **C** | Connection Index First | Audit, CMDB validation, “who connects to who” | Less visual; fastest answer |
| **D** | Infographic Export | Management docs, change records, PDF | Static-friendly; less interactive |

Open UI shells: [standard-map-demo-index.html](../docs/06-ui-ux/mockups/standard-map-demo-index.html)

---

## Connection map visualization (how links are drawn)

**Rule:** Map is always available **alongside** briefing + connection index — not instead of them. User switches map style via toolbar; table and detail panel stay synced.

Open map viz demos: [standard-map-viz-demo-index.html](../docs/06-ui-ux/mockups/standard-map-viz-demo-index.html)

| ID | Style | NOC | NetEng | When to use |
|----|-------|-----|--------|-------------|
| **V1** | Tier hierarchy (top-down) | ★★★★★ | ★★★★ | Default daily view; matches campus tiers |
| **V2** | Radial hub (core-centric) | ★★★ | ★★★★★ | Core dependency, design review |
| **V3** | Schematic orthogonal (Visio) | ★★★★ | ★★★★ | Export/PDF, change records, port labels on links |
| **V4** | Neighborhood focus (1–2 hop) | ★★★★★ | ★★★★ | Troubleshooting; avoids hairball on 50+ devices |
| **V5** | Matrix / adjacency grid | ★★ | ★★★★★ | Audit, unidirectional CDP, orphan detection |

**Recommended product default:** V1 (Tier) + quick toggle to V4 (Focus). Export uses V3. Audit session optional V5.

---

## Implementation roadmap (after demo selection)

| Phase | Scope | Effort |
|-------|--------|--------|
| **R1** | `ConnectionRecord` builder in adapters + manifest; new HTML shell from chosen demo | L |
| **R2** | Swiss Tools wizard: scope preview → run → inline preview frame (not only new tab) | M |
| **R3** | Enrichment commands + STP cross-link badges | M |
| **R4** | Path trace (A→B), export PDF matching demo D | M |
| **R5** | L3 SVI overlay (optional, site-wide) | L |

---

## Success criteria (NetEng sign-off)

- [ ] Engineer answers “what is connected to CORE-01 Gi1/0/48?” in **< 30 s** without clicking more than twice.  
- [ ] Shift handoff PDF includes site, time, failed hosts, top 20 links, role legend.  
- [ ] Truncation at 150 devices is **impossible to miss** in UI and export.  
- [ ] Same connection row appears in web preview, exported HTML, and ZIP manifest.

---

*Next step: User selects demo A / B / C / D (or hybrid). Then implement R1 against `utils/report_formatter.py` + Swiss Tools tab.*
