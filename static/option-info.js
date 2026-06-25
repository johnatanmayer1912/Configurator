/** Option encyclopedia — info popups for wizard choices */

function getOptionHelp(optionId) {
    const entry = catalog.option_help?.[optionId];
    if (entry) return entry;
    const feat = catalog.features?.find((f) => f.id === optionId);
    if (feat) return { title: feat.label, summary: feat.description, cli: feat.cli };
    const base = catalog.baseline_options?.find((b) => b.id === optionId);
    if (base) return { title: base.label, summary: base.description, cli: base.cli };
    const dl = catalog.downlink_presets?.find((d) => d.id === optionId);
    if (dl) return { title: dl.label, summary: dl.description };
    const field = catalog.field_hints?.[optionId];
    if (field) return { title: field.label || optionId, summary: field.hint, why: field.why };
    return null;
}

function showOptionInfo(optionId) {
    const data = getOptionHelp(optionId);
    const modal = document.getElementById("optionInfoModal");
    if (!modal) return;
    const title = document.getElementById("optionInfoTitle");
    const body = document.getElementById("optionInfoBody");
    if (!data) {
        if (title) title.textContent = "Option help";
        if (body) body.innerHTML = "<p class='field-note'>No detailed help for this option yet.</p>";
        modal.classList.remove("hidden");
        return;
    }
    if (title) title.textContent = data.title || optionId;
    const rows = [];
    if (data.summary) rows.push(`<p><strong>What it does</strong><br>${escapeHtml(data.summary)}</p>`);
    if (data.why) rows.push(`<p><strong>Why it matters</strong><br>${escapeHtml(data.why)}</p>`);
    if (data.when) rows.push(`<p><strong>When to use</strong><br>${escapeHtml(data.when)}</p>`);
    if (data.cli) rows.push(`<p><strong>CLI effect</strong></p><pre class="info-cli">${escapeHtml(data.cli)}</pre>`);
    if (data.caution) rows.push(`<p class="info-caution"><strong>Note</strong> — ${escapeHtml(data.caution)}</p>`);
    if (data.source) rows.push(`<p class="field-note">Reference: ${escapeHtml(data.source)}</p>`);
    if (body) body.innerHTML = rows.join("") || `<p>${escapeHtml(data.summary || "")}</p>`;
    modal.classList.remove("hidden");
}

function closeOptionInfo() {
    document.getElementById("optionInfoModal")?.classList.add("hidden");
}

function createInfoButton(optionId) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "info-btn";
    btn.setAttribute("aria-label", `Learn more about ${optionId}`);
    btn.textContent = "i";
    btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        showOptionInfo(optionId);
    });
    return btn;
}

function labelWithInfo(text, optionId) {
    const wrap = document.createElement("span");
    wrap.className = "toggle-label-wrap";
    const label = document.createElement("span");
    label.textContent = text;
    wrap.appendChild(label);
    wrap.appendChild(createInfoButton(optionId));
    return wrap;
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeOptionInfo();
});
