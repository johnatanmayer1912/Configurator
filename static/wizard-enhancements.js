/** Wizard UX v5 — modes, progress meter, undo, training, release notes, version diff, hostname hints. */

let wizardMode = localStorage.getItem("nxos_wizard_mode") || "quick";
let trainingMode = localStorage.getItem("nxos_training_mode") === "1";
const undoStack = [];
const MAX_UNDO = 12;
let lastNxosVersion = null;

function pushUndo(label) {
    if (typeof getLinkPlannerPayload !== "function") return;
    undoStack.push({
        label,
        ts: Date.now(),
        snapshot: {
            link: getLinkPlannerPayload(),
            hostname: document.getElementById("hostname")?.value,
            mgmt_ip: document.getElementById("mgmt_ip")?.value,
            mgmt_gw: document.getElementById("mgmt_gw")?.value,
        },
    });
    if (undoStack.length > MAX_UNDO) undoStack.shift();
    renderUndoControl();
}

function restoreUndo() {
    const item = undoStack.pop();
    if (!item) return;
    const s = item.snapshot;
    if (s.hostname) document.getElementById("hostname").value = s.hostname;
    if (s.mgmt_ip) document.getElementById("mgmt_ip").value = s.mgmt_ip;
    if (s.mgmt_gw) document.getElementById("mgmt_gw").value = s.mgmt_gw;
    if (s.link?.downlink_options && typeof applyLinkPlannerDefaults === "function") {
        applyLinkPlannerDefaults(s.link);
    }
    flashToast?.(`Restored: ${item.label}`, "ok");
    renderUndoControl();
    scheduleLivePreview?.();
}

function renderUndoControl() {
    const el = document.getElementById("undoControl");
    if (!el) return;
    if (!undoStack.length) {
        el.hidden = true;
        return;
    }
    el.hidden = false;
    const last = undoStack[undoStack.length - 1];
    el.textContent = `Undo: ${last.label}`;
}

function setWizardMode(mode) {
    wizardMode = mode === "architect" ? "architect" : "quick";
    localStorage.setItem("nxos_wizard_mode", wizardMode);
    document.querySelectorAll("[data-wizard-mode]").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.wizardMode === wizardMode);
    });
    const q = document.getElementById("fabricQuestionnaireCard");
    const topo = document.getElementById("topologyPanel");
    if (q) q.hidden = wizardMode !== "architect";
    if (topo) topo.hidden = wizardMode !== "architect";
    flashToast?.(wizardMode === "architect" ? "Architect mode — questionnaire and topology enabled." : "Quick mode — minimal steps.", "ok");
}

function toggleTrainingMode() {
    trainingMode = !trainingMode;
    localStorage.setItem("nxos_training_mode", trainingMode ? "1" : "0");
    document.body.classList.toggle("training-mode", trainingMode);
    const btn = document.getElementById("trainingModeToggle");
    if (btn) btn.setAttribute("aria-pressed", trainingMode ? "true" : "false");
    flashToast?.(trainingMode ? "Training mode on — extra tips shown." : "Training mode off.", "ok");
}

async function showReleaseNotesModal() {
    const modal = document.getElementById("releaseNotesModal");
    const body = document.getElementById("releaseNotesBody");
    if (!modal || !body) return;
    try {
        const res = await fetch("/release/notes");
        const data = await res.json();
        body.textContent = data.excerpt || `Version ${data.version}`;
        modal.classList.remove("hidden");
    } catch (e) {
        flashToast?.("Could not load release notes.", "warn");
    }
}

function closeReleaseNotesModal() {
    document.getElementById("releaseNotesModal")?.classList.add("hidden");
}

async function onNxosVersionChangeDiff() {
    const sel = document.getElementById("nxos_version");
    if (!sel) return;
    const box = document.getElementById("versionDiffBox");
    const cur = sel.value;
    if (!lastNxosVersion || lastNxosVersion === cur) {
        lastNxosVersion = cur;
        if (box) box.hidden = true;
        return;
    }
    try {
        const res = await fetch(`/util/version-diff?from_id=${encodeURIComponent(lastNxosVersion)}&to_id=${encodeURIComponent(cur)}`, {
            headers: typeof authHeaders === "function" ? authHeaders(false) : {},
        });
        if (!res.ok) throw new Error("diff failed");
        const data = await res.json();
        if (box) {
            box.hidden = !(data.changes || []).length;
            box.innerHTML = (data.changes || [])
                .map((c) => `<div class="version-diff-line ${c.level}">${escapeHtml(c.text)}</div>`)
                .join("");
        }
        lastNxosVersion = cur;
    } catch {
        if (box) box.hidden = true;
    }
}

async function refreshHostnameHints() {
    const host = document.getElementById("hostname")?.value?.trim() || "";
    const site = document.getElementById("site_name")?.value?.trim() || "";
    const role = selectedScenario?.role || roadmap?.mode || "leaf";
    const pair = document.getElementById("generate_pair")?.checked;
    const note = document.getElementById("hostname_hint_box");
    if (!note || !host) return;
    try {
        const q = new URLSearchParams({ hostname: host, site, role, pair: pair ? "true" : "false" });
        const res = await fetch(`/util/hostname-hints?${q}`, { headers: typeof authHeaders === "function" ? authHeaders(false) : {} });
        const data = await res.json();
        const lines = [...(data.hints || [])];
        if (!data.site_valid && site) lines.push(data.site_message);
        note.textContent = lines.length ? lines.join(" · ") : "";
        note.classList.toggle("warn", !data.valid);
    } catch {
        note.textContent = "";
    }
}

function updateReadinessMeter(actionData) {
    const meter = document.getElementById("readinessMeter");
    if (!meter) return;
    const lab = actionData?.lab_ready !== false;
    const items = actionData?.items || [];
    const prod = items.filter((i) => i.tier === "production" && i.status !== "ok");
    const labItems = items.filter((i) => i.tier !== "production" && i.status !== "ok");
    meter.innerHTML = `
        <div class="readiness-row"><span>Lab ready</span><span class="badge ${lab && !labItems.length ? "ok" : "warn"}">${lab && !labItems.length ? "Yes" : "Review"}</span></div>
        <div class="readiness-row"><span>Production</span><span class="badge ${prod.length ? "warn" : "ok"}">${prod.length ? `${prod.length} open` : "Optional OK"}</span></div>`;
}

function enhanceDefaultTooltips() {
    document.querySelectorAll("[data-why-default]").forEach((el) => {
        const key = el.dataset.whyDefault;
        const help = catalog.option_help?.[key] || catalog.field_hints?.[key]?.why;
        if (help && !el.title) el.title = help;
    });
}

function initWizardEnhancements() {
    document.querySelectorAll("[data-wizard-mode]").forEach((btn) => {
        btn.addEventListener("click", () => setWizardMode(btn.dataset.wizardMode));
    });
    setWizardMode(wizardMode);
    if (trainingMode) toggleTrainingMode();

    const verSel = document.getElementById("nxos_version");
    if (verSel) {
        lastNxosVersion = verSel.value;
        verSel.addEventListener("change", () => {
            updateVersionNote?.();
            onNxosVersionChangeDiff();
        });
    }
    ["hostname", "site_name"].forEach((id) => {
        document.getElementById(id)?.addEventListener("input", () => {
            refreshHostnameHints();
        });
    });
    document.getElementById("generate_pair")?.addEventListener("change", refreshHostnameHints);

    const ver = document.getElementById("buildVersion")?.textContent || "";
    if (ver && !sessionStorage.getItem("nxos_release_seen")) {
        sessionStorage.setItem("nxos_release_seen", "1");
        setTimeout(showReleaseNotesModal, 800);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(initWizardEnhancements, 100);
});

function _readLinkRowsForBudget() {
    const rows = typeof linkPlannerRows !== "undefined" ? linkPlannerRows : { downlink: [], uplink: [] };
    const toEntry = (r, kind) => ({
        id: r.id,
        enabled: r.enabled !== false,
        po_id: r.po_id,
        members: typeof parsePortList === "function" ? parsePortList(r.members) : r.members,
        link_kind: kind,
    });
    return [
        ...(rows.downlink || []).filter((r) => r.enabled !== false).map((r) => toEntry(r, "downlink")),
        ...(rows.uplink || []).filter((r) => r.enabled !== false).map((r) => toEntry(r, "uplink")),
    ];
}

async function refreshCapacityHint() {
    const el = document.getElementById("capacityHint");
    if (!el || typeof currentStep === "undefined" || currentStep !== 4) return;
    try {
        const res = await fetch("/util/port-budget", {
            method: "POST",
            headers: typeof authHeaders === "function" ? authHeaders() : { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: document.getElementById("model")?.value,
                row: {},
                peer_link_interfaces: typeof parsePortList === "function" ? parsePortList(document.getElementById("vpc_pl_ints")?.value) : [],
                keepalive_interfaces: typeof parsePortList === "function" ? parsePortList(document.getElementById("vpc_ka_ints")?.value) : [],
                link_rows: _readLinkRowsForBudget(),
            }),
        });
        if (!res.ok) { el.textContent = ""; return; }
        const data = await res.json();
        el.textContent = data.free_count != null
            ? `Port budget: ${data.free_count} free of ${data.total_ports} · fiber: ${(data.fiber_uplink_available || []).slice(0, 4).join(", ")}`
            : "";
    } catch {
        el.textContent = "";
    }
}
