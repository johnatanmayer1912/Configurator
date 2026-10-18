/** Config Builder — questionnaire wizard (customize-your-switch) */

let builderAnswers = {};
let builderStep = 0;
let builderQuestions = [];

async function openConfigBuilder() {
    builderAnswers = {};
    builderStep = 0;
    document.getElementById("builderModal").classList.remove("hidden");
    await refreshBuilderStep();
}

function closeConfigBuilder() {
    document.getElementById("builderModal").classList.add("hidden");
}

async function refreshBuilderStep() {
    const res = await fetch("/builder/questions", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ answers: builderAnswers }),
    });
    if (!res.ok) {
        flashToast("Config Builder failed to load.", "err");
        return;
    }
    const data = await res.json();
    builderQuestions = data.questions || [];
    if (builderStep >= builderQuestions.length) builderStep = Math.max(0, builderQuestions.length - 1);
    renderBuilderQuestion();
}

function renderBuilderQuestion() {
    const q = builderQuestions[builderStep];
    const body = document.getElementById("builderBody");
    const progress = document.getElementById("builderProgress");
    if (!q) {
        body.innerHTML = "<p>Loading...</p>";
        return;
    }
    progress.textContent = `Step ${builderStep + 1} of ${builderQuestions.length}`;
    let html = `<h3>${escapeHtml(q.title)}</h3>`;
    if (q.help) html += `<p class="field-note">${escapeHtml(q.help)}</p>`;
    const val = builderAnswers[q.id] ?? q.prefill ?? "";

    if (q.id === "running_config" && builderAnswers._detection_summary) {
        html += `<div class="info-box"><strong>Detected:</strong><ul>${builderAnswers._detection_summary.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul></div>`;
    } else if (builderAnswers._detection_summary?.length && builderStep > 0) {
        html += `<div class="info-box subtle"><strong>From your config:</strong> ${escapeHtml(builderAnswers._detection_summary.slice(0, 4).join(" · "))}</div>`;
    }

    if (q.type === "choice") {
        html += `<div class="builder-choices">`;
        (q.options || []).forEach((opt) => {
            const sel = val === opt.value ? " selected" : "";
            html += `<button type="button" class="builder-choice${sel}" data-value="${escapeHtml(opt.value)}" data-action="pick-builder-choice" data-question="${q.id}">${escapeHtml(opt.label)}</button>`;
        });
        html += `</div>`;
    } else if (q.type === "textarea") {
        html += `<textarea id="builderField" rows="10" placeholder="Paste running-config here...">${escapeHtml(String(val))}</textarea>`;
    } else if (q.type === "confirm") {
        html += `<div class="info-box" id="builderSummary">Analyzing your choices...</div>`;
        loadBuilderSummary();
    } else {
        html += `<input type="text" id="builderField" value="${escapeHtml(String(val))}" placeholder="${escapeHtml(q.placeholder || "")}">`;
    }
    body.innerHTML = html;
}

function pickBuilderChoice(qid, value) {
    builderAnswers[qid] = value;
    document.querySelectorAll(".builder-choice").forEach((b) => b.classList.toggle("selected", b.dataset.value === value));
}

async function builderNext() {
    const q = builderQuestions[builderStep];
    if (!q) return;

    if (q.type === "textarea" || q.type === "text") {
        const el = document.getElementById("builderField");
        builderAnswers[q.id] = el ? el.value.trim() : "";
    }
    if (q.type === "choice" && q.required && !builderAnswers[q.id]) {
        flashToast("Please select an option.", "warn");
        return;
    }
    if (q.id === "running_config" && builderAnswers.start_mode === "paste") {
        const text = builderAnswers.running_config || "";
        if (text.length < 20) {
            flashToast("Paste a running-config (at least a few lines).", "warn");
            return;
        }
        const res = await fetch("/builder/parse", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ running_config: text }),
        });
        if (res.ok) {
            const data = await res.json();
            builderAnswers._detection_summary = data.summary;
            Object.assign(builderAnswers, data.suggested_answers || {});
            renderBuilderQuestion();
            flashToast("Config analyzed — review detected values below.", "ok");
            return;
        }
        flashToast("Could not parse running-config — check format and try again.", "err");
        return;
    }

    if (builderStep < builderQuestions.length - 1) {
        builderStep++;
        await refreshBuilderStep();
        return;
    }
    await applyBuilderRecommendation();
}

async function builderBack() {
    if (builderStep > 0) {
        builderStep--;
        await refreshBuilderStep();
    }
}

async function loadBuilderSummary() {
    const box = document.getElementById("builderSummary");
    if (!box) return;
    try {
        const res = await fetch("/builder/recommend", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ answers: builderAnswers }),
        });
        const data = await res.json();
        box.innerHTML = `<ul>${(data.summary || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul>`;
        builderAnswers._recommendation = data;
    } catch {
        box.textContent = "Could not build recommendation.";
    }
}

async function applyBuilderRecommendation() {
    let rec = builderAnswers._recommendation;
    if (!rec) {
        const res = await fetch("/builder/recommend", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ answers: builderAnswers }),
        });
        if (!res.ok) {
            flashToast("Recommendation failed.", "err");
            return;
        }
        rec = await res.json();
    }
    const w = rec.wizard;
    const scenarioCard = document.querySelector(`.scenario-card[data-id="${w.scenario_id}"]`);
    selectScenario(w.scenario_id, scenarioCard);
    document.getElementById("site_name").value = w.site_name || "HQ_DC";
    document.getElementById("hostname").value = w.hostname || "";
    document.getElementById("mgmt_ip").value = w.mgmt_ip || "";
    document.getElementById("mgmt_gw").value = w.mgmt_gw || "";
    document.getElementById("generate_pair").checked = !!w.generate_pair;
    const ov = w.overrides || {};
    if (ov.motd) document.getElementById("motd").value = ov.motd;
    if (ov.security_tier) document.getElementById("security_tier").value = ov.security_tier;
    if (ov.ntp_server) document.getElementById("ntp_server").value = ov.ntp_server;
    if (ov.logging_host) document.getElementById("logging_host").value = ov.logging_host;
    if (ov.snmp_location) document.getElementById("snmp_location").value = ov.snmp_location;
    if (ov.vpc_domain_id) document.getElementById("vpc_domain").value = ov.vpc_domain_id;
    if (ov.peer_link_interfaces) document.getElementById("vpc_pl_ints").value = ov.peer_link_interfaces;
    if (ov.local_keepalive_ip) document.getElementById("local_ka").value = ov.local_keepalive_ip;
    if (ov.remote_keepalive_ip) document.getElementById("remote_ka").value = ov.remote_keepalive_ip;
    if (ov.features?.length) applyFeatureDefaults(ov.features);
    if (ov.interface_lines) document.getElementById("interfacesArea").value = ov.interface_lines;
    if (ov.custom_vlans?.length) {
        document.getElementById("vlanList").innerHTML = "";
        ov.custom_vlans.forEach((v) => {
            addVlanRow();
            const row = document.querySelector("#vlanList .vlan-row:last-child");
            if (row) {
                row.querySelector(".vlan-id").value = v.id;
                row.querySelector(".vlan-name").value = v.name || "";
            }
        });
    }
    updateVpcVisibility();
    updateBadges();
    closeConfigBuilder();
    flashToast("Config Builder applied — review Steps 2–5, then Validate.", "ok");
    goToStep(2);
}
