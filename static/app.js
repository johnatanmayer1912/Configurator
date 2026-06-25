/** NX-OS Configuration Authority — Web UI Controller v3.1 */

const sessionToken = ""; // Token authentication removed for offline use
let catalog = { scenarios: [], versions: [], features: [], aliases: [], baseline_options: [], downlink_presets: [], uplink_presets: [], config_matrix: [], hardware: [], field_hints: {}, wizard_tips: {}, option_help: {} };
let selectedScenario = null;
let currentStep = 1;
let vlanCount = 0;
let lastConfigPreview = "";
let lastPrimaryConfig = "";
let lastExportDir = "";
let systemPaths = { vault_dir: "" };

function authHeaders(json = true) {
    const h = {};
    if (json) h["Content-Type"] = "application/json";
    // Token authentication removed for offline use
    return h;
}

function hintFor(fieldId) {
    const h = catalog.field_hints[fieldId];
    if (!h) return "";
    return h.hint || "";
}

function whyFor(fieldId) {
    const h = catalog.field_hints[fieldId];
    return h ? (h.why || "") : "";
}

function attachFieldHints() {
    const map = {
        hostname: "hostname", mgmt_ip: "mgmt_ip", mgmt_gw: "mgmt_gw",
        nxos_version: "nxos_version", vpc_domain: "vpc_domain",
        vpc_pl_ints: "vpc_pl_ints", local_ka: "local_ka", remote_ka: "remote_ka",
    };
    Object.entries(map).forEach(([elId, hintKey]) => {
        const el = document.getElementById(elId);
        const note = document.getElementById(`${elId}_note`);
        if (!el) return;
        const hint = hintFor(hintKey);
        if (hint) el.title = hint;
        if (note && hint) note.textContent = hint;
    });
    updateWizardTip();
}

function updateWizardTip() {
    const box = document.getElementById("wizardTipBox");
    if (!box) return;
    const tip = catalog.wizard_tips[`step_${currentStep}`] || "";
    box.textContent = tip || "Complete each step. Validate before Build.";
}

async function loadCatalog() {
    try {
        const res = await fetch("/catalog");
        if (!res.ok) throw new Error(`Catalog load failed: ${res.status}`);
        catalog = await res.json();
        
        // Validate catalog structure
        if (!catalog.versions || !Array.isArray(catalog.versions)) {
            console.error("Invalid catalog: missing versions array");
            catalog.versions = [];
        }
        if (!catalog.hardware || !Array.isArray(catalog.hardware)) {
            console.error("Invalid catalog: missing hardware array");
            catalog.hardware = [];
        }
        if (!catalog.features || !Array.isArray(catalog.features)) {
            console.error("Invalid catalog: missing features array");
            catalog.features = [];
        }
        if (!catalog.baseline_options || !Array.isArray(catalog.baseline_options)) {
            console.error("Invalid catalog: missing baseline_options array");
            catalog.baseline_options = [];
        }
        if (!catalog.scenarios || !Array.isArray(catalog.scenarios)) {
            console.error("Invalid catalog: missing scenarios array");
            catalog.scenarios = [];
        }
        
        renderScenarios();
        renderVersions();
        renderHardware();
        renderFeatures();
        renderBaselineOptions();
        if (typeof applyLinkPlannerDefaults === "function") applyLinkPlannerDefaults();
        renderAliases();
        attachFieldHints();
        renderModeChoices?.();
    } catch (err) {
        console.error("Catalog load error:", err);
        flashToast?.("Failed to load configuration catalog. Please refresh.", "err");
        // Initialize with empty arrays to prevent crashes
        catalog = {
            versions: [],
            hardware: [],
            features: [],
            baseline_options: [],
            scenarios: [],
            aliases: [],
            config_matrix: [],
            field_hints: {},
            wizard_tips: {},
            option_help: {}
        };
    }
}

function normalizeHostnameField() {
    const el = document.getElementById("hostname");
    if (!el) return;
    const clean = typeof sanitizeHostname === "function" ? sanitizeHostname(el.value) : el.value.replace(/_/g, "-");
    if (clean !== el.value) el.value = clean;
}

async function loadVersion() {
    try {
        const res = await fetch("/version");
        if (res.ok) {
            const data = await res.json();
            const versionEl = document.getElementById("buildVersion");
            const badgeEl = document.getElementById("offlineBadge");
            if (versionEl) versionEl.textContent = `Build ${data.version} · Web · Local`;
            if (badgeEl) badgeEl.textContent = "Offline · Local Engine";
        } else {
            console.error("Version endpoint returned:", res.status);
            const versionEl = document.getElementById("buildVersion");
            if (versionEl) versionEl.textContent = "Build Unknown · Web · Local";
        }
    } catch (err) {
        console.error("Failed to load version:", err);
        const versionEl = document.getElementById("buildVersion");
        if (versionEl) versionEl.textContent = "Build Unknown · Web · Local";
    }
}

function renderScenarios() {
    const grid = document.getElementById("scenarioGrid");
    if (!grid) return;
    const hwNote = document.getElementById("expertHardwareNote");
    if (hwNote && catalog.hardware?.length) {
        const names = catalog.hardware.map((h) => h.display_name).filter(Boolean).join(" · ");
        hwNote.textContent = `Hardware profiles: ${names}`;
    }
    catalog.scenarios.forEach((s) => {
        const row = catalog.config_matrix?.find((m) => m.scenario_id === s.id);
        const speed = row?.speed_tier || "";
        const model = s.defaults?.model || "";
        const card = document.createElement("button");
        card.type = "button";
        card.className = "scenario-card";
        card.dataset.id = s.id;
        const tag = `${s.redundancy === "vpc" ? "vPC" : "Standalone"} · ${s.role}${speed ? ` · ${speed}` : ""}${model ? ` · ${model}` : ""}`;
        const speedBadge = speed ? `<span class="speed-badge">${escapeHtml(speed)}</span>` : "";
        card.innerHTML = `<div class="scenario-name">${escapeHtml(s.name)} ${speedBadge}</div>
            <div class="scenario-desc">${escapeHtml(s.description)}</div>
            <div class="scenario-tag">${tag}</div>`;
        card.onclick = () => selectScenario(s.id, card);
        grid.appendChild(card);
    });
}

function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function selectScenario(id, el) {
    selectedScenario = catalog.scenarios.find((s) => s.id === id);
    document.querySelectorAll(".scenario-card").forEach((c) => c.classList.remove("selected"));
    if (el) el.classList.add("selected");
    const help = document.getElementById("scenarioHelp");
    if (help) help.innerHTML = `<strong>${escapeHtml(selectedScenario.name)}</strong><br>${escapeHtml(selectedScenario.help || selectedScenario.description)}`;
    syncRoadmapFromScenario?.(selectedScenario);
    applyScenarioDefaults();
    renderInterfacePlanner?.();
    updateBadges();
    scheduleLivePreview?.();
}

function applyScenarioDefaults() {
    if (!selectedScenario) return;
    const d = selectedScenario.defaults || {};
    document.getElementById("hostname").value = sanitizeHostname?.(d.hostname || guessHostname(selectedScenario)) || (d.hostname || guessHostname(selectedScenario)).replace(/_/g, "-");
    document.getElementById("site_name").value = "HQ_DC";
    document.getElementById("network_name").value = "HQ_DC";
    document.getElementById("site_location").value = "HQ_DC";
    document.getElementById("mgmt_ip").value = "10.10.10.10/24";
    document.getElementById("mgmt_gw").value = "10.10.10.1";
    document.getElementById("motd").value = d.motd || "Authorized Access Only";
    if (d.security_tier) document.getElementById("security_tier").value = d.security_tier;
    document.getElementById("ntp_server").value = d.ntp_server || "10.255.255.254";
    document.getElementById("logging_host").value = d.logging_host || "10.255.255.254";
    if (d.model) document.getElementById("model").value = d.model;
    if (d.nxos_version) document.getElementById("nxos_version").value = d.nxos_version;
    document.getElementById("generate_pair").checked = !!selectedScenario.pair_mode;
    const bringUp = document.getElementById("bring_up_spare_ports");
    if (bringUp) bringUp.checked = d.bring_up_spare_ports !== false;
    document.getElementById("vpc_domain").value = d.vpc_domain_id || 100;
    document.getElementById("vpc_pl_id").value = d.vpc_peer_link_id ?? 1;
    applyVpcSuggestions(true);
    applyBaselineDefaults(d.baseline_options || []);
    if (typeof applyLinkPlannerDefaults === "function") {
        applyLinkPlannerDefaults({ downlink_options: d.downlink_options || {}, uplink_options: d.uplink_options || {} });
    }
    if (d.keepalive_vrf) document.getElementById("keepalive_vrf").value = d.keepalive_vrf;
    if (d.local_keepalive_ip) document.getElementById("local_ka").value = d.local_keepalive_ip;
    if (d.remote_keepalive_ip) document.getElementById("remote_ka").value = d.remote_keepalive_ip;
    if (d.keepalive_po_id) document.getElementById("vpc_ka_po").value = d.keepalive_po_id;
    applyFeatureDefaults(d.features || []);
    updateVersionNote();
    updateVpcVisibility();
    syncFeatureDependencies();
    if (typeof wrapExpandableOptions === "function") setTimeout(wrapExpandableOptions, 100);
    scheduleLivePreview?.();
}

function guessHostname(s) {
    const map = { access: "ACCESS-SW-01", leaf: "DC-LEAF-01-A", spine: "CORE1-VPC" };
    return map[s.role] || "NXOS-SW-01";
}

function renderVersions() {
    const sel = document.getElementById("nxos_version");
    if (!sel) {
        console.error("nxos_version select element not found");
        return;
    }
    sel.innerHTML = "";
    if (!catalog.versions || catalog.versions.length === 0) {
        const opt = document.createElement("option");
        opt.value = "9.3";
        opt.textContent = "NX-OS 9.3.x (Default)";
        sel.appendChild(opt);
        console.warn("No versions in catalog, using default");
    } else {
        catalog.versions.forEach((v) => {
            const opt = document.createElement("option");
            opt.value = v.id;
            const star = v.min_recommended ? " ★" : "";
            opt.textContent = `${v.label}${star}`;
            opt.title = v.notes || v.label;
            sel.appendChild(opt);
        });
    }
    sel.onchange = updateVersionNote;
}

function updateVersionNote() {
    const id = document.getElementById("nxos_version").value;
    const v = catalog.versions.find((x) => x.id === id);
    const note = document.getElementById("versionNote");
    if (note) note.textContent = v ? v.notes : "";
    const why = document.getElementById("nxos_version_why");
    if (why) why.textContent = whyFor("nxos_version");
}

function renderHardware() {
    const sel = document.getElementById("model");
    if (!sel) {
        console.error("model select element not found");
        return;
    }
    sel.innerHTML = "";
    if (!catalog.hardware || catalog.hardware.length === 0) {
        const opt = document.createElement("option");
        opt.value = "Generic";
        opt.textContent = "Generic (Default)";
        sel.appendChild(opt);
        console.warn("No hardware profiles in catalog, using default");
    } else {
        catalog.hardware.forEach((h) => {
            const opt = document.createElement("option");
            opt.value = h.display_name;
            const badge = h.primary_speed_label || (h.speed_badges || [])[0] || "";
            const cls = h.device_class ? ` · ${h.device_class}` : "";
            opt.textContent = `${h.display_name}${badge ? ` · ${badge}` : ""}${cls}`;
            sel.appendChild(opt);
        });
    }
    sel.onchange = () => {
        applyVpcSuggestions(true);
        if (!linkPlannerCustomized && typeof resetLinkPlannerFromScenario === "function") resetLinkPlannerFromScenario();
        scheduleLivePreview?.();
    };
}

function featureEnabled(id) {
    const cb = document.querySelector(`#featureGrid input[data-feature="${id}"]`);
    return cb ? cb.checked : false;
}

function syncFeatureDependencies() {
    const vpcOn = featureEnabled("vpc") || selectedScenario?.redundancy === "vpc";
    document.querySelectorAll("#featureGrid input[data-feature]").forEach((cb) => {
        const meta = catalog.features.find((f) => f.id === cb.dataset.feature);
        if (!meta) return;
        let blocked = false;
        let reason = "";
        if (meta.requires_feature && !featureEnabled(meta.requires_feature)) {
            blocked = true;
            reason = `Requires ${meta.requires_feature}`;
        }
        if (meta.requires_redundancy === "vpc" && selectedScenario?.redundancy !== "vpc" && !featureEnabled("vpc")) {
            blocked = true;
            reason = "Requires vPC scenario or vpc feature";
        }
        cb.disabled = blocked;
        cb.closest(".feature-chip")?.classList.toggle("feature-blocked", blocked);
        if (blocked) {
            cb.checked = false;
            cb.title = reason;
        }
    });
    updateVpcVisibility();
    updateHsrpCardVisibility();
}

function updateHsrpCardVisibility() {
    const card = document.getElementById("cardHsrpGateway");
    if (!card) return;
    const show = featureEnabled("hsrp");
    card.hidden = !show;
    card.style.display = show ? "block" : "none";
}

function renderFeatures() {
    const grid = document.getElementById("featureGrid");
    if (!grid) return;
    grid.innerHTML = "";
    catalog.features.forEach((f) => {
        const label = document.createElement("label");
        label.className = "toggle-row";
        label.title = f.description;
        label.appendChild(typeof labelWithInfo === "function" ? labelWithInfo(f.label, f.id) : document.createTextNode(f.label));
        const input = document.createElement("input");
        input.type = "checkbox";
        input.className = "toggle-input";
        input.dataset.feature = f.id;
        if (f.default) input.checked = true;
        label.appendChild(input);
        grid.appendChild(label);
    });
    grid.addEventListener("change", syncFeatureDependencies);
    if (typeof wrapExpandableOptions === "function") wrapExpandableOptions();
}

function renderBaselineOptions() {
    const grid = document.getElementById("baselineGrid");
    if (!grid) {
        console.error("baselineGrid element not found");
        return;
    }
    grid.innerHTML = "";
    const options = catalog.baseline_options || [];
    if (options.length === 0) {
        const msg = document.createElement("div");
        msg.className = "field-note";
        msg.textContent = "No baseline options available";
        grid.appendChild(msg);
        console.warn("No baseline options in catalog");
        return;
    }
    options.forEach((b) => {
        const label = document.createElement("label");
        label.className = "toggle-row";
        label.title = b.description || "";
        const labelText = typeof labelWithInfo === "function" ? labelWithInfo(b.label, b.id) : document.createTextNode(b.label);
        label.appendChild(labelText);
        const input = document.createElement("input");
        input.type = "checkbox";
        input.className = "toggle-input";
        input.dataset.baseline = b.id;
        if (b.default) input.checked = true;
        label.appendChild(input);
        grid.appendChild(label);
    });
    if (typeof wrapExpandableOptions === "function") wrapExpandableOptions();
}

function renderDownlinkPresets() {
    const grid = document.getElementById("downlinkGrid");
    if (!grid) return;
    grid.innerHTML = "";
    (catalog.downlink_presets || []).forEach((d) => {
        const label = document.createElement("label");
        label.className = "toggle-row";
        label.title = d.description;
        label.appendChild(typeof labelWithInfo === "function" ? labelWithInfo(d.label, d.id) : document.createTextNode(d.label));
        const input = document.createElement("input");
        input.type = "checkbox";
        input.className = "toggle-input";
        input.dataset.downlink = d.id;
        if (d.default) input.checked = true;
        label.appendChild(input);
        grid.appendChild(label);
    });
    if (typeof wrapExpandableOptions === "function") wrapExpandableOptions();
}

function applyConfigPreset(preset) {
    const hardenedBaselines = [
        "baseline_copp", "baseline_no_dns_lookup", "baseline_icmp_redirects",
        "baseline_errdisable_recovery", "baseline_logging_source", "baseline_snmp_traps",
        "baseline_cli_aliases", "baseline_cfs",
    ];
    const standardBaselines = (catalog.baseline_options || []).filter((b) => b.default).map((b) => b.id);

    document.querySelectorAll("#baselineGrid input[data-baseline]").forEach((cb) => {
        const on = preset === "hardened" ? hardenedBaselines.includes(cb.dataset.baseline) : standardBaselines.includes(cb.dataset.baseline);
        cb.checked = on;
    });
    document.querySelectorAll("#featureGrid input[data-feature]").forEach((cb) => {
        const id = cb.dataset.feature;
        if (preset === "hardened") {
            if (id === "nxapi" || id === "bash") cb.checked = false;
            if (id === "ntp" || id === "logging") cb.checked = true;
            if (id === "aaa_tacacs") cb.checked = true;
        } else {
            const meta = catalog.features.find((f) => f.id === id);
            cb.checked = !!meta?.default;
        }
    });
    if (preset === "hardened") {
        document.getElementById("security_tier").value = "hardened";
        onSecurityTierChange();
    } else {
        document.getElementById("security_tier").value = "standard";
    }
    syncFeatureDependencies();
    flashToast(preset === "hardened" ? "Hardened preset applied — review toggles and fill TACACS placeholders." : "Standard preset applied.", "ok");
    scheduleLivePreview?.();
    updateBadges();
}

function applyBaselineDefaults(ids) {
    document.querySelectorAll("#baselineGrid input[data-baseline]").forEach((cb) => {
        cb.checked = ids.includes(cb.dataset.baseline);
    });
}

function applyDownlinkDefaults(options) {
    document.querySelectorAll("#downlinkGrid input[data-downlink]").forEach((cb) => {
        const id = cb.dataset.downlink;
        if (Object.prototype.hasOwnProperty.call(options, id)) {
            cb.checked = !!options[id];
        }
    });
}

function getBaselineOptions() {
    return [...document.querySelectorAll("#baselineGrid input[data-baseline]:checked")].map((cb) => cb.dataset.baseline);
}

function getDownlinkOptions() {
    const out = {};
    document.querySelectorAll("#downlinkGrid input[data-downlink]").forEach((cb) => {
        out[cb.dataset.downlink] = cb.checked;
    });
    return out;
}

function renderAliases() {
    const list = document.getElementById("aliasList");
    list.innerHTML = "";
    (catalog.aliases || []).forEach((a) => {
        const item = document.createElement("details");
        item.className = "alias-item";
        item.innerHTML = `<summary>${escapeHtml(a.label)}</summary><pre>${escapeHtml(a.snippet)}</pre><p class="field-note">${escapeHtml(a.description)}</p>`;
        list.appendChild(item);
    });
}

function applyFeatureDefaults(ids) {
    document.querySelectorAll("#featureGrid input[data-feature]").forEach((cb) => {
        cb.checked = ids.includes(cb.dataset.feature);
    });
    syncFeatureDependencies();
}

function getEnabledFeatures() {
    return [...document.querySelectorAll("#featureGrid input[data-feature]:checked")].map((cb) => cb.dataset.feature);
}

function applyVpcSuggestions(force = false) {
    const model = document.getElementById("model").value;
    const hw = catalog.hardware.find((h) => h.display_name === model);
    const hint = document.getElementById("vpcPortHint");
    const kaHint = document.getElementById("vpcKaHint");
    const plField = document.getElementById("vpc_pl_ints");
    const kaField = document.getElementById("vpc_ka_ints");
    const hasUserPorts = plField && plField.value.trim().length > 0;
    const hasKaPorts = kaField && kaField.value.trim().length > 0;
    if (hw && hw.vpc_peer_link?.length) {
        if (force || !hasUserPorts) {
            plField.value = hw.vpc_peer_link.join(", ");
        }
        if (kaField && (force || !hasKaPorts) && hw.vpc_keepalive?.length) {
            kaField.value = hw.vpc_keepalive.join(", ");
        }
        const portNote = `Suggested peer-link: ${hw.vpc_peer_link.join(", ")} | keepalive: ${(hw.vpc_keepalive || []).join(", ")}`;
        if (hint) hint.textContent = portNote;
        if (kaHint) kaHint.textContent = portNote;
    } else {
        const fallback = hintFor("vpc_pl_ints") || "Select a hardware model for port suggestions.";
        if (hint) hint.textContent = fallback;
        if (kaHint) kaHint.textContent = fallback;
    }
}

function updateVpcVisibility() {
    const needsVpc = selectedScenario?.redundancy === "vpc" || getEnabledFeatures().includes("vpc");
    const card = document.getElementById("cardVpcWiring");
    if (card) card.style.display = needsVpc ? "block" : "none";
    if (typeof renderLinkPlanner === "function") renderLinkPlanner();
    if (typeof syncPortMapEditorVisibility === "function") syncPortMapEditorVisibility();
}

function wizardNav(dir) {
    if (dir > 0) {
        const errors = preflightErrorsForStep(currentStep);
        if (errors.length) {
            flashToast(errors[0], "warn");
            updateBadges();
            return;
        }
    }
    goToStep(Math.max(1, Math.min(5, currentStep + dir)));
}

function goToStep(n) {
    if (n > currentStep) {
        for (let s = currentStep; s < n; s++) {
            const errors = preflightErrorsForStep(s);
            if (errors.length) {
                flashToast(`Step ${s}: ${errors[0]}`, "warn");
                return;
            }
        }
    }
    currentStep = n;
    document.querySelectorAll(".wizard-step").forEach((s) => s.classList.remove("active"));
    document.getElementById(`step-${n}`).classList.add("active");
    document.querySelectorAll(".step-btn").forEach((b) => {
        const step = Number(b.dataset.step);
        b.classList.toggle("active", step === n);
        b.classList.toggle("done", step < n);
        b.setAttribute("aria-current", step === n ? "step" : "false");
    });
    if (n === 5) buildReviewPayload();
    if (n === 4) {
        applyRoadmapToWizard?.();
        applyVpcSuggestions(true);
        updateVpcVisibility();
        if (typeof resetLinkPlannerFromScenario === "function") resetLinkPlannerFromScenario();
        renderConfigureCards?.();
        renderInterfacePlanner?.();
    }
    onRoadmapStepEnter?.(n);
    updateWizardTip();
}

document.querySelectorAll(".step-btn").forEach((btn) => {
    btn.onclick = () => goToStep(Number(btn.dataset.step));
});

function preflightErrorsForStep(step) {
    if (step === 1) {
        if (selectedScenario) return [];
        return typeof roadmapStepValid === "function" && roadmapStepValid(1) ? [] : ["Choose a switch role (Mode)."];
    }
    if (step === 2) {
        if (selectedScenario) return [];
        return typeof roadmapStepValid === "function" && roadmapStepValid(2) ? [] : ["Choose vPC yes or no."];
    }
    if (step === 3) {
        if (selectedScenario) return [];
        return typeof roadmapStepValid === "function" && roadmapStepValid(3) ? [] : ["Choose a port speed tier."];
    }
    if (step >= 4) {
        const errors = [];
        normalizeHostnameField();
        const hn = document.getElementById("hostname").value.trim();
        if (!hn) errors.push("Hostname is required.");
        if (hn && !/^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$/.test(hn)) errors.push("Hostname: letters, numbers, hyphens only (no underscores).");
        if (!document.getElementById("mgmt_ip").value.includes("/")) errors.push("Management IP must include CIDR (e.g. 10.0.0.1/24).");
        if (!document.getElementById("mgmt_gw").value.trim()) errors.push("Management gateway is required.");
        if (!selectedScenario) errors.push("Complete Mode → vPC → Speed steps first.");
        const needsVpc = selectedScenario?.redundancy === "vpc" || getEnabledFeatures().includes("vpc");
        if (needsVpc) {
            if (!document.getElementById("local_ka").value.trim()) errors.push("Local keepalive IP required for vPC.");
            if (!document.getElementById("remote_ka").value.trim()) errors.push("Remote keepalive IP required for vPC.");
            if (!document.getElementById("vpc_pl_ints").value.trim()) errors.push("Peer-link interfaces required for vPC.");
        }
        if (typeof interfacePlanPreflightErrors === "function") {
            errors.push(...interfacePlanPreflightErrors());
        }
        return errors;
    }
    return [];
}

function preflightErrors() {
    const all = [];
    for (let s = 1; s <= 4; s++) all.push(...preflightErrorsForStep(s));
    return [...new Set(all)];
}

function updateBadges() {
    const errors = preflightErrors();
    const ok = errors.length === 0;
    document.getElementById("globalReadyBadge").className = ok ? "badge ok" : "badge err";
    document.getElementById("globalReadyBadge").textContent = ok ? "Ready to Build" : `${errors.length} issue(s)`;
    document.getElementById("scenarioBadge").textContent = selectedScenario ? `Scenario: ${selectedScenario.name}` : "Scenario: —";
    document.getElementById("scenarioBadge").className = selectedScenario ? "badge ok" : "badge err";
    document.getElementById("identityBadge").className = ok ? "badge ok" : "badge err";
    document.getElementById("identityBadge").textContent = ok ? "Identity: Ready" : "Identity: Pending";
    document.getElementById("generateBtn").disabled = !ok;
    const pre = document.getElementById("preflightList");
    if (pre) pre.innerHTML = errors.length ? errors.map((e) => `<li>${escapeHtml(e)}</li>`).join("") : "<li class='ok-item'>All preflight checks passed.</li>";
}

function onSecurityTierChange() {
    const tier = document.getElementById("security_tier").value;
    if (tier === "hardened") {
        document.querySelectorAll('#featureGrid input[data-feature="nxapi"], #featureGrid input[data-feature="bash"]').forEach(cb => { cb.checked = false; });
        const logCb = document.querySelector('#featureGrid input[data-feature="logging"]');
        const ntpCb = document.querySelector('#featureGrid input[data-feature="ntp"]');
        if (logCb) logCb.checked = true;
        if (ntpCb) ntpCb.checked = true;
        if (!document.getElementById("logging_host").value) document.getElementById("logging_host").value = "10.255.255.254";
        flashToast("Hardened tier: NX-API/bash disabled, syslog/NTP enforced.", "ok");
    }
    syncFeatureDependencies();
    updateBadges();
}

function collectManualOverrides() {
    const custom_vlans = [];
    const custom_svis = [];
    document.querySelectorAll("#vlanList .vlan-row").forEach((row) => {
        const vid = row.querySelector(".vlan-id")?.value;
        const name = row.querySelector(".vlan-name")?.value;
        const sviIp = row.querySelector(".svi-ip")?.value;
        if (vid) custom_vlans.push({ id: Number(vid), name: name || undefined });
        if (vid && sviIp) custom_svis.push({ vlan_id: Number(vid), ip_address: sviIp });
    });
    const hsrpVlan = document.getElementById("hsrp_vlan_id")?.value?.trim();
    const hsrpSvi = document.getElementById("hsrp_svi_ip")?.value?.trim();
    if (hsrpVlan && hsrpSvi && featureEnabled("hsrp")) {
        const vid = Number(hsrpVlan);
        if (vid >= 1 && vid <= 4094) {
            custom_svis.push({ vlan_id: vid, ip_address: hsrpSvi });
            custom_vlans.push({ id: vid, name: `HSRP_${vid}` });
        }
    }
    const ifaceLines = document.getElementById("interfacesArea")?.value.trim() || "";
    const out = {};
    if (custom_vlans.length) out.custom_vlans = custom_vlans;
    if (custom_svis.length) out.custom_svis = custom_svis;
    if (ifaceLines) out.interface_lines = ifaceLines;
    return out;
}

function buildScenarioPayload() {
    normalizeHostnameField();
    const features = getEnabledFeatures();
    if (document.getElementById("snmp_location").value.trim()) features.push("snmp");
    const spectrumEl = document.getElementById("spectrum_user");
    return {
        scenario_id: selectedScenario?.id,
        hostname: document.getElementById("hostname").value.trim(),
        site_name: document.getElementById("site_name").value.trim() || "DEFAULT_SITE",
        mgmt_ip: document.getElementById("mgmt_ip").value.trim(),
        mgmt_gw: document.getElementById("mgmt_gw").value.trim(),
        generate_pair: document.getElementById("generate_pair").checked,
        overrides: {
            model: document.getElementById("model").value,
            nxos_version: document.getElementById("nxos_version").value,
            motd: document.getElementById("motd").value,
            security_tier: document.getElementById("security_tier").value,
            features: [...new Set(features)],
            vpc_domain_id: Number(document.getElementById("vpc_domain").value),
            vpc_peer_link_id: Number(document.getElementById("vpc_pl_id").value),
            peer_link_interfaces: document.getElementById("vpc_pl_ints").value.trim(),
            keepalive_interfaces: document.getElementById("vpc_ka_ints")?.value.trim() || "",
            keepalive_vrf: document.getElementById("keepalive_vrf")?.value.trim() || "management",
            keepalive_po_id: Number(document.getElementById("vpc_ka_po")?.value || 2),
            baseline_options: getBaselineOptions(),
            ...(typeof getLinkPlannerPayload === "function" ? getLinkPlannerPayload() : {}),
            bring_up_spare_ports: document.getElementById("bring_up_spare_ports")?.checked !== false,
            local_keepalive_ip: document.getElementById("local_ka").value.trim(),
            remote_keepalive_ip: document.getElementById("remote_ka").value.trim(),
            ntp_server: document.getElementById("ntp_server").value.trim(),
            logging_host: document.getElementById("logging_host").value.trim(),
            snmp_location: document.getElementById("snmp_location").value.trim(),
            site_location: document.getElementById("site_location")?.value.trim() || "",
            network_name: document.getElementById("network_name")?.value.trim() || document.getElementById("site_name").value.trim(),
            snmp_trap_host_1: document.getElementById("snmp_trap_host_1")?.value.trim() || "",
            snmp_trap_host_2: document.getElementById("snmp_trap_host_2")?.value.trim() || "",
            snmp_v3_user: document.getElementById("snmp_v3_user")?.value.trim() || "",
            boot_image: document.getElementById("boot_image")?.value.trim() || "",
            tacacs_server_1: document.getElementById("tacacs_server_1")?.value.trim() || "",
            tacacs_key: document.getElementById("tacacs_key")?.value.trim() || "",
            spectrum_user: spectrumEl?.type === "checkbox" ? spectrumEl.checked : false,
            admin_user: document.getElementById("admin_user").value.trim(),
            admin_password: document.getElementById("admin_password").value,
            inject_cli_reference: document.getElementById("inject_cli_reference")?.checked || false,
            export_dir: document.getElementById("exportDir")?.value.trim() || "",
            ...collectManualOverrides(),
            ...collectInterfacePlans?.(),
        },
    };
}

function buildReviewPayload() {
    document.getElementById("payloadReview").textContent = JSON.stringify(buildScenarioPayload(), null, 2);
    updateBadges();
}

async function requestBuild() {
    const errors = preflightErrors();
    if (errors.length) {
        setOutput("Preflight blocked:\n- " + errors.join("\n- "));
        return;
    }
    if (needsHardenedSecretsConfirm()) {
        document.getElementById("hardenedSecretsModal")?.classList.remove("hidden");
        return;
    }
    await runScenario("generate");
}

function needsHardenedSecretsConfirm() {
    const tier = document.getElementById("security_tier")?.value;
    if (tier !== "hardened") return false;
    const tacacs = document.getElementById("tacacs_key")?.value?.trim();
    const adminPw = document.getElementById("admin_password")?.value?.trim();
    return !!(tacacs || adminPw);
}

function closeHardenedSecretsModal() {
    document.getElementById("hardenedSecretsModal")?.classList.add("hidden");
}

async function confirmHardenedBuild() {
    closeHardenedSecretsModal();
    await runScenario("generate");
}

async function runScenario(mode) {
    const errors = preflightErrors();
    if (errors.length) {
        setOutput("Preflight blocked:\n- " + errors.join("\n- "));
        return;
    }
    setBusy(true);
    setOutput(mode === "preview" ? "Validating and rendering preview..." : "Building configuration...");
    const endpoint = mode === "preview" ? "/scenario/preview" : "/scenario/generate";
    try {
        const res = await fetch(endpoint, { method: "POST", headers: authHeaders(), body: JSON.stringify(buildScenarioPayload()) });
        const result = await res.json();
        if (!res.ok) {
            setOutput(`Error (${res.status}):\n${JSON.stringify(result, null, 2)}`);
            return;
        }
        if (mode === "preview") {
            lastConfigPreview = result.config_preview || "";
            if (result.action_required) renderActionRequired?.(result.action_required);
            if (result.cli_blocks) renderSelectedCli?.(result.cli_blocks, lastSelectedOptionId);
            const live = document.getElementById("liveCliOutput");
            if (live) live.textContent = lastConfigPreview;
            setOutput(formatPreview(result) + "\n\n--- CLI PREVIEW ---\n\n" + lastConfigPreview);
            if (result.pair_preview?.secondary_config_preview) {
                setOutput(document.getElementById("statusOutput").textContent + "\n\n--- SECONDARY CLI PREVIEW ---\n\n" + result.pair_preview.secondary_config_preview);
            }
            showCompliance(result.compliance_findings);
            if (result.pair_preview?.pair_validation?.errors?.length) {
                flashToast("vPC pair validation: " + result.pair_preview.pair_validation.errors.join("; "), "warn");
            }
        } else {
            lastPrimaryConfig = (result.results || [])[0]?.config_preview || "";
            const parts = (result.results || []).map((r) => `=== ${r.hostname} ===\n${r.config_preview || r.message}`);
            setOutput(parts.join("\n\n"));
            showCompliance(result.compliance_findings);
            fetchVault();
            fetchCheckpoints();
            if (result.export) showBuildSuccess(result.export, lastPrimaryConfig);
            else flashToast("Configuration built successfully.", "ok");
        }
    } catch (err) {
        setOutput("Engine error: " + err.message);
        flashToast(err.message, "err");
    } finally {
        setBusy(false);
    }
}

function setBusy(on) {
    document.getElementById("generateBtn").disabled = on || preflightErrors().length > 0;
    document.querySelectorAll(".btn-secondary, .wizard-footer .btn-primary").forEach((b) => { b.disabled = on; });
}

function formatPreview(r) {
    let text = `Scenario: ${r.scenario_name}\nNX-OS: ${r.nxos_version}\nStatus: ${r.status}\n\n`;
    text += "Summary:\n" + (r.summary_lines || []).map((l) => "  • " + l).join("\n") + "\n";
    if (r.validation_errors?.length) text += "\nValidation:\n" + r.validation_errors.join("\n");
    if (r.pair_preview) text += `\nvPC Pair: ${r.pair_preview.primary.hostname} + ${r.pair_preview.secondary_hostname}\n`;
    return text;
}

function showCompliance(findings) {
    const panel = document.getElementById("compliancePanel");
    const list = document.getElementById("complianceList");
    if (!findings?.length) { panel.style.display = "none"; return; }
    panel.style.display = "block";
    list.innerHTML = findings.map((f) => `<div class="finding-${f.level}">[${f.level.toUpperCase()}] ${escapeHtml(f.message)}</div>`).join("");
}

function setOutput(text) {
    const el = document.getElementById("statusOutput");
    const live = document.getElementById("liveCliOutput");
    if (el) el.textContent = text;
    if (live && text.includes("--- CLI PREVIEW ---")) {
        live.textContent = text.split("--- CLI PREVIEW ---")[1]?.trim() || text;
    }
}

function flashToast(msg, type) {
    const t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.className = `toast toast-${type} show`;
    setTimeout(() => t.classList.remove("show"), 3500);
}

async function copyOutput() {
    try {
        await navigator.clipboard.writeText(document.getElementById("statusOutput").textContent);
        flashToast("CLI copied to clipboard.", "ok");
    } catch {
        flashToast("Copy failed — select text manually.", "err");
    }
}

function applySafeDefaults() {
    if (!selectedScenario && catalog.scenarios.length) selectScenario(catalog.scenarios[0].id, document.querySelector(".scenario-card"));
    document.getElementById("local_ka").value = "10.255.255.1";
    document.getElementById("remote_ka").value = "10.255.255.2";
    applyVpcSuggestions();
    updateBadges();
    flashToast("Safe defaults applied.", "ok");
}

function addVlanRow() {
    const row = document.createElement("div");
    row.className = "grid-2 vlan-row";
    row.innerHTML = `<input type="number" class="vlan-id" placeholder="VLAN ID"><input type="text" class="vlan-name" placeholder="Name">
        <input type="text" class="svi-ip" placeholder="SVI IP"><button type="button" class="btn-outline" onclick="this.parentElement.remove()">Remove</button>`;
    document.getElementById("vlanList").appendChild(row);
}

async function expandRange() {
    const range = document.getElementById("rangeInput").value;
    if (!range) return;
    const res = await fetch(`/util/expand-range?range_str=${encodeURIComponent(range)}`);
    if (!res.ok) { flashToast("Range expansion failed.", "err"); return; }
    const data = await res.json();
    const area = document.getElementById("interfacesArea");
    area.value += (area.value ? "\n" : "") + data.expanded.join("\n");
}

async function fetchCheckpoints() {
    const list = document.getElementById("checkpointList");
    if (!list) return;
    const res = await fetch("/checkpoints", { headers: authHeaders(false) });
    if (!res.ok) { list.textContent = "Checkpoints unavailable."; return; }
    const items = await res.json();
    list.innerHTML = items.slice(0, 15).map((c) => {
        const safe = c.filename.replace(/'/g, "\\'");
        return `<div class="checkpoint-row">
            <button type="button" class="vault-item" onclick="viewCheckpoint('${safe}')">
                <span>${escapeHtml(c.filename)}</span><span class="vault-type">${escapeHtml(c.timestamp)}</span>
            </button>
            <button type="button" class="btn-outline btn-sm" onclick="restoreCheckpoint('${safe}')" aria-label="Restore ${escapeHtml(c.filename)}">Restore</button>
        </div>`;
    }).join("") || "<p class='field-note'>No checkpoints yet.</p>";
}

async function restoreCheckpoint(filename) {
    if (!confirm(`Restore wizard from ${filename}? Unsaved changes will be lost.`)) return;
    const res = await fetch(`/checkpoints/${encodeURIComponent(filename)}/restore-preview`, { headers: authHeaders(false) });
    if (!res.ok) { flashToast("Restore failed.", "err"); return; }
    const { checkpoint: cp } = await res.json();
    document.getElementById("hostname").value = cp.hostname || "";
    document.getElementById("mgmt_ip").value = cp.mgmt_ip || "";
    document.getElementById("mgmt_gw").value = cp.mgmt_gw || "";
    document.getElementById("motd").value = cp.motd || "Authorized Access Only";
    if (cp.model) document.getElementById("model").value = cp.model;
    if (cp.nxos_version) document.getElementById("nxos_version").value = cp.nxos_version;
    if (cp.security_tier) document.getElementById("security_tier").value = cp.security_tier;
    if (cp.network_name) document.getElementById("network_name").value = cp.network_name;
    if (cp.site_location) document.getElementById("site_location").value = cp.site_location;
    document.getElementById("ntp_server").value = (cp.ntp_servers || []).join(", ");
    document.getElementById("logging_host").value = (cp.logging_hosts || []).join(", ");
    document.getElementById("snmp_location").value = cp.snmp_location || "";
    document.getElementById("admin_user").value = cp.admin_user || "admin";
    if (cp.tacacs_server_1) document.getElementById("tacacs_server_1").value = cp.tacacs_server_1;
    if (cp.baseline_options?.length) applyBaselineDefaults(cp.baseline_options);
    if (cp.enabled_features?.length) applyFeatureDefaults(cp.enabled_features);
    if (cp.vpc) {
        document.getElementById("vpc_domain").value = cp.vpc.domain_id;
        document.getElementById("vpc_pl_id").value = cp.vpc.peer_link_id;
        document.getElementById("vpc_pl_ints").value = (cp.vpc.peer_link_interfaces || []).join(", ");
        document.getElementById("vpc_ka_ints").value = (cp.vpc.keepalive_interfaces || []).join(", ");
        document.getElementById("local_ka").value = cp.vpc.local_keepalive_ip || "";
        document.getElementById("remote_ka").value = cp.vpc.remote_keepalive_ip || "";
        if (typeof portMapCustomMode !== "undefined") portMapCustomMode = true;
    }
    updateVpcVisibility();
    if (typeof renderPortMapChips === "function") renderPortMapChips();
    updateBadges();
    flashToast("Checkpoint restored to wizard.", "ok");
    goToStep(4);
}

async function compareConfig() {
    const baseline = document.getElementById("baselineConfig")?.value || "";
    let proposed = lastConfigPreview;
    if (!proposed) {
        const out = document.getElementById("statusOutput")?.textContent || "";
        const idx = out.indexOf("--- CLI PREVIEW ---");
        proposed = idx >= 0 ? out.slice(idx + 20).trim() : out;
    }
    if (!baseline.trim()) { flashToast("Paste a running-config first.", "warn"); return; }
    if (!proposed || proposed.startsWith("Complete the wizard")) {
        flashToast("Validate or Build first to generate proposed config.", "warn");
        return;
    }
    try {
        const res = await fetch("/util/diff-config", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ baseline, proposed }),
        });
        const data = await res.json();
        const el = document.getElementById("diffOutput");
        if (el) el.textContent = data.diff || "No differences.";
        flashToast("Diff complete.", "ok");
    } catch (err) {
        flashToast("Diff failed: " + err.message, "err");
    }
}

async function viewCheckpoint(filename) {
    const res = await fetch(`/checkpoints/${encodeURIComponent(filename)}`, { headers: authHeaders(false) });
    if (res.ok) setOutput(JSON.stringify(await res.json(), null, 2));
}

async function fetchVault() {
    const list = document.getElementById("vaultList");
    const host = document.getElementById("vaultFilter")?.value || "";
    const site = document.getElementById("vaultSiteFilter")?.value.trim() || "";
    const scenario = document.getElementById("vaultScenarioFilter")?.value.trim() || "";
    const artifactType = document.getElementById("vaultTypeFilter")?.value || "";
    const params = new URLSearchParams();
    if (host) params.set("hostname", host);
    if (site) params.set("site", site);
    if (scenario) params.set("scenario", scenario);
    if (artifactType) params.set("artifact_type", artifactType);
    const url = params.toString() ? `/history?${params}` : "/history";
    const res = await fetch(url, { headers: authHeaders(false) });
    if (!res.ok) { list.textContent = "Vault unavailable."; return; }
    const files = await res.json();
    updateVaultFilterOptions(files);
    list.innerHTML = files.slice(0, 40).map((f) => {
        const base = f.split("/").pop();
        let type = "artifact";
        if (base.includes("_config")) type = "config";
        else if (base.endsWith("manifest.json")) type = "manifest";
        else if (base.includes("CHANGE_PACKAGE")) type = "package";
        else if (base.endsWith("_device.json")) type = "json";
        else if (base.includes("_risk")) type = "risk";
        else if (base.includes("_diff")) type = "diff";
        const safe = f.replace(/'/g, "\\'");
        return `<button type="button" class="vault-item" data-type="${type}" onclick="viewVault('${safe}')"><span>${escapeHtml(f)}</span><span class="vault-type">${type}</span></button>`;
    }).join("") || "<p class='field-note'>No artifacts yet — Build to create your first config.</p>";
}

function updateVaultFilterOptions(files) {
    const sel = document.getElementById("vaultFilter");
    if (!sel) return;
    const current = sel.value;
    const hosts = new Set();
    files.forEach((f) => {
        const base = f.split("/").pop();
        const m = base.match(/_([A-Za-z0-9][A-Za-z0-9-]{0,62})_\d{8}_\d{6}_config\.txt$/);
        if (m) hosts.add(m[1]);
    });
    sel.innerHTML = `<option value="">All devices</option>` +
        [...hosts].sort().map((h) => `<option value="${escapeHtml(h)}"${h === current ? " selected" : ""}>${escapeHtml(h)}</option>`).join("");
}

async function loadSystemPaths() {
    const res = await fetch("/system/paths", { headers: authHeaders(false) });
    if (!res.ok) return;
    systemPaths = await res.json();
    const hint = document.getElementById("vaultPathHint");
    if (hint && systemPaths.vault_dir) hint.textContent = systemPaths.vault_dir;
}

function saveExportDir() {
    const v = document.getElementById("exportDir")?.value.trim() || "";
    try { localStorage.setItem("nxos_export_dir", v); } catch { /* ignore */ }
}

function loadExportDir() {
    try {
        const v = localStorage.getItem("nxos_export_dir") || "";
        const el = document.getElementById("exportDir");
        if (el) el.value = v;
    } catch { /* ignore */ }
}

function dismissFirstRunHint() {
    const el = document.getElementById("firstRunHint");
    if (el) el.hidden = true;
    try { localStorage.setItem("nxos_hint_dismissed", "1"); } catch { /* ignore */ }
}

function showFirstRunHint() {
    try {
        if (localStorage.getItem("nxos_hint_dismissed") === "1") return;
    } catch { /* ignore */ }
    const el = document.getElementById("firstRunHint");
    if (el) el.hidden = false;
}

function showBuildSuccess(exportInfo, configText) {
    lastExportDir = exportInfo.output_dir || "";
    lastPrimaryConfig = configText || lastPrimaryConfig;
    const modal = document.getElementById("buildSuccessModal");
    const pathEl = document.getElementById("buildSuccessPath");
    const filesEl = document.getElementById("buildSuccessFiles");
    if (pathEl) {
        let msg = `Saved to: ${exportInfo.output_dir}`;
        if (exportInfo.batch_folder) msg += ` (vPC pair folder: ${exportInfo.batch_folder})`;
        pathEl.textContent = msg;
    }
    if (filesEl) {
        filesEl.innerHTML = (exportInfo.files || []).map((f) => `<li>${escapeHtml(f)}</li>`).join("");
    }
    modal?.classList.remove("hidden");
}

function closeBuildSuccess() {
    document.getElementById("buildSuccessModal")?.classList.add("hidden");
}

function restartFromBuildSuccess() {
    closeBuildSuccess();
    restartConfiguration();
}

function restartConfiguration() {
    if (!confirm("Restart configuration? Unsaved wizard choices will be cleared. Saved vault files are kept.")) return;

    resetRoadmap?.();
    selectedScenario = null;
    currentStep = 1;
    lastConfigPreview = "";
    lastPrimaryConfig = "";
    lastExportDir = "";
    clearConfigStudioPreview?.();
    clearInterfacePlans?.();

    document.querySelectorAll(".scenario-card").forEach((c) => c.classList.remove("selected"));
    const help = document.getElementById("scenarioHelp");
    if (help) help.innerHTML = "";

    const clearIds = [
        "hostname", "mgmt_ip", "mgmt_gw", "site_name", "network_name", "site_location",
        "motd", "ntp_server", "logging_host", "snmp_location", "snmp_trap_host_1",
        "snmp_trap_host_2", "snmp_v3_user", "boot_image", "tacacs_server_1", "tacacs_key",
        "admin_user", "vpc_pl_ints", "vpc_ka_ints", "interfacesArea", "rangeInput",
    ];
    clearIds.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });

    document.getElementById("vlanList").innerHTML = "";
    vlanCount = 0;
    document.getElementById("generate_pair").checked = false;
    const bringUp = document.getElementById("bring_up_spare_ports");
    if (bringUp) bringUp.checked = true;
    document.getElementById("vpc_domain").value = "100";
    document.getElementById("vpc_pl_id").value = "1";
    document.getElementById("local_ka").value = "10.255.255.1";
    document.getElementById("remote_ka").value = "10.255.255.2";
    if (document.getElementById("keepalive_vrf")) document.getElementById("keepalive_vrf").value = "management";
    if (document.getElementById("vpc_ka_po")) document.getElementById("vpc_ka_po").value = "2";

    document.querySelectorAll("#featureGrid input[data-feature]").forEach((cb) => { cb.checked = false; });
    document.querySelectorAll("#baselineGrid input[data-baseline]").forEach((cb) => { cb.checked = false; });
    if (typeof resetLinkPlannerFromScenario === "function") resetLinkPlannerFromScenario();

    const compare = document.getElementById("compareRunningConfig");
    if (compare) compare.value = "";

    showCompliance([]);
    setOutput("");
    renderStudioIdle?.("Start Mode → vPC → Speed to build a new configuration.");
    const status = document.getElementById("livePreviewStatus");
    if (status) status.textContent = "";
    const modelSummary = document.getElementById("modelSummary");
    if (modelSummary) modelSummary.innerHTML = "";
    const actionList = document.getElementById("actionRequiredList");
    if (actionList) actionList.innerHTML = "<li class='ok-item'>Pick a role to begin.</li>";

    goToStep(1);
    renderModeChoices?.();
    updateRoadmapSummary?.();
    updateBadges();
    updateVpcVisibility();
    flashToast("Configuration restarted — wizard cleared.", "ok");
}

async function openVaultFolder() {
    await openFolderPath(systemPaths.vault_dir);
}

async function openLastExportFolder() {
    await openFolderPath(lastExportDir || systemPaths.vault_dir);
    closeBuildSuccess();
}

async function openFolderPath(path) {
    if (!path) {
        flashToast("Folder path unknown.", "warn");
        return;
    }
    const res = await fetch("/system/open-folder", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ path }),
    });
    if (res.ok) flashToast("Opened folder.", "ok");
    else flashToast("Could not open folder.", "err");
}

async function copyPrimaryConfig() {
    const text = lastPrimaryConfig || lastConfigPreview;
    if (!text) { flashToast("No config to copy.", "warn"); return; }
    try {
        await navigator.clipboard.writeText(text);
        flashToast("Primary config copied.", "ok");
    } catch {
        flashToast("Copy failed.", "err");
    }
}

async function viewVault(filename) {
    const res = await fetch(`/history/${encodeURIComponent(filename)}`, { headers: authHeaders(false) });
    if (res.ok) setOutput(await res.text());
}

async function shutdownSystem() {
    if (!confirm("Stop the Configuration Authority program?")) return;
    try {
        const res = await fetch("/system/shutdown", { method: "POST" });
        if (!res.ok) {
            flashToast(`Stop failed (${res.status}). Close the console window or run scripts\\stop_configurator.ps1`, "err");
            return;
        }
        let stopped = false;
        for (let i = 0; i < 12; i++) {
            await new Promise((r) => setTimeout(r, 500));
            try {
                await fetch("/version", { signal: AbortSignal.timeout(800) });
            } catch {
                stopped = true;
                break;
            }
        }
        if (stopped) {
            document.body.innerHTML = "<div class='container'><h1>System Offline</h1><p>Program stopped. You can close this tab.</p></div>";
        } else {
            flashToast("Server still running — close the console window or run scripts\\stop_configurator.ps1", "warn");
        }
    } catch {
        flashToast("Stop request failed — close the console window manually.", "err");
    }
}

function openHelp() { document.getElementById("helpModal").classList.remove("hidden"); }
function closeHelp() { document.getElementById("helpModal").classList.add("hidden"); }

["hostname", "mgmt_ip", "mgmt_gw", "site_name", "local_ka", "remote_ka", "vpc_pl_ints"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", updateBadges);
});

function propagateTokenToAdminLink() {
    const link = document.getElementById("adminLink");
    if (link) {
        link.href = `/admin`; // Token authentication removed for offline use
    }
}

(async function init() {
    try {
        propagateTokenToAdminLink();
        await loadVersion();
        await loadCatalog();
        await loadSystemPaths();
        loadExportDir();
        showFirstRunHint();
        await fetchVault();
        await fetchCheckpoints();
        updateBadges();
        updateWizardTip();
    } catch (err) {
        setOutput("Startup error: " + err.message);
    }
})();
