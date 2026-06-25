/** Port map editor — operator-friendly vPC peer-link / keepalive assignment (UI/UX council). */

let portMapCustomMode = false;

function isGenericModel() {
    const model = document.getElementById("model")?.value || "";
    return model === "Generic" || !model;
}

function shouldShowPortMapEditor() {
    const needsVpc = selectedScenario?.redundancy === "vpc" || (typeof getEnabledFeatures === "function" && getEnabledFeatures().includes("vpc"));
    return needsVpc && (portMapCustomMode || isGenericModel());
}

function syncPortMapEditorVisibility() {
    const panel = document.getElementById("portMapEditorPanel");
    const toggle = document.getElementById("customPortMapToggle");
    if (!panel) return;
    const show = shouldShowPortMapEditor();
    panel.hidden = !show;
    if (toggle) toggle.checked = portMapCustomMode || isGenericModel();
    const pl = document.getElementById("vpc_pl_ints");
    const ka = document.getElementById("vpc_ka_ints");
    const editable = show;
    if (pl) {
        pl.readOnly = !editable;
        pl.classList.toggle("readonly-field", !editable);
        pl.classList.toggle("port-map-editable", editable);
    }
    if (ka) {
        ka.readOnly = !editable;
        ka.classList.toggle("readonly-field", !editable);
        ka.classList.toggle("port-map-editable", editable);
    }
}

function onCustomPortMapToggle() {
    const toggle = document.getElementById("customPortMapToggle");
    portMapCustomMode = !!toggle?.checked;
    if (portMapCustomMode) {
        syncPortMapEditorVisibility();
        flashToast?.("Custom port map enabled — edit peer-link and keepalive ports.", "ok");
    } else if (!isGenericModel()) {
        applyVpcSuggestions?.(true);
        syncPortMapEditorVisibility();
        flashToast?.("Using hardware profile defaults.", "ok");
    }
    scheduleLivePreview?.();
}

function parsePortList(raw) {
    return String(raw || "")
        .split(/[,;\s]+/)
        .map((s) => s.trim())
        .filter(Boolean);
}

function renderPortMapChips() {
    const plChips = document.getElementById("peerLinkChips");
    const kaChips = document.getElementById("keepaliveChips");
    if (!plChips || !kaChips) return;
    const pl = parsePortList(document.getElementById("vpc_pl_ints")?.value);
    const ka = parsePortList(document.getElementById("vpc_ka_ints")?.value);
    const chip = (name) => `<span class="port-chip" title="${escapeHtml(name)}">${escapeHtml(name)}</span>`;
    plChips.innerHTML = pl.length ? pl.map(chip).join("") : "<span class='field-note'>No peer-link ports</span>";
    kaChips.innerHTML = ka.length ? ka.map(chip).join("") : "<span class='field-note'>No keepalive ports</span>";
}

function syncPortFieldsFromEditor() {
    const plRaw = document.getElementById("portMapPeerInput")?.value.trim();
    const kaRaw = document.getElementById("portMapKaInput")?.value.trim();
    if (plRaw) document.getElementById("vpc_pl_ints").value = plRaw;
    if (kaRaw) document.getElementById("vpc_ka_ints").value = kaRaw;
    renderPortMapChips();
    scheduleLivePreview?.();
}

async function expandPortMapRange(target) {
    const inputId = target === "ka" ? "portMapKaInput" : "portMapPeerInput";
    const fieldId = target === "ka" ? "vpc_ka_ints" : "vpc_pl_ints";
    const range = document.getElementById(inputId)?.value.trim();
    if (!range) {
        flashToast?.("Enter a range like Ethernet1/49-50", "warn");
        return;
    }
    try {
        const res = await fetch(`/util/expand-range?range_str=${encodeURIComponent(range)}`, { headers: authHeaders(false) });
        if (!res.ok) throw new Error("expand failed");
        const data = await res.json();
        const expanded = (data.expanded || []).join(", ");
        document.getElementById(inputId).value = expanded;
        document.getElementById(fieldId).value = expanded;
        renderPortMapChips();
        scheduleLivePreview?.();
        flashToast?.("Range expanded.", "ok");
    } catch (e) {
        flashToast?.("Could not expand range.", "err");
    }
}

function initPortMapEditor() {
    const modelSel = document.getElementById("model");
    if (modelSel) {
        modelSel.addEventListener("change", () => {
            if (isGenericModel()) portMapCustomMode = true;
            applyVpcSuggestions?.(!portMapCustomMode && !isGenericModel());
            syncPortMapEditorVisibility();
            renderPortMapChips();
        });
    }
    ["vpc_pl_ints", "vpc_ka_ints"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("input", renderPortMapChips);
    });
    syncPortMapEditorVisibility();
    renderPortMapChips();
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(initPortMapEditor, 0);
});
