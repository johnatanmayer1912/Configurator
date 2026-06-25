/** Live topology diagram (B2) — clean, legible fabric sketch from wizard state. */

const TOPO_W = 360;
const TOPO_H = 210;
const NODE_W = 104;
const NODE_H = 42;

function topoNode(cx, cy, label, cls) {
    const x = cx - NODE_W / 2;
    const y = cy - NODE_H / 2;
    return (
        `<rect x="${x}" y="${y}" width="${NODE_W}" height="${NODE_H}" rx="9" class="topo-node ${cls}"/>` +
        `<text x="${cx}" y="${cy + 4}" text-anchor="middle" class="topo-label">${escapeHtml(label)}</text>`
    );
}

function topoLink(x1, y1, x2, y2, cls) {
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="topo-link ${cls}"/>`;
}

function topoCaption(x, y, text) {
    return `<text x="${x}" y="${y}" text-anchor="middle" class="topo-caption">${escapeHtml(text)}</text>`;
}

function renderTopologyDiagram() {
    const host = document.getElementById("topologySvg");
    const finalHost = document.getElementById("finalTopologySvg");
    if (!host && !finalHost) return;

    const scenario = selectedScenario?.id || "";
    const isCore = scenario === "vpc_core_pair";
    const isVpc = selectedScenario?.redundancy === "vpc" || roadmap?.vpc;
    const rows = typeof linkPlannerRows !== "undefined" ? linkPlannerRows : { downlink: [], uplink: [] };
    
    const downlinks = (rows.downlink || []).filter((r) => r.enabled !== false);
    const uplinks = (rows.uplink || []).filter((r) => r.enabled !== false);
    const dl = downlinks.length;
    const ul = uplinks.length;

    const nodeW = 104;
    const nodeH = 42;
    const gap = 30;
    const maxNodes = Math.max(2, Math.max(1, dl), Math.max(1, ul));
    const TOPO_W = Math.max(360, maxNodes * (nodeW + gap));
    const TOPO_H = 280;
    const midX = TOPO_W / 2;

    let svg = `<svg viewBox="0 0 ${TOPO_W} ${TOPO_H}" class="topology-svg" role="img" aria-label="Fabric topology diagram">`;
    svg += `
    <defs>
        <filter id="topoShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.35"/>
        </filter>
    </defs>
    `;

    const topoCurve = (x1, y1, x2, y2, cls) => {
        const midY = (y1 + y2) / 2;
        return `<path d="M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}" class="topo-link ${cls}" fill="none"/>`;
    };
    
    const topoNodeF = (cx, cy, label, cls) => {
        const x = cx - nodeW / 2;
        const y = cy - nodeH / 2;
        return (
            `<rect x="${x}" y="${y}" width="${nodeW}" height="${nodeH}" rx="10" class="topo-node ${cls}" filter="url(#topoShadow)"/>` +
            `<text x="${cx}" y="${cy + 4}" text-anchor="middle" class="topo-label">${escapeHtml(label)}</text>`
        );
    };

    if (isVpc) {
        const leftX = midX - 80;
        const rightX = midX + 80;
        const topY = 46;
        const midY = 136;
        const botY = 226;
        const selfLabel = isCore ? "Core vPC-A" : "This switch";
        const peerLabel = isCore ? "Core vPC-B" : "vPC peer (-B)";

        if (ul === 0) {
            svg += topoCurve(leftX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoCurve(rightX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoNodeF(midX, topY, "Uplink ▲", "spine");
        } else {
            const startX = midX - ((ul - 1) * (nodeW + gap)) / 2;
            uplinks.forEach((u, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(leftX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                svg += topoCurve(rightX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                svg += topoNodeF(nx, topY, u.label || "Spine", "spine");
            });
        }

        svg += `<line x1="${leftX + nodeW / 2}" y1="${midY}" x2="${rightX - nodeW / 2}" y2="${midY}" class="topo-link peer"/>`;
        svg += topoCaption(midX, midY - 14, "peer-link + keepalive");
        svg += topoNodeF(leftX, midY, selfLabel, "core");
        svg += topoNodeF(rightX, midY, peerLabel, "peer");

        if (dl === 0) {
            svg += topoCurve(leftX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoCurve(rightX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoNodeF(midX, botY, "Hosts / Leaf ▼", "leaf");
        } else {
            const startX = midX - ((dl - 1) * (nodeW + gap)) / 2;
            downlinks.forEach((d, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(leftX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                svg += topoCurve(rightX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                svg += topoNodeF(nx, botY, d.label || "Leaf", "leaf");
            });
        }
    } else {
        const topY = 46;
        const midY = 136;
        const botY = 226;
        
        if (ul === 0) {
            svg += topoCurve(midX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoNodeF(midX, topY, "Uplink ▲", "spine");
        } else {
            const startX = midX - ((ul - 1) * (nodeW + gap)) / 2;
            uplinks.forEach((u, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(midX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                svg += topoNodeF(nx, topY, u.label || "Spine", "spine");
            });
        }
        
        svg += topoNodeF(midX, midY, "This switch", "access");

        if (dl === 0) {
            svg += topoCurve(midX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoNodeF(midX, botY, "Access hosts ▼", "leaf");
        } else {
            const startX = midX - ((dl - 1) * (nodeW + gap)) / 2;
            downlinks.forEach((d, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(midX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                svg += topoNodeF(nx, botY, d.label || "Host", "leaf");
            });
        }
    }

    svg += "</svg>";
    if (host) host.innerHTML = svg;
    if (finalHost) finalHost.innerHTML = svg;
}

let _topoLastSignature = "";
document.addEventListener("DOMContentLoaded", () => {
    setInterval(() => {
        const panel = document.getElementById("topologyPanel");
        const finalPanel = document.getElementById("finalTopologyPanel");
        const onStep4 = document.getElementById("step-4")?.classList.contains("active");
        const onStep5 = document.getElementById("step-5")?.classList.contains("active");
        
        const show4 = onStep4 && panel && !panel.hidden;
        const show5 = onStep5 && finalPanel && !finalPanel.hidden;
        if (!show4 && !show5) return;
        
        const rows = typeof linkPlannerRows !== "undefined" ? linkPlannerRows : { downlink: [], uplink: [] };
        const sig = `${selectedScenario?.id || ""}|${selectedScenario?.redundancy || ""}|${JSON.stringify(rows)}`;
        if (sig === _topoLastSignature) return;
        _topoLastSignature = sig;
        renderTopologyDiagram();
    }, 1000);
});
