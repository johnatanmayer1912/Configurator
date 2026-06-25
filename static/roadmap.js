/** Configuration Roadmap — Mode → vPC → Speed → auto scenario */



const ROADMAP = {

    modes: [

        { id: "core", label: "Core / Spine", desc: "40G fabric — Nexus 9336C, vPC pairs, leaf downlinks", speeds: ["40G"], icon: "40G", model: "Nexus 9336C-FX2" },

        { id: "leaf", label: "Leaf / ToR", desc: "10G fabric — Nexus 93180, server ports + uplinks", speeds: ["10G"], icon: "10G", model: "Nexus 93180YC-EX" },

        { id: "access", label: "Access", desc: "1G closets — Nexus 9348, standalone or vPC pair", speeds: ["1G"], icon: "1G", model: "Nexus 9348GC-FXP" },

        { id: "oob", label: "Out-of-Band", desc: "Bootstrap only — hostname, mgmt0, minimal features", speeds: ["Multi"], icon: "OOB", model: "Generic" },

    ],

};



const SPEED_INFO = {

    "40G": {

        label: "40G Core",

        model: "Nexus 9336C-FX2",

        desc: "Institutional dual-core vPC or standalone spine — QSFP28 ports.",

        helpId: "speed_40g",

    },

    "10G": {

        label: "10G Leaf",

        model: "Nexus 93180YC-EX",

        desc: "ToR / leaf — access VLANs, uplinks Eth1/49–50, optional vPC pair.",

        helpId: "speed_10g",

    },

    "1G": {

        label: "1G Access",

        model: "Nexus 9348GC-FXP",

        desc: "IDF closet — 48×1G access, uplink trunks, standalone or vPC pair.",

        helpId: "speed_1g",

    },

    Multi: {

        label: "Management",

        model: "Generic",

        desc: "OOB bootstrap — expand later in lab.",

        helpId: "mode_oob",

    },

};



let roadmap = { mode: null, vpc: null, speed: null };



function resetRoadmap() {

    roadmap = { mode: null, vpc: null, speed: null };

}



function sanitizeHostname(value) {

    return String(value || "")

        .trim()

        .replace(/_/g, "-")

        .replace(/[^a-zA-Z0-9-]/g, "")

        .slice(0, 63);

}



function isValidHostname(value) {

    const h = sanitizeHostname(value);

    return h.length > 0 && /^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$/.test(h);

}



function resolveScenarioFromRoadmap() {

    const { mode, vpc, speed } = roadmap;

    if (mode === "oob") return "mgmt_oob";

    if (mode === "access") return roadmap.vpc ? "vpc_access_pair" : "standalone_access";

    if (mode === "core") return vpc ? "vpc_core_pair" : "spine_core";

    if (mode === "leaf") {

        if (vpc && speed === "10G") return "vpc_leaf_pair";

        if (!vpc) return "standalone_leaf";

        return "vpc_leaf_pair";

    }

    return null;

}



function defaultHostnameForRoadmap() {

    const { mode, vpc } = roadmap;

    if (mode === "core" && vpc) return "CORE1-VPC";

    if (mode === "core") return "CORE-SPINE-01";

    if (mode === "leaf" && vpc) return "DC-LEAF-01-A";

    if (mode === "leaf") return "DC-LEAF-01";

    if (mode === "access" && vpc) return "ACCESS-SW-01-A";

    if (mode === "access") return "ACCESS-SW-01";

    return "NXOS-SW-01";

}



function defaultModelForRoadmap() {

    const modeObj = ROADMAP.modes.find((m) => m.id === roadmap.mode);

    if (modeObj?.model) return modeObj.model;

    const { speed } = roadmap;

    if (speed === "40G") return "Nexus 9336C-FX2";

    if (speed === "1G") return "Nexus 9348GC-FXP";

    if (speed === "10G") return "Nexus 93180YC-EX";

    return "Generic";

}



function refreshVpcPortsFromRoadmap() {

    const model = defaultModelForRoadmap();

    const modelEl = document.getElementById("model");

    if (modelEl && model && model !== "Generic") modelEl.value = model;

    applyVpcSuggestions?.(true);

}



function renderModeChoices() {
    const grid = document.getElementById("modeGrid");
    if (!grid) {
        console.error("modeGrid element not found");
        return;
    }
    grid.innerHTML = "";
    
    if (!ROADMAP || !ROADMAP.modes || !Array.isArray(ROADMAP.modes)) {
        console.error("ROADMAP.modes not available");
        return;
    }
    
    ROADMAP.modes.forEach((m) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `choice-card${roadmap.mode === m.id ? " selected" : ""}`;
        btn.innerHTML = `
            <span class="choice-top">
                <span class="choice-badge">${escapeHtml(m.icon)}</span>
                <button type="button" class="info-btn" aria-label="Learn more" onclick="event.stopPropagation(); showOptionInfo('mode_${m.id}')">i</button>
            </span>
            <strong>${escapeHtml(m.label)}</strong>
            <span class="choice-desc">${escapeHtml(m.desc)}</span>
            <span class="choice-model-hint">${escapeHtml(m.model)}</span>`;
        btn.onclick = () => {
            roadmap.mode = m.id;
            roadmap.vpc = null;
            roadmap.speed = m.speeds[0] === "Multi" ? "Multi" : null;
            renderModeChoices();
            updateRoadmapSummary();
            refreshVpcPortsFromRoadmap();
            if (m.id === "oob") applyRoadmapToWizard();
        };
        grid.appendChild(btn);
    });
}



function renderVpcChoices() {
    const grid = document.getElementById("vpcChoiceGrid");
    const section = document.getElementById("vpcChoiceSection");
    if (!grid || !section) {
        console.error("vpcChoiceGrid or vpcChoiceSection element not found");
        return;
    }
    
    if (roadmap.mode === "oob") {
        section.hidden = true;
        roadmap.vpc = false;
        return;
    }
    
    section.hidden = false;
    grid.innerHTML = "";
    
    [
        { id: true, label: "Yes — vPC pair", desc: "Dual switches, peer-link + keepalive", helpId: "vpc_yes" },
        { id: false, label: "No — standalone", desc: "Single switch, no vPC domain", helpId: "vpc_no" },
    ].forEach((opt) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `choice-card${roadmap.vpc === opt.id ? " selected" : ""}`;
        btn.innerHTML = `<div class="choice-top"><strong>${escapeHtml(opt.label)}</strong><button type="button" class="info-btn" aria-label="Learn more" onclick="event.stopPropagation(); showOptionInfo('${opt.helpId}')">i</button></div><span class="choice-desc">${escapeHtml(opt.desc)}</span>`;
        btn.onclick = () => {
            roadmap.vpc = opt.id;
            renderVpcChoices();
            updateRoadmapSummary();
            refreshVpcPortsFromRoadmap();
        };
        grid.appendChild(btn);
    });
}



function updateSpeedStepNote() {

    const note = document.getElementById("speedStepNote");

    const section = document.getElementById("speedSection");

    if (!note) return;

    const mode = ROADMAP.modes.find((m) => m.id === roadmap.mode);

    const speed = roadmap.speed || mode?.speeds?.[0];

    const info = SPEED_INFO[speed] || {};

    if (section?.hidden && speed) {

        note.hidden = false;

        note.textContent = `Auto-selected: ${info.label || speed} → ${info.model || defaultModelForRoadmap()}. ${info.desc || ""}`;

    } else {

        note.hidden = true;

        note.textContent = "";

    }

}



function renderSpeedChoices() {
    const grid = document.getElementById("speedGrid");
    const section = document.getElementById("speedSection");
    if (!grid || !section) {
        console.error("speedGrid or speedSection element not found");
        return;
    }
    
    const mode = ROADMAP.modes?.find((m) => m.id === roadmap.mode);
    const speeds = mode?.speeds || [];
    
    if (speeds.length <= 1) {
        section.hidden = true;
        if (speeds[0]) roadmap.speed = speeds[0];
        updateSpeedStepNote();
        return;
    }
    
    section.hidden = false;
    updateSpeedStepNote();
    grid.innerHTML = "";
    
    speeds.forEach((sp) => {
        const info = SPEED_INFO[sp] || { label: sp, desc: "", model: "", helpId: null };
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `choice-card${roadmap.speed === sp ? " selected" : ""}`;

        const infoBtn = info.helpId ? `<button type="button" class="info-btn" aria-label="Learn more" onclick="event.stopPropagation(); showOptionInfo('${info.helpId}')">i</button>` : "";
        btn.innerHTML = `
            <span class="choice-top">
                <span class="choice-badge">${escapeHtml(sp)}</span>
                ${infoBtn}
            </span>
            <strong>${escapeHtml(info.label || sp + " fabric")}</strong>
            <span class="choice-desc">${escapeHtml(info.desc)}</span>
            <span class="choice-model-hint">${escapeHtml(info.model)}</span>`;
        btn.onclick = () => {
            roadmap.speed = sp;
            renderSpeedChoices();
            updateRoadmapSummary();
            refreshVpcPortsFromRoadmap();
        };
        grid.appendChild(btn);
    });
}



function updateRoadmapSummary() {
    const el = document.getElementById("roadmapSummary");
    if (!el) return;
    
    const parts = [];
    if (roadmap.mode && ROADMAP.modes) {
        const mode = ROADMAP.modes.find((m) => m.id === roadmap.mode);
        if (mode) parts.push(mode.label || roadmap.mode);
    }
    
    if (roadmap.vpc !== null && roadmap.mode !== "oob") {
        parts.push(roadmap.vpc ? "vPC pair" : "Standalone");
    }
    
    if (roadmap.speed) parts.push(roadmap.speed);
    
    const scenarioId = resolveScenarioFromRoadmap();
    if (scenarioId && catalog.scenarios) {
        const sc = catalog.scenarios.find((s) => s.id === scenarioId);
        if (sc) parts.push(sc.name || scenarioId);
    }
    
    const model = defaultModelForRoadmap();
    if (model && model !== "Generic") parts.push(model);

    el.textContent = parts.length ? parts.join(" → ") : "Pick a role — we map model, vPC, and scenario for you.";
    updateConfigurePathBanner();
}



function updateConfigurePathBanner() {
    const banner = document.getElementById("configurePathBanner");
    if (!banner) return;
    
    const scenarioId = resolveScenarioFromRoadmap() || selectedScenario?.id;
    const sc = catalog.scenarios?.find((s) => s.id === scenarioId) || selectedScenario;
    
    if (!sc) {
        banner.textContent = "";
        banner.hidden = true;
        return;
    }
    
    const speed = roadmap.speed || "";
    const tier = speed ? `${speed}` : "";
    banner.hidden = false;
    banner.innerHTML = `<strong>${escapeHtml(tier)}${tier ? " · " : ""}${escapeHtml(sc.name)}</strong>`;
    
    const detail = document.getElementById("configurePathDetail");
    const more = document.getElementById("configurePathMore");
    const help = sc.help || sc.description || "";
    
    if (detail) {
        detail.textContent = help;
        detail.hidden = true;
    }
    
    if (more) more.hidden = !help;
}



function toggleConfigurePathDetail() {

    const detail = document.getElementById("configurePathDetail");

    if (detail) detail.hidden = !detail.hidden;

}



function applyRoadmapToWizard() {

    const scenarioId = resolveScenarioFromRoadmap();

    if (!scenarioId) return;

    selectedScenario = catalog.scenarios.find((s) => s.id === scenarioId);

    if (!selectedScenario) return;



    const hn = defaultHostnameForRoadmap();

    document.getElementById("hostname").value = hn;

    document.getElementById("model").value = defaultModelForRoadmap();

    document.getElementById("generate_pair").checked = !!roadmap.vpc && !!selectedScenario.pair_mode;



    applyScenarioDefaults();

    updateBadges();

    updateConfigurePathBanner();

    renderInterfacePlanner?.();

    scheduleLivePreview?.();

}



function roadmapStepValid(step) {

    if (step === 1) return !!roadmap.mode;

    if (step === 2) {

        if (roadmap.mode === "oob") return true;

        return roadmap.vpc !== null;

    }

    if (step === 3) return !!roadmap.speed || roadmap.mode === "oob";

    return true;

}



function onRoadmapStepEnter(step) {

    if (step === 1) renderModeChoices();

    if (step === 2) renderVpcChoices();

    if (step === 3) {

        renderSpeedChoices();

        updateSpeedStepNote();

    }

    if (step === 4) {

        applyRoadmapToWizard();

        renderConfigureCards();

    }

    updateRoadmapSummary();

}



function syncRoadmapFromScenario(scenario) {

    if (!scenario) return;

    if (scenario.role === "spine" || scenario.id === "vpc_core_pair" || scenario.id === "spine_core") {

        roadmap.mode = "core";

        roadmap.vpc = scenario.redundancy === "vpc";

        roadmap.speed = "40G";

    } else if (scenario.role === "leaf") {

        roadmap.mode = "leaf";

        roadmap.vpc = scenario.redundancy === "vpc";

        roadmap.speed = "10G";

    } else if (scenario.role === "access") {

        roadmap.mode = "access";

        roadmap.vpc = scenario.redundancy === "vpc";

        roadmap.speed = "1G";

    } else {

        roadmap.mode = "oob";

        roadmap.vpc = false;

        roadmap.speed = "Multi";

    }

    updateRoadmapSummary();

}



function onRoadmapNextFromStep3() {

    if (!selectedScenario) applyRoadmapToWizard();

}



function renderConfigureCards() {

    const badge = document.getElementById("configureModelBadge");

    const model = document.getElementById("model")?.value;

    const hw = catalog.hardware?.find((h) => h.display_name === model);

    if (badge && hw) {

        badge.textContent = `${hw.primary_speed_label || "Multi"} tier · ${hw.total_ports || "?"} ports`;

        badge.title = hw.display_name;

    }

    const isOob = selectedScenario?.id === "mgmt_oob" || roadmap.mode === "oob";

    const isCore = selectedScenario?.id === "vpc_core_pair";

    const needsVpc = roadmap.vpc || selectedScenario?.redundancy === "vpc";



    const presetStrip = document.getElementById("presetStrip");

    if (presetStrip) presetStrip.hidden = isOob;



    const baselineCard = document.getElementById("cardBaseline");

    if (baselineCard) baselineCard.style.display = isOob ? "none" : "block";



    const vpcCard = document.getElementById("cardVpcWiring");

    if (vpcCard) vpcCard.style.display = needsVpc && !isOob ? "block" : "none";



    const dlCard = document.getElementById("cardVpcLinks");

    if (dlCard && typeof shouldShowLinkPlanner === "function") {
        dlCard.style.display = shouldShowLinkPlanner() ? "block" : "none";
    }



    const featuresBlock = document.getElementById("featuresAdvanced");

    if (featuresBlock) {

        featuresBlock.open = !isOob;

        featuresBlock.style.display = isOob ? "none" : "block";

    }



    const grid = document.querySelector(".option-b-grid");

    if (grid && isOob) grid.style.gridTemplateColumns = "1fr";



    updateConfigurePathBanner();

    wrapExpandableOptions?.();

}


