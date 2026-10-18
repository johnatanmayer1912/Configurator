/** Live topology diagram (B2) — clean, legible fabric sketch from wizard state. */

const TOPO_W = 360;
const TOPO_H = 210;
const NODE_W = 80;
const NODE_H = 36;

function topoNode(cx, cy, label, cls, tooltip = null, nodeId = null) {
    const x = cx - NODE_W / 2;
    const y = cy - NODE_H / 2;
    let node = `<rect x="${x}" y="${y}" width="${NODE_W}" height="${NODE_H}" rx="9" class="topo-node ${cls}"`;
    if (nodeId) {
        node += ` data-node-id="${nodeId}"`;
    }
    node += `>`;
    if (tooltip) {
        node += `<title>${escapeHtml(tooltip)}</title>`;
    }
    node += `</rect>`;
    node += `<text x="${cx}" y="${cy + 4}" text-anchor="middle" class="topo-label">${escapeHtml(label)}</text>`;
    return node;
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

    // Check if in multi-switch mode
    if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode && typeof deployment !== 'undefined' && deployment.switches.length > 0) {
        renderMultiSwitchTopology(host, finalHost);
        return;
    }

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
            <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.25"/>
        </filter>
        <filter id="topoGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <linearGradient id="nodeGradientCore" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#0A84FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#007AFF;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="nodeGradientPeer" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#30D158;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#28CD41;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="nodeGradientSpine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#FF9F0A;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#FF9500;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="nodeGradientLeaf" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#BF5AF2;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#AF52DE;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="nodeGradientAccess" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#64D2FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#5AC8FA;stop-opacity:1" />
        </linearGradient>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0A84FF" opacity="0.6"/>
        </marker>
    </defs>
    `;

    const topoCurve = (x1, y1, x2, y2, cls) => {
        const midY = (y1 + y2) / 2;
        return `<path d="M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}" class="topo-link ${cls}" fill="none"/>`;
    };
    
    const topoNodeF = (cx, cy, label, cls, tooltip = null, nodeId = null) => {
        const x = cx - nodeW / 2;
        const y = cy - nodeH / 2;
        let gradientId = "nodeGradientAccess";
        if (cls === "core") gradientId = "nodeGradientCore";
        else if (cls === "peer") gradientId = "nodeGradientPeer";
        else if (cls === "spine") gradientId = "nodeGradientSpine";
        else if (cls === "leaf") gradientId = "nodeGradientLeaf";
        
        let node = `<g class="topo-node-group" style="cursor: pointer;"`;
        if (nodeId) {
            node += ` data-node-id="${nodeId}"`;
            node += ` data-action="select-topology-node"`;
        }
        node += `>`;
        
        let rect = `<rect x="${x}" y="${y}" width="${nodeW}" height="${nodeH}" rx="12" class="topo-node ${cls}" filter="url(#topoShadow)" fill="url(#${gradientId})"`;
        rect += ` style="transition: all 0.2s ease;"`;
        rect += ` onmouseover="this.setAttribute('filter', 'url(#topoGlow)')"`;
        rect += ` onmouseout="this.setAttribute('filter', 'url(#topoShadow)')"`;
        if (tooltip) {
            rect += `><title>${escapeHtml(tooltip)}</title></rect>`;
        } else {
            rect += `></rect>`;
        }
        node += rect;
        node += `<text x="${cx}" y="${cy + 4}" text-anchor="middle" class="topo-label" style="font-weight: 600; fill: white; pointer-events: none;">${escapeHtml(label)}</text>`;
        node += `</g>`;
        return node;
    };

    if (isVpc) {
        const leftX = midX - 80;
        const rightX = midX + 80;
        const topY = 46;
        const midY = 136;
        const botY = 226;
        
        // Get device info for tooltips
        const hostname = document.getElementById("hostname")?.value || "Switch";
        const mgmtIp = document.getElementById("mgmt_ip")?.value || "";
        const siteName = document.getElementById("site_name")?.value || "";
        const vpcDomain = document.getElementById("vpc_domain")?.value || "100";
        
        // Use actual hostname for self, generate peer hostname
        const selfLabel = hostname.substring(0, 8);
        const secondaryHostname = document.getElementById("hostname_secondary")?.value || "";
        let peerHostname;
        if (secondaryHostname) {
            peerHostname = secondaryHostname;
        } else {
            // Generate peer hostname by replacing -A with -B, or adding -B if no suffix
            if (hostname.endsWith("-A")) {
                peerHostname = hostname.replace(/-A$/, "-B");
            } else {
                peerHostname = hostname + "-B";
            }
        }
        const peerLabel = peerHostname.substring(0, 8);
        
        const selfTooltip = `${hostname}\nMgmt IP: ${mgmtIp}\nSite: ${siteName}\nvPC Domain: ${vpcDomain}\nUplinks: ${ul}\nDownlinks: ${dl}`;
        const peerTooltip = `vPC Peer\nHostname: ${peerHostname}\nMgmt IP: ${document.getElementById("mgmt_ip_secondary")?.value || "Auto-generated"}\nvPC Domain: ${vpcDomain}\nUplinks: ${ul}\nDownlinks: ${dl}`;

        if (ul === 0) {
            svg += topoCurve(leftX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoCurve(rightX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoNodeF(midX, topY, "▲", "spine", "Uplink to spine");
        } else {
            const startX = midX - ((ul - 1) * (nodeW + gap)) / 2;
            uplinks.forEach((u, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(leftX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                svg += topoCurve(rightX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                const shortLabel = u.description?.substring(0, 8) || u.label?.substring(0, 8) || "Spine";
                const tooltip = `Uplink: ${u.description || u.label}\nMembers: ${u.members}\nPo ID: ${u.po_id}`;
                svg += topoNodeF(nx, topY, shortLabel, "spine", tooltip, `uplink-${i}`);
            });
        }

        svg += `<line x1="${leftX + nodeW / 2}" y1="${midY}" x2="${rightX - nodeW / 2}" y2="${midY}" class="topo-link peer"/>`;
        svg += topoCaption(midX, midY - 14, "peer-link");
        svg += topoNodeF(leftX, midY, selfLabel, "core", selfTooltip, "node-self");
        svg += topoNodeF(rightX, midY, peerLabel, "peer", peerTooltip, "node-peer");

        if (dl === 0) {
            svg += topoCurve(leftX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoCurve(rightX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoNodeF(midX, botY, "▼", "leaf", "Downlinks to hosts/leaf");
        } else {
            const startX = midX - ((dl - 1) * (nodeW + gap)) / 2;
            downlinks.forEach((d, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(leftX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                svg += topoCurve(rightX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                const shortLabel = d.description?.substring(0, 8) || d.label?.substring(0, 8) || "Leaf";
                const tooltip = `Downlink: ${d.description || d.label}\nMembers: ${d.members}\nPo ID: ${d.po_id}\nvPC ID: ${d.vpc_id}`;
                svg += topoNodeF(nx, botY, shortLabel, "leaf", tooltip, `downlink-${i}`);
            });
        }
    } else {
        const topY = 46;
        const midY = 136;
        const botY = 226;
        
        const hostname = document.getElementById("hostname")?.value || "Switch";
        const mgmtIp = document.getElementById("mgmt_ip")?.value || "";
        const siteName = document.getElementById("site_name")?.value || "";
        const selfTooltip = `${hostname}\nMgmt IP: ${mgmtIp}\nSite: ${siteName}\nUplinks: ${ul}\nDownlinks: ${dl}`;
        
        if (ul === 0) {
            svg += topoCurve(midX, midY - nodeH / 2, midX, topY + nodeH / 2, "up");
            svg += topoNodeF(midX, topY, "▲", "spine", "Uplink to spine");
        } else {
            const startX = midX - ((ul - 1) * (nodeW + gap)) / 2;
            uplinks.forEach((u, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(midX, midY - nodeH / 2, nx, topY + nodeH / 2, "up");
                const shortLabel = u.description?.substring(0, 8) || u.label?.substring(0, 8) || "Spine";
                const tooltip = `Uplink: ${u.description || u.label}\nMembers: ${u.members}\nPo ID: ${u.po_id}`;
                svg += topoNodeF(nx, topY, shortLabel, "spine", tooltip, `uplink-${i}`);
            });
        }
        
        svg += topoNodeF(midX, midY, "SW", "access", selfTooltip, "node-self");

        if (dl === 0) {
            svg += topoCurve(midX, midY + nodeH / 2, midX, botY - nodeH / 2, "down");
            svg += topoNodeF(midX, botY, "▼", "leaf", "Downlinks to hosts");
        } else {
            const startX = midX - ((dl - 1) * (nodeW + gap)) / 2;
            downlinks.forEach((d, i) => {
                const nx = startX + i * (nodeW + gap);
                svg += topoCurve(midX, midY + nodeH / 2, nx, botY - nodeH / 2, "down");
                const shortLabel = d.description?.substring(0, 8) || d.label?.substring(0, 8) || "Host";
                const tooltip = `Downlink: ${d.description || d.label}\nMembers: ${d.members}\nPo ID: ${d.po_id}`;
                svg += topoNodeF(nx, botY, shortLabel, "leaf", tooltip, `downlink-${i}`);
            });
        }
    }

    svg += "</svg>";
    if (host) host.innerHTML = svg;
    if (finalHost) finalHost.innerHTML = svg;
    
    // Render port panel in review step for single-switch mode
    if (finalHost && typeof renderSwitchPortPanel === 'function') {
        renderSwitchPortPanel(null);
    }
}

function renderMultiSwitchTopology(host, finalHost) {
    const switches = deployment.switches;
    const vpcPairs = deployment.vpc_pairs || [];
    const uplinks = deployment.uplinks || [];
    
    // Enhanced layout for enterprise-level presentation
    const nodeW = 140;
    const nodeH = 70;
    const gap = 60;
    
    // Group switches by role using role field directly
    const coreSwitches = switches.filter(s => s.role === "core");
    const spineSwitches = switches.filter(s => s.role === "spine");
    const leaf10gSwitches = switches.filter(s => s.role === "leaf" && (s.model?.includes("93180") || s.model?.toLowerCase().includes("10g")));
    const leaf1gSwitches = switches.filter(s => s.role === "leaf" && (s.model?.includes("9348") || s.model?.toLowerCase().includes("1g")));
    // Catch-all: any leaf that didn't match the specific model patterns above
    const classifiedLeafHostnames = new Set([...leaf10gSwitches, ...leaf1gSwitches].map(s => s.hostname));
    const genericLeafSwitches = switches.filter(s =>
        s.role === "leaf" && !classifiedLeafHostnames.has(s.hostname)
    );
    // Any switch with an unrecognised role ends up here
    const otherSwitches = switches.filter(s =>
        s.role !== "core" && s.role !== "spine" && s.role !== "leaf"
    );

    const maxSwitchesInRow = Math.max(
        coreSwitches.length, spineSwitches.length,
        leaf10gSwitches.length, leaf1gSwitches.length,
        genericLeafSwitches.length, otherSwitches.length, 1
    );
    const TOPO_W = Math.max(500, maxSwitchesInRow * (nodeW + gap) + gap * 2);
    // Grow the height dynamically to accommodate additional rows
    const rowCount = [coreSwitches, spineSwitches, leaf10gSwitches, leaf1gSwitches, genericLeafSwitches, otherSwitches]
        .filter(arr => arr.length > 0).length;
    const TOPO_H = Math.max(400, 80 + rowCount * (nodeH + gap + 20));
    
    let svg = `<svg viewBox="0 0 ${TOPO_W} ${TOPO_H}" class="topology-svg" role="img" aria-label="Multi-switch deployment topology">`;
    
    // Add enterprise-grade styling with Apple-level gradients
    svg += `
    <defs>
        <filter id="nodeShadow" x="-30%" y="-30%" width="160%" height="160%">
            <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.25"/>
        </filter>
        <filter id="nodeGlow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="connectionGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <linearGradient id="gradientCore" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#007AFF;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#0055D4;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#003D99;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradientLeaf10g" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#34C759;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#30B050;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#248A3D;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradientLeaf1g" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#FF9500;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#FF8800;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#CC7A00;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradientSpine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#AF52DE;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#9B4DD4;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8B45C7;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradientDefault" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#8E8E93;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#636366;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#48484A;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradientVpc" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#007AFF;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#00C7BE;stop-opacity:0.8" />
        </linearGradient>
    </defs>
    `;
    
    // Enhanced node with status indicators
    const topoNode = (cx, cy, label, cls, tooltip = null, hostname = null, status = "ok") => {
        const x = cx - nodeW / 2;
        const y = cy - nodeH / 2;
        
        let gradientId = "gradientDefault";
        if (cls === "core") gradientId = "gradientCore";
        else if (cls === "leaf_10g") gradientId = "gradientLeaf10g";
        else if (cls === "leaf_1g") gradientId = "gradientLeaf1g";
        else if (cls === "spine") gradientId = "gradientSpine";
        
        const displayLabel = label.length > 12 ? label.substring(0, 12) + "..." : label;
        const clickHostname = hostname || label;
        
        // Status indicator color with Apple-level refinement
        let statusColor = "#34C759"; // Apple green for ok
        if (status === "warning") statusColor = "#FF9500"; // Apple orange
        if (status === "error") statusColor = "#FF3B30"; // Apple red
        
        let node = `<g class="topo-node-group" style="cursor: pointer;" data-action="select-topology-node" data-node-id="${clickHostname}">`;
        node += `<rect x="${x}" y="${y}" width="${nodeW}" height="${nodeH}" rx="16" class="topo-node ${cls}" fill="url(#${gradientId})" stroke="rgba(255,255,255,0.3)" stroke-width="2" filter="url(#nodeShadow)" style="transition: all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);">`;
        if (tooltip) {
            node += `<title>${escapeHtml(tooltip)}</title>`;
        }
        node += `</rect>`;
        
        // Status indicator dot with glow
        node += `<circle cx="${x + nodeW - 16}" cy="${y + 16}" r="7" fill="${statusColor}" stroke="rgba(255,255,255,0.8)" stroke-width="2" filter="url(#connectionGlow)"/>`;
        
        // Hostname with refined typography
        node += `<text x="${cx}" y="${cy - 10}" text-anchor="middle" class="topo-label" style="font-size: 14px; font-weight: 700; fill: white; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; letter-spacing: -0.5px; pointer-events: none;">${escapeHtml(displayLabel)}</text>`;
        
        // Role badge with refined styling
        let roleLabel = cls.replace("leaf_", "").toUpperCase();
        node += `<text x="${cx}" y="${cy + 14}" text-anchor="middle" class="topo-role" style="font-size: 11px; font-weight: 600; fill: rgba(255,255,255,0.95); font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; letter-spacing: 0.5px; pointer-events: none;">${escapeHtml(roleLabel)}</text>`;
        
        node += `</g>`;
        return node;
    };
    
    // Enhanced connection with validation indicators and Apple-level styling
    const topoConnection = (x1, y1, x2, y2, cls = "default", label = null, validated = true) => {
        let link = `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="topo-link ${cls}"`;
        
        if (cls === "vpc") {
            link += ` stroke="url(#gradientVpc)" stroke-width="5" stroke-linecap="round" filter="url(#connectionGlow)"`;
        } else if (validated) {
            link += ` stroke="#34C759" stroke-width="3" stroke-linecap="round" stroke-opacity="0.9"`;
        } else {
            link += ` stroke="#FF3B30" stroke-width="3" stroke-linecap="round" stroke-dasharray="8,4" stroke-opacity="0.9"`;
        }
        link += ` style="transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);" onmouseover="this.setAttribute('stroke-width', '${cls === 'vpc' ? '7' : '5'}'); this.style.opacity='1'" onmouseout="this.setAttribute('stroke-width', '${cls === 'vpc' ? '5' : '3'}'); this.style.opacity='0.9'"`;
        link += `/>`;
        
        if (label) {
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2 - 14;
            const bgColor = validated ? "rgba(52, 199, 89, 0.95)" : "rgba(255, 59, 48, 0.95)";
            link += `<rect x="${midX - 24}" y="${midY - 11}" width="48" height="22" rx="6" fill="${bgColor}" stroke="rgba(255,255,255,0.3)" stroke-width="1" filter="url(#nodeShadow)" style="pointer-events: none;"/>`;
            link += `<text x="${midX}" y="${midY + 5}" text-anchor="middle" class="topo-caption" style="font-size: 12px; font-weight: 700; fill: white; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; pointer-events: none;">${escapeHtml(label)}</text>`;
        }
        
        return link;
    };
    
    // Calculate positions with better spacing
    const positions = {};
    let yOffset = 60;
    
    // Helper to assign a row of switches to positions
    const assignRow = (group, role) => {
        if (group.length === 0) return;
        const startX = (TOPO_W - group.length * (nodeW + gap)) / 2 + nodeW / 2;
        group.forEach((sw, i) => {
            const cx = startX + i * (nodeW + gap);
            positions[sw.hostname] = { x: cx, y: yOffset, role };
        });
        yOffset += gap + nodeH + 20;
    };

    // Row order: spine → core → 10G leaf → 1G leaf → generic leaf → other
    assignRow(spineSwitches, "spine");
    assignRow(coreSwitches, "core");
    assignRow(leaf10gSwitches, "leaf_10g");
    assignRow(leaf1gSwitches, "leaf_1g");
    assignRow(genericLeafSwitches, "leaf_10g");  // render generic leaf same style as 10G
    assignRow(otherSwitches, "default");
    
    // Validate connections
    const validateUplink = (fromSw, toSw) => {
        const fromPos = positions[fromSw];
        const toPos = positions[toSw];
        if (!fromPos || !toPos) return false;
        
        // Check if uplink exists in deployment
        const uplink = uplinks.find(u => u.from === fromSw && u.to === toSw);
        return !!uplink;
    };
    
    // Draw vPC peer links with enhanced styling
    vpcPairs.forEach(pair => {
        const fromPos = positions[pair.primary];
        const toPos = positions[pair.secondary];
        if (fromPos && toPos) {
            svg += topoConnection(fromPos.x, fromPos.y, toPos.x, toPos.y, "vpc", `vPC ${pair.domain}`, true);
        }
    });
    
    // Draw validated uplinks
    uplinks.forEach(uplink => {
        const fromPos = positions[uplink.from];
        const toPos = positions[uplink.to];
        if (fromPos && toPos) {
            const validated = true; // Assume validated if in deployment
            svg += topoConnection(fromPos.x, fromPos.y + nodeH / 2, toPos.x, toPos.y - nodeH / 2, "uplink", `PO${uplink.po_id}`, validated);
        }
    });
    
    // Draw all switches with status indicators
    switches.forEach((sw) => {
        const pos = positions[sw.hostname];
        if (!pos) return;
        
        // Determine status based on configuration
        let status = "ok";
        const vpcPair = vpcPairs.find(p => p.primary === sw.hostname || p.secondary === sw.hostname);
        
        // Check for configuration issues
        if (!sw.mgmt_ip || sw.mgmt_ip === "") {
            status = "warning";
        }
        if (vpcPair && !sw.vpc_domain) {
            status = "warning";
        }
        
        const vpcInfo = vpcPair ? `vPC Domain ${vpcPair.domain}` : 'Standalone';
        const uplinkCount = uplinks.filter(u => u.from === sw.hostname || u.to === sw.hostname).length;
        
        const tooltip = `${sw.hostname}\nModel: ${sw.model}\nMgmt IP: ${sw.mgmt_ip || 'Not configured'}\nRole: ${pos.role}\n${vpcInfo}\nUplinks: ${uplinkCount}\nStatus: ${status.toUpperCase()}\n\nClick to view configuration`;
        
        svg += topoNode(pos.x, pos.y, sw.hostname, pos.role, tooltip, sw.hostname, status);
    });
    
    svg += "</svg>";
    if (host) host.innerHTML = svg;
    if (finalHost) finalHost.innerHTML = svg;
    
    // Enhanced legend with status indicators
    const legend = `
    <div style="display: flex; justify-content: center; gap: 25px; margin-top: 20px; font-size: 13px; color: #98989D; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #0A84FF, #0055D4); border: 2px solid white; border-radius: 6px;"></div>
            <span>Core Switch</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #30D158, #248A3D); border: 2px solid white; border-radius: 6px;"></div>
            <span>10G Leaf</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #FF9F0A, #CC7A00); border: 2px solid white; border-radius: 6px;"></div>
            <span>1G Leaf</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: #30D158; border: 2px solid white; border-radius: 50%;"></div>
            <span>Configured</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: #FF9F0A; border: 2px solid white; border-radius: 50%;"></div>
            <span>Warning</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background: #FF453A; border: 2px solid white; border-radius: 50%;"></div>
            <span>Error</span>
        </div>
    </div>
    `;
    
    if (host) {
        const legendDiv = document.createElement("div");
        legendDiv.innerHTML = legend;
        host.parentNode.insertBefore(legendDiv, host.nextSibling);
    }
    if (finalHost) {
        const legendDiv = document.createElement("div");
        legendDiv.innerHTML = legend;
        finalHost.parentNode.insertBefore(legendDiv, finalHost.nextSibling);
    }
    
    // Render deployment summary and port panel in review
    if (finalHost && switches.length > 0) {
        if (typeof renderDeploymentSummary === 'function') {
            renderDeploymentSummary();
        }
        // Don't automatically render port panel for first switch in multi-switch mode
        // Let user click on topology nodes to see individual switch configurations
        console.log("Multi-switch topology rendered with", switches.length, "switches");
    } else if (finalHost && !multiSwitchMode) {
        // Single switch mode - render port panel
        if (typeof renderSwitchPortPanel === 'function') {
            renderSwitchPortPanel(null);
        }
    }
}

let _topoLastSignature = "";
document.addEventListener("DOMContentLoaded", () => {
    setInterval(() => {
        const panel = document.getElementById("topologyPanel");
        const finalPanel = document.getElementById("finalTopologyPanel");
        const onStep7 = document.getElementById("step-7")?.classList.contains("active");
        const onStep8 = document.getElementById("step-8")?.classList.contains("active");
        
        const show7 = onStep7 && panel && !panel.hidden;
        const show8 = onStep8 && finalPanel && !finalPanel.hidden;
        if (!show7 && !show8) return;
        
        const rows = typeof linkPlannerRows !== "undefined" ? linkPlannerRows : { downlink: [], uplink: [] };
        const isMultiSwitchMode = typeof multiSwitchMode !== "undefined" ? multiSwitchMode : false;
        const deploymentSig = typeof deployment !== "undefined" && deployment ? JSON.stringify({
            switches: deployment.switches?.length || 0,
            vpc_pairs: deployment.vpc_pairs?.length || 0,
            uplinks: deployment.uplinks?.length || 0
        }) : "";

        const sig = `${selectedScenario?.id || ""}|${selectedScenario?.redundancy || ""}|${JSON.stringify(rows)}|${isMultiSwitchMode}|${deploymentSig}`;
        if (sig === _topoLastSignature) return;
        _topoLastSignature = sig;
        renderTopologyDiagram();
    }, 1000);
});
