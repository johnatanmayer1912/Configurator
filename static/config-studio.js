/** Configuration Studio v3.1 — live preview, action required, per-option CLI */

let livePreviewTimer = null;
let lastSelectedOptionId = null;
let lastPreviewData = null;

const LIVE_DEBOUNCE_MS = 400;

function formatPreviewError(data) {
    const detail = data?.detail;
    if (!detail) return "Preview unavailable. Check hostname and management IP.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
        return detail.map((d) => {
            const field = (d.loc || []).slice(-1)[0] || "field";
            const msg = String(d.msg || "").replace(/^Value error,\s*/i, "");
            return `${field}: ${msg}`;
        }).join(" · ");
    }
    return "Preview unavailable. Fix validation errors and try again.";
}

function scheduleLivePreview() {
    if (!selectedScenario) return;
    clearTimeout(livePreviewTimer);
    const status = document.getElementById("livePreviewStatus");
    if (status) status.textContent = "Updating preview…";
    livePreviewTimer = setTimeout(runLivePreview, LIVE_DEBOUNCE_MS);
}

async function runLivePreview() {
    if (!selectedScenario) return;
    if (typeof normalizeHostnameField === "function") normalizeHostnameField();
    const hnEl = document.getElementById("hostname");
    const hn = hnEl?.value.trim() || "";
    if (typeof isValidHostname === "function" && !isValidHostname(hn)) {
        renderStudioIdle("Hostname must use letters, numbers, and hyphens only (e.g. CORE1-VPC).");
        const status = document.getElementById("livePreviewStatus");
        if (status) status.textContent = "Fix hostname to preview";
        return;
    }
    const payload = buildScenarioPayload();
    if (!payload.hostname || !payload.mgmt_ip) {
        renderStudioIdle("Enter hostname and management IP to see live preview.");
        return;
    }
    try {
        const res = await fetch("/scenario/preview", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) {
            renderStudioIdle(formatPreviewError(data));
            const status = document.getElementById("livePreviewStatus");
            if (status) status.textContent = "Validation error";
            return;
        }
        lastPreviewData = data;
        lastConfigPreview = data.config_preview || "";
        renderStudioPanels(data);
        updateModelSummary(data.model_meta);
    } catch (err) {
        renderStudioIdle("Live preview error: " + err.message);
    }
}

function renderStudioIdle(msg) {
    const live = document.getElementById("liveCliOutput");
    const status = document.getElementById("livePreviewStatus");
    if (live) live.textContent = msg;
    if (status && !status.textContent) status.textContent = "";
}

function clearConfigStudioPreview() {
    clearTimeout(livePreviewTimer);
    livePreviewTimer = null;
    lastPreviewData = null;
    lastSelectedOptionId = null;
    renderStudioIdle("Start Mode → vPC → Speed to build a new configuration.");
    const box = document.getElementById("selectedCliOutput");
    const label = document.getElementById("selectedCliLabel");
    if (box) box.textContent = "Toggle a feature or baseline option to see its CLI.";
    if (label) label.textContent = "Selected option";
}

function renderStudioPanels(data) {
    renderActionRequired(data.action_required);
    renderSelectedCli(data.cli_blocks, lastSelectedOptionId);
    const live = document.getElementById("liveCliOutput");
    const status = document.getElementById("livePreviewStatus");
    if (live) live.textContent = data.config_preview || "";
    if (status) {
        const labReady = data.action_required?.lab_ready;
        const prod = data.action_required?.production_pending_count ?? 0;
        const planner = (data.planner_warnings || []).length;
        let base = labReady
            ? (prod ? `Lab ready · ${prod} optional for production` : "Lab ready")
            : "Complete required fields";
        if (planner) base += ` · ${planner} planner warning(s)`;
        status.textContent = base;
    }
    if (data.planner_warnings?.length) {
        flashToast?.(data.planner_warnings[0], "warn");
    }
    setOutput(data.config_preview || "");
}

function renderActionRequired(actionData) {
    const box = document.getElementById("actionRequiredList");
    const title = document.getElementById("actionRequiredTitle");
    if (!box) return;

    const lab = actionData?.lab_remarks || [];
    const prod = actionData?.production_remarks || [];
    const labReady = actionData?.lab_ready !== false && lab.filter((r) => r.severity === "required").length === 0;

    if (typeof updateReadinessMeter === "function") {
        updateReadinessMeter({
            lab_ready: labReady,
            items: [
                ...lab.map((r) => ({ tier: "lab", status: r.severity === "required" ? "open" : "ok" })),
                ...prod.map(() => ({ tier: "production", status: "open" })),
            ],
        });
    }
    if (typeof refreshCapacityHint === "function") refreshCapacityHint();

    if (title) {
        if (labReady) {
            title.textContent = prod.length
                ? `Lab ready · ${prod.length} before production`
                : "Lab ready";
        } else {
            title.textContent = `Fix to continue (${lab.length})`;
        }
    }

    if (labReady && !prod.length) {
        box.innerHTML = "<li class='ok-item'>Ready for lab paste — no blockers.</li>";
        return;
    }

    let html = "";
    if (!labReady && lab.length) {
        html += lab.map((r) => formatRemarkLi(r, "remark-required")).join("");
    } else if (labReady) {
        html += "<li class='ok-item'>Ready for lab paste.</li>";
    }
    if (prod.length) {
        html += `<li class="remark-section-head">Before production paste (optional for lab)</li>`;
        html += prod.map((r) => formatRemarkLi(r, r.severity === "required" ? "remark-required" : "remark-recommended")).join("");
    }
    box.innerHTML = html || "<li class='ok-item'>No items.</li>";
}

function formatRemarkLi(r, cls) {
    const step = r.wizard_step ? `Step ${r.wizard_step}` : "";
    return `<li class="${cls}">${escapeHtml(r.message)} ${step ? `<span class="remark-step">${escapeHtml(step)}</span>` : ""}</li>`;
}

function renderSelectedCli(blocks, optionId) {
    const box = document.getElementById("selectedCliOutput");
    const label = document.getElementById("selectedCliLabel");
    if (!box) return;
    const list = blocks || [];
    let block = list.find((b) => b.id === optionId);
    if (!block && list.length) block = list[list.length - 1];
    if (label) label.textContent = block ? `Selected: ${block.label}` : "Selected option";
    box.textContent = block ? block.snippet : "Toggle a feature or baseline option to see its CLI.";
}

function highlightCliBlock(optionId) {
    lastSelectedOptionId = optionId;
    if (lastPreviewData) renderSelectedCli(lastPreviewData.cli_blocks, optionId);
    else {
        const snippet = lookupCatalogCli(optionId);
        const label = document.getElementById("selectedCliLabel");
        const box = document.getElementById("selectedCliOutput");
        if (label) label.textContent = `Selected: ${optionId}`;
        if (box) box.textContent = snippet || "CLI block will appear after preview.";
    }
}

function lookupCatalogCli(optionId) {
    const feat = (catalog.features || []).find((f) => f.id === optionId);
    if (feat?.cli) return feat.cli;
    const base = (catalog.baseline_options || []).find((b) => b.id === optionId);
    if (base?.cli) return base.cli;
    const dl = (catalog.downlink_presets || []).find((d) => d.id === optionId);
    if (dl) return `interface port-channel${dl.po_id}\n  vpc ${dl.vpc_id}\n! ${dl.description}`;
    return "";
}

function updateModelSummary(meta) {
    const el = document.getElementById("modelSummary");
    if (!el || !meta) return;
    const badges = (meta.speed_badges || []).map((s) => `<span class="speed-badge">${escapeHtml(s)}</span>`).join(" ");
    const groups = (meta.port_groups || []).map((g) => `${g.end - g.start + 1}×${g.speed}`).join(", ");
    el.innerHTML = `${badges}<span class="field-note">${escapeHtml(meta.display_name || "")} — ${escapeHtml(groups)}</span>`;
}

function attachStudioListeners() {
    const wizard = document.querySelector(".wizard-panel");
    if (!wizard) return;
    wizard.addEventListener("change", () => { scheduleLivePreview(); updateBadges(); });
    wizard.addEventListener("input", () => { scheduleLivePreview(); updateBadges(); });
    document.getElementById("hostname")?.addEventListener("blur", () => {
        if (typeof normalizeHostnameField === "function") normalizeHostnameField();
        scheduleLivePreview();
    });
    document.getElementById("featureGrid")?.addEventListener("change", (e) => {
        if (e.target.dataset?.feature) highlightCliBlock(e.target.dataset.feature);
    });
    document.getElementById("baselineGrid")?.addEventListener("change", (e) => {
        if (e.target.dataset?.baseline) highlightCliBlock(e.target.dataset.baseline);
    });
    document.getElementById("cardVpcLinks")?.addEventListener("change", (e) => {
        const row = e.target.closest(".link-plan-row");
        if (row && typeof highlightCliBlock === "function") {
            const kind = row.dataset.kind === "downlink" ? "downlink_10g_leaf" : "uplink_fiber_pair";
            highlightCliBlock(kind);
        }
    });
}

function wrapExpandableOptions() {
    document.querySelectorAll("#baselineGrid .toggle-row").forEach((chip) => {
        const input = chip.querySelector("input");
        if (!input) return;
        const id = input.dataset.feature || input.dataset.baseline || input.dataset.downlink;
        chip.addEventListener("click", (e) => {
            if (e.target.tagName === "INPUT") return;
            input.checked = !input.checked;
            input.dispatchEvent(new Event("change", { bubbles: true }));
            highlightCliBlock(id);
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        attachStudioListeners();
        wrapExpandableOptions();
    }, 500);
});
