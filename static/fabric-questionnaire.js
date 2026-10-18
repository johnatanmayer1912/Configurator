/** Fabric links questionnaire (A2) — skippable guided flow for Architect mode. */

let questionnaireStep = 0;
let questionnaireAnswers = { downlink_count: 1, uplink_count: 1, skipped: false };

function startFabricQuestionnaire() {
    questionnaireStep = 0;
    questionnaireAnswers = { downlink_count: 1, uplink_count: 1, skipped: false };
    renderQuestionnaireStep();
    document.getElementById("fabricQuestionnaireModal")?.classList.remove("hidden");
}

function closeFabricQuestionnaire() {
    document.getElementById("fabricQuestionnaireModal")?.classList.add("hidden");
}

function skipFabricQuestionnaire() {
    questionnaireAnswers.skipped = true;
    closeFabricQuestionnaire();
    flashToast?.("Using institutional defaults — edit Fabric links anytime.", "ok");
}

async function applyQuestionnaireToPlanner() {
    const dl = Number(questionnaireAnswers.downlink_count || 0);
    const ul = Number(questionnaireAnswers.uplink_count || 0);
    if (typeof resetLinkPlannerFromScenario === "function") resetLinkPlannerFromScenario();
    if (typeof linkPlannerRows !== "undefined") {
        linkPlannerRows.downlink.forEach((r, i) => { r.enabled = i < dl; });
        linkPlannerRows.uplink.forEach((r, i) => { r.enabled = i < ul; });
        if (questionnaireAnswers.downlink_name) {
            const row = linkPlannerRows.downlink[0];
            if (row) row.description = questionnaireAnswers.downlink_name;
        }
        if (questionnaireAnswers.uplink_name) {
            const row = linkPlannerRows.uplink[0];
            if (row) row.description = questionnaireAnswers.uplink_name;
        }
        if (questionnaireAnswers.auto_ports) {
            await suggestAllLinkMembers();
        }
        linkPlannerCustomized = true;
        renderLinkPlanner?.();
    }
    pushUndo?.("Questionnaire apply");
    closeFabricQuestionnaire();
    scheduleLivePreview?.();
}

async function suggestAllLinkMembers() {
    const payload = collectLinkValidatePayload?.() || {};
    for (const kind of ["downlink", "uplink"]) {
        const rows = linkPlannerRows?.[kind] || [];
        for (const row of rows) {
            if (!row.enabled) continue;
            const pool = kind === "uplink" ? "fiber" : "access";
            try {
                const res = await fetch("/util/suggest-members", {
                    method: "POST",
                    headers: typeof authHeaders === "function" ? authHeaders() : { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        model: document.getElementById("model")?.value,
                        row: { pool, count: 2 },
                        peer_link_interfaces: parsePortList?.(document.getElementById("vpc_pl_ints")?.value) || [],
                        keepalive_interfaces: parsePortList?.(document.getElementById("vpc_ka_ints")?.value) || [],
                        link_rows: typeof getLinkPlannerPayload === "function" ? [...(getLinkPlannerPayload().downlinks || []), ...(getLinkPlannerPayload().uplinks || [])] : [],
                    }),
                });
                const data = await res.json();
                if (data.ports?.length) row.members = data.ports.join(", ");
            } catch { /* ignore */ }
        }
    }
}

function collectLinkValidatePayload() {
    const pl = document.getElementById("vpc_pl_ints")?.value || "";
    const ka = document.getElementById("vpc_ka_ints")?.value || "";
    return {
        model: document.getElementById("model")?.value,
        peer_link_interfaces: (typeof parsePortList === "function" ? parsePortList(pl) : pl.split(",")),
        keepalive_interfaces: (typeof parsePortList === "function" ? parsePortList(ka) : ka.split(",")),
    };
}

function renderQuestionnaireStep() {
    const body = document.getElementById("fabricQuestionnaireBody");
    const steps = [
        {
            title: "How many downlink bundles?",
            html: `<p class="field-note">Core switches: Po toward leaf pairs. Leaf/access: usually 0.</p>
                <div class="choice-grid choice-grid-3">
                    ${[0, 1, 2].map((n) => `<button type="button" class="choice-card" data-action="questionnaire-pick" data-key="downlink_count" data-value="${n}">${n}</button>`).join("")}
                </div>`,
        },
        {
            title: "Downlink description (optional)",
            html: `<input type="text" id="qDownName" class="full-width" placeholder="Connected_to_NET_LEAF_10G_SW1+SW2" value="${questionnaireAnswers.downlink_name || ""}">
                <button type="button" class="btn-secondary btn-sm" data-action="questionnaire-downlink-continue">Continue</button>`,
        },
        {
            title: "How many uplink bundles toward spine?",
            html: `<p class="field-note">Fiber ports 49–54 on 93180/9348 (peer-link excluded automatically).</p>
                <div class="choice-grid choice-grid-3">
                    ${[0, 1, 2].map((n) => `<button type="button" class="choice-card" data-action="questionnaire-pick" data-key="uplink_count" data-value="${n}">${n}</button>`).join("")}
                </div>`,
        },
        {
            title: "Auto-suggest free ports?",
            html: `<p class="field-note">We fill member ports from the hardware budget — you can edit after.</p>
                <button type="button" class="btn-primary" data-action="questionnaire-auto-ports" data-auto="true">Yes, suggest ports</button>
                <button type="button" class="btn-outline" data-action="questionnaire-auto-ports" data-auto="false">No, I'll type members</button>`,
        },
    ];
    const step = steps[questionnaireStep] || steps[steps.length - 1];
    if (body) {
        body.innerHTML = `<h4>${escapeHtml(step.title)}</h4>${step.html}
            <div class="questionnaire-nav">
                <button type="button" class="btn-ghost btn-sm" data-action="skip-fabric-questionnaire">Skip — use defaults</button>
                ${questionnaireStep > 0 ? `<button type="button" class="btn-outline btn-sm" data-action="questionnaire-prev">Back</button>` : ""}
            </div>`;
    }
}

function questionnairePick(key, val) {
    questionnaireAnswers[key] = val;
    if (key === "downlink_count" && val === 0) questionnaireStep = 2;
    else questionnaireNext();
}

function questionnaireNext() {
    questionnaireStep += 1;
    if (questionnaireStep >= 4) {
        applyQuestionnaireToPlanner();
        return;
    }
    if (questionnaireStep === 1 && questionnaireAnswers.downlink_count === 0) questionnaireStep = 2;
    renderQuestionnaireStep();
}

function questionnairePrev() {
    questionnaireStep = Math.max(0, questionnaireStep - 1);
    renderQuestionnaireStep();
}
