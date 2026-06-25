/** Admin — Po allocation map editor (C2). */

let poMapData = { models: {}, default_ranges: {} };
const adminToken = ""; // Token authentication removed for offline use

function authHeaders() {
    const h = { "Content-Type": "application/json" };
    // Token authentication removed for offline use
    return h;
}

function setStatus(msg) {
    const el = document.getElementById("poMapStatus");
    if (el) el.textContent = msg;
}

function propagateTokenToBackLink() {
    const back = document.getElementById("backToWizard");
    if (back) back.href = `/`; // Token authentication removed for offline use
}

async function loadPoMap() {
    try {
        const res = await fetch("/admin/po-map", { headers: authHeaders() });
        if (!res.ok) {
            setStatus(`Load failed (HTTP ${res.status}).`);
            return;
        }
        poMapData = await res.json();
        renderPoMapEditor();
        setStatus("Loaded.");
    } catch (err) {
        setStatus(`Load error: ${err.message}`);
    }
}

function renderPoMapEditor() {
    const root = document.getElementById("poMapEditor");
    if (!root) return;
    const models = Object.keys(poMapData.models || {});
    let html = "<table class='link-plan-table'><thead><tr><th>Model</th><th>Peer</th><th>KA</th><th>Planner</th><th>Downlink</th><th>Uplink</th></tr></thead><tbody>";
    models.forEach((m) => {
        const row = poMapData.models[m];
        html += `<tr data-model="${m}">
            <td>${m}</td>
            ${["peer_link", "keepalive", "planner", "downlink", "uplink"].map((k) => {
                const v = row[k] || [];
                return `<td><input type="text" class="po-range-input" data-key="${k}" value="${v[0] || ""}-${v[1] || ""}" placeholder="10-19"></td>`;
            }).join("")}
        </tr>`;
    });
    html += "</tbody></table>";
    root.innerHTML = html;
}

function parseRange(s) {
    const parts = String(s).split("-").map((x) => parseInt(x.trim(), 10));
    if (parts.length >= 2 && !Number.isNaN(parts[0]) && !Number.isNaN(parts[1])) return [parts[0], parts[1]];
    return null;
}

async function savePoMap() {
    const models = {};
    document.querySelectorAll("#poMapEditor tr[data-model]").forEach((tr) => {
        const m = tr.dataset.model;
        const entry = {};
        tr.querySelectorAll(".po-range-input").forEach((inp) => {
            const r = parseRange(inp.value);
            if (r) entry[inp.dataset.key] = r;
        });
        models[m] = entry;
    });
    const res = await fetch("/admin/po-map", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ models }),
    });
    if (res.ok) {
        setStatus("Saved — wizard uses new ranges on next validate.");
        poMapData = await res.json();
    } else {
        setStatus(`Save failed (HTTP ${res.status}).`);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    propagateTokenToBackLink();
    loadPoMap();
});
