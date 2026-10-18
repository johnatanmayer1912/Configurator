/** Interface Planner — per-port presets, vPC port-channels, custom CLI */

let interfacePlans = [];

/** Fields that show/hide sections — full re-render. Text fields update model only. */
const STRUCTURAL_PLAN_FIELDS = new Set(["preset", "vpc_port_channel", "mode"]);

function clearInterfacePlans() {
    interfacePlans = [];
    renderInterfacePlanner();
}

function defaultVlanHints() {
    const hints = [];
    const sc = selectedScenario?.defaults || {};
    const base = Number(sc.base_access_vlan || 100);
    const count = Number(sc.access_vlan_count || 4);
    for (let i = 0; i < count; i++) {
        const id = base + i;
        hints.push({ id, name: `FABRIC_${id}` });
    }
    document.querySelectorAll("#vlanList .vlan-row").forEach((row) => {
        const id = Number(row.querySelector(".vlan-id")?.value);
        const name = row.querySelector(".vlan-name")?.value?.trim();
        if (id) hints.push({ id, name: name || `VLAN_${id}` });
    });
    interfacePlans.forEach((p) => {
        if (p.vlan_id) hints.push({ id: Number(p.vlan_id), name: p.vlan_name || `VLAN_${p.vlan_id}` });
    });
    const seen = new Set();
    return hints.filter((h) => {
        if (seen.has(h.id)) return false;
        seen.add(h.id);
        return true;
    });
}

function isVpcPairScenario() {
    if (!selectedScenario) return false;
    return !!(selectedScenario.pair_mode && (selectedScenario.redundancy === "vpc" || selectedScenario.pair_mode));
}

function isVpcPairBuild() {
    const gen = document.getElementById("generate_pair")?.checked;
    return !!(gen && isVpcPairScenario());
}

function presetAllowsVpcPo(presetId) {
    const meta = presetMeta(presetId);
    return meta.allows_vpc_po !== false && !["custom", "bring_up", "routed"].includes(presetId);
}

function wantsVpcPortChannel(plan) {
    if (!isVpcPairScenario() || !presetAllowsVpcPo(plan.preset)) return false;
    if (plan.vpc_port_channel === false) return false;
    return plan.vpc_port_channel === true || ["access_vlan", "trunk_all", "trunk_custom"].includes(plan.preset);
}

function getUsedInterfaces() {
    const used = new Set();
    
    // Get vPC peer-link ports
    const peerLink = document.getElementById("vpc_pl_ints")?.value || "";
    if (peerLink) {
        peerLink.split(",").forEach(p => used.add(p.trim()));
    }
    
    // Get vPC keepalive ports
    const keepalive = document.getElementById("vpc_ka_ints")?.value || "";
    if (keepalive) {
        keepalive.split(",").forEach(p => used.add(p.trim()));
    }
    
    // Get uplink/downlink members from link planner
    if (typeof linkPlannerRows !== "undefined") {
        [...(linkPlannerRows.downlink || []), ...(linkPlannerRows.uplink || [])].forEach(row => {
            if (row.members) {
                row.members.split(",").forEach(p => used.add(p.trim()));
            }
        });
    }
    
    // Get interfaces already used in other plans
    interfacePlans.forEach(plan => {
        if (plan.interface) used.add(plan.interface.trim());
    });
    
    return used;
}

function hardwarePortOptions() {
    const model = document.getElementById("model")?.value;
    const hw = (catalog.hardware || []).find((h) => h.display_name === model);
    const total = hw?.total_ports || 54;
    const ports = [];
    const used = getUsedInterfaces();
    
    for (let i = 1; i <= total; i++) {
        const port = `Ethernet1/${i}`;
        ports.push({
            value: port,
            disabled: used.has(port),
            label: used.has(port) ? `${port} (used)` : port
        });
    }
    return ports;
}

function planFieldEl(planId, field) {
    const card = document.querySelector(`[data-plan-id="${planId}"]`);
    return card?.querySelector(`[data-field="${field}"]`) || null;
}

function addInterfacePlanRow(prefill = {}) {
    const vpcDefault = isVpcPairScenario() && presetAllowsVpcPo(prefill.preset || "access_vlan");
    interfacePlans.push({
        id: `plan_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        interface: prefill.interface || "",
        preset: prefill.preset || "access_vlan",
        vpc_port_channel: prefill.vpc_port_channel ?? vpcDefault,
        mode: prefill.mode || "access",
        vlan_id: prefill.vlan_id || "",
        vlan_name: prefill.vlan_name || "",
        trunk_vlans: prefill.trunk_vlans || "1-4094",
        description: prefill.description || "",
        custom_cli: prefill.custom_cli || "",
    });
    renderInterfacePlanner();
    scheduleLivePreview?.();
}

function removeInterfacePlanRow(planId) {
    interfacePlans = interfacePlans.filter((p) => p.id !== planId);
    renderInterfacePlanner();
    scheduleLivePreview?.();
}

function updateInterfacePlan(planId, field, value) {
    const plan = interfacePlans.find((p) => p.id === planId);
    if (!plan) return;
    plan[field] = value;

    if (field === "vlan_id") {
        const hints = defaultVlanHints();
        const match = hints.find((h) => String(h.id) === String(value));
        if (match && !plan.vlan_name) {
            plan.vlan_name = match.name;
            const nameInput = planFieldEl(planId, "vlan_name");
            if (nameInput) nameInput.value = match.name;
        }
        refreshVlanHintList();
    }

    if (field === "preset") {
        if (value === "custom") {
            plan.vpc_port_channel = false;
        } else if (isVpcPairScenario() && presetAllowsVpcPo(value)) {
            plan.vpc_port_channel = true;
        }
    }

    if (STRUCTURAL_PLAN_FIELDS.has(field)) {
        renderInterfacePlanner();
    }

    scheduleLivePreview?.();
}

function presetMeta(presetId) {
    return (catalog.interface_presets || []).find((p) => p.id === presetId) || {};
}

function refreshPortDatalist() {
    const ports = hardwarePortOptions();
    let dl = document.getElementById("ifacePortList");
    if (!dl) {
        dl = document.createElement("datalist");
        dl.id = "ifacePortList";
        document.body.appendChild(dl);
    }
    // For datalist, we can't disable options, so just show all
    dl.innerHTML = ports.map((p) => `<option value="${escapeHtml(p.value)}"${p.disabled ? ' disabled' : ''}>`).join("");
}

function refreshVlanHintList() {
    const vlanHints = defaultVlanHints();
    let vdl = document.getElementById("vlanHintList");
    if (!vdl) {
        vdl = document.createElement("datalist");
        vdl.id = "vlanHintList";
        document.body.appendChild(vdl);
    }
    vdl.innerHTML = vlanHints.map((v) => `<option value="${v.id}">${escapeHtml(v.name)}</option>`).join("");
}

function renderInterfacePlanner() {
    const list = document.getElementById("interfacePlanList");
    const card = document.getElementById("cardInterfacePlanner");
    if (!list || !card) return;

    const presets = catalog.interface_presets || [];
    const vpcPair = isVpcPairScenario();

    if (!interfacePlans.length) {
        list.innerHTML = `<p class="field-note">No custom interfaces — output is vPC + uplinks only. Click <strong>+ Add interface</strong> to configure server or lab ports.</p>`;
        return;
    }

    list.innerHTML = interfacePlans.map((plan) => {
        const meta = presetMeta(plan.preset);
        const useVpcPo = wantsVpcPortChannel(plan);
        const showVlan = meta.needs_vlan || (useVpcPo && plan.mode === "access");
        const showTrunk = meta.needs_trunk || (useVpcPo && plan.mode === "trunk");
        const showCustom = meta.needs_custom_cli || plan.preset === "custom";
        const allowVpcPo = vpcPair && presetAllowsVpcPo(plan.preset);

        const presetOpts = presets.map((p) =>
            `<option value="${escapeHtml(p.id)}"${plan.preset === p.id ? " selected" : ""}>${escapeHtml(p.label)}</option>`
        ).join("");

        return `<div class="iface-plan-card" data-plan-id="${escapeHtml(plan.id)}">
            <div class="iface-plan-header">
                <strong>Interface</strong>
                <button type="button" class="btn-outline btn-sm" data-action="remove-plan">Remove</button>
            </div>
            <div class="grid-2">
                <div class="form-group">
                    <label>Port</label>
                    <select data-field="interface" class="interface-port-select">
                        <option value="">Select port...</option>
                        ${hardwarePortOptions().map(p => 
                            `<option value="${escapeHtml(p.value)}"${p.disabled ? ' disabled' : ''}${plan.interface === p.value ? ' selected' : ''}>${escapeHtml(p.label)}</option>`
                        ).join("")}
                    </select>
                </div>
                <div class="form-group">
                    <label>Preset</label>
                    <select data-field="preset">${presetOpts}</select>
                    <div class="field-note">${escapeHtml(meta.description || "")}</div>
                </div>
            </div>
            ${allowVpcPo ? `<label class="toggle-row iface-vpc-po-row">
                <span>Build vPC port-channel (Po ≥ ${catalog.interface_po_start || 10})</span>
                <input type="checkbox" class="toggle-input" data-field="vpc_port_channel" ${useVpcPo ? "checked" : ""}>
            </label>` : ""}
            ${useVpcPo && allowVpcPo ? `<div class="iface-mode-row">
                <label><input type="radio" data-field="mode" name="mode_${plan.id}" value="access" ${plan.mode === "access" ? "checked" : ""}> Access</label>
                <label><input type="radio" data-field="mode" name="mode_${plan.id}" value="trunk" ${plan.mode === "trunk" ? "checked" : ""}> Trunk</label>
            </div>` : ""}
            ${showVlan ? `<div class="grid-2">
                <div class="form-group">
                    <label>VLAN ID</label>
                    <input type="number" data-field="vlan_id" min="1" max="4094" list="vlanHintList" value="${escapeHtml(String(plan.vlan_id || ""))}" placeholder="100">
                </div>
                <div class="form-group">
                    <label>VLAN name</label>
                    <input type="text" data-field="vlan_name" value="${escapeHtml(plan.vlan_name || "")}" placeholder="SERVERS_100">
                </div>
            </div>` : ""}
            ${showTrunk ? `<div class="form-group">
                <label>Trunk allowed VLANs</label>
                <input type="text" data-field="trunk_vlans" value="${escapeHtml(plan.trunk_vlans || "1-4094")}">
            </div>` : ""}
            <div class="form-group">
                <label>Description (optional)</label>
                <input type="text" data-field="description" value="${escapeHtml(plan.description || "")}" placeholder="Server_Port_05">
            </div>
            ${showCustom ? `<div class="form-group">
                <label>Custom CLI (one command per line)</label>
                <textarea rows="3" data-field="custom_cli" placeholder="switchport mode access&#10;switchport access vlan 200">${escapeHtml(plan.custom_cli || "")}</textarea>
            </div>` : ""}
        </div>`;
    }).join("");

    refreshPortDatalist();
    refreshVlanHintList();
}

function collectInterfacePlans() {
    syncInterfacePlansFromDom();
    const out = interfacePlans
        .filter((p) => (p.interface || "").trim())
        .map((p) => {
            const row = {
                interface: p.interface.trim(),
                preset: p.preset,
                description: (p.description || "").trim(),
            };
            if (wantsVpcPortChannel(p)) {
                row.vpc_port_channel = true;
                row.mode = p.mode || (String(p.preset).startsWith("trunk") ? "trunk" : "access");
            } else if (isVpcPairScenario() && p.vpc_port_channel === false) {
                row.vpc_port_channel = false;
            }
            const vlanId = Number(p.vlan_id);
            if (vlanId >= 1) row.vlan_id = vlanId;
            if (p.vlan_name) row.vlan_name = p.vlan_name.trim();
            if (p.trunk_vlans) row.trunk_vlans = p.trunk_vlans.trim();
            if (p.custom_cli) row.custom_cli = p.custom_cli.trim();
            return row;
        });
    return out.length ? { interface_plans: out } : {};
}

/** Pull latest values from DOM before build/preview (safety if model drifted). */
function syncInterfacePlansFromDom() {
    document.querySelectorAll("#interfacePlanList [data-plan-id]").forEach((card) => {
        const planId = card.dataset.planId;
        const plan = interfacePlans.find((p) => p.id === planId);
        if (!plan) return;
        card.querySelectorAll("[data-field]").forEach((el) => {
            const field = el.dataset.field;
            if (!field) return;
            if (el.type === "checkbox") plan[field] = el.checked;
            else if (el.type === "radio") {
                if (el.checked) plan[field] = el.value;
            } else plan[field] = el.value;
        });
    });
}

function interfacePlanPreflightErrors() {
    syncInterfacePlansFromDom();
    const errors = [];
    for (const p of interfacePlans) {
        if (!(p.interface || "").trim()) continue;
        if (wantsVpcPortChannel(p) && (p.mode || "access") === "access") {
            const vlanId = Number(p.vlan_id);
            if (!vlanId || vlanId < 1) {
                errors.push(`Interface Planner: ${p.interface.trim()} needs a VLAN ID for vPC port-channel access.`);
            }
        }
    }
    return errors;
}

function initInterfacePlannerEvents() {
    const list = document.getElementById("interfacePlanList");
    if (!list || list.dataset.eventsBound === "1") return;
    list.dataset.eventsBound = "1";

    list.addEventListener("input", (e) => {
        const field = e.target.dataset?.field;
        const card = e.target.closest("[data-plan-id]");
        if (!field || !card || e.target.type === "radio") return;
        updateInterfacePlan(card.dataset.planId, field, e.target.value);
    });

    list.addEventListener("change", (e) => {
        const t = e.target;
        const field = t.dataset?.field;
        const card = t.closest("[data-plan-id]");
        if (!field || !card) return;
        if (t.type === "radio" && !t.checked) return;
        const value = t.type === "checkbox" ? t.checked : t.value;
        updateInterfacePlan(card.dataset.planId, field, value);
    });

    list.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-action='remove-plan']");
        if (!btn) return;
        const card = btn.closest("[data-plan-id]");
        if (card) removeInterfacePlanRow(card.dataset.planId);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initInterfacePlannerEvents();
});
