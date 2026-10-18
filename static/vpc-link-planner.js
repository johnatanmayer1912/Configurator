/** vPC Link Planner — editable downlinks and uplinks for 40G / 10G / 1G scenarios. */

let linkPlannerCustomized = false;
let linkPlannerRows = { downlink: [], uplink: [] };

function matrixRowForScenario(scenarioId) {
    return (catalog.config_matrix || []).find((r) => r.scenario_id === scenarioId) || {};
}

function hardwareProfile() {
    const model = document.getElementById("model")?.value || "";
    return (catalog.hardware || []).find((h) => h.display_name === model) || {};
}

function reservedVpcPorts(hw) {
    const out = new Set();
    (hw.vpc_peer_link || []).forEach((p) => out.add(p));
    (hw.vpc_keepalive || []).forEach((p) => out.add(p));
    return out;
}

function fiberUplinkPool(hw) {
    const excluded = reservedVpcPorts(hw);
    const pool = [];
    (hw.port_groups || []).forEach((grp) => {
        const start = Number(grp.start || 0);
        if (start < 49) return;
        const end = Number(grp.end || start);
        for (let i = start; i <= end; i += 1) {
            const name = `Ethernet1/${i}`;
            if (!excluded.has(name)) pool.push(name);
        }
    });
    return pool.sort(ethSortKey);
}

function coreUplinkPool(hw, count = 2) {
    const excluded = reservedVpcPorts(hw);
    const total = Number(hw.total_ports || 0);
    const pool = [];
    for (let i = total; i >= 1; i -= 1) {
        const name = `Ethernet1/${i}`;
        if (excluded.has(name)) continue;
        pool.push(name);
        if (pool.length >= count) break;
    }
    return pool.sort(ethSortKey);
}

function ethSortKey(name) {
    const parts = String(name).replace("Ethernet", "").split("/").map(Number);
    return parts.some((n) => Number.isNaN(n)) ? [0, 0] : parts;
}

function parsePortList(raw) {
    if (Array.isArray(raw)) return raw.map((p) => String(p).trim()).filter(Boolean);
    return String(raw || "")
        .split(/[,;\s]+/)
        .map((s) => s.trim())
        .filter(Boolean);
}

function resolvePresetMembers(preset, hw) {
    const explicit = parsePortList(preset.members);
    if (explicit.length) return explicit;
    const src = preset.members_from || "";
    const fiber = fiberUplinkPool(hw);
    if (src === "fiber_pool") return fiber.slice(0, 2);
    if (src === "fiber_pool_secondary") return fiber.slice(2, 4);
    if (src === "core_pool") return coreUplinkPool(hw, 2);
    return [];
}

function presetCatalog(kind) {
    return kind === "downlink" ? (catalog.downlink_presets || []) : (catalog.uplink_presets || []);
}

function allowedPresetIds(scenarioId, kind) {
    const row = matrixRowForScenario(scenarioId);
    const key = kind === "downlink" ? "downlink_presets" : "uplink_presets";
    return Object.prototype.hasOwnProperty.call(row, key) ? row[key] : null;
}

function buildDefaultRows(kind) {
    const scenarioId = selectedScenario?.id;
    if (!scenarioId) return [];
    const allowed = allowedPresetIds(scenarioId, kind);
    const hw = hardwareProfile();
    const options = kind === "downlink"
        ? (selectedScenario?.defaults?.downlink_options || {})
        : (selectedScenario?.defaults?.uplink_options || {});
    const rows = [];
    presetCatalog(kind).forEach((preset) => {
        let enabled;
        if (Array.isArray(allowed)) {
            if (!allowed.includes(preset.id)) {
                enabled = !!options[preset.id];
            } else {
                enabled = Object.prototype.hasOwnProperty.call(options, preset.id)
                    ? !!options[preset.id]
                    : !!preset.default;
            }
        } else {
            enabled = Object.prototype.hasOwnProperty.call(options, preset.id)
                ? !!options[preset.id]
                : !!preset.default;
        }
        const show = !Array.isArray(allowed) || allowed.includes(preset.id) || !!options[preset.id];
        if (!show && !enabled) return;
        rows.push({
            id: preset.id,
            kind,
            label: preset.label,
            enabled,
            po_id: preset.po_id,
            vpc_id: preset.vpc_id ?? preset.po_id,
            description: preset.description || preset.label,
            members: resolvePresetMembers(preset, hw).join(", "),
            mtu: preset.mtu || "",
            show: true,
        });
    });
    return rows;
}

function resetLinkPlannerFromScenario() {
    linkPlannerCustomized = false;
    linkPlannerRows = {
        downlink: buildDefaultRows("downlink"),
        uplink: buildDefaultRows("uplink"),
    };
    renderLinkPlanner();
}

function shouldShowLinkPlanner() {
    if (!selectedScenario) return false;
    const row = matrixRowForScenario(selectedScenario.id);
    const hasDown = Array.isArray(row.downlink_presets) && row.downlink_presets.length > 0;
    const hasUp = Array.isArray(row.uplink_presets) && row.uplink_presets.length > 0;
    const isVpc = selectedScenario.redundancy === "vpc";
    return hasDown || hasUp || isVpc;
}

function renderLinkPlanner() {
    const card = document.getElementById("cardVpcLinks");
    if (!card) return;
    const show = shouldShowLinkPlanner();
    card.style.display = show ? "block" : "none";
    if (!show) return;

    const hw = hardwareProfile();
    const fiber = fiberUplinkPool(hw);
    const hint = document.getElementById("linkPlannerHint");
    if (hint) {
        hint.textContent = fiber.length
            ? `Fiber uplink pool: ${fiber.join(", ")} (peer-link and keepalive auto-reserved).`
            : "Edit Po ID, members, and descriptions — defaults follow hardware profile.";
    }

    renderLinkSection("downlink", linkPlannerRows.downlink);
    renderLinkSection("uplink", linkPlannerRows.uplink);
}

function renderLinkSection(kind, rows) {
    const tbody = document.getElementById(kind === "downlink" ? "downlinkPlanBody" : "uplinkPlanBody");
    const section = document.getElementById(kind === "downlink" ? "linkSectionDown" : "linkSectionUp");
    if (!tbody || !section) return;
    section.hidden = false;
    if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="link-empty-state">No ${kind}s yet — use <strong>+ Add ${kind}</strong> or the guided questionnaire. Lab OK with defaults.</td></tr>`;
        return;
    }
    tbody.innerHTML = "";
    rows.forEach((row, idx) => {
        const tr = document.createElement("tr");
        tr.className = "link-plan-row";
        tr.dataset.kind = kind;
        tr.dataset.index = String(idx);
        tr.dataset.id = row.id || "";
        tr.innerHTML = `
            <td class="link-plan-toggle">
                <input type="checkbox" class="toggle-input link-enabled" ${row.enabled ? "checked" : ""} aria-label="Enable ${escapeHtml(row.label)}">
            </td>
            <td><input type="text" class="link-plan-label-input" value="${escapeHtml(row.label)}" title="${escapeHtml(row.label)}" aria-label="Preset Name"></td>
            <td><input type="number" class="link-po" min="1" max="4096" value="${row.po_id}" aria-label="Port-channel ID"></td>
            <td><input type="number" class="link-vpc" min="1" max="4096" value="${row.vpc_id}" aria-label="vPC ID"></td>
            <td class="link-members-cell">
                <input type="text" class="link-members" value="${escapeHtml(row.members)}" placeholder="Ethernet1/49, Ethernet1/50" autocomplete="off">
                <button type="button" class="btn-outline btn-xs link-expand" title="Expand range" data-action="expand-link-members">Expand</button>
                <button type="button" class="btn-outline btn-xs link-suggest" title="Suggest free ports" data-action="suggest-members-row">Suggest</button>
            </td>
            <td><input type="text" class="link-desc" value="${escapeHtml(row.description)}" autocomplete="off"></td>
            <td class="link-plan-actions">
                <button type="button" class="btn-ghost btn-xs link-remove" title="Remove row">×</button>
            </td>`;
        tbody.appendChild(tr);
    });
}

function onLinkPlannerChange() {
    linkPlannerCustomized = true;
    syncLinkPlannerFromDom();
    scheduleLivePreview?.();
    refreshCapacityHint?.();
    if (typeof renderTopologyDiagram === "function") renderTopologyDiagram();
    
    // Show topology panel when links are configured
    const topoPanel = document.getElementById("topologyPanel");
    if (topoPanel) {
        const hasLinks = (linkPlannerRows.downlink?.length > 0) || (linkPlannerRows.uplink?.length > 0);
        topoPanel.hidden = !hasLinks;
        if (hasLinks) topoPanel.style.display = "block";
    }
}

function syncLinkPlannerFromDom() {
    ["downlink", "uplink"].forEach((kind) => {
        const tbody = document.getElementById(kind === "downlink" ? "downlinkPlanBody" : "uplinkPlanBody");
        if (!tbody) return;
        const rows = [];
        tbody.querySelectorAll("tr.link-plan-row").forEach((tr) => {
            rows.push({
                id: tr.dataset.id || `${kind}_custom_${rows.length}`,
                kind,
                label: tr.querySelector(".link-plan-label-input")?.value?.trim() || "Custom link",
                enabled: tr.querySelector(".link-enabled")?.checked ?? true,
                po_id: Number(tr.querySelector(".link-po")?.value || 0),
                vpc_id: Number(tr.querySelector(".link-vpc")?.value || 0),
                description: tr.querySelector(".link-desc")?.value?.trim() || "",
                members: tr.querySelector(".link-members")?.value?.trim() || "",
                show: true,
            });
        });
        linkPlannerRows[kind] = rows;
    });
}

function addCustomLinkRow(kind) {
    linkPlannerCustomized = true;
    const nextPo = kind === "downlink" ? 22 : 32;
    linkPlannerRows[kind].push({
        id: `${kind}_custom_${Date.now()}`,
        kind,
        label: kind === "downlink" ? "Custom downlink" : "Custom uplink",
        enabled: true,
        po_id: nextPo,
        vpc_id: nextPo,
        description: kind === "downlink" ? "Connected_to_LEAF_PAIR" : "Connected_to_SPINE_PAIR",
        members: "",
        show: true,
    });
    renderLinkPlanner();
    scheduleLivePreview?.();
    refreshCapacityHint?.();
}

async function expandLinkMembers(btn) {
    const input = btn.closest("td")?.querySelector(".link-members");
    if (!input?.value.trim()) {
        flashToast?.("Please enter a range to expand.", "warn");
        return;
    }
    try {
        const res = await fetch(`/util/expand-range?range_str=${encodeURIComponent(input.value.trim())}`, {
            headers: typeof authHeaders === "function" ? authHeaders(false) : {},
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        input.value = (data.expanded || []).join(", ");
        onLinkPlannerChange();
    } catch (err) {
        flashToast?.(`Expand failed: ${err.message}`, "warn");
    }
}

function applyLinkPlannerDefaults(options = {}) {
    const downOpts = options.downlink_options || selectedScenario?.defaults?.downlink_options || {};
    const upOpts = options.uplink_options || selectedScenario?.defaults?.uplink_options || {};
    linkPlannerCustomized = false;
    linkPlannerRows = {
        downlink: buildDefaultRows("downlink").map((r) => ({
            ...r,
            enabled: Object.prototype.hasOwnProperty.call(downOpts, r.id) ? !!downOpts[r.id] : r.enabled,
        })),
        uplink: buildDefaultRows("uplink").map((r) => ({
            ...r,
            enabled: Object.prototype.hasOwnProperty.call(upOpts, r.id) ? !!upOpts[r.id] : r.enabled,
        })),
    };
    renderLinkPlanner();
}

function getLinkPlannerPayload() {
    syncLinkPlannerFromDom();
    const downlink_options = {};
    const uplink_options = {};
    const downlinks = [];
    const uplinks = [];

    linkPlannerRows.downlink.forEach((row) => {
        if (row.id) downlink_options[row.id] = !!row.enabled;
        if (!row.enabled) return;
        downlinks.push({
            id: row.id,
            enabled: true,
            po_id: row.po_id,
            vpc_id: row.vpc_id,
            description: row.description,
            members: parsePortList(row.members),
            link_kind: "downlink",
        });
    });
    linkPlannerRows.uplink.forEach((row) => {
        if (row.id) uplink_options[row.id] = !!row.enabled;
        if (!row.enabled) return;
        uplinks.push({
            id: row.id,
            enabled: true,
            po_id: row.po_id,
            vpc_id: row.vpc_id,
            description: row.description,
            members: parsePortList(row.members),
            link_kind: "uplink",
            mode: "trunk",
        });
    });

    const out = { downlink_options, uplink_options };
    if (linkPlannerCustomized || downlinks.length) out.downlinks = downlinks;
    if (linkPlannerCustomized || uplinks.length) out.uplinks = uplinks;
    return out;
}

function initLinkPlannerEvents() {
    const root = document.getElementById("cardVpcLinks");
    if (!root || root.dataset.bound) return;
    root.dataset.bound = "1";
    root.addEventListener("change", (e) => {
        if (e.target.closest(".link-plan-row")) onLinkPlannerChange();
    });
    root.addEventListener("input", (e) => {
        if (e.target.matches(".link-po, .link-vpc, .link-members, .link-desc")) onLinkPlannerChange();
    });
    root.addEventListener("click", (e) => {
        const removeBtn = e.target.closest(".link-remove");
        if (removeBtn) {
            const tr = removeBtn.closest("tr");
            const kind = tr?.dataset.kind;
            const idx = Number(tr?.dataset.index);
            if (kind && !Number.isNaN(idx)) {
                linkPlannerRows[kind].splice(idx, 1);
                linkPlannerCustomized = true;
                renderLinkPlanner();
                scheduleLivePreview?.();
    refreshCapacityHint?.();
            }
        }
    });
    root.addEventListener("blur", (e) => {
        if (e.target.matches(".link-po, .link-members")) validateLinkRowAsync(e.target.closest("tr"));
    }, true);
    root.addEventListener("keydown", (e) => {
        const tr = e.target.closest(".link-plan-row");
        if (!tr) return;
        if (e.key === "Enter" && e.target.matches(".link-members")) {
            e.preventDefault();
            tr.querySelector(".link-expand")?.click();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initLinkPlannerEvents();
});

async function validateLinkRowAsync(tr) {
    if (!tr) return;
    syncLinkPlannerFromDom();
    const kind = tr.dataset.kind;
    const idx = Number(tr.dataset.index);
    const row = linkPlannerRows[kind]?.[idx];
    if (!row) return;
    const payload = typeof getLinkPlannerPayload === "function" ? getLinkPlannerPayload() : {};
    const allRows = [...(payload.downlinks || []), ...(payload.uplinks || [])];
    try {
        const res = await fetch("/util/validate-link", {
            method: "POST",
            headers: typeof authHeaders === "function" ? authHeaders() : { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: document.getElementById("model")?.value,
                row: { ...row, po_id: Number(tr.querySelector(".link-po")?.value || row.po_id), members: tr.querySelector(".link-members")?.value },
                peer_link_interfaces: parsePortList(document.getElementById("vpc_pl_ints")?.value),
                keepalive_interfaces: parsePortList(document.getElementById("vpc_ka_ints")?.value),
                link_rows: allRows,
                exclude_po: Number(tr.querySelector(".link-po")?.value),
            }),
        });
        const data = await res.json();
        tr.querySelector(".link-po")?.classList.toggle("input-conflict", !data.valid);
        if (!data.valid && data.suggestions?.next_po_id) {
            showPoConflictDialog(tr, data);
        }
    } catch { /* silent */ }
}

function showPoConflictDialog(tr, data) {
    const modal = document.getElementById("poConflictModal");
    const msg = document.getElementById("poConflictMessage");
    if (!modal || !msg) return;
    msg.textContent = (data.conflicts || []).map((c) => c.message).join(" ");
    modal.dataset.targetKind = tr.dataset.kind;
    modal.dataset.targetIndex = tr.dataset.index;
    modal.dataset.suggestPo = String(data.suggestions?.next_po_id || "");
    modal.classList.remove("hidden");
}

function resolvePoConflict(useNext) {
    const modal = document.getElementById("poConflictModal");
    if (!modal) return;
    const kind = modal.dataset.targetKind;
    const idx = Number(modal.dataset.targetIndex);
    if (useNext && kind && !Number.isNaN(idx)) {
        const po = Number(modal.dataset.suggestPo);
        if (linkPlannerRows[kind]?.[idx]) {
            linkPlannerRows[kind][idx].po_id = po;
            linkPlannerRows[kind][idx].vpc_id = po;
        }
        renderLinkPlanner();
        onLinkPlannerChange();
        pushUndo?.("Po conflict auto-fix");
    }
    modal.classList.add("hidden");
}

async function suggestMembersForRow(btn) {
    const tr = btn.closest("tr");
    if (!tr) return;
    const kind = tr.dataset.kind;
    const pool = kind === "uplink" ? "fiber" : "access";
    try {
        const res = await fetch("/util/suggest-members", {
            method: "POST",
            headers: typeof authHeaders === "function" ? authHeaders() : { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: document.getElementById("model")?.value,
                row: { pool, count: 2 },
                peer_link_interfaces: parsePortList(document.getElementById("vpc_pl_ints")?.value),
                keepalive_interfaces: parsePortList(document.getElementById("vpc_ka_ints")?.value),
                link_rows: typeof getLinkPlannerPayload === "function" ? [...(getLinkPlannerPayload().downlinks || []), ...(getLinkPlannerPayload().uplinks || [])] : [],
            }),
        });
        const data = await res.json();
        const input = tr.querySelector(".link-members");
        if (input && data.ports?.length) {
            input.value = data.ports.join(", ");
            onLinkPlannerChange();
            flashToast?.("Suggested free ports applied.", "ok");
        } else {
            flashToast?.("No free ports available in pool.", "warn");
        }
    } catch (e) {
        flashToast?.("Could not suggest ports.", "warn");
    }
}

function toggleLinkPlannerExpert() {
    const card = document.getElementById("cardVpcLinks");
    const body = document.getElementById("linkPlannerExpertBody");
    const toggle = document.getElementById("linkPlannerExpertToggle");
    if (!body) return;
    const open = body.hidden;
    body.hidden = !open;
    if (toggle) toggle.textContent = open ? "Hide expert table" : "Customize links (expert)";
    if (card) card.classList.toggle("link-planner-compact", !open);
}

