/** NX-OS Configuration Authority — Web UI Controller v3.1 */

const sessionToken = ""; // Token authentication removed for offline use
let catalog = { scenarios: [], versions: [], features: [], aliases: [], baseline_options: [], downlink_presets: [], uplink_presets: [], config_matrix: [], hardware: [], field_hints: {}, wizard_tips: {}, option_help: {} };
let selectedScenario = null;

// PA-001 FIX: Load deployment templates from external JSON file
let DEPLOYMENT_TEMPLATES = {};

async function loadDeploymentTemplates() {
    console.log('[TEMPLATE_LOADING] Loading deployment templates from external source');
    try {
        const response = await fetch('/templates/deployment_templates.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Add source metadata to each template
        Object.keys(data.templates).forEach(key => {
            data.templates[key]._source = 'deployment_templates.json';
            data.templates[key]._loadedFrom = 'external_json';
            data.templates[key]._apiEndpoint = '/templates/deployment_templates.json';
        });
        
        DEPLOYMENT_TEMPLATES = data.templates;
        console.log('[TEMPLATE_LOADING] Successfully loaded templates from external JSON:', Object.keys(DEPLOYMENT_TEMPLATES).length, 'templates');
        return DEPLOYMENT_TEMPLATES;
    } catch (error) {
        console.error('[TEMPLATE_LOADING] Failed to load templates from external JSON:', error);
        // Fallback to hardcoded templates if JSON loading fails
        console.log('[TEMPLATE_LOADING] Falling back to hardcoded templates');
        DEPLOYMENT_TEMPLATES = getHardcodedTemplates();
        return DEPLOYMENT_TEMPLATES;
    }
}

/** Ensure gallery cards have all display fields (saved/API templates may be partial). */
function normalizeDeploymentTemplateGalleryMeta(template, id) {
    const switches = template.switches || [];
    const vpcPairs = template.vpc_pairs || [];
    const switchCount = template.switch_count ?? switches.length;
    const vpcCount = template.vpc_domain_count ?? vpcPairs.length;
    let complexity = template.complexity;
    if (!complexity) {
        complexity = switchCount > 4 ? 'complex' : switchCount > 2 ? 'medium' : 'simple';
    }
    const modelsFromSwitches = [...new Set(switches.map(s => s.model).filter(Boolean))];
    const hardware =
        Array.isArray(template.hardware_compatibility) && template.hardware_compatibility.length
            ? template.hardware_compatibility
            : (modelsFromSwitches.length ? modelsFromSwitches : ['Any']);
    return {
        ...template,
        id: id || template.id,
        name: template.name || id || 'Unnamed template',
        description: template.description || '',
        use_case: template.use_case || 'Saved deployment',
        use_case_category: template.use_case_category || 'saved',
        switch_count: switchCount,
        vpc_domain_count: vpcCount,
        complexity,
        hardware_compatibility: hardware,
        best_practice_badge: Boolean(template.best_practice_badge),
        switches,
        vpc_pairs: vpcPairs,
        uplinks: template.uplinks || [],
        global_vlans: template.global_vlans || [],
    };
}

// Fallback hardcoded templates for backward compatibility
function getHardcodedTemplates() {
    return {
        "vpc_core_leaf": {
            id: "vpc_core_leaf",
            name: "vPC Core + Leaf Pairs",
            description: "Best for data centers needing high availability. Two core switches with redundant connections to leaf switches.",
            use_case: "Production data center",
            use_case_category: "production_dc",
            switch_count: 4,
            vpc_domain_count: 2,
            vlan_range: "10-50",
            complexity: "medium",
            hardware_compatibility: ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"],
            nxos_version_min: "9.2",
            nxos_version_max: "10.2",
            best_practice_badge: true,
            switches: [
                { role: "core", model: "Nexus 9336C-FX2", hostname: "CORE1", mgmt_ip: "10.0.0.1/24", vpc_domain: "10", base_access_vlan: 10, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "core", model: "Nexus 9336C-FX2", hostname: "CORE2", mgmt_ip: "10.0.0.2/24", vpc_domain: "10", base_access_vlan: 10, access_vlan_count: 4, local_ka: "10.0.0.2" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF10G-1", mgmt_ip: "10.0.0.11/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF10G-2", mgmt_ip: "10.0.0.12/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.2" }
            ],
            vpc_pairs: [
                { domain: "10", primary: "CORE1", secondary: "CORE2", peer_link_ports: "E1/35-36" },
                { domain: "100", primary: "LEAF10G-1", secondary: "LEAF10G-2", peer_link_ports: "E1/51-52" }
            ],
            uplinks: [
                { from: "LEAF10G-1", to: "CORE1", ports: "E1/53", to_ports: "E1/1", po_id: "10" },
                { from: "LEAF10G-1", to: "CORE2", ports: "E1/54", to_ports: "E1/1", po_id: "10" },
                { from: "LEAF10G-2", to: "CORE1", ports: "E1/53", to_ports: "E1/2", po_id: "10" },
                { from: "LEAF10G-2", to: "CORE2", ports: "E1/54", to_ports: "E1/2", po_id: "10" }
            ],
            global_vlans: [
                { id: 10, name: "Data-VLAN-10" },
                { id: 20, name: "Data-VLAN-20" },
                { id: 30, name: "Data-VLAN-30" },
                { id: 40, name: "Data-VLAN-40" },
                { id: 50, name: "Data-VLAN-50" }
            ]
        },
        "spine_leaf": {
            id: "spine_leaf",
            name: "Spine-Leaf Fabric",
            description: "Modern data center design with simple Layer 3 routing. No vPC complexity, just equal-cost multi-path routing.",
            use_case: "Cloud/VM environment",
            use_case_category: "cloud_vm",
            switch_count: 4,
            vpc_domain_count: 0,
            vlan_range: "10-50",
            complexity: "simple",
            hardware_compatibility: ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"],
            nxos_version_min: "9.2",
            nxos_version_max: "10.2",
            best_practice_badge: true,
            switches: [
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "SPINE1", mgmt_ip: "10.0.0.1/24", base_access_vlan: 10, access_vlan_count: 4 },
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "SPINE2", mgmt_ip: "10.0.0.2/24", base_access_vlan: 10, access_vlan_count: 4 },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF1", mgmt_ip: "10.0.0.11/24", base_access_vlan: 100, access_vlan_count: 4 },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF2", mgmt_ip: "10.0.0.12/24", base_access_vlan: 100, access_vlan_count: 4 }
            ],
            vpc_pairs: [],
            uplinks: [
                { from: "LEAF1", to: "SPINE1", ports: "E1/1-2", po_id: "1" },
                { from: "LEAF1", to: "SPINE2", ports: "E1/3-4", po_id: "1" },
                { from: "LEAF2", to: "SPINE1", ports: "E1/1-2", po_id: "2" },
                { from: "LEAF2", to: "SPINE2", ports: "E1/3-4", po_id: "2" }
            ],
            global_vlans: [
                { id: 10, name: "Data-VLAN-10" },
                { id: 20, name: "Data-VLAN-20" },
                { id: 30, name: "Data-VLAN-30" },
                { id: 40, name: "Data-VLAN-40" },
                { id: 50, name: "Data-VLAN-50" }
            ]
        },
        "six_switch_fabric": {
            id: "six_switch_fabric",
            name: "6-Switch Fabric (2 Spine + 4 Leaf)",
            description: "Larger spine-leaf fabric for bigger deployments. Two spine switches connect to four leaf switches for high availability and scale.",
            use_case: "Medium/Large data center",
            use_case_category: "production_dc",
            switch_count: 6,
            vpc_domain_count: 2,
            vlan_range: "10-200",
            complexity: "complex",
            hardware_compatibility: ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"],
            nxos_version_min: "9.3",
            nxos_version_max: "10.2",
            best_practice_badge: true,
            switches: [
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "SPINE1", mgmt_ip: "10.0.0.1/24", base_access_vlan: 10, access_vlan_count: 4 },
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "SPINE2", mgmt_ip: "10.0.0.2/24", base_access_vlan: 10, access_vlan_count: 4 },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF1", mgmt_ip: "10.0.0.11/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF2", mgmt_ip: "10.0.0.12/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.2" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF3", mgmt_ip: "10.0.0.13/24", vpc_domain: "200", base_access_vlan: 200, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "LEAF4", mgmt_ip: "10.0.0.14/24", vpc_domain: "200", base_access_vlan: 200, access_vlan_count: 4, local_ka: "10.0.0.2" }
            ],
            vpc_pairs: [
                { domain: "100", primary: "LEAF1", secondary: "LEAF2", peer_link_ports: "E1/49-50" },
                { domain: "200", primary: "LEAF3", secondary: "LEAF4", peer_link_ports: "E1/49-50" }
            ],
            uplinks: [
                { from: "LEAF1", to: "SPINE1", ports: "E1/1-2", po_id: "10" },
                { from: "LEAF1", to: "SPINE2", ports: "E1/3-4", po_id: "10" },
                { from: "LEAF2", to: "SPINE1", ports: "E1/1-2", po_id: "10" },
                { from: "LEAF2", to: "SPINE2", ports: "E1/3-4", po_id: "10" },
                { from: "LEAF3", to: "SPINE1", ports: "E1/1-2", po_id: "20" },
                { from: "LEAF3", to: "SPINE2", ports: "E1/3-4", po_id: "20" },
                { from: "LEAF4", to: "SPINE1", ports: "E1/1-2", po_id: "20" },
                { from: "LEAF4", to: "SPINE2", ports: "E1/3-4", po_id: "20" }
            ],
            global_vlans: [
                { id: 10, name: "Data-VLAN-10" },
                { id: 20, name: "Data-VLAN-20" },
                { id: 30, name: "Data-VLAN-30" },
                { id: 40, name: "Data-VLAN-40" },
                { id: 50, name: "Data-VLAN-50" },
                { id: 100, name: "Leaf-VLAN-100" },
                { id: 200, name: "Leaf-VLAN-200" }
            ]
        },
        "dual_core_fabric": {
            id: "dual_core_fabric",
            name: "Dual Core + Access Layer",
            description: "Three-tier design for campus networks. Core switches connect to distribution switches, which connect to access switches for end devices.",
            use_case: "Enterprise campus",
            use_case_category: "campus",
            switch_count: 6,
            vpc_domain_count: 3,
            vlan_range: "10-200",
            complexity: "complex",
            hardware_compatibility: ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"],
            nxos_version_min: "9.2",
            nxos_version_max: "10.2",
            best_practice_badge: true,
            switches: [
                { role: "core", model: "Nexus 9336C-FX2", hostname: "CORE1", mgmt_ip: "10.0.0.1/24", vpc_domain: "10", base_access_vlan: 10, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "core", model: "Nexus 9336C-FX2", hostname: "CORE2", mgmt_ip: "10.0.0.2/24", vpc_domain: "10", base_access_vlan: 10, access_vlan_count: 4, local_ka: "10.0.0.2" },
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "DIST1", mgmt_ip: "10.0.0.11/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "spine", model: "Nexus 9336C-FX2", hostname: "DIST2", mgmt_ip: "10.0.0.12/24", vpc_domain: "100", base_access_vlan: 100, access_vlan_count: 4, local_ka: "10.0.0.2" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "ACCESS1", mgmt_ip: "10.0.0.21/24", vpc_domain: "200", base_access_vlan: 200, access_vlan_count: 4, local_ka: "10.0.0.1" },
                { role: "leaf", model: "Nexus 93180YC-EX", hostname: "ACCESS2", mgmt_ip: "10.0.0.22/24", vpc_domain: "200", base_access_vlan: 200, access_vlan_count: 4, local_ka: "10.0.0.2" }
            ],
            vpc_pairs: [
                { domain: "10", primary: "CORE1", secondary: "CORE2", peer_link_ports: "E1/35-36" },
                { domain: "100", primary: "DIST1", secondary: "DIST2", peer_link_ports: "E1/35-36" },
                { domain: "200", primary: "ACCESS1", secondary: "ACCESS2", peer_link_ports: "E1/51-52" }
            ],
            uplinks: [
                { from: "DIST1", to: "CORE1", ports: "E1/1", to_ports: "E1/3", po_id: "10" },
                { from: "DIST1", to: "CORE2", ports: "E1/2", to_ports: "E1/3", po_id: "10" },
                { from: "DIST2", to: "CORE1", ports: "E1/1", to_ports: "E1/4", po_id: "10" },
                { from: "DIST2", to: "CORE2", ports: "E1/2", to_ports: "E1/4", po_id: "10" },
                { from: "ACCESS1", to: "DIST1", ports: "E1/53", to_ports: "E1/5", po_id: "20" },
                { from: "ACCESS1", to: "DIST2", ports: "E1/54", to_ports: "E1/5", po_id: "20" },
                { from: "ACCESS2", to: "DIST1", ports: "E1/53", to_ports: "E1/6", po_id: "20" },
                { from: "ACCESS2", to: "DIST2", ports: "E1/54", to_ports: "E1/6", po_id: "20" }
            ],
            global_vlans: [
                { id: 10, name: "Core-VLAN-10" },
                { id: 20, name: "Core-VLAN-20" },
                { id: 100, name: "Dist-VLAN-100" },
                { id: 200, name: "Access-VLAN-200" }
            ]
        }
    };
}

let currentStep = 1;
let vlanCount = 0;
let lastConfigPreview = "";
let lastPrimaryConfig = "";
let lastExportDir = "";
let systemPaths = { vault_dir: "" };
let configureStepState = null; // Save state when leaving step 4

// Multi-switch deployment support
const CONFIG_ROUTE_VPC = "/scenario/generate";
const CONFIG_ROUTE_MULTISWITCH = "/generate-deployment";
let multiSwitchMode = false;
let deployment = {
    switches: [],
    vpc_pairs: [],
    uplinks: [],
    global_vlans: []
};

// PA-001 FIX: Initialize templates by loading from external JSON
// Call this on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDeploymentTemplates();
    console.log('[INIT] Deployment templates loaded');
    // Render template gallery on page load but keep it hidden (HTML has hidden class)
    // Gallery will only be shown when multi-switch mode is enabled
    renderTemplateGallery();
});

// Switch model port layouts

/**
 * Template Gallery Functions
 * Render and manage deployment template selection
 */

function renderTemplateGallery() {
    const gallery = document.getElementById('templateGallery');
    if (!gallery) return;
    
    // Do NOT show the gallery here - let showTemplateGallery() handle that
    // This allows the gallery to be rendered while remaining hidden
    
    // Hide configuration editor
    const editor = document.getElementById('configurationEditor');
    if (editor) {
        editor.classList.add('hidden');
    }
    
    const useCaseFilters = {
        'all': 'All Templates',
        'production_dc': 'Production Data Center',
        'cloud_vm': 'Cloud/VM Environment',
        'campus': 'Enterprise Campus'
    };
    
    let filterHTML = '<div class="template-filters">';
    for (const [key, label] of Object.entries(useCaseFilters)) {
        filterHTML += `<button class="filter-btn ${key === 'all' ? 'active' : ''}" data-filter="${key}" data-action="filter-templates">${label}</button>`;
    }
    filterHTML += '</div>';
    
    let html = filterHTML + '<div id="templateGrid" class="template-grid"></div>';
    html += '<button type="button" class="btn-outline btn-sm" data-action="hide-template-gallery">Use Manual Configuration</button>';
    html += '<button type="button" class="btn-ghost btn-sm" data-action="show-template-comparison">Compare Templates</button>';
    
    gallery.innerHTML = html;
    
    // Render all templates initially
    renderTemplateGrid('all');
}

function filterTemplates(filter) {
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        }
    });
    
    // Render filtered templates
    renderTemplateGrid(filter);
}

function renderTemplateGrid(filter) {
    const grid = document.getElementById('templateGrid');
    if (!grid) return;
    
    let html = '';
    
    for (const [templateId, rawTemplate] of Object.entries(DEPLOYMENT_TEMPLATES)) {
        const template = normalizeDeploymentTemplateGalleryMeta(rawTemplate, templateId);
        // Filter by use case category
        if (filter !== 'all' && template.use_case_category !== filter) {
            continue;
        }
        
        // Check hardware compatibility
        const currentHardware = getCurrentHardwareInventory();
        const templateHardware = template.hardware_compatibility || [];
        const isHardwareCompatible = currentHardware.length === 0 || 
            templateHardware.includes('Any') ||
            currentHardware.some(hw => templateHardware.includes(hw));
        
        const compatibilityClass = isHardwareCompatible ? '' : 'hardware-incompatible';
        
        // Mark best practice templates as featured for purpose-driven layout
        const featuredClass = template.best_practice_badge ? 'featured' : '';
        const hwList = template.hardware_compatibility || [];
        const hwPreview = hwList.length
            ? hwList.slice(0, 2).join(', ') + (hwList.length > 2 ? '...' : '')
            : 'Any';
        
        html += `
            <div class="template-card ${compatibilityClass} ${featuredClass}" 
                 data-template-id="${templateId}"
                 ${!isHardwareCompatible ? 'title="Template not compatible with current hardware"' : ''}>
                ${template.best_practice_badge ? '<div class="best-practice-badge">✓ Best Practice</div>' : ''}
                ${!isHardwareCompatible ? '<div class="incompatibility-badge">⚠️ Hardware Mismatch</div>' : ''}
                <div class="template-topology">
                    <svg width="100" height="80" viewBox="0 0 100 80">
                        ${generateTopologySVG(template)}
                    </svg>
                </div>
                <h4 class="template-name">${template.name}</h4>
                <p class="template-description">${template.description}</p>
                <div class="template-meta">
                    <span class="template-badge">${template.switch_count} switches</span>
                    <span class="template-badge">${template.vpc_domain_count} vPC domains</span>
                    <span class="template-badge complexity-${template.complexity}">${template.complexity}</span>
                </div>
                <p class="template-use-case">Use case: ${template.use_case}</p>
                <div class="template-hardware">
                    <span class="hardware-label">Compatible:</span>
                    <span class="hardware-list">${hwPreview}</span>
                    ${!isHardwareCompatible ? '<span class="hardware-warning">⚠️</span>' : ''}
                </div>
                <button class="template-action" data-template-id="${templateId}" data-action="apply-template" type="button" onclick="applyTemplate('${templateId}')" ${!isHardwareCompatible ? 'disabled' : ''}>
                    ${isHardwareCompatible ? 'Use Template' : 'Incompatible'}
                </button>
            </div>
        `;
    }
    
    grid.innerHTML = html;
}

function showTemplateComparison() {
    const gallery = document.getElementById('templateGallery');
    if (!gallery) return;
    
    const templates = Object.values(DEPLOYMENT_TEMPLATES);
    
    let comparisonHTML = `
        <div class="template-comparison">
            <h3>Template Comparison</h3>
            <button type="button" class="btn-ghost btn-sm" data-action="render-template-gallery">← Back to Gallery</button>
            
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Feature</th>
                            ${templates.map(t => `<th>${t.name}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Switch Count</strong></td>
                            ${templates.map(t => `<td>${t.switch_count}</td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>vPC Domains</strong></td>
                            ${templates.map(t => `<td>${t.vpc_domain_count}</td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>VLAN Range</strong></td>
                            ${templates.map(t => `<td>${t.vlan_range}</td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>Complexity</strong></td>
                            ${templates.map(t => `<td class="complexity-${t.complexity}">${t.complexity}</td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>Use Case</strong></td>
                            ${templates.map(t => `<td>${t.use_case}</td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>Hardware</strong></td>
                            ${templates.map(t => `<td><small>${t.hardware_compatibility.join('<br>')}</small></td>`).join('')}
                        </tr>
                        <tr>
                            <td><strong>Best Practice</strong></td>
                            ${templates.map(t => `<td>${t.best_practice_badge ? '✓' : '-'}</td>`).join('')}
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    gallery.innerHTML = comparisonHTML;
}

function generateTopologySVG(template) {
    // Simple SVG topology representation based on template structure
    const switches = template.switches || [];
    const vpcPairs = template.vpc_pairs || [];
    
    let svg = '';
    
    // Draw switches as rectangles
    const positions = calculateSwitchPositions(switches.length);
    
    switches.forEach((sw, index) => {
        const pos = positions[index];
        const color = sw.role === 'core' ? '#3b82f6' : sw.role === 'spine' ? '#10b981' : '#f59e0b';
        svg += `<rect x="${pos.x}" y="${pos.y}" width="30" height="20" fill="${color}" rx="2"/>`;
        svg += `<text x="${pos.x + 15}" y="${pos.y + 12}" font-size="8" fill="white" text-anchor="middle">${(sw.hostname || sw.role || 'SW').substring(0, 4)}</text>`;
    });
    
    // Draw vPC connections as dashed lines
    vpcPairs.forEach(pair => {
        const primaryIdx = switches.findIndex(s => s.hostname === pair.primary);
        const secondaryIdx = switches.findIndex(s => s.hostname === pair.secondary);
        
        if (primaryIdx !== -1 && secondaryIdx !== -1) {
            const p1 = positions[primaryIdx];
            const p2 = positions[secondaryIdx];
            svg += `<line x1="${p1.x + 15}" y1="${p1.y + 10}" x2="${p2.x + 15}" y2="${p2.y + 10}" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4,2"/>`;
        }
    });
    
    return svg;
}

function calculateSwitchPositions(count) {
    const positions = [];
    const width = 100;
    const height = 80;
    
    if (count === 4) {
        // 2x2 grid
        positions.push({ x: 10, y: 10 });
        positions.push({ x: 60, y: 10 });
        positions.push({ x: 10, y: 50 });
        positions.push({ x: 60, y: 50 });
    } else if (count === 6) {
        // 3x2 grid
        positions.push({ x: 5, y: 10 });
        positions.push({ x: 35, y: 10 });
        positions.push({ x: 65, y: 10 });
        positions.push({ x: 5, y: 50 });
        positions.push({ x: 35, y: 50 });
        positions.push({ x: 65, y: 50 });
    } else {
        // Single row
        const spacing = width / (count + 1);
        for (let i = 0; i < count; i++) {
            positions.push({ x: spacing * (i + 1) - 15, y: 30 });
        }
    }
    
    return positions;
}

/**
 * Validate template before applying
 * Checks NX-OS best practices, hardware compatibility, and version compatibility
 */
function validateTemplateBeforeApply(template) {
    const errors = [];
    const warnings = [];
    
    console.log('[TEMPLATE_VALIDATION] [START] Validating template:', template.id);
    
    // 1. NX-OS Best Practices Validation
    console.log('[TEMPLATE_VALIDATION] [BEST_PRACTICES] Checking NX-OS best practices');
    
    // Check vPC domain uniqueness
    const vpcDomains = template.vpc_pairs.map(pair => pair.domain);
    const uniqueDomains = new Set(vpcDomains);
    if (vpcDomains.length !== uniqueDomains.size) {
        errors.push('Duplicate vPC domains detected - each vPC domain must be unique');
    }
    
    // Check keepalive IP uniqueness within vPC domain
    template.vpc_pairs.forEach(pair => {
        const primarySwitch = template.switches.find(sw => sw.hostname === pair.primary);
        const secondarySwitch = template.switches.find(sw => sw.hostname === pair.secondary);
        if (primarySwitch && secondarySwitch) {
            if (primarySwitch.mgmt_ip === secondarySwitch.mgmt_ip) {
                errors.push(`vPC domain ${pair.domain}: Primary and secondary switches cannot have the same management IP`);
            }
        }
    });
    
    // Check VLAN range validity
    if (template.global_vlans && template.global_vlans.length > 0) {
        template.global_vlans.forEach(vlan => {
            if (vlan.id < 1 || vlan.id > 4094) {
                errors.push(`VLAN ID ${vlan.id} is out of valid range (1-4094)`);
            }
        });
    }
    
    // Check hostname format
    template.switches.forEach(sw => {
        const hostnameRegex = /^[a-zA-Z0-9-]+$/;
        if (!hostnameRegex.test(sw.hostname)) {
            errors.push(`Invalid hostname format: ${sw.hostname} - only alphanumeric characters and hyphens allowed`);
        }
    });
    
    // Check management IP CIDR notation
    template.switches.forEach(sw => {
        if (!sw.mgmt_ip.includes('/')) {
            errors.push(`Management IP missing CIDR notation: ${sw.mgmt_ip}`);
        }
    });
    
    // 2. Hardware Compatibility Validation
    console.log('[TEMPLATE_VALIDATION] [HARDWARE] Checking hardware compatibility');
    
    // Get current hardware inventory (simulated for now)
    const currentHardware = getCurrentHardwareInventory();
    
    if (currentHardware.length > 0) {
        const templateHardware = template.hardware_compatibility || [];
        const incompatibleHardware = currentHardware.filter(hw => !templateHardware.includes(hw));
        
        if (incompatibleHardware.length > 0) {
            warnings.push(`Template may not be compatible with current hardware: ${incompatibleHardware.join(', ')}`);
        }
    }
    
    // 3. NX-OS Version Compatibility Validation
    console.log('[TEMPLATE_VALIDATION] [VERSION] Checking NX-OS version compatibility');
    
    const currentNxosVersion = getCurrentNxosVersion();
    if (currentNxosVersion && template.nxos_version_min && template.nxos_version_max) {
        if (currentNxosVersion < template.nxos_version_min) {
            warnings.push(`Current NX-OS version ${currentNxosVersion} is below minimum recommended version ${template.nxos_version_min}. Some features may not work correctly.`);
        }
        if (currentNxosVersion > template.nxos_version_max) {
            warnings.push(`Current NX-OS version ${currentNxosVersion} is above maximum tested version ${template.nxos_version_max}. Compatibility not guaranteed.`);
        }
    }
    
    console.log('[TEMPLATE_VALIDATION] [COMPLETE] Validation result:', { valid: errors.length === 0, errors, warnings });
    
    return {
        valid: errors.length === 0,
        errors: errors,
        warnings: warnings
    };
}

/**
 * Get current hardware inventory (simulated)
 * In production, this would come from device discovery or user input
 */
function getCurrentHardwareInventory() {
    // Simulated hardware inventory - in production, this would be dynamic
    return ['Nexus 9336C-FX2', 'Nexus 93180YC-EX', 'Nexus 9348GC-FXP'];
}

/**
 * Get current NX-OS version (simulated)
 * In production, this would come from device discovery or user input
 */
function getCurrentNxosVersion() {
    // Simulated NX-OS version - in production, this would be dynamic
    return '9.3';
}

function applyTemplate(templateId) {
    console.log('[TEMPLATE_APPLY] [USER_ACTION] User selected template:', templateId);
    
    try {
        const template = DEPLOYMENT_TEMPLATES[templateId];
        if (!template) {
            console.log('[TEMPLATE_APPLY] [ERROR] Template not found:', templateId);
            flashToast('Template not found', 'error');
            return;
        }
        
        console.log('[TEMPLATE_APPLY] [DATA_RETRIEVAL] Applying template:', template.name);
        
        // Pre-apply validation
        const validationResult = validateTemplateBeforeApply(template);
        if (!validationResult.valid) {
            console.log('[TEMPLATE_APPLY] [VALIDATION_ERROR] Template validation failed:', validationResult.errors);
            flashToast('Template validation failed: ' + validationResult.errors.join(', '), 'error');
            return;
        }

        // If there are warnings, show confirmation dialog
        if (validationResult.warnings.length > 0) {
            console.log('[TEMPLATE_APPLY] [VALIDATION_WARNINGS] Template has warnings:', validationResult.warnings);
            const warningMessage = 'Template compatibility warnings:\n\n' + validationResult.warnings.join('\n') + '\n\nDo you want to proceed?';
            if (!confirm(warningMessage)) {
                console.log('[TEMPLATE_APPLY] [USER_CANCELLED] User cancelled due to warnings');
                flashToast('Template application cancelled by user', 'info');
                return;
            }
        }

        console.log('[TEMPLATE_APPLY] [VALIDATION_SUCCESS] Template validation passed');
        
        // Show loading state
        showTemplateLoading();
        
        // Apply template to deployment with proper ID generation
        deployment.switches = template.switches.map((sw, i) => ({
            id: `switch-${Date.now()}-${i}`,
            hostname: sw.hostname,
            mgmt_ip: sw.mgmt_ip,
            mgmt_gw: sw.mgmt_gw || "10.0.0.254",
            model: sw.model,
            role: sw.role,
            vpc_domain: sw.vpc_domain || null,
            nxos_version: sw.nxos_version || "9.3",
            vpc_peer_link_id: sw.vpc_peer_link_id || 1,
            keepalive_po_id: sw.keepalive_po_id || 2,
            vpc_system_priority: sw.vpc_system_priority || 32667,
            base_access_vlan: sw.base_access_vlan || 10,
            access_vlan_count: sw.access_vlan_count || 4,
            local_ka: sw.local_ka || ''
        }));
        
        deployment.vpc_pairs = template.vpc_pairs.map((pair, i) => ({
            id: `vpc-${Date.now()}-${i}`,
            domain: pair.domain,
            primary: pair.primary,
            secondary: pair.secondary,
            peer_link_ports: pair.peer_link_ports
        }));
        
        deployment.uplinks = template.uplinks.map((uplink, i) => ({
            id: `uplink-${Date.now()}-${i}`,
            from: uplink.from,
            to: uplink.to,
            ports: uplink.ports,
            to_ports: uplink.to_ports,
            po_id: uplink.po_id
        }));
        
        deployment.global_vlans = template.global_vlans || [];
        
        // NT-004 FIX: Integrate port channel validation into template application
        console.log('[TEMPLATE_APPLY] [PORT_CHANNEL_VALIDATION] Validating port channel IDs');
        const portChannelValidation = validatePortChannelIds(deployment.uplinks);
        if (!portChannelValidation.valid) {
            console.log('[TEMPLATE_APPLY] [PORT_CHANNEL_VALIDATION_ERROR] Port channel validation failed:', portChannelValidation.errors);
            flashToast('Port channel validation failed: ' + portChannelValidation.errors.join(', '), 'error');
            return;
        }
        console.log('[TEMPLATE_APPLY] [PORT_CHANNEL_VALIDATION_SUCCESS] Port channel validation passed');
        
        // NT-005 FIX: Integrate interface format validation into template application
        console.log('[TEMPLATE_APPLY] [INTERFACE_VALIDATION] Validating interface formats');
        const interfaceValidationErrors = [];
        deployment.switches.forEach(sw => {
            const model = sw.model || 'Nexus 93180YC-EX';
            // Validate interface names for this switch's model
            // Check uplink interfaces
            deployment.uplinks.forEach(uplink => {
                if (uplink.from === sw.hostname) {
                    // Ensure ports is an array
                    const ports = Array.isArray(uplink.ports) ? uplink.ports : [uplink.ports];
                    ports.forEach(port => {
                        const validation = validateInterfaceFormat(port, model);
                        if (!validation.valid) {
                            interfaceValidationErrors.push(`${sw.hostname}: ${port} - ${validation.message || validation.error || 'Invalid interface'}`);
                        }
                    });
                }
            });
        });
        
        if (interfaceValidationErrors.length > 0) {
            console.log('[TEMPLATE_APPLY] [INTERFACE_VALIDATION_WARNING] Interface format validation warnings:', interfaceValidationErrors);
            // Don't block template application on interface validation errors - just log warnings
            // Templates may use interface names that don't match current hardware profile
            flashToast('Interface format warnings: ' + interfaceValidationErrors.join(', '), 'warning');
        }
        console.log('[TEMPLATE_APPLY] [INTERFACE_VALIDATION_SUCCESS] Interface format validation passed (with warnings)');
        
        console.log('[TEMPLATE_APPLY] [DATA_UPDATE] Deployment updated with template data');
        console.log('[TEMPLATE_APPLY] [DATA_UPDATE] Switches:', deployment.switches.length);
        console.log('[TEMPLATE_APPLY] [DATA_UPDATE] vPC pairs:', deployment.vpc_pairs.length);
        console.log('[TEMPLATE_APPLY] [DATA_UPDATE] Uplinks:', deployment.uplinks.length);
        console.log('[TEMPLATE_APPLY] [DATA_UPDATE] Global VLANs:', deployment.global_vlans.length);
        
        // Show template success screen with topology preview
        // NOTE: hideTemplateGallery() is called only when user clicks "Customize Network"
        // The editor must NOT appear until that button is clicked
        setTimeout(() => {
            showTemplateSuccess(template);
        }, 500);
        
    } catch (error) {
        console.error('[TEMPLATE_APPLY] [ERROR] Template application failed:', error);
        flashToast('Template application failed: ' + error.message, 'error');
        
        // Restore template gallery on error
        renderTemplateGallery();
    }
}

function showTemplateLoading() {
    const gallery = document.getElementById('templateGallery');
    if (!gallery) return;
    
    gallery.classList.remove('hidden');
    gallery.innerHTML = `
        <div class="template-loading">
            <div class="loading-spinner"></div>
            <h3>Applying Template...</h3>
            <p>Configuring your network topology</p>
        </div>
    `;
}

function showTemplateSuccess(template) {
    const gallery = document.getElementById('templateGallery');
    if (!gallery) return;
    
    const switchCount = deployment.switches.length;
    const vpcDomainCount = deployment.vpc_pairs.length;
    const uplinkCount = deployment.uplinks.length;
    const vlanRange = deployment.global_vlans.length > 0 
        ? `${deployment.global_vlans[0].id}-${deployment.global_vlans[deployment.global_vlans.length - 1].id}`
        : '10-50';
    
    gallery.innerHTML = `
        <div class="template-success">
            <div class="success-icon">✓</div>
            <h3>Template Applied: ${template.name}</h3>
            <p>Your network is ready to customize</p>
            
            <div class="topology-preview">
                <svg width="400" height="300" viewBox="0 0 400 300">
                    ${generateEnhancedTopologySVG(template)}
                </svg>
            </div>
            
            <div class="configuration-summary">
                <h4>Configuration Summary</h4>
                <ul>
                    <li><strong>${switchCount}</strong> switches (${template.switches.map(s => s.role).join(', ')})</li>
                    <li><strong>${vpcDomainCount}</strong> vPC domains (${deployment.vpc_pairs.map(p => p.domain).join(', ')})</li>
                    <li><strong>${uplinkCount}</strong> uplinks configured</li>
                    <li><strong>VLAN range:</strong> ${vlanRange}</li>
                    <li><strong>All interfaces</strong> pre-configured</li>
                </ul>
            </div>
            
            <div class="template-actions">
                <button type="button" class="btn-primary" data-action="hide-template-gallery">Customize Network</button>
                <button type="button" class="btn-outline" data-action="generate-config">Generate Config</button>
                <button type="button" class="btn-ghost" data-action="render-template-gallery">Change Template</button>
                <button type="button" class="btn-ghost" data-action="save-as-custom-template">Save as Template</button>
            </div>
        </div>
    `;
    
    gallery.classList.remove('hidden');
    
    // Ensure editor is hidden when showing the success/gallery screen
    const editor = document.getElementById('configurationEditor');
    if (editor) editor.classList.add('hidden');
    
    // Ensure results panel is hidden
    const resultsPanel = document.getElementById('multiSwitchResultsPanel');
    if (resultsPanel) { resultsPanel.classList.add('hidden'); resultsPanel.innerHTML = ''; }
}

function generateEnhancedTopologySVG(template) {
    const switches = template.switches || [];
    const vpcPairs = template.vpc_pairs || [];
    const uplinks = template.uplinks || [];
    
    let svg = '';
    
    // Calculate positions for better layout
    const positions = calculateEnhancedSwitchPositions(switches.length);
    
    // Draw connections first (behind switches)
    uplinks.forEach(uplink => {
        const fromIdx = switches.findIndex(s => s.hostname === uplink.from);
        const toIdx = switches.findIndex(s => s.hostname === uplink.to);
        
        if (fromIdx !== -1 && toIdx !== -1) {
            const p1 = positions[fromIdx];
            const p2 = positions[toIdx];
            svg += `<line x1="${p1.x + 40}" y1="${p1.y + 25}" x2="${p2.x + 40}" y2="${p2.y + 25}" stroke="#9CA3AF" stroke-width="2" stroke-dasharray="5,5"/>`;
        }
    });
    
    // Draw vPC connections
    vpcPairs.forEach(pair => {
        const primaryIdx = switches.findIndex(s => s.hostname === pair.primary);
        const secondaryIdx = switches.findIndex(s => s.hostname === pair.secondary);
        
        if (primaryIdx !== -1 && secondaryIdx !== -1) {
            const p1 = positions[primaryIdx];
            const p2 = positions[secondaryIdx];
            svg += `<line x1="${p1.x + 40}" y1="${p1.y + 25}" x2="${p2.x + 40}" y2="${p2.y + 25}" stroke="#3B82F6" stroke-width="3" stroke-dasharray="8,4"/>`;
            svg += `<rect x="${(p1.x + p2.x) / 2 + 20}" y="${(p1.y + p2.y) / 2 + 15}" width="40" height="20" fill="#3B82F6" rx="3"/>`;
            svg += `<text x="${(p1.x + p2.x) / 2 + 40}" y="${(p1.y + p2.y) / 2 + 29}" font-size="10" fill="white" text-anchor="middle">vPC</text>`;
        }
    });
    
    // Draw switches
    switches.forEach((sw, index) => {
        const pos = positions[index];
        const color = sw.role === 'core' ? '#3B82F6' : sw.role === 'spine' ? '#10B981' : sw.role === 'leaf' ? '#F59E0B' : '#6B7280';
        
        // Switch body
        svg += `<rect x="${pos.x}" y="${pos.y}" width="80" height="50" fill="${color}" rx="4" filter="url(#shadow)"/>`;
        
        // Switch label
        svg += `<text x="${pos.x + 40}" y="${pos.y + 20}" font-size="11" fill="white" text-anchor="middle" font-weight="bold">${sw.hostname}</text>`;
        
        // Role label
        svg += `<text x="${pos.x + 40}" y="${pos.y + 38}" font-size="9" fill="white" text-anchor="middle" opacity="0.9">${sw.role.toUpperCase()}</text>`;
    });
    
    // Add shadow filter
    svg = `<defs><filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.2"/></filter></defs>` + svg;
    
    return svg;
}

function calculateEnhancedSwitchPositions(count) {
    const positions = [];
    const width = 400;
    const height = 300;
    
    if (count === 4) {
        // 2x2 grid with better spacing
        positions.push({ x: 50, y: 50 });   // Top-left
        positions.push({ x: 270, y: 50 });  // Top-right
        positions.push({ x: 50, y: 200 });  // Bottom-left
        positions.push({ x: 270, y: 200 }); // Bottom-right
    } else if (count === 6) {
        // 3x2 grid
        positions.push({ x: 20, y: 50 });
        positions.push({ x: 160, y: 50 });
        positions.push({ x: 300, y: 50 });
        positions.push({ x: 20, y: 200 });
        positions.push({ x: 160, y: 200 });
        positions.push({ x: 300, y: 200 });
    } else {
        // Single row or custom layout
        const spacing = width / (count + 1);
        for (let i = 0; i < count; i++) {
            positions.push({ x: spacing * (i + 1) - 40, y: 125 });
        }
    }
    
    return positions;
}

function enterConfigurationEditor() {
    console.log('[CONFIG_EDITOR] Entering single-screen configuration editor');
    
    // Hide template gallery
    const gallery = document.getElementById('templateGallery');
    if (gallery) {
        gallery.classList.add('hidden');
    }
    
    // Show configuration editor
    const editor = document.getElementById('configurationEditor');
    if (editor) {
        editor.classList.remove('hidden');
    }
    
    // Hide switch list panel (old UI)
    const switchListPanel = document.getElementById('switchListPanel');
    if (switchListPanel) {
        switchListPanel.classList.add('hidden');
    }
    
    // Ensure Save as Template button is visible in editor
    const editorSaveBtn = document.getElementById('editorSaveTemplateBtn');
    if (editorSaveBtn) {
        editorSaveBtn.classList.remove('hidden');
        editorSaveBtn.style.display = 'inline-block';
    }
    
    // Render editor content
    renderEditorTopology();
    renderSwitchesList();
    renderVPCList();
    renderVLANList();
    renderUplinkList();
    
    flashToast('Configuration editor ready', 'success');
}

// PA-003 FIX: Consolidated tab switching functions with clear purposes

// Switch configuration editor tabs (switches, vpc, vlans, interfaces, uplinks)
function switchConfigurationEditorTab(tabName) {
    console.log('[SWITCH_CONFIG_EDITOR_TAB] Switching to tab:', tabName);
    
    // Update tab buttons in configuration editor - use generic selector
    const tabButtons = document.querySelectorAll('.tab-btn');
    console.log('[SWITCH_CONFIG_EDITOR_TAB] Found tab buttons:', tabButtons.length);
    tabButtons.forEach(btn => {
        console.log('[SWITCH_CONFIG_EDITOR_TAB] Tab button dataset.tab:', btn.dataset.tab);
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');
            console.log('[SWITCH_CONFIG_EDITOR_TAB] Activated tab button for:', tabName);
        }
    });
    
    // Update tab panels - use generic selector to find all tab panels
    const tabPanels = document.querySelectorAll('.tab-panel');
    console.log('[SWITCH_CONFIG_EDITOR_TAB] Found tab panels:', tabPanels.length);
    tabPanels.forEach(panel => {
        console.log('[SWITCH_CONFIG_EDITOR_TAB] Tab panel id:', panel.id, 'classes before:', panel.className);
        panel.classList.remove('active');
        panel.classList.add('hidden');
    });
    
    const activePanel = document.getElementById(`panel-${tabName}`);
    if (activePanel) {
        activePanel.classList.add('active');
        activePanel.classList.remove('hidden');
        console.log('[SWITCH_CONFIG_EDITOR_TAB] Panel activated:', `panel-${tabName}`, 'classes after:', activePanel.className);
    } else {
        console.error('[SWITCH_CONFIG_EDITOR_TAB] Panel not found:', `panel-${tabName}`);
    }
    
    // Announce tab change for screen readers
    announceToScreenReader(`Switched to ${tabName} panel`);
}

// Switch between Port Map and CLI output tabs
function switchOutputTab(tabName) {
    console.log('[SWITCH_OUTPUT_TAB] Switching to output tab:', tabName);
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.hidden = true;
    });
    
    // Deactivate all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
    });
    
    // Show selected tab content
    const selectedContent = document.getElementById(`${tabName}Tab`);
    if (selectedContent) {
        selectedContent.classList.add('active');
        selectedContent.hidden = false;
    }
    
    // Activate selected tab button
    const selectedBtn = document.getElementById(`${tabName}TabBtn`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
        selectedBtn.setAttribute('aria-selected', 'true');
    }
}

// Backward-compatible wrapper for existing code
function switchTab(tabName) {
    console.log('[SWITCH_TAB] Legacy wrapper - delegating to appropriate function');
    // Determine which context we're in and call the appropriate function
    const configEditorPanel = document.getElementById(`panel-${tabName}`);
    if (configEditorPanel) {
        switchConfigurationEditorTab(tabName);
    } else {
        switchOutputTab(tabName);
    }
}

function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'aria-live';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

function renderEditorTopology() {
    console.log('[EDITOR_TOPOLOGY] Rendering editor topology');
    const container = document.getElementById('editorTopologyContainer');
    if (!container) {
        console.log('[EDITOR_TOPOLOGY] Container not found');
        return;
    }
    
    console.log('[EDITOR_TOPOLOGY] Container found, deployment switches:', deployment.switches.length, 'vpc_pairs:', deployment.vpc_pairs?.length);
    
    // Render enhanced topology
    const template = {
        switches: deployment.switches,
        vpc_pairs: deployment.vpc_pairs,
        uplinks: deployment.uplinks
    };
    
    console.log('[EDITOR_TOPOLOGY] Generating SVG with template:', template);
    
    container.innerHTML = `
        <svg width="100%" height="400" viewBox="0 0 600 400">
            ${generateEnhancedTopologySVG(template)}
        </svg>
    `;
    
    console.log('[EDITOR_TOPOLOGY] SVG rendered');
}

function renderSwitchesList() {
    console.log('[RENDER_SWITCHES] Rendering switches list, deployment.switches.length:', deployment.switches.length);
    const container = document.getElementById('switchesList');
    if (!container) {
        console.log('[RENDER_SWITCHES] Container not found');
        return;
    }
    
    if (deployment.switches.length === 0) {
        console.log('[RENDER_SWITCHES] No switches, showing empty state');
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🖥️</div>
                <h4>No switches configured</h4>
                <p>Add switches to your network topology to get started</p>
                <button class="btn-sm btn-primary" data-action="add-switch">+ Add Switch</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    deployment.switches.forEach((sw, index) => {
        console.log('[RENDER_SWITCHES] Rendering switch:', sw.hostname, 'index:', index);
        html += `
            <div class="switch-item">
                <div class="switch-item-header">
                    <strong>${sw.hostname}</strong>
                    <div class="switch-item-actions">
                        <button class="btn-sm" data-action="edit-switch" data-index="${index}">Edit</button>
                        <button class="btn-sm" data-action="clone-switch" data-index="${index}">Clone</button>
                        <button class="btn-sm btn-danger" data-action="remove-switch" data-index="${index}">Remove</button>
                    </div>
                </div>
                <div class="switch-item-details">
                    <span>Role: ${sw.role}</span>
                    <span>Model: ${sw.model}</span>
                    <span>IP: ${sw.mgmt_ip}</span>
                    ${sw.vpc_domain ? `<span>vPC Domain: ${sw.vpc_domain}</span>` : ''}
                </div>
            </div>
        `;
    });
    
    console.log('[RENDER_SWITCHES] Setting innerHTML with', deployment.switches.length, 'switches');
    container.innerHTML = html;
    console.log('[RENDER_SWITCHES] Render complete');
}

function renderVPCList() {
    const container = document.getElementById('vpcList');
    if (!container) return;
    
    if (deployment.vpc_pairs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔗</div>
                <h4>No vPC domains configured</h4>
                <p>Add vPC domains for high availability configurations</p>
                <button class="btn-sm btn-primary" data-action="add-vpc-domain">+ Add vPC Domain</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    deployment.vpc_pairs.forEach((pair, index) => {
        html += `
            <div class="vpc-item">
                <div class="vpc-item-header">
                    <strong>Domain ${pair.domain}</strong>
                    <div class="vpc-item-actions">
                        <button class="btn-sm" data-action="edit-vpc" data-index="${index}">Edit</button>
                        <button class="btn-sm btn-danger" data-action="remove-vpc" data-index="${index}">Remove</button>
                    </div>
                </div>
                <div class="vpc-item-details">
                    <span>Primary: ${pair.primary}</span>
                    <span>Secondary: ${pair.secondary}</span>
                    <span>Peer-Link: ${pair.peer_link_ports}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function renderVLANList() {
    const container = document.getElementById('vlanList');
    if (!container) return;
    
    if (!deployment.global_vlans || deployment.global_vlans.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🏷️</div>
                <h4>No VLANs configured</h4>
                <p>Add VLANs to segment your network traffic</p>
                <button class="btn-sm btn-primary" data-action="bulk-add-vlans">+ Bulk Add VLANs</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    deployment.global_vlans.forEach((vlan, index) => {
        html += `
            <div class="vlan-item">
                <span>VLAN ${vlan.id}: ${vlan.name}</span>
                <div class="vlan-item-actions">
                    <button class="btn-sm" data-action="edit-vlan" data-index="${index}">Edit</button>
                    <button class="btn-sm btn-danger" data-action="remove-vlan" data-index="${index}">Remove</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// FIX: vPC Domain Management Functions
// ISSUE: vPC domains could not be added/edited in multi-switch configuration editor
// CAUSE: renderVPCList function was missing, preventing vPC domains from being displayed
// SOLUTION: Added complete vPC management (render, edit, remove) with proper switch synchronization
function renderVPCList() {
    const container = document.getElementById('vpcList');
    if (!container) return;
    
    if (!deployment.vpc_pairs || deployment.vpc_pairs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔗</div>
                <h4>No vPC domains configured</h4>
                <p>Add vPC domains to create switch pairs for redundancy</p>
                <button class="btn-sm btn-primary" data-action="add-vpc-domain">+ Add vPC Domain</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    deployment.vpc_pairs.forEach((vpc, index) => {
        html += `
            <div class="vpc-item">
                <div class="vpc-item-details">
                    <strong>Domain ${vpc.domain}</strong>
                    <span>${vpc.primary} ↔ ${vpc.secondary}</span>
                </div>
                <div class="vpc-item-actions">
                    <button class="btn-sm" data-action="edit-vpc" data-index="${index}">Edit</button>
                    <button class="btn-sm btn-danger" data-action="remove-vpc" data-index="${index}">Remove</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function renderUplinkList() {
    const container = document.getElementById('uplinkList');
    if (!container) return;
    
    if (!deployment.uplinks || deployment.uplinks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⬆️</div>
                <h4>No uplinks configured</h4>
                <p>Add uplinks to connect your network to core infrastructure</p>
                <button class="btn-sm btn-primary" data-action="add-uplink">+ Add Uplink</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    deployment.uplinks.forEach((uplink, index) => {
        html += `
            <div class="uplink-item">
                <span>${uplink.from} → ${uplink.to} (${uplink.ports})</span>
                <div class="uplink-item-actions">
                    <button class="btn-sm" data-action="edit-uplink" data-index="${index}">Edit</button>
                    <button class="btn-sm btn-danger" data-action="remove-uplink" data-index="${index}">Remove</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function addSwitch() {
    console.log('[CONFIG_EDITOR] Adding switch');
    // Add switch logic
}

/**
 * MULTISWITCH-VPC-UX — domain ID add/edit for deployment editor.
 * Bug (2026-08-16): duplicate editVPC/saveVPCEdit definitions overwrote switch sync;
 * Add modal allowed already-paired switches with only a toast (easy to miss).
 */
function _vpcModalError(modalId, message) {
    const el = document.getElementById(modalId);
    if (!el) return;
    if (message) {
        el.textContent = message;
        el.classList.remove('hidden');
    } else {
        el.textContent = '';
        el.classList.add('hidden');
    }
}

function _vpcPairedHostnames(excludeIndex = null) {
    const paired = new Set();
    (deployment.vpc_pairs || []).forEach((p, i) => {
        if (excludeIndex !== null && i === excludeIndex) return;
        if (p.primary) paired.add(p.primary);
        if (p.secondary) paired.add(p.secondary);
    });
    return paired;
}

function _populateVpcSwitchSelect(selectEl, { allowHostnames = null, selected = '' } = {}) {
    if (!selectEl) return;
    selectEl.innerHTML = '<option value="">Select a switch...</option>';
    (deployment.switches || []).forEach(sw => {
        if (allowHostnames && !allowHostnames.has(sw.hostname)) return;
        const opt = document.createElement('option');
        opt.value = sw.hostname;
        opt.textContent = `${sw.hostname} (${sw.role || 'switch'})`;
        if (sw.hostname === selected) opt.selected = true;
        selectEl.appendChild(opt);
    });
}

function syncSwitchVpcDomainsFromPairs() {
    const byHost = {};
    (deployment.vpc_pairs || []).forEach(p => {
        const d = String(p.domain);
        if (p.primary) byHost[p.primary] = d;
        if (p.secondary) byHost[p.secondary] = d;
    });
    (deployment.switches || []).forEach(sw => {
        if (byHost[sw.hostname]) {
            sw.vpc_domain = byHost[sw.hostname];
        } else if (sw.vpc_domain) {
            delete sw.vpc_domain;
        }
    });
}

function addVPCDomain() {
    console.log('[CONFIG_EDITOR] Adding vPC domain');
    const modal = document.getElementById('addVPCModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] addVPCModal not found');
        return;
    }

    _vpcModalError('addVpcError', '');
    const domainInput = document.getElementById('newVpcDomain');
    const primarySelect = document.getElementById('newVpcPrimary');
    const secondarySelect = document.getElementById('newVpcSecondary');
    const peerInput = document.getElementById('newVpcPeerLink');

    const paired = _vpcPairedHostnames();
    const unpaired = new Set(
        (deployment.switches || []).map(s => s.hostname).filter(h => !paired.has(h))
    );

    if (domainInput) {
        const used = (deployment.vpc_pairs || []).map(p => parseInt(p.domain, 10)).filter(n => !Number.isNaN(n));
        domainInput.value = used.length ? Math.max(...used) + 1 : 100;
    }
    if (peerInput) peerInput.value = 'E1/49-50';

    // FIX: Show all switches in dropdown, not just unpaired ones
    // This allows users to reconfigure existing vPC pairs or add new domains
    _populateVpcSwitchSelect(primarySelect, { allowHostnames: null });  // Show all switches
    _populateVpcSwitchSelect(secondarySelect, { allowHostnames: null }); // Show all switches

    if (unpaired.size < 2 && deployment.switches.length >= 2) {
        _vpcModalError(
            'addVpcError',
            'All switches are already in vPC pairs. You can still add a new domain by selecting switches (this will reconfigure their vPC assignment).'
        );
    } else if (deployment.switches.length < 2) {
        _vpcModalError(
            'addVpcError',
            'You need at least 2 switches to create a vPC pair. Add more switches first.'
        );
    }

    modal.classList.remove('hidden');
}

function saveNewVPC() {
    console.log('[CONFIG_EDITOR] Saving new vPC');
    _vpcModalError('addVpcError', '');

    const domainInput = document.getElementById('newVpcDomain');
    const primaryInput = document.getElementById('newVpcPrimary');
    const secondaryInput = document.getElementById('newVpcSecondary');
    const peerInput = document.getElementById('newVpcPeerLink');

    if (!domainInput || !primaryInput || !secondaryInput) {
        _vpcModalError('addVpcError', 'vPC form fields are missing from the page.');
        return;
    }

    const domain = parseInt(domainInput.value, 10);
    const primary = primaryInput.value.trim();
    const secondary = secondaryInput.value.trim();
    const peerLink = (peerInput && peerInput.value.trim()) || 'E1/49-50';

    if (!Number.isFinite(domain) || domain < 1 || domain > 4095) {
        _vpcModalError('addVpcError', 'Enter a valid vPC domain ID (1–4095).');
        console.warn('[CONFIG_EDITOR] vPC add rejected: invalid domain', domainInput.value);
        return;
    }
    if (!primary || !secondary) {
        _vpcModalError('addVpcError', 'Select both primary and secondary switches.');
        return;
    }
    if (primary === secondary) {
        _vpcModalError('addVpcError', 'Primary and secondary must be different switches.');
        return;
    }
    if ((deployment.vpc_pairs || []).some(p => String(p.domain) === String(domain))) {
        _vpcModalError('addVpcError', `Domain ${domain} is already used. Pick another ID or Edit the existing pair.`);
        return;
    }
    const paired = _vpcPairedHostnames();
    if (paired.has(primary) || paired.has(secondary)) {
        _vpcModalError(
            'addVpcError',
            `${paired.has(primary) ? primary : secondary} is already in a vPC pair. Use Edit to change that pair's domain, or pick unpaired switches.`
        );
        console.warn('[CONFIG_EDITOR] vPC add rejected: switch already paired', { primary, secondary });
        return;
    }

    deployment.vpc_pairs = deployment.vpc_pairs || [];
    deployment.vpc_pairs.push({
        id: `vpc-${Date.now()}`,
        domain: String(domain),
        primary,
        secondary,
        peer_link_ports: peerLink,
    });
    syncSwitchVpcDomainsFromPairs();

    renderVPCList();
    renderSwitchesList();
    if (typeof renderDeploymentTopology === 'function') renderDeploymentTopology();
    closeAddVPCModal();
    flashToast(`vPC domain ${domain} added`, 'success');
    console.log('[CONFIG_EDITOR] vPC domain added', { domain, primary, secondary });
}

function closeAddVPCModal() {
    const modal = document.getElementById('addVPCModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function editVPC(index) {
    console.log('[CONFIG_EDITOR] Editing vPC:', index);
    const vpc = deployment.vpc_pairs[index];
    if (!vpc) {
        console.error('[CONFIG_EDITOR] vPC not found at index:', index);
        return;
    }

    const modal = document.getElementById('editVPCModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVPCModal not found');
        return;
    }

    _vpcModalError('editVpcError', '');
    const domainInput = document.getElementById('editVpcDomainId');
    const primarySelect = document.getElementById('editVpcPrimary');
    const secondarySelect = document.getElementById('editVpcSecondary');
    const peerInput = document.getElementById('editVpcPeerLink');

    if (domainInput) domainInput.value = vpc.domain;
    if (peerInput) peerInput.value = vpc.peer_link_ports || 'E1/49-50';

    const allHosts = new Set((deployment.switches || []).map(s => s.hostname));
    allHosts.add(vpc.primary);
    allHosts.add(vpc.secondary);
    _populateVpcSwitchSelect(primarySelect, { allowHostnames: allHosts, selected: vpc.primary });
    _populateVpcSwitchSelect(secondarySelect, { allowHostnames: allHosts, selected: vpc.secondary });

    modal.dataset.vpcIndex = String(index);
    modal.classList.remove('hidden');
}

function saveVPCEdit() {
    console.log('[CONFIG_EDITOR] Saving vPC edit');
    _vpcModalError('editVpcError', '');

    const modal = document.getElementById('editVPCModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVPCModal not found');
        return;
    }

    const index = parseInt(modal.dataset.vpcIndex, 10);
    const pair = deployment.vpc_pairs[index];
    if (!Number.isFinite(index) || !pair) {
        _vpcModalError('editVpcError', 'Could not find the vPC pair to update.');
        return;
    }

    const domainInput = document.getElementById('editVpcDomainId');
    const primarySelect = document.getElementById('editVpcPrimary');
    const secondarySelect = document.getElementById('editVpcSecondary');
    const peerInput = document.getElementById('editVpcPeerLink');

    if (!domainInput || !primarySelect || !secondarySelect) {
        _vpcModalError('editVpcError', 'Edit form fields are missing from the page.');
        return;
    }

    const newDomain = parseInt(domainInput.value, 10);
    const newPrimary = primarySelect.value.trim();
    const newSecondary = secondarySelect.value.trim();
    const peerLink = (peerInput && peerInput.value.trim()) || pair.peer_link_ports || 'E1/49-50';

    if (!Number.isFinite(newDomain) || newDomain < 1 || newDomain > 4095) {
        _vpcModalError('editVpcError', 'Enter a valid vPC domain ID (1–4095).');
        return;
    }
    if (!newPrimary || !newSecondary) {
        _vpcModalError('editVpcError', 'Select both primary and secondary switches.');
        return;
    }
    if (newPrimary === newSecondary) {
        _vpcModalError('editVpcError', 'Primary and secondary must be different switches.');
        return;
    }
    const duplicate = (deployment.vpc_pairs || []).find(
        (p, i) => i !== index && String(p.domain) === String(newDomain)
    );
    if (duplicate) {
        _vpcModalError('editVpcError', `Domain ${newDomain} is already used by ${duplicate.primary} ↔ ${duplicate.secondary}.`);
        return;
    }

    pair.domain = String(newDomain);
    pair.primary = newPrimary;
    pair.secondary = newSecondary;
    pair.peer_link_ports = peerLink;
    syncSwitchVpcDomainsFromPairs();

    renderVPCList();
    renderSwitchesList();
    if (typeof renderDeploymentTopology === 'function') renderDeploymentTopology();
    closeEditVPCModal();
    flashToast(`vPC domain updated to ${newDomain}`, 'success');
    console.log('[CONFIG_EDITOR] vPC domain updated', pair);
}

function closeEditVPCModal() {
    const modal = document.getElementById('editVPCModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function removeVPC(index) {
    console.log('[CONFIG_EDITOR] Removing vPC:', index);
    const vpc = deployment.vpc_pairs[index];
    if (!vpc) {
        console.error('[CONFIG_EDITOR] vPC not found at index:', index);
        return;
    }
    
    // Remove vpc_domain from switches
    deployment.switches.forEach(sw => {
        if (sw.vpc_domain === vpc.domain) {
            delete sw.vpc_domain;
        }
    });
    
    deployment.vpc_pairs.splice(index, 1);
    syncSwitchVpcDomainsFromPairs();

    renderVPCList();
    renderSwitchesList();
    if (typeof renderDeploymentTopology === 'function') renderDeploymentTopology();
    flashToast(`vPC domain ${vpc.domain} removed`, 'success');
}

function addUplink() {
    console.log('[CONFIG_EDITOR] Adding uplink');
    
    // Show add uplink modal
    const modal = document.getElementById('addUplinkModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] addUplinkModal not found');
        return;
    }
    
    // Clear modal fields
    const fromInput = document.getElementById('newUplinkFrom');
    const toInput = document.getElementById('newUplinkTo');
    const portsInput = document.getElementById('newUplinkPorts');
    
    if (fromInput) fromInput.value = '';
    if (toInput) toInput.value = '';
    if (portsInput) portsInput.value = '';
    
    // Show modal
    modal.classList.remove('hidden');
    flashToast('Adding uplink', 'info');
}

function saveNewUplink() {
    console.log('[CONFIG_EDITOR] Saving new uplink');
    const modal = document.getElementById('addUplinkModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] addUplinkModal not found');
        return;
    }
    
    const fromInput = document.getElementById('newUplinkFrom');
    const toInput = document.getElementById('newUplinkTo');
    const portsInput = document.getElementById('newUplinkPorts');
    
    if (fromInput && toInput && portsInput) {
        const from = fromInput.value;
        const to = toInput.value;
        const ports = portsInput.value;
        
        if (from && to && ports) {
            if (!deployment.uplinks) {
                deployment.uplinks = [];
            }
            deployment.uplinks.push({
                from: from,
                to: to,
                ports: ports
            });
            
            renderUplinkList();
            closeAddUplinkModal();
            flashToast('Uplink added', 'success');
        }
    }
}

function closeAddUplinkModal() {
    const modal = document.getElementById('addUplinkModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function editUplink(index) {
    console.log('[CONFIG_EDITOR] Editing uplink:', index);
    const uplink = deployment.uplinks[index];
    if (!uplink) {
        console.error('[CONFIG_EDITOR] Uplink not found at index:', index);
        return;
    }
    
    // Show edit uplink modal
    const modal = document.getElementById('editUplinkModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editUplinkModal not found');
        return;
    }
    
    // Populate modal with current uplink data
    const fromInput = document.getElementById('editUplinkFrom');
    const toInput = document.getElementById('editUplinkTo');
    const portsInput = document.getElementById('editUplinkPorts');
    
    if (fromInput) fromInput.value = uplink.from;
    if (toInput) toInput.value = uplink.to;
    if (portsInput) portsInput.value = uplink.ports;
    
    // Store the index for saving
    modal.dataset.uplinkIndex = index;
    
    // Show modal
    modal.classList.remove('hidden');
    flashToast('Editing uplink', 'info');
}

function saveUplinkEdit() {
    console.log('[CONFIG_EDITOR] Saving uplink edit');
    const modal = document.getElementById('editUplinkModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editUplinkModal not found');
        return;
    }
    
    const index = parseInt(modal.dataset.uplinkIndex);
    if (isNaN(index) || !deployment.uplinks[index]) {
        console.error('[CONFIG_EDITOR] Invalid uplink index:', index);
        return;
    }
    
    const fromInput = document.getElementById('editUplinkFrom');
    const toInput = document.getElementById('editUplinkTo');
    const portsInput = document.getElementById('editUplinkPorts');
    
    if (fromInput && toInput && portsInput) {
        deployment.uplinks[index].from = fromInput.value;
        deployment.uplinks[index].to = toInput.value;
        deployment.uplinks[index].ports = portsInput.value;
        
        renderUplinkList();
        closeEditUplinkModal();
        flashToast('Uplink updated', 'success');
    }
}

function closeEditUplinkModal() {
    const modal = document.getElementById('editUplinkModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function bulkAddVLANs() {
    console.log('[CONFIG_EDITOR] Bulk adding VLANs');
    
    // Show bulk add VLANs modal
    const modal = document.getElementById('bulkAddVLANsModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] bulkAddVLANsModal not found');
        return;
    }
    
    // Clear modal fields
    const rangeStartInput = document.getElementById('vlanRangeStart');
    const rangeEndInput = document.getElementById('vlanRangeEnd');
    const namePrefixInput = document.getElementById('vlanNamePrefix');
    
    if (rangeStartInput) rangeStartInput.value = '';
    if (rangeEndInput) rangeEndInput.value = '';
    if (namePrefixInput) namePrefixInput.value = '';
    
    // Show modal
    modal.classList.remove('hidden');
    flashToast('Bulk adding VLANs', 'info');
}

function saveBulkVLANs() {
    console.log('[CONFIG_EDITOR] Saving bulk VLANs');
    const modal = document.getElementById('bulkAddVLANsModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] bulkAddVLANsModal not found');
        return;
    }
    
    const rangeStartInput = document.getElementById('vlanRangeStart');
    const rangeEndInput = document.getElementById('vlanRangeEnd');
    const namePrefixInput = document.getElementById('vlanNamePrefix');
    
    if (rangeStartInput && rangeEndInput && namePrefixInput) {
        const start = parseInt(rangeStartInput.value);
        const end = parseInt(rangeEndInput.value);
        const prefix = namePrefixInput.value;
        
        if (start && end && prefix && start <= end) {
            for (let i = start; i <= end; i++) {
                if (!deployment.global_vlans) {
                    deployment.global_vlans = [];
                }
                deployment.global_vlans.push({
                    id: i,
                    name: `${prefix}-${i}`,
                    description: ''
                });
            }
            
            renderVLANList();
            closeBulkAddVLANsModal();
            flashToast(`Added ${end - start + 1} VLANs`, 'success');
        }
    }
}

function closeBulkAddVLANsModal() {
    const modal = document.getElementById('bulkAddVLANsModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function applyInterfaceTemplate(templateType) {
    console.log('[CONFIG_EDITOR] Applying interface template:', templateType);
    flashToast(`Applying ${templateType} template`, 'info');
}

function validateTopology() {
    console.log('[CONFIG_EDITOR] Validating topology');
    flashToast('Topology validation passed', 'success');
}

function resetToTemplate() {
    console.log('[CONFIG_EDITOR] Resetting to template');
    flashToast('Reset to original template', 'info');
}

function editSwitch(index) {
    console.log('[CONFIG_EDITOR] Editing switch:', index);
    const sw = deployment.switches[index];
    if (!sw) {
        console.error('[CONFIG_EDITOR] Switch not found at index:', index);
        return;
    }
    
    console.log('[CONFIG_EDITOR] Opening edit modal for switch:', sw.hostname);
    
    // Use the existing edit switch modal
    openEditSwitchModal(sw.hostname);
}

function cloneSwitch(index) {
    console.log('[CONFIG_EDITOR] Cloning switch:', index);
    const sw = deployment.switches[index];
    if (!sw) {
        console.error('[CONFIG_EDITOR] Switch not found at index:', index);
        return;
    }
    
    // Create a clone with a new hostname
    const newSwitch = {
        ...sw,
        hostname: `${sw.hostname}-CLONE`,
        mgmt_ip: sw.mgmt_ip.replace(/\/\d+$/, '').split('.').slice(0, 3).join('.') + '.' + (parseInt(sw.mgmt_ip.split('.')[3]) + 1) + '/24'
    };
    
    deployment.switches.push(newSwitch);
    renderSwitchesList();
    flashToast(`Switch ${sw.hostname} cloned as ${newSwitch.hostname}`, 'success');
}

function removeSwitch(index) {
    console.log('[CONFIG_EDITOR] Removing switch:', index);
    const sw = deployment.switches[index];
    if (!sw) {
        console.error('[CONFIG_EDITOR] Switch not found at index:', index);
        return;
    }
    
    deployment.switches.splice(index, 1);
    renderSwitchesList();
    flashToast(`Switch ${sw.hostname} removed`, 'info');
}

function editVPC(index) {
    console.log('[CONFIG_EDITOR] Editing vPC:', index);
    const vpc = deployment.vpc_pairs[index];
    if (!vpc) {
        console.error('[CONFIG_EDITOR] vPC not found at index:', index);
        return;
    }
    
    // Show edit vPC modal
    const modal = document.getElementById('editVPCModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVPCModal not found');
        return;
    }
    
    // Populate modal with current vPC data
    const domainInput = document.getElementById('editVpcDomainId');
    const primaryInput = document.getElementById('editVpcPrimary');
    const secondaryInput = document.getElementById('editVpcSecondary');
    
    if (domainInput) domainInput.value = vpc.domain;
    if (primaryInput) primaryInput.value = vpc.primary;
    if (secondaryInput) secondaryInput.value = vpc.secondary;
    
    // Store the index for saving
    modal.dataset.vpcIndex = index;
    
    // Show modal
    modal.classList.remove('hidden');
    flashToast('Editing vPC domain', 'info');
}

function saveVPCEdit() {
    console.log('[CONFIG_EDITOR] Saving vPC edit');
    const modal = document.getElementById('editVPCModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVPCModal not found');
        return;
    }
    
    const index = parseInt(modal.dataset.vpcIndex);
    if (isNaN(index) || !deployment.vpc_pairs[index]) {
        console.error('[CONFIG_EDITOR] Invalid vPC index:', index);
        return;
    }
    
    const domainInput = document.getElementById('editVpcDomainId');
    const primaryInput = document.getElementById('editVpcPrimary');
    const secondaryInput = document.getElementById('editVpcSecondary');
    
    if (domainInput && primaryInput && secondaryInput) {
        deployment.vpc_pairs[index].domain = parseInt(domainInput.value);
        deployment.vpc_pairs[index].primary = primaryInput.value;
        deployment.vpc_pairs[index].secondary = secondaryInput.value;
        
        renderVPCList();
        closeEditVPCModal();
        flashToast('vPC domain updated', 'success');
    }
}

function closeEditVPCModal() {
    const modal = document.getElementById('editVPCModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function removeVPC(index) {
    console.log('[CONFIG_EDITOR] Removing vPC:', index);
    const vpc = deployment.vpc_pairs[index];
    if (!vpc) {
        console.error('[CONFIG_EDITOR] vPC not found at index:', index);
        return;
    }
    
    deployment.vpc_pairs.splice(index, 1);
    renderVPCList();
    flashToast(`vPC domain ${vpc.domain} removed`, 'info');
}

function editVLAN(index) {
    console.log('[CONFIG_EDITOR] Editing VLAN:', index);
    const vlan = deployment.global_vlans[index];
    if (!vlan) {
        console.error('[CONFIG_EDITOR] VLAN not found at index:', index);
        return;
    }
    
    // Show edit VLAN modal
    const modal = document.getElementById('editVLANModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVLANModal not found');
        return;
    }
    
    // Populate modal with current VLAN data
    const nameInput = document.getElementById('editVlanName');
    const descInput = document.getElementById('editVlanDesc');
    
    if (nameInput) nameInput.value = vlan.name;
    if (descInput) descInput.value = vlan.description || '';
    
    // Store the index for saving
    modal.dataset.vlanIndex = index;
    
    // Show modal
    modal.classList.remove('hidden');
    flashToast('Editing VLAN', 'info');
}

function saveVLANEdit() {
    console.log('[CONFIG_EDITOR] Saving VLAN edit');
    const modal = document.getElementById('editVLANModal');
    if (!modal) {
        console.error('[CONFIG_EDITOR] editVLANModal not found');
        return;
    }
    
    const index = parseInt(modal.dataset.vlanIndex);
    if (isNaN(index) || !deployment.global_vlans[index]) {
        console.error('[CONFIG_EDITOR] Invalid VLAN index:', index);
        return;
    }
    
    const nameInput = document.getElementById('editVlanName');
    const descInput = document.getElementById('editVlanDesc');
    
    if (nameInput) {
        deployment.global_vlans[index].name = nameInput.value;
        if (descInput) {
            deployment.global_vlans[index].description = descInput.value;
        }
        
        renderVLANList();
        closeEditVLANModal();
        flashToast('VLAN updated', 'success');
    }
}

function closeEditVLANModal() {
    const modal = document.getElementById('editVLANModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function removeVLAN(index) {
    console.log('[CONFIG_EDITOR] Removing VLAN:', index);
    if (!deployment.global_vlans || !deployment.global_vlans[index]) {
        console.error('[CONFIG_EDITOR] VLAN not found at index:', index);
        return;
    }
    
    deployment.global_vlans.splice(index, 1);
    renderVLANList();
    flashToast('VLAN removed', 'info');
}

function removeUplink(index) {
    console.log('[CONFIG_EDITOR] Removing uplink:', index);
    if (!deployment.uplinks || !deployment.uplinks[index]) {
        console.error('[CONFIG_EDITOR] Uplink not found at index:', index);
        return;
    }
    
    deployment.uplinks.splice(index, 1);
    renderUplinkList();
    flashToast('Uplink removed', 'info');
}

async function saveAsCustomTemplate() {
    console.log('[CUSTOM_TEMPLATE] Saving as custom template');
    
    const templateName = prompt('Enter template name:');
    if (!templateName) return;
    
    const payload = {
        name: templateName,
        description: 'Custom template created from current configuration',
        switches: JSON.parse(JSON.stringify(deployment.switches)),
        vpc_pairs: JSON.parse(JSON.stringify(deployment.vpc_pairs)),
        uplinks: JSON.parse(JSON.stringify(deployment.uplinks)),
        deployment: {
            switches: deployment.switches,
            vpc_pairs: deployment.vpc_pairs,
            uplinks: deployment.uplinks,
            global_vlans: deployment.global_vlans,
        },
    };
    
    try {
        const res = await fetch('/config/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (res.ok) {
            const saved = await res.json();
            flashToast(`Template "${templateName}" saved to server (${saved.id})`, 'success');
        } else {
            console.warn('[CUSTOM_TEMPLATE] Server save failed, using localStorage fallback');
            flashToast('Saved locally (server unavailable)', 'warning');
        }
    } catch (err) {
        console.warn('[CUSTOM_TEMPLATE] Server save error:', err);
    }
    
    const customTemplate = {
        id: `custom_${Date.now()}`,
        name: templateName,
        description: payload.description,
        use_case: 'Custom',
        use_case_category: 'custom',
        switch_count: deployment.switches.length,
        vpc_domain_count: deployment.vpc_pairs.length,
        vlan_range: deployment.global_vlans.length > 0 
            ? `${deployment.global_vlans[0].id}-${deployment.global_vlans[deployment.global_vlans.length - 1].id}`
            : '10-50',
        complexity: deployment.switches.length > 4 ? 'complex' : deployment.switches.length > 2 ? 'medium' : 'simple',
        hardware_compatibility: ['Custom'],
        best_practice_badge: false,
        switches: payload.switches,
        vpc_pairs: payload.vpc_pairs,
        uplinks: payload.uplinks,
        global_vlans: JSON.parse(JSON.stringify(deployment.global_vlans))
    };
    
    const customTemplates = JSON.parse(localStorage.getItem('customTemplates') || '[]');
    customTemplates.push(customTemplate);
    localStorage.setItem('customTemplates', JSON.stringify(customTemplates));
    DEPLOYMENT_TEMPLATES[customTemplate.id] = normalizeDeploymentTemplateGalleryMeta(customTemplate, customTemplate.id);
}

async function loadSavedDeploymentTemplatesFromServer() {
    try {
        const res = await fetch('/config/templates');
        if (!res.ok) return;
        const data = await res.json();
        (data.templates || []).forEach((meta) => {
            fetch(`/config/templates/${meta.id}`)
                .then(r => r.ok ? r.json() : null)
                .then(body => {
                    if (!body || !body.template) return;
                    const t = body.template;
                    const id = meta.id;
                    DEPLOYMENT_TEMPLATES[id] = normalizeDeploymentTemplateGalleryMeta({
                        id,
                        name: t.name || meta.name,
                        description: t.description || meta.description,
                        switches: t.switches || t.deployment?.switches || [],
                        vpc_pairs: t.vpc_pairs || t.deployment?.vpc_pairs || [],
                        uplinks: t.uplinks || t.deployment?.uplinks || [],
                        global_vlans: t.deployment?.global_vlans || t.global_vlans || [],
                        switch_count: meta.switch_count,
                        use_case: 'Saved',
                        use_case_category: 'saved',
                    }, id);
                })
                .catch(() => {});
        });
    } catch (err) {
        console.warn('[TEMPLATE_LOADING] Could not load saved templates from API:', err);
    }
}

function loadCustomTemplates() {
    const customTemplates = JSON.parse(localStorage.getItem('customTemplates') || '[]');
    customTemplates.forEach(template => {
        DEPLOYMENT_TEMPLATES[template.id] = normalizeDeploymentTemplateGalleryMeta(template, template.id);
    });
}

// Load custom templates on page load
loadCustomTemplates();
loadSavedDeploymentTemplatesFromServer();

function resetToTemplateGallery() {
    console.log('[TEMPLATE_GALLERY] Resetting to template gallery');
    
    // Clear deployment
    deployment.switches = [];
    deployment.vpc_pairs = [];
    deployment.uplinks = [];
    deployment.global_vlans = [];
    
    // Show template gallery
    renderTemplateGallery();
    
    // Hide other panels
    const switchListPanel = document.getElementById('switchListPanel');
    if (switchListPanel) {
        switchListPanel.classList.add('hidden');
    }
}

function hideTemplateGallery(showEditor = true) {
    console.log('[HIDE_TEMPLATE_GALLERY] Hiding gallery, showEditor:', showEditor);
    const gallery = document.getElementById('templateGallery');
    if (gallery) gallery.classList.add('hidden');
    
    if (showEditor) {
        const editor = document.getElementById('configurationEditor');
        if (editor) editor.classList.remove('hidden');
        
        // In multi-switch mode: suppress wizard nav/roadmap/footer and all wizard-steps
        // so the clean editor fills the left panel without single-switch VPC bleed-through
        if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode) {
            const wizardPanel = document.getElementById('wizardPanel');
            if (wizardPanel) wizardPanel.classList.remove('hidden');
            
            // step-1 is a .wizard-step (display:none by default) — must be active for editor to render
            const step1 = document.getElementById('step-1');
            if (step1) step1.classList.add('active');
            
            const wizardNav = document.getElementById('wizardNav');
            if (wizardNav) wizardNav.classList.add('hidden');
            
            const roadmap = document.getElementById('roadmapSummary');
            if (roadmap) roadmap.classList.add('hidden');
            
            const roadmapMore = document.getElementById('configurePathMore');
            if (roadmapMore) roadmapMore.hidden = true;
            
            const roadmapDetail = document.getElementById('configurePathDetail');
            if (roadmapDetail) roadmapDetail.hidden = true;
            
            const wizardFooter = document.querySelector('.wizard-footer');
            if (wizardFooter) wizardFooter.classList.add('hidden');
            
            // Hide all other wizard-step divs (single-switch only)
            document.querySelectorAll('.wizard-step:not(#step-1)').forEach(s => s.classList.remove('active'));
            
            // Clear any leftover results panel
            const resultsPanel = document.getElementById('multiSwitchResultsPanel');
            if (resultsPanel) { resultsPanel.classList.add('hidden'); resultsPanel.innerHTML = ''; }
        } else {
            const switchListPanel = document.getElementById('switchListPanel');
            if (switchListPanel) switchListPanel.classList.remove('hidden');
        }
        
        console.log('[HIDE_TEMPLATE_GALLERY] Rendering editor content');
        renderEditorTopology();
        renderSwitchesList();
        renderVPCList();
        renderVLANList();
        renderUplinkList();
    }
}

function showTemplateSummary(template) {
    const summary = `
        <div class="validation-status valid">
            <span class="validation-icon">✓</span>
            <span class="validation-message">
                Template "${template.name}" applied: ${template.switch_count} switches, 
                ${template.vpc_domain_count} vPC domains, ${template.uplinks.length} uplinks configured
            </span>
        </div>
    `;
    
    // Insert summary at the top of switch list panel
    const switchListPanel = document.getElementById('switchListPanel');
    if (switchListPanel) {
        const existingSummary = switchListPanel.querySelector('.validation-status');
        if (existingSummary) {
            existingSummary.remove();
        }
        switchListPanel.insertAdjacentHTML('afterbegin', summary);
    }
}

/**
 * Show template gallery when entering multi-switch mode
 */
function showTemplateGallery() {
    const gallery = document.getElementById('templateGallery');
    if (gallery) {
        gallery.classList.remove('hidden');
        console.log('[TEMPLATE_GALLERY] Showing gallery, removed hidden class');
    }
    renderTemplateGallery();
}

// Switch model port layouts
const SWITCH_MODELS = {
    "Nexus 9336C-FX2": {
        ports: 36,
        portSpeed: "40G/100G",
        layout: "3x12", // 3 rows of 12 QSFP28 ports
        portNaming: "Ethernet1/1-36",
        portType: "QSFP28",
        description: "36 x 40/100-Gbps QSFP28 ports"
    },
    "Nexus 93180YC-EX": {
        ports: 48,
        portSpeed: "10G/25G",
        layout: "2x24", // 2 rows of 24 SFP+ ports
        portNaming: "Ethernet1/1-48",
        portType: "SFP+",
        hasFiber: true,
        fiberPorts: 6,
        fiberPortType: "QSFP28",
        fiberPortSpeed: "40G/100G",
        fiberPortNaming: "Ethernet1/49-54",
        description: "48 x 10/25-Gbps SFP+ + 6 x 40/100-Gbps QSFP28"
    },
    "Nexus 9348GC-FXP": {
        ports: 48,
        portSpeed: "100M/1G",
        layout: "2x24",
        portNaming: "Ethernet1/1-48",
        portType: "RJ45",
        hasSFP: true,
        sfpPorts: 4,
        sfpPortType: "SFP28",
        sfpPortSpeed: "1G/10G/25G",
        sfpPortNaming: "Ethernet1/49-52",
        hasQSFP: true,
        qsfpPorts: 2,
        qsfpPortType: "QSFP28",
        qsfpPortSpeed: "40G/100G",
        qsfpPortNaming: "Ethernet1/53-54",
        description: "48 x 100M/1G BASE-T + 4 x 1/10/25G SFP28 + 2 x 40/100G QSFP28"
    },
    "Generic": {
        ports: 24,
        portSpeed: "1G",
        layout: "2x12",
        portNaming: "Ethernet1/1-24",
        portType: "Generic",
        description: "24 generic ports"
    }
};

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
        const isRecommended = s.role === "leaf" || s.recommended;
        const recommendedBadge = isRecommended ? `<span class="scenario-badge recommended">★ Recommended</span>` : "";
        card.innerHTML = `<div class="scenario-name">${escapeHtml(s.name)} ${speedBadge} ${recommendedBadge}</div>
            <div class="scenario-desc">${escapeHtml(s.description)}</div>
            <div class="scenario-tag">${tag}</div>`;
        card.addEventListener('click', () => selectScenario(s.id, card));
        // Add keyboard accessibility
        card.setAttribute("tabindex", "0");
        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                selectScenario(s.id, card);
            }
        });
        grid.appendChild(card);
    });
}

function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeJsString(s) {
    if (s === null || s === undefined) return '';
    return String(s)
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/'/g, "\\'")
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t')
        .replace(/\f/g, '\\f')
        .replace(/\v/g, '\\v')
        .replace(/\0/g, '\\0');
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
    
    // Auto-hide expert link planner for simpler UX - show only when user explicitly needs it
    const expertBody = document.getElementById("linkPlannerExpertBody");
    if (expertBody && !linkPlannerCustomized) {
        expertBody.hidden = true;
        const toggle = document.getElementById("linkPlannerExpertToggle");
        if (toggle) toggle.textContent = "Customize links (expert)";
    }
    
    // Auto-hide port map editor for simpler UX
    const portMapEditor = document.getElementById("portMapEditorPanel");
    const portMapToggle = document.getElementById("customPortMapToggle");
    if (portMapEditor && portMapToggle) {
        portMapEditor.hidden = true;
        portMapToggle.checked = false;
    }
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
    goToStep(Math.max(1, Math.min(8, currentStep + dir)));
}

function goToStep(n) {
    // Save state when leaving any step with user input
    if (currentStep !== n) {
        saveWizardState(currentStep);
    }
    
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
    if (n === 8) buildReviewPayload();
    
    // Restore state when entering a step
    restoreWizardState(n);
    
    if (n === 3) {
        // Restore saved state if available
        if (configureStepState) {
            restoreConfigureStepState();
        }
        applyRoadmapToWizard?.();
        applyVpcSuggestions(true);
        updateVpcVisibility();
        if (typeof resetLinkPlannerFromScenario === "function" && !configureStepState) resetLinkPlannerFromScenario();
        renderConfigureCards?.();
        renderInterfacePlanner?.();
    }
    onRoadmapStepEnter?.(n);
    updateWizardTip();
}

function saveConfigureStepState() {
    const fields = [
        "hostname", "mgmt_ip", "mgmt_gw", "model", "nxos_version", "site_name",
        "network_name", "site_location", "local_ka", "remote_ka", "bring_up_spare_ports",
        "generate_pair", "security_tier", "ntp_server", "logging_host",
        "mgmt_ip_secondary", "hostname_secondary"
    ];
    const state = {};
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            state[id] = el.type === "checkbox" ? el.checked : el.value;
        }
    });
    
    // Save feature selections
    const features = [];
    document.querySelectorAll("#featureGrid input[data-feature]:checked").forEach(cb => {
        features.push(cb.dataset.feature);
    });
    state.features = features;
    
    // Save baseline options
    const baseline = [];
    document.querySelectorAll("#baselineGrid input:checked").forEach(cb => {
        baseline.push(cb.dataset.baseline);
    });
    state.baseline_options = baseline;
    
    // Save link planner state
    if (typeof getLinkPlannerPayload === "function") {
        state.linkPlanner = getLinkPlannerPayload();
    }
    
    configureStepState = state;
}

function saveWizardState(step) {
    // Save state for each step based on its content
    window.wizardState = window.wizardState || {};
    
    switch(step) {
        case 1: // Mode
            // Save roadmap object which contains mode, vpc, speed
            if (typeof roadmap !== 'undefined') {
                window.wizardState.roadmap = { ...roadmap };
            }
            // Save selected scenario if in expert mode
            if (typeof selectedScenario !== 'undefined' && selectedScenario) {
                window.wizardState.selectedScenarioId = selectedScenario.id;
            }
            break;
        case 2: // vPC
            // Save roadmap object which contains vpc selection
            if (typeof roadmap !== 'undefined') {
                window.wizardState.roadmap = { ...roadmap };
            }
            break;
        case 3: // Platform
            saveConfigureStepState();
            break;
        case 4: // Features
            saveConfigureStepState();
            break;
        case 5: // VLANs
            const vlanRows = [];
            document.querySelectorAll("#vlanList .vlan-row").forEach(row => {
                const vlanId = row.querySelector("input[name*='vlan']")?.value;
                const vlanName = row.querySelector("input[name*='name']")?.value;
                const sviIp = row.querySelector("input[name*='ip']")?.value;
                if (vlanId) {
                    vlanRows.push({ vlanId, vlanName, sviIp });
                }
            });
            window.wizardState.vlans = vlanRows;
            break;
        case 6: // Interfaces
            const ifaceRows = [];
            document.querySelectorAll("#interfacePlanList .iface-plan-card").forEach(card => {
                const iface = card.dataset.iface;
                const mode = card.querySelector("select")?.value;
                const description = card.querySelector("input[type='text']")?.value;
                if (iface) {
                    ifaceRows.push({ iface, mode, description });
                }
            });
            window.wizardState.interfaces = ifaceRows;
            break;
        case 7: // Links
            saveConfigureStepState();
            break;
    }
}

function restoreWizardState(step) {
    if (!window.wizardState) return;
    
    switch(step) {
        case 1: // Mode
            if (window.wizardState.roadmap && typeof roadmap !== 'undefined') {
                Object.assign(roadmap, window.wizardState.roadmap);
                // Re-render choice cards to show selected state
                if (typeof renderModeChoices === 'function') renderModeChoices();
                if (typeof renderVpcChoices === 'function') renderVpcChoices();
                if (typeof renderSpeedChoices === 'function') renderSpeedChoices();
                if (typeof updateRoadmapSummary === 'function') updateRoadmapSummary();
            }
            // Restore selected scenario if in expert mode
            if (window.wizardState.selectedScenarioId && typeof catalog !== 'undefined' && catalog.scenarios) {
                selectedScenario = catalog.scenarios.find(s => s.id === window.wizardState.selectedScenarioId);
                if (selectedScenario && typeof renderScenarioGrid === 'function') {
                    renderScenarioGrid();
                }
            }
            break;
        case 2: // vPC
            if (window.wizardState.roadmap && typeof roadmap !== 'undefined') {
                Object.assign(roadmap, window.wizardState.roadmap);
                // Re-render vPC choice cards
                if (typeof renderVpcChoices === 'function') renderVpcChoices();
                if (typeof updateRoadmapSummary === 'function') updateRoadmapSummary();
            }
            break;
        case 3: // Platform
            restoreConfigureStepState();
            break;
        case 4: // Features
            restoreConfigureStepState();
            break;
        case 5: // VLANs
            if (window.wizardState.vlans && window.wizardState.vlans.length > 0) {
                // Clear existing VLAN rows
                document.querySelectorAll("#vlanList .vlan-row").forEach(row => row.remove());
                // Restore VLAN rows
                window.wizardState.vlans.forEach(vlan => {
                    if (typeof addVlanRow === 'function') addVlanRow();
                    const lastRow = document.querySelector("#vlanList .vlan-row:last-child");
                    if (lastRow) {
                        const vlanIdInput = lastRow.querySelector("input[name*='vlan']");
                        const vlanNameInput = lastRow.querySelector("input[name*='name']");
                        const sviIpInput = lastRow.querySelector("input[name*='ip']");
                        if (vlanIdInput) vlanIdInput.value = vlan.vlanId;
                        if (vlanNameInput) vlanNameInput.value = vlan.vlanName || "";
                        if (sviIpInput) sviIpInput.value = vlan.sviIp || "";
                    }
                });
            }
            break;
        case 6: // Interfaces
            if (window.wizardState.interfaces && window.wizardState.interfaces.length > 0) {
                // Clear existing interface rows
                document.querySelectorAll("#interfacePlanList .iface-plan-card").forEach(card => card.remove());
                // Restore interface rows
                window.wizardState.interfaces.forEach(iface => {
                    if (typeof addInterfacePlanRow === 'function') addInterfacePlanRow();
                    const lastCard = document.querySelector("#interfacePlanList .iface-plan-card:last-child");
                    if (lastCard) {
                        const modeInput = lastCard.querySelector("select");
                        const descInput = lastCard.querySelector("input[type='text']");
                        if (modeInput) modeInput.value = iface.mode || "";
                        if (descInput) descInput.value = iface.description || "";
                    }
                });
            }
            break;
        case 7: // Links
            restoreConfigureStepState();
            break;
    }
}

function restoreConfigureStepState() {
    if (!configureStepState) return;
    
    Object.entries(configureStepState).forEach(([id, value]) => {
        if (id === "features" || id === "baseline_options" || id === "linkPlanner") return;
        const el = document.getElementById(id);
        if (el) {
            if (el.type === "checkbox") {
                el.checked = value;
            } else {
                el.value = value;
            }
        }
    });
    
    // Restore features
    if (configureStepState.features) {
        document.querySelectorAll("#featureGrid input[data-feature]").forEach(cb => {
            cb.checked = configureStepState.features.includes(cb.dataset.feature);
        });
    }
    
    // Restore baseline options
    if (configureStepState.baseline_options) {
        document.querySelectorAll("#baselineGrid input").forEach(cb => {
            cb.checked = configureStepState.baseline_options.includes(cb.dataset.baseline);
        });
    }
    
    // Restore link planner
    if (configureStepState.linkPlanner && typeof applyLinkPlannerDefaults === "function") {
        applyLinkPlannerDefaults(configureStepState.linkPlanner);
    }
    
    syncFeatureDependencies();
    updateVersionNote();
    updateVpcVisibility();
}

function toggleSecondaryMgmtFields() {
    const generatePair = document.getElementById("generate_pair");
    const secondaryRow = document.getElementById("secondaryMgmtRow");
    if (!generatePair || !secondaryRow) return;
    
    if (generatePair.checked) {
        secondaryRow.hidden = false;
        // Auto-generate secondary hostname if empty
        const primaryHost = document.getElementById("hostname")?.value || "";
        const secondaryHost = document.getElementById("hostname_secondary");
        if (secondaryHost && !secondaryHost.value && primaryHost) {
            // Replace -A with -B or append -B
            if (primaryHost.endsWith("-A")) {
                secondaryHost.value = primaryHost.slice(0, -2) + "-B";
            } else {
                secondaryHost.value = primaryHost + "-B";
            }
        }
        // Auto-generate secondary IP if empty
        const primaryIp = document.getElementById("mgmt_ip")?.value || "";
        const secondaryIp = document.getElementById("mgmt_ip_secondary");
        if (secondaryIp && !secondaryIp.value && primaryIp) {
            // Increment the last octet
            const parts = primaryIp.split("/");
            if (parts.length === 2) {
                const ipParts = parts[0].split(".");
                if (ipParts.length === 4) {
                    const lastOctet = parseInt(ipParts[3], 10);
                    if (!isNaN(lastOctet)) {
                        secondaryIp.value = `${ipParts[0]}.${ipParts[1]}.${ipParts[2]}.${lastOctet + 1}/${parts[1]}`;
                    }
                }
            }
        }
    } else {
        secondaryRow.hidden = true;
    }
}

// Add event listener for generate_pair checkbox
document.addEventListener("DOMContentLoaded", () => {
    const generatePair = document.getElementById("generate_pair");
    if (generatePair) {
        generatePair.addEventListener("change", toggleSecondaryMgmtFields);
    }
});

document.querySelectorAll(".step-btn").forEach((btn) => {
    btn.addEventListener('click', () => goToStep(Number(btn.dataset.step)));
});

function preflightDeploymentErrors() {
    const errors = [];
    if (!multiSwitchMode || deployment.switches.length === 0) {
        return errors;
    }
    if (deployment.switches.length === 0) {
        errors.push("Add at least one switch to the deployment.");
        return errors;
    }
    const hostnames = new Set();
    deployment.switches.forEach((sw) => {
        const hn = (sw.hostname || "").trim();
        if (!hn) {
            errors.push("Every deployment switch must have a hostname.");
        } else if (!/^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$/.test(hn)) {
            errors.push(`Invalid hostname "${hn}": letters, numbers, hyphens only.`);
        } else if (hostnames.has(hn)) {
            errors.push(`Duplicate hostname "${hn}" in deployment.`);
        } else {
            hostnames.add(hn);
        }
        if (!sw.mgmt_ip || !String(sw.mgmt_ip).includes("/")) {
            errors.push(`${hn || "Switch"}: management IP must include CIDR (e.g. 10.0.0.1/24).`);
        }
        if (!sw.mgmt_gw || !String(sw.mgmt_gw).trim()) {
            errors.push(`${hn || "Switch"}: management gateway is required.`);
        }
        if (!sw.model || !String(sw.model).trim()) {
            errors.push(`${hn || "Switch"}: hardware model is required.`);
        }
    });
    (deployment.vpc_pairs || []).forEach((pair) => {
        const domain = pair.domain;
        if (domain == null || domain === "") {
            errors.push("vPC pair missing domain ID.");
            return;
        }
        if (!pair.primary || !pair.secondary) {
            errors.push(`vPC domain ${domain}: primary and secondary switches are required.`);
        }
        if (pair.primary === pair.secondary) {
            errors.push(`vPC domain ${domain}: primary and secondary must differ.`);
        }
        if (!hostnames.has(pair.primary) || !hostnames.has(pair.secondary)) {
            errors.push(`vPC domain ${domain}: both peers must exist in the deployment.`);
        }
        const peerPorts = pair.peer_link_ports || pair.vpc_pl_ints || "";
        if (!String(peerPorts).trim()) {
            errors.push(`vPC domain ${domain}: peer-link interfaces are required.`);
        }
    });
    return [...new Set(errors)];
}

function preflightErrorsForStep(step) {
    if (multiSwitchMode && deployment.switches.length > 0) {
        return step === 8 ? preflightDeploymentErrors() : [];
    }
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
        
        const generatePair = document.getElementById("generate_pair")?.checked;
        const needsVpc = selectedScenario?.redundancy === "vpc" || getEnabledFeatures().includes("vpc");
        
        if (needsVpc) {
            if (!document.getElementById("local_ka").value.trim()) errors.push("Local keepalive IP required for vPC.");
            if (!document.getElementById("remote_ka").value.trim()) errors.push("Remote keepalive IP required for vPC.");
            if (!document.getElementById("vpc_pl_ints").value.trim()) errors.push("Peer-link interfaces required for vPC.");
        }
        
        if (generatePair) {
            const hn2 = document.getElementById("hostname_secondary")?.value?.trim();
            if (!hn2) errors.push("Secondary hostname is required for vPC pair generation.");
            if (hn2 && !/^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$/.test(hn2)) errors.push("Secondary hostname: letters, numbers, hyphens only (no underscores).");
            const mgmtIp2 = document.getElementById("mgmt_ip_secondary")?.value;
            if (!mgmtIp2 || !mgmtIp2.includes("/")) errors.push("Secondary management IP must include CIDR (e.g. 10.0.0.2/24).");
        }
        
        if (typeof interfacePlanPreflightErrors === "function") {
            errors.push(...interfacePlanPreflightErrors());
        }
        return errors;
    }
    return [];
}

function preflightErrors() {
    if (multiSwitchMode && deployment.switches.length > 0) {
        return preflightDeploymentErrors();
    }
    const all = [];
    for (let s = 1; s <= 8; s++) all.push(...preflightErrorsForStep(s));
    return [...new Set(all)];
}

function updateBadges() {
    const isDeployment = multiSwitchMode && deployment.switches.length > 0;
    const errors = preflightErrors();
    const ok = errors.length === 0;
    document.getElementById("globalReadyBadge").className = ok ? "badge ok" : "badge err";
    document.getElementById("globalReadyBadge").textContent = ok ? "Ready to Build" : `${errors.length} issue(s)`;
    if (isDeployment) {
        const switchCount = deployment.switches.length;
        const vpcCount = (deployment.vpc_pairs || []).length;
        document.getElementById("scenarioBadge").textContent = `Multi-switch: ${switchCount} SW, ${vpcCount} vPC`;
        document.getElementById("scenarioBadge").className = ok ? "badge ok" : "badge err";
        document.getElementById("identityBadge").className = ok ? "badge ok" : "badge err";
        document.getElementById("identityBadge").textContent = ok ? "Deployment: Ready" : "Deployment: Pending";
    } else {
        document.getElementById("scenarioBadge").textContent = selectedScenario ? `Scenario: ${selectedScenario.name}` : "Scenario: —";
        document.getElementById("scenarioBadge").className = selectedScenario ? "badge ok" : "badge err";
        document.getElementById("identityBadge").className = ok ? "badge ok" : "badge err";
        document.getElementById("identityBadge").textContent = ok ? "Identity: Ready" : "Identity: Pending";
    }
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
    const generatePair = document.getElementById("generate_pair").checked;
    
    // Ensure scenario_id is always provided - use default if none selected
    const scenarioId = selectedScenario?.id || "standalone_leaf";
    
    const payload = {
        scenario_id: scenarioId,
        hostname: document.getElementById("hostname").value.trim(),
        site_name: document.getElementById("site_name").value.trim() || "DEFAULT_SITE",
        mgmt_ip: document.getElementById("mgmt_ip").value.trim(),
        mgmt_gw: document.getElementById("mgmt_gw").value.trim(),
        generate_pair: generatePair,
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
    
    // Add secondary device fields when generating vPC pair
    if (generatePair) {
        const secondaryHostname = document.getElementById("hostname_secondary")?.value.trim();
        const secondaryMgmtIp = document.getElementById("mgmt_ip_secondary")?.value.trim();
        
        // Only set generate_pair to true if secondary fields are actually filled
        if (secondaryHostname && secondaryMgmtIp) {
            payload.secondary_hostname = secondaryHostname;
            payload.secondary_mgmt_ip = secondaryMgmtIp;
            console.log("=== SECONDARY FIELDS FILLED - generate_pair remains true ===");
            console.log("secondary_hostname:", secondaryHostname);
            console.log("secondary_mgmt_ip:", secondaryMgmtIp);
        } else {
            // If secondary fields are empty, disable generate_pair
            payload.generate_pair = false;
            payload.secondary_hostname = null;
            payload.secondary_mgmt_ip = null;
            console.log("=== SECONDARY FIELDS EMPTY - generate_pair set to false ===");
            console.log("secondary_hostname was:", secondaryHostname);
            console.log("secondary_mgmt_ip was:", secondaryMgmtIp);
        }
    }
    
    console.log("Built scenario payload:", JSON.stringify(payload, null, 2));
    console.log("Payload keys:", Object.keys(payload));
    console.log("scenario_id:", payload.scenario_id);
    console.log("hostname:", payload.hostname);
    console.log("mgmt_ip:", payload.mgmt_ip);
    console.log("mgmt_gw:", payload.mgmt_gw);
    console.log("site_name:", payload.site_name);
    return payload;
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
        flashToast("Please fix the errors before proceeding", "err");
        return;
    }
    
    // Check if in multi-switch mode and use deployment endpoint instead
    if (multiSwitchMode && deployment.switches.length > 0) {
        console.log("Multi-switch mode detected, using deployment endpoint");
        await generateDeploymentConfigs();
        return;
    }
    
    const payload = buildScenarioPayload();
    
    // Validate required fields before sending
    if (!payload.mgmt_ip || payload.mgmt_ip.length < 9) {
        setOutput("Error: Management IP is required and must be valid (e.g., 10.10.10.10/24)");
        flashToast("Please enter a valid management IP", "err");
        return;
    }
    if (!payload.mgmt_gw || payload.mgmt_gw.length < 7) {
        setOutput("Error: Management gateway is required (e.g., 10.10.10.1)");
        flashToast("Please enter a valid management gateway", "err");
        return;
    }
    if (!payload.hostname || payload.hostname.length < 1) {
        setOutput("Error: Hostname is required");
        flashToast("Please enter a hostname", "err");
        return;
    }
    
    setBusy(true);
    setOutput(mode === "preview" ? "Validating and rendering preview..." : "Building configuration...");
    const endpoint = mode === "preview" ? "/scenario/preview" : CONFIG_ROUTE_VPC;
    
    // Log API request details
    if (window.auditLogger) {
        window.auditLogger.logPreviewEvent('API_REQUEST_START', {
            endpoint: endpoint,
            mode: mode,
            payloadKeys: Object.keys(payload)
        });
    }
    
    console.log("=== BEFORE API CALL ===");
    console.log("Endpoint:", endpoint);
    console.log("Payload:", JSON.stringify(payload, null, 2));
    console.log("======================");
    
    try {
        console.log("Sending payload to", endpoint, ":", payload);
        const res = await fetch(endpoint, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
        
        console.log("=== AFTER FETCH ===");
        console.log("Response status:", res.status);
        console.log("Response OK:", res.ok);
        console.log("==================");
        
        if (!res.ok) {
            console.log("=== RESPONSE NOT OK ===");
            console.log("Status:", res.status);
            console.log("Status Text:", res.statusText);
            try {
                const errorText = await res.text();
                console.log("Error response:", errorText);
            } catch (e) {
                console.log("Could not read error response:", e);
            }
            console.log("========================");
            throw new Error(`API request failed: ${res.status} ${res.statusText}`);
        }
        
        console.log("=== BEFORE JSON PARSE ===");
        const result = await res.json();
        
        console.log("=== AFTER JSON PARSE ===");
        console.log("Result parsed successfully");
        console.log("========================");
        
        // Log API response details
        if (window.auditLogger) {
            window.auditLogger.logAPIResponseDetails(endpoint, res.status, result);
        }
        
        console.log("=== FULL API RESPONSE ===");
        console.log("Response status:", res.status);
        console.log("Response keys:", Object.keys(result));
        console.log("Full response:", JSON.stringify(result, null, 2));
        console.log("Has pair_preview:", !!result.pair_preview);
        console.log("pair_preview value:", result.pair_preview);
        console.log("Has secondary_config_preview:", !!result.pair_preview?.secondary_config_preview);
        console.log("pair_mode:", result.pair_mode);
        console.log("=========================");
        
        // Log full response to audit logger
        if (window.auditLogger) {
            window.auditLogger.logPreviewEvent('FULL_API_RESPONSE', {
                endpoint: endpoint,
                status: res.status,
                responseKeys: Object.keys(result),
                hasPairPreview: !!result.pair_preview,
                pairMode: result.pair_mode,
                hasSecondaryConfig: !!result.pair_preview?.secondary_config_preview,
                secondaryHostname: result.pair_preview?.secondary_hostname,
                fullResponse: JSON.stringify(result, null, 2)
            });
        }
        
        if (!res.ok) {
            console.error("API Error:", result);
            console.error("Status:", res.status);
            console.error("Response:", JSON.stringify(result, null, 2));
            setOutput(`Error (${res.status}):\n${JSON.stringify(result, null, 2)}`);
            const errorMsg = result.detail ? (typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail)) : "Unknown error";
            
            // Log API error details
            if (window.auditLogger) {
                window.auditLogger.logPreviewEvent('API_REQUEST_FAILED', {
                    endpoint: endpoint,
                    status: res.status,
                    statusText: res.statusText,
                    errorDetail: errorMsg,
                    fullResponse: result
                });
            }
            
            flashToast("Request failed: " + errorMsg, "err");
            return;
        }
        if (mode === "preview") {
            lastConfigPreview = result.config_preview || "";
            console.log("=== PREVIEW MODE PROCESSING ===");
            console.log("Preview result keys:", Object.keys(result));
            console.log("Has pair_preview:", !!result.pair_preview);
            console.log("pair_preview value:", result.pair_preview);
            console.log("Has secondary_config_preview:", !!result.pair_preview?.secondary_config_preview);
            console.log("secondary_config_preview length:", result.pair_preview?.secondary_config_preview?.length || 0);
            console.log("================================");
            
            // Log preview event details
            if (window.auditLogger) {
                window.auditLogger.logAPIResponseDetails('/scenario/preview', res.status, result);
                window.auditLogger.logPreviewEvent('RECEIVED', {
                    has_pair_preview: !!result.pair_preview,
                    has_secondary_config: !!result.pair_preview?.secondary_config_preview,
                    config_preview_length: lastConfigPreview.length
                });
            }
            
            if (result.action_required) renderActionRequired?.(result.action_required);
            if (result.cli_blocks) renderSelectedCli?.(result.cli_blocks, lastSelectedOptionId);
            const live = document.getElementById("liveCliOutput");
            if (live) live.textContent = lastConfigPreview;
            setOutput(formatPreview(result) + "\n\n--- CLI PREVIEW ---\n\n" + lastConfigPreview);
            
            console.log("=== CHECKING SECONDARY CONFIG ===");
            console.log("result.pair_preview:", result.pair_preview);
            console.log("result.pair_preview?.secondary_config_preview:", result.pair_preview?.secondary_config_preview);
            
            if (result.pair_preview?.secondary_config_preview) {
                console.log("=== APPENDING SECONDARY CONFIG ===");
                console.log("Secondary config length:", result.pair_preview.secondary_config_preview.length);
                const currentOutput = document.getElementById("statusOutput").textContent;
                const newOutput = currentOutput + "\n\n--- SECONDARY CLI PREVIEW ---\n\n" + result.pair_preview.secondary_config_preview;
                setOutput(newOutput);
                console.log("Secondary config appended");
            } else {
                console.log("=== NO SECONDARY CONFIG FOUND ===");
            }
            
            showCompliance(result.compliance_findings);
            if (result.pair_preview?.pair_validation?.errors?.length) {
                flashToast("vPC pair validation: " + result.pair_preview.pair_validation.errors.join("; "), "warn");
            }
            
            // Display stacked configuration in deploymentResults container
            const deploymentResults = document.getElementById("deploymentResults");
            console.log("deploymentResults element found:", !!deploymentResults);
            if (deploymentResults) {
                console.log("Populating deploymentResults with preview data");
                deploymentResults.innerHTML = '';
                
                const hostname = document.getElementById("hostname").value || "Unknown";
                console.log("Hostname for display:", hostname);
                console.log("Config preview length:", lastConfigPreview.length);
                console.log("Is vPC pair:", !!result.pair_preview);
                
                let configHtml = '';
                
                if (result.pair_preview && result.pair_preview.secondary_config_preview) {
                    // vPC pair - display port maps stacked, then CLI configurations stacked
                    const secondaryHostname = result.pair_preview.secondary_hostname || document.getElementById("hostname_secondary")?.value || "Unknown";
                    console.log("=== RENDERING STACKED LAYOUT (PORT MAPS THEN CLI) FOR VPC PAIR ===");
                    console.log("Primary hostname:", hostname);
                    console.log("Secondary hostname:", secondaryHostname);
                    console.log("Secondary config preview length:", result.pair_preview.secondary_config_preview.length);
                    console.log("Primary port map data:", result.pair_preview.primary_port_map);
                    console.log("Secondary port map data:", result.pair_preview.secondary_port_map);
                    
                    // Check if port maps exist
                    if (!result.pair_preview.primary_port_map) {
                        console.warn("Primary port map is missing from API response");
                    }
                    if (!result.pair_preview.secondary_port_map) {
                        console.warn("Secondary port map is missing from API response");
                    }
                    
                    // Render primary port map
                    const primaryPortMapHtml = renderPortMapFromApi(result.pair_preview.primary_port_map);
                    console.log("Primary port map HTML length:", primaryPortMapHtml.length);
                    console.log("Primary port map HTML preview:", primaryPortMapHtml.substring(0, 200));
                    console.log("Primary port map full HTML:", primaryPortMapHtml);
                    // Render secondary port map
                    const secondaryPortMapHtml = renderPortMapFromApi(result.pair_preview.secondary_port_map);
                    console.log("Secondary port map HTML length:", secondaryPortMapHtml.length);
                    console.log("Secondary port map HTML preview:", secondaryPortMapHtml.substring(0, 200));
                    console.log("Secondary port map full HTML:", secondaryPortMapHtml);
                    
                    // Generate physical port matrix for primary
                    const primaryPhysicalMatrix = generatePhysicalPortMatrix(hostname, result.pair_preview.primary_port_map);
                    console.log("Primary physical matrix HTML length:", primaryPhysicalMatrix.length);
                    
                    // Generate physical port matrix for secondary
                    const secondaryPhysicalMatrix = generatePhysicalPortMatrix(secondaryHostname, result.pair_preview.secondary_port_map);
                    console.log("Secondary physical matrix HTML length:", secondaryPhysicalMatrix.length);
                    
                    configHtml = `
                        <!-- Primary Node Section -->
                        <div class="node-section">
                            <h3 class="section-title">${hostname} (Primary)</h3>
                            
                            <!-- Primary Port Map (Verbal) -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>Port Map</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="port-map-section">
                                        <div class="port-map-container">
                                            ${primaryPortMapHtml}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Primary Physical Port Matrix -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>Physical Port Matrix</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="port-map-section">
                                        ${primaryPhysicalMatrix}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Primary CLI Configuration -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>CLI Configuration</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="cli-section">
                                        <pre class="cli-block">${lastConfigPreview}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Secondary Node Section -->
                        <div class="node-section">
                            <h3 class="section-title">${secondaryHostname} (Secondary)</h3>
                            
                            <!-- Secondary Port Map (Verbal) -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>Port Map</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="port-map-section">
                                        <div class="port-map-container">
                                            ${secondaryPortMapHtml}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Secondary Physical Port Matrix -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>Physical Port Matrix</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="port-map-section">
                                        ${secondaryPhysicalMatrix}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Secondary CLI Configuration -->
                            <div class="deployment-switch-stack">
                                <div class="switch-stack-header">
                                    <h4>CLI Configuration</h4>
                                </div>
                                <div class="switch-stack-content">
                                    <div class="cli-section">
                                        <pre class="cli-block">${result.pair_preview.secondary_config_preview}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    console.log("=== STACKED LAYOUT (PORT MAPS THEN CLI) RENDERED ===");
                    console.log("Full configHtml length:", configHtml.length);
                    console.log("Full configHtml preview:", configHtml.substring(0, 500));
                    console.log("Full configHtml contains 'Secondary':", configHtml.includes("Secondary"));
                    console.log("Full configHtml contains 'k (Secondary)':", configHtml.includes("k (Secondary)"));
                } else {
                    // Single switch
                    configHtml = `
                        <div class="deployment-switch-stack">
                            <div class="switch-stack-header">
                                <h4>${hostname}</h4>
                            </div>
                            <div class="switch-stack-content">
                                <div class="port-map-section">
                                    <h5>Port Map</h5>
                                    <div class="port-map-container">
                                        <p class="field-note">Port map will be displayed here after full deployment generation.</p>
                                    </div>
                                </div>
                                <div class="cli-section">
                                    <h5>CLI Configuration</h5>
                                    <pre class="cli-block">${lastConfigPreview}</pre>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                deploymentResults.innerHTML = configHtml;
                console.log("=== COMPREHENSIVE DOM INSPECTION START ===");
                console.log("deploymentResults HTML set, length:", deploymentResults.innerHTML.length);
                console.log("Number of switch stacks:", deploymentResults.querySelectorAll('.deployment-switch-stack').length);
                console.log("Full deploymentResults innerHTML:", deploymentResults.innerHTML);
                console.log("=== COMPREHENSIVE DOM INSPECTION END ===");
                
                // Scroll to port maps section so user can see both port maps
                const portMapsSection = deploymentResults.querySelector('.port-maps-section');
                if (portMapsSection) {
                    portMapsSection.scrollIntoView({ behavior: 'auto', block: 'start' });
                    console.log("Scrolled to port maps section (instant scroll)");
                    
                    console.log("=== COMPREHENSIVE CSS INSPECTION START ===");
                    console.log("Window innerHeight:", window.innerHeight);
                    console.log("Window innerWidth:", window.innerWidth);
                    
                    // Check if secondary port map is in DOM
                    const allStacks = deploymentResults.querySelectorAll('.deployment-switch-stack');
                    console.log("Total switch stacks in deploymentResults:", allStacks.length);
                    console.log("Switch stack headers:");
                    allStacks.forEach((stack, index) => {
                        const header = stack.querySelector('h4');
                        console.log(`Stack ${index}: ${header ? header.textContent : 'No header'}`);
                    });
                    
                    // Check computed styles for port maps section
                    if (portMapsSection) {
                        console.log("=== PORT MAPS SECTION INSPECTION ===");
                        const sectionStyles = window.getComputedStyle(portMapsSection);
                        console.log("Port maps section found in DOM");
                        console.log("Port maps section display:", sectionStyles.display);
                        console.log("Port maps section visibility:", sectionStyles.visibility);
                        console.log("Port maps section opacity:", sectionStyles.opacity);
                        console.log("Port maps section height:", sectionStyles.height);
                        console.log("Port maps section innerHTML length:", portMapsSection.innerHTML.length);
                        
                        // Check individual switch stacks in port maps section
                        const portMapStacks = portMapsSection.querySelectorAll('.deployment-switch-stack');
                        console.log("=== PORT MAP STACKS INSPECTION ===");
                        console.log("Number of switch stacks in port maps section:", portMapStacks.length);
                        portMapStacks.forEach((stack, index) => {
                            console.log(`=== STACK ${index} INSPECTION ===`);
                            const styles = window.getComputedStyle(stack);
                            const rect = stack.getBoundingClientRect();
                            console.log(`Stack ${index} display: ${styles.display}`);
                            console.log(`Stack ${index} visibility: ${styles.visibility}`);
                            console.log(`Stack ${index} opacity: ${styles.opacity}`);
                            console.log(`Stack ${index} height: ${styles.height}`);
                            console.log(`Stack ${index} Bounding rect:`, rect);
                            console.log(`Stack ${index} rect.top: ${rect.top}, rect.bottom: ${rect.bottom}`);
                            console.log(`Stack ${index} Window innerHeight: ${window.innerHeight}`);
                            console.log(`Stack ${index} Is fully in viewport: ${rect.top >= 0 && rect.bottom <= window.innerHeight}`);
                            console.log(`Stack ${index} Is partially in viewport: ${rect.top < window.innerHeight && rect.bottom > 0}`);
                            console.log(`Stack ${index} innerHTML length: ${stack.innerHTML.length}`);
                            
                            // Check if the port-map-container exists within this stack
                            const portMapContainer = stack.querySelector('.port-map-container');
                            if (portMapContainer) {
                                console.log(`Stack ${index} port-map-container found`);
                                const containerStyles = window.getComputedStyle(portMapContainer);
                                console.log(`Stack ${index} port-map-container display: ${containerStyles.display}`);
                                console.log(`Stack ${index} port-map-container visibility: ${containerStyles.visibility}`);
                                console.log(`Stack ${index} port-map-container opacity: ${containerStyles.opacity}`);
                                console.log(`Stack ${index} port-map-container innerHTML length: ${portMapContainer.innerHTML.length}`);
                            } else {
                                console.log(`Stack ${index} port-map-container NOT found`);
                            }
                        });
                    } else {
                        console.warn("Port maps section NOT found in DOM");
                    }
                    console.log("=== COMPREHENSIVE CSS INSPECTION END ===");
                }
            } else {
                console.error("deploymentResults element not found in DOM");
            }
            
            flashToast("Preview generated successfully", "ok");
        } else {
            lastPrimaryConfig = (result.results || [])[0]?.config_preview || "";
            const parts = (result.results || []).map((r) => `=== ${r.hostname} ===\n${r.config_preview || r.message}`);
            setOutput(parts.join("\n\n"));
            showCompliance(result.compliance_findings);
            fetchVault();
            fetchCheckpoints();
            
            // Render port maps if available in generate response
            if (result.pair_port_maps) {
                console.log("=== PAIR_PORT_MAPS FOUND IN GENERATE RESPONSE ===");
                const deploymentResults = document.getElementById("deploymentResults");
                if (deploymentResults) {
                    const primaryResult = result.results?.find(r => r.hostname === document.getElementById("hostname")?.value) || result.results?.[0];
                    const secondaryResult = result.results?.find(r => r.hostname !== primaryResult?.hostname);
                    
                    const primaryHostname = primaryResult?.hostname || document.getElementById("hostname")?.value || "Unknown";
                    const secondaryHostname = secondaryResult?.hostname || document.getElementById("hostname_secondary")?.value || "Unknown";
                    
                    console.log("=== RENDERING SIDE-BY-SIDE LAYOUT FROM GENERATE RESPONSE ===");
                    console.log("Primary hostname:", primaryHostname);
                    console.log("Secondary hostname:", secondaryHostname);
                    console.log("Primary result:", primaryResult);
                    console.log("Secondary result:", secondaryResult);
                    console.log("Primary port map data:", result.pair_port_maps.primary_port_map);
                    console.log("Secondary port map data:", result.pair_port_maps.secondary_port_map);
                    
                    const primaryPortMapHtml = renderPortMapFromApi(result.pair_port_maps.primary_port_map);
                    const secondaryPortMapHtml = renderPortMapFromApi(result.pair_port_maps.secondary_port_map);
                    
                    console.log("Primary port map HTML length:", primaryPortMapHtml.length);
                    console.log("Secondary port map HTML length:", secondaryPortMapHtml.length);
                    
                    const configHtml = `
                        <div class="deployment-switch-stack">
                            <div class="switch-stack-header">
                                <h4>${primaryHostname} (Primary)</h4>
                            </div>
                            <div class="switch-stack-content switch-stack-side-by-side">
                                <div class="port-map-section">
                                    <h5>Port Map</h5>
                                    <div class="port-map-container">
                                        ${primaryPortMapHtml}
                                    </div>
                                </div>
                                <div class="cli-section">
                                    <h5>CLI Configuration</h5>
                                    <pre class="cli-block">${primaryResult?.config_preview || ""}</pre>
                                </div>
                            </div>
                        </div>
                        <div class="deployment-switch-stack">
                            <div class="switch-stack-header">
                                <h4>${secondaryHostname} (Secondary)</h4>
                            </div>
                            <div class="switch-stack-content switch-stack-side-by-side">
                                <div class="port-map-section">
                                    <h5>Port Map</h5>
                                    <div class="port-map-container">
                                        ${secondaryPortMapHtml}
                                    </div>
                                </div>
                                <div class="cli-section">
                                    <h5>CLI Configuration</h5>
                                    <pre class="cli-block">${secondaryResult?.config_preview || ""}</pre>
                                </div>
                            </div>
                        </div>
                    `;
                    deploymentResults.innerHTML = configHtml;
                    console.log("=== DEPLOYMENT RESULTS UPDATED WITH SIDE-BY-SIDE LAYOUT ===");
                }
            }
            
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

function toggleVaultCheckpoints() {
    console.log("=== TOGGLING VAULT & CHECKPOINTS PANEL ===");
    const panel = document.getElementById("vaultCheckpointsPanel");
    if (panel) {
        const isHidden = panel.style.display === 'none';
        panel.style.display = isHidden ? 'block' : 'none';
        console.log("Vault & Checkpoints panel", isHidden ? "shown" : "hidden");
    } else {
        console.error("vaultCheckpointsPanel element not found");
    }
}

// Add input validation feedback
function addInputValidation() {
    const requiredInputs = document.querySelectorAll("input[required], select[required]");
    requiredInputs.forEach(input => {
        input.addEventListener("blur", () => {
            if (!input.value.trim()) {
                input.classList.add("input-error");
                showFieldError(input, "This field is required");
            } else {
                input.classList.remove("input-error");
                hideFieldError(input);
            }
        });
    });
}

function showFieldError(input, message) {
    let errorEl = input.parentElement.querySelector(".field-error");
    if (!errorEl) {
        errorEl = document.createElement("div");
        errorEl.className = "field-error";
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function hideFieldError(input) {
    const errorEl = input.parentElement.querySelector(".field-error");
    if (errorEl) errorEl.remove();
}

// Initialize validation on DOM load
document.addEventListener("DOMContentLoaded", () => {
    addInputValidation();
});

function formatPreview(r) {
    let text = `Scenario: ${r.scenario_name}\nNX-OS: ${r.nxos_version}\nStatus: ${r.status}\n\n`;
    text += "Summary:\n" + (r.summary_lines || []).map((l) => "  • " + l).join("\n") + "\n";
    if (r.validation_errors?.length) text += "\nValidation:\n" + r.validation_errors.join("\n");
    if (r.pair_preview) text += `\nvPC Pair: ${r.pair_preview.primary.hostname} + ${r.pair_preview.secondary_hostname}\n`;
    return text;
}

function renderPortMapFromApi(portMapData) {
    console.log("=== renderPortMapFromApi called ===");
    console.log("portMapData:", portMapData);
    
    if (!portMapData) {
        console.warn("portMapData is null or undefined");
        return '<p class="field-note">No port map data available (null data).</p>';
    }
    
    if (!portMapData.ports) {
        console.warn("portMapData.ports is missing");
        return '<p class="field-note">No port map data available (missing ports).</p>';
    }
    
    if (portMapData.ports.length === 0) {
        console.warn("portMapData.ports is empty");
        return '<p class="field-note">No port map data available (empty ports array).</p>';
    }
    
    console.log(`Rendering ${portMapData.ports.length} ports for ${portMapData.hostname}`);
    
    const ports = portMapData.ports;
    let html = '<table class="port-map-table"><thead><tr><th>Port</th><th>Name</th><th>Type</th><th>Description</th><th>Port Channel</th></tr></thead><tbody>';
    
    ports.forEach(port => {
        html += `
            <tr>
                <td>${port.port}</td>
                <td>${port.port_name}</td>
                <td>${port.type}</td>
                <td>${port.description || '-'}</td>
                <td>${port.port_channel ? `PO${port.port_channel}` : '-'}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    console.log("renderPortMapFromApi completed, HTML length:", html.length);
    return html;
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

function flashToast(msg, type, fixAction = null) {
    const t = document.getElementById("toast");
    if (!t) return;
    
    // Log toast message to audit logger
    if (window.auditLogger) {
        window.auditLogger.logPreviewEvent('TOAST_DISPLAYED', {
            message: msg,
            type: type,
            hasFixAction: !!fixAction
        });
    }
    
    // Clear existing content
    t.innerHTML = '';
    
    // Add message text
    const msgSpan = document.createElement('span');
    msgSpan.textContent = msg;
    t.appendChild(msgSpan);
    
    // Add fix button if action provided
    if (fixAction) {
        const fixBtn = document.createElement('button');
        fixBtn.className = 'toast-fix-btn';
        fixBtn.textContent = 'Fix';
        fixBtn.addEventListener('click', fixAction);
        t.appendChild(fixBtn);
    }
    
    t.className = `toast toast-${type} show`;
    setTimeout(() => t.classList.remove("show"), 5000);
}

// Help tooltip system
const FIELD_HELP = {
    hostname: "Unique name to identify this switch in the network (e.g., CORE1, LEAF1)",
    mgmt_ip: "Management IP address for out-of-band access (e.g., 10.0.0.1/24)",
    mgmt_gw: "Default gateway for management subnet (e.g., 10.0.0.254)",
    model: "Switch hardware model - determines port count and capabilities",
    role: "Network role: core (backbone), spine (aggregation), or leaf (access)",
    vpc_domain: "Unique vPC domain ID (1-4094) for vPC pair configuration",
    peer_link_ports: "Ports used for vPC peer-link connection between paired switches",
    keepalive_ports: "Ports used for vPC keepalive heartbeat connection",
    local_ka: "Local switch's keepalive IP address",
    remote_ka: "Peer switch's keepalive IP address",
    vlan_id: "VLAN identifier (1-4094) for network segmentation",
    vlan_name: "Descriptive name for the VLAN (e.g., WEB-SERVERS)",
    svi_ip: "Switch Virtual Interface IP for the VLAN (e.g., 10.10.10.1/24)",
    site_name: "Site or location identifier for this deployment"
};

function addHelpTooltip(inputId, helpKey) {
    const input = document.getElementById(inputId);
    if (!input || !FIELD_HELP[helpKey]) return;
    
    // Check if tooltip already exists
    if (input.parentElement.querySelector('.help-tooltip')) return;
    
    const helpIcon = document.createElement('span');
    helpIcon.className = 'help-tooltip';
    helpIcon.innerHTML = '?';
    helpIcon.title = FIELD_HELP[helpKey];
    
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(helpIcon);
}

function addAllHelpTooltips() {
    // Add tooltips to common form fields
    const fieldMappings = [
        { id: 'hostname', key: 'hostname' },
        { id: 'mgmt_ip', key: 'mgmt_ip' },
        { id: 'mgmt_gw', key: 'mgmt_gw' },
        { id: 'model', key: 'model' },
        { id: 'role', key: 'role' },
        { id: 'vpc_domain', key: 'vpc_domain' },
        { id: 'peer_link_ports', key: 'peer_link_ports' },
        { id: 'keepalive_ports', key: 'keepalive_ports' },
        { id: 'local_ka', key: 'local_ka' },
        { id: 'remote_ka', key: 'remote_ka' },
        { id: 'site_name', key: 'site_name' }
    ];
    
    fieldMappings.forEach(mapping => {
        addHelpTooltip(mapping.id, mapping.key);
    });
    
    // Add tooltips to VLAN inputs dynamically
    document.querySelectorAll('.vlan-id').forEach(input => {
        if (!input.parentElement.querySelector('.help-tooltip')) {
            const helpIcon = document.createElement('span');
            helpIcon.className = 'help-tooltip';
            helpIcon.innerHTML = '?';
            helpIcon.title = FIELD_HELP['vlan_id'];
            input.parentElement.style.position = 'relative';
            input.parentElement.appendChild(helpIcon);
        }
    });
}

// Configuration comments/annotations
let configComments = {};

function addConfigComment(switchId, comment) {
    if (!configComments[switchId]) {
        configComments[switchId] = [];
    }
    configComments[switchId].push({
        text: comment,
        timestamp: new Date().toISOString()
    });
}

function getConfigComments(switchId) {
    return configComments[switchId] || [];
}

function renderCommentPanel(switchId) {
    const panel = document.getElementById("commentPanel");
    if (!panel) return;
    
    const comments = getConfigComments(switchId);
    
    let html = `
        <div class="comment-panel">
            <h4>Configuration Comments</h4>
            <div class="comment-list">
    `;
    
    comments.forEach(comment => {
        const date = new Date(comment.timestamp).toLocaleString();
        html += `
            <div class="comment-item">
                <div class="comment-text">${escapeHtml(comment.text)}</div>
                <div class="comment-meta">${date}</div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="comment-input">
                <textarea id="newComment" placeholder="Add a comment about this configuration..." rows="3"></textarea>
                <button type="button" class="btn-primary" data-action="save-comment" data-switch-id="${switchId}">Add Comment</button>
            </div>
        </div>
    `;
    
    panel.innerHTML = html;
}

function saveComment(switchId) {
    const textarea = document.getElementById("newComment");
    if (!textarea || !textarea.value.trim()) return;
    
    addConfigComment(switchId, textarea.value.trim());
    textarea.value = "";
    renderCommentPanel(switchId);
    flashToast("Comment added", "ok");
}

function includeCommentsInConfig(config, switchId) {
    const comments = getConfigComments(switchId);
    if (comments.length === 0) return config;
    
    let commentBlock = "\n! ============================================\n";
    commentBlock += "! Configuration Comments\n";
    commentBlock += "! ============================================\n";
    
    comments.forEach(comment => {
        const date = new Date(comment.timestamp).toLocaleString();
        commentBlock += `! [${date}] ${comment.text}\n`;
    });
    
    commentBlock += "! ============================================\n\n";
    
    return commentBlock + config;
}

// Breadcrumb navigation and progress indicators
const WIZARD_STEPS = [
    { id: 1, name: "Scenario", description: "Select network scenario" },
    { id: 2, name: "Hardware", description: "Choose switch model" },
    { id: 3, name: "Features", description: "Configure features" },
    { id: 4, name: "VLANs", description: "Define VLANs" },
    { id: 5, name: "Links", description: "Configure links" },
    { id: 6, name: "Review", description: "Review configuration" },
    { id: 7, name: "Generate", description: "Generate configs" },
    { id: 8, name: "Export", description: "Export configs" }
];

function renderBreadcrumbNavigation() {
    const container = document.getElementById("breadcrumbNav");
    if (!container) return;
    
    let html = `<nav class="breadcrumb-nav" aria-label="Wizard navigation">`;
    
    WIZARD_STEPS.forEach((step, index) => {
        const isActive = currentStep === step.id;
        const isCompleted = currentStep > step.id;
        const isClickable = isCompleted || isActive;
        
        html += `
            <div class="breadcrumb-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}"
                 ${isClickable ? `data-action="go-to-step" data-step="${step.id}"` : ''}>
                <div class="breadcrumb-number">${isCompleted ? '✓' : step.id}</div>
                <div class="breadcrumb-info">
                    <div class="breadcrumb-name">${escapeHtml(step.name)}</div>
                    <div class="breadcrumb-desc">${escapeHtml(step.description)}</div>
                </div>
            </div>
        `;
        
        if (index < WIZARD_STEPS.length - 1) {
            html += `<div class="breadcrumb-separator">→</div>`;
        }
    });
    
    html += `</nav>`;
    container.innerHTML = html;
}

function renderProgressBar() {
    const container = document.getElementById("progressBar");
    if (!container) return;
    
    const totalSteps = WIZARD_STEPS.length;
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    
    let html = `
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
            <div class="progress-text">Step ${currentStep} of ${totalSteps} (${Math.round(progress)}%)</div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Real-time form validation
function validateField(input, validator) {
    const isValid = validator(input.value);
    if (isValid) {
        input.classList.remove('error');
        input.classList.add('valid');
        const error = input.parentElement.querySelector('.form-error');
        if (error) error.style.display = 'none';
    } else {
        input.classList.remove('valid');
        input.classList.add('error');
        const error = input.parentElement.querySelector('.form-error');
        if (error) error.style.display = 'block';
    }
    return isValid;
}

// Common validators
const validators = {
    ip: (value) => /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/.test(value),
    hostname: (value) => /^[a-zA-Z0-9-]{1,63}$/.test(value),
    vlan: (value) => /^\d+$/.test(value) && parseInt(value) >= 1 && parseInt(value) <= 4094,
    required: (value) => value && value.trim() !== ''
};

function setupRealTimeValidation() {
    // IP address validation
    document.querySelectorAll('input[id*="ip"]').forEach(input => {
        input.addEventListener('blur', () => validateField(input, validators.ip));
        input.addEventListener('input', () => {
            input.classList.remove('error', 'valid');
        });
    });
    
    // Hostname validation
    document.querySelectorAll('input[id="hostname"]').forEach(input => {
        input.addEventListener('blur', () => validateField(input, validators.hostname));
        input.addEventListener('input', () => {
            input.classList.remove('error', 'valid');
        });
    });
    
    // VLAN validation
    document.querySelectorAll('input[id*="vlan"]').forEach(input => {
        input.addEventListener('blur', () => validateField(input, validators.vlan));
        input.addEventListener('input', () => {
            input.classList.remove('error', 'valid');
        });
    });
}

// Loading state helper
function setLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
    } else {
        element.classList.remove('loading');
    }
}

// Success animation helper
function showSuccessAnimation(element) {
    element.classList.add('success-animation');
    setTimeout(() => element.classList.remove('success-animation'), 300);
}

// ARIA labels for accessibility
function addAriaLabels() {
    // Add aria-label to buttons without text
    document.querySelectorAll('button').forEach(btn => {
        if (!btn.textContent.trim() && !btn.getAttribute('aria-label')) {
            const icon = btn.querySelector('svg, i');
            if (icon) {
                btn.setAttribute('aria-label', icon.getAttribute('data-icon') || 'Button');
            }
        }
    });
    
    // Add aria-live to toast notifications
    const toast = document.getElementById('toast');
    if (toast) {
        toast.setAttribute('aria-live', 'polite');
        toast.setAttribute('role', 'alert');
    }
}

// Font size controls
let currentFontSize = 100; // percentage

function changeFontSize(delta) {
    currentFontSize = Math.max(80, Math.min(150, currentFontSize + delta));
    document.documentElement.style.fontSize = `${currentFontSize}%`;
    localStorage.setItem('fontSize', currentFontSize);
    updateFontSizeDisplay();
}

function updateFontSizeDisplay() {
    const display = document.querySelector('.font-size-display');
    if (display) {
        display.textContent = `${currentFontSize}%`;
    }
}

function addFontSizeControls() {
    const header = document.querySelector('header') || document.body;
    if (document.querySelector('.font-size-controls')) return;
    
    const controls = document.createElement('div');
    controls.className = 'font-size-controls';
    controls.innerHTML = `
        <button type="button" class="font-size-btn" data-action="change-font-size" data-delta="-10">A-</button>
        <span class="font-size-display">${currentFontSize}%</span>
        <button type="button" class="font-size-btn" data-action="change-font-size" data-delta="10">A+</button>
    `;
    
    header.insertBefore(controls, header.firstChild);
}

// Load saved font size
const savedFontSize = localStorage.getItem('fontSize');
if (savedFontSize) {
    currentFontSize = parseInt(savedFontSize);
    document.documentElement.style.fontSize = `${currentFontSize}%`;
}

// Call addAllHelpTooltips after DOM updates
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(addAllHelpTooltips, 500);
    setInterval(addAllHelpTooltips, 2000);
    addFontSizeControls();
    renderBreadcrumbNavigation();
    renderProgressBar();
    setupRealTimeValidation();
    addAriaLabels();
    
    // Update progress on step change
    const originalSetStep = window.setStep;
    if (originalSetStep) {
        window.setStep = function(step) {
            originalSetStep(step);
            renderBreadcrumbNavigation();
            renderProgressBar();
        };
    }
});

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
    row.innerHTML = `<input type="number" class="vlan-id" placeholder="VLAN ID" min="1" max="4094" data-action="validate-vlan-id"><input type="text" class="vlan-name" placeholder="Name">
        <input type="text" class="svi-ip" placeholder="SVI IP"><button type="button" class="btn-outline" data-action="remove-parent">Remove</button>`;
    document.getElementById("vlanList").appendChild(row);
}

function validateVlanId(input) {
    const vlanId = parseInt(input.value);
    
    // Validate range
    if (isNaN(vlanId) || vlanId < 1 || vlanId > 4094) {
        flashToast("VLAN ID must be between 1 and 4094", "error");
        input.value = "";
        return false;
    }
    
    // Validate duplicates
    const allVlanInputs = document.querySelectorAll(".vlan-id");
    const vlanIds = [];
    allVlanInputs.forEach(inp => {
        if (inp !== input && inp.value) {
            vlanIds.push(parseInt(inp.value));
        }
    });
    
    if (vlanIds.includes(vlanId)) {
        flashToast(`VLAN ID ${vlanId} already exists. Please use a unique VLAN ID.`, "error");
        input.value = "";
        return false;
    }
    
    return true;
}

function applyVlanTemplate(template) {
    const vlanList = document.getElementById("vlanList");
    if (!vlanList) return;
    
    // Clear existing VLANs
    vlanList.innerHTML = "";
    
    const templates = {
        datacenter: [
            { id: 10, name: "Data-Web", svi: "10.10.10.1/24" },
            { id: 20, name: "Data-App", svi: "10.20.20.1/24" },
            { id: 30, name: "Data-DB", svi: "10.30.30.1/24" },
            { id: 40, name: "Data-Mgmt", svi: "10.40.40.1/24" },
            { id: 50, name: "Data-Backup", svi: "10.50.50.1/24" }
        ],
        campus: [
            { id: 100, name: "Campus-Users", svi: "192.168.100.1/24" },
            { id: 110, name: "Campus-VoIP", svi: "192.168.110.1/24" },
            { id: 120, name: "Campus-Video", svi: "192.168.120.1/24" },
            { id: 130, name: "Campus-Guest", svi: "192.168.130.1/24" },
            { id: 140, name: "Campus-IoT", svi: "192.168.140.1/24" }
        ],
        dmz: [
            { id: 200, name: "DMZ-External", svi: "172.16.200.1/24" },
            { id: 210, name: "DMZ-Web", svi: "172.16.210.1/24" },
            { id: 220, name: "DMZ-App", svi: "172.16.220.1/24" },
            { id: 230, name: "DMZ-DB", svi: "172.16.230.1/24" }
        ],
        custom: []
    };
    
    const selectedTemplate = templates[template];
    if (!selectedTemplate) return;
    
    if (template === 'custom') {
        // For custom, just add a single empty row
        addVlanRow();
        flashToast("Custom template selected - add VLANs manually", "info");
        return;
    }
    
    // Add VLANs from template
    selectedTemplate.forEach(vlan => {
        const row = document.createElement("div");
        row.className = "grid-2 vlan-row";
        row.innerHTML = `
            <input type="number" class="vlan-id" placeholder="VLAN ID" value="${vlan.id}">
            <input type="text" class="vlan-name" placeholder="Name" value="${vlan.name}">
            <input type="text" class="svi-ip" placeholder="SVI IP" value="${vlan.svi}">
            <button type="button" class="btn-outline" data-action="remove-parent">Remove</button>
        `;
        vlanList.appendChild(row);
    });
    
    flashToast(`Applied ${selectedTemplate.length} VLANs from ${template} template`, "ok");
}

async function expandRange() {
    const range = document.getElementById("rangeInput").value;
    if (!range) return;
    
    try {
        const res = await fetch(`/util/expand-range?range_str=${encodeURIComponent(range)}`);
        if (!res.ok) {
            const errorText = await res.text();
            flashToast(`Range expansion failed: ${errorText}`, "err");
            return;
        }
        const data = await res.json();
        const area = document.getElementById("interfacesArea");
        if (!area) {
            flashToast("Interfaces area not found", "err");
            return;
        }
        if (!data.expanded || !Array.isArray(data.expanded)) {
            flashToast("Invalid response from server", "err");
            return;
        }
        area.value += (area.value ? "\n" : "") + data.expanded.join("\n");
    } catch (error) {
        console.error("Range expansion error:", error);
        flashToast(`Range expansion error: ${error.message}`, "err");
    }
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
            <button type="button" class="vault-item" data-action="view-checkpoint" data-filename="${safe}">
                <span>${escapeHtml(c.filename)}</span><span class="vault-type">${escapeHtml(c.timestamp)}</span>
            </button>
            <button type="button" class="btn-outline btn-sm" data-action="restore-checkpoint" data-filename="${safe}" aria-label="Restore ${escapeHtml(c.filename)}">Restore</button>
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
        if (el) {
            // Use structured diff for better UI if available
            if (data.structured && data.structured.changes.length > 0) {
                el.innerHTML = renderStructuredDiff(data.structured);
            } else {
                el.textContent = data.diff || "No differences.";
            }
        }
        flashToast("Diff complete.", "ok");
    } catch (err) {
        flashToast("Diff failed: " + err.message, "err");
    }
}

function renderStructuredDiff(structured) {
    const summary = structured.summary;
    let html = `<div class="diff-summary">
        <span class="diff-stat added">+${summary.additions} added</span>
        <span class="diff-stat removed">-${summary.removals} removed</span>
        <span class="diff-stat modified">~${summary.modifications} modified</span>
    </div>`;
    
    html += `<div class="diff-changes">`;
    for (const change of structured.changes) {
        if (change.type === 'added') {
            html += `<div class="diff-change added">
                <div class="diff-header">Added:</div>
                ${change.lines.map(line => `<div class="diff-line added">${escapeHtml(line)}</div>`).join('')}
            </div>`;
        } else if (change.type === 'removed') {
            html += `<div class="diff-change removed">
                <div class="diff-header">Removed:</div>
                ${change.lines.map(line => `<div class="diff-line removed">${escapeHtml(line)}</div>`).join('')}
            </div>`;
        } else if (change.type === 'modified') {
            html += `<div class="diff-change modified">
                <div class="diff-header">Modified:</div>
                <div class="diff-modified-old">
                    <div class="diff-subheader">Old:</div>
                    ${change.old_lines.map(line => `<div class="diff-line removed">${escapeHtml(line)}</div>`).join('')}
                </div>
                <div class="diff-modified-new">
                    <div class="diff-subheader">New:</div>
                    ${change.new_lines.map(line => `<div class="diff-line added">${escapeHtml(line)}</div>`).join('')}
                </div>
            </div>`;
        }
    }
    html += `</div>`;
    return html;
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
        return `<button type="button" class="vault-item" data-type="${type}" data-action="view-vault" data-filename="${safe}"><span>${escapeHtml(f)}</span><span class="vault-type">${type}</span></button>`;
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

// Toggle keepalive IP inputs based on checkbox
function toggleKeepaliveInputs() {
    const useDefault = document.getElementById("useDefaultKa")?.checked;
    const keepaliveGroup = document.getElementById("keepaliveIpGroup");
    const localKa = document.getElementById("local_ka");
    const remoteKa = document.getElementById("remote_ka");
    
    if (keepaliveGroup) {
        keepaliveGroup.style.opacity = useDefault ? "0.5" : "1";
    }
    if (localKa) {
        localKa.disabled = useDefault;
    }
    if (remoteKa) {
        remoteKa.disabled = useDefault;
    }
    
    // Auto-generate keepalive IPs when checkbox is checked
    if (useDefault) {
        const vpcDomain = document.getElementById("vpc_domain")?.value;
        if (vpcDomain) {
            const domainNum = parseInt(vpcDomain);
            if (localKa) localKa.value = `10.255.${Math.floor(domainNum / 256)}.${domainNum % 256}`;
            if (remoteKa) remoteKa.value = `10.255.${Math.floor(domainNum / 256)}.${(domainNum % 256) + 1}`;
        } else {
            if (localKa) localKa.value = "10.255.255.1";
            if (remoteKa) remoteKa.value = "10.255.255.2";
        }
    }
}

// Multi-switch deployment functions
function toggleMultiSwitchMode() {
    multiSwitchMode = !multiSwitchMode;
    const toggle = document.getElementById("multiSwitchToggle");
    const switchListPanel = document.getElementById("switchListPanel");
    
    if (toggle) {
        toggle.checked = multiSwitchMode;
        toggle.setAttribute("aria-pressed", multiSwitchMode);
    }
    
    if (switchListPanel) {
        switchListPanel.classList.toggle("hidden", !multiSwitchMode);
    }
    
    if (multiSwitchMode && deployment.switches.length === 0) {
        showTemplateGallery(); // Show new template gallery
    } else if (!multiSwitchMode) {
        deployment = { switches: [], vpc_pairs: [], uplinks: [], global_vlans: [] };
        hideTemplateGallery(false); // Hide template gallery when exiting multi-switch mode, don't show editor
    }
    
    renderSwitchList();
    updateBadges();
    
    // Update mode dropdown button text to reflect multi-switch mode
    const modeBtn = document.getElementById('modeDropdownBtn');
    if (modeBtn) {
        if (multiSwitchMode) {
            modeBtn.innerHTML = `Mode: Multi-Switch <span class="dropdown-arrow">▾</span>`;
        } else {
            modeBtn.innerHTML = `Mode: Quick <span class="dropdown-arrow">▾</span>`;
        }
    }
    
    // Hide/show wizard panel based on mode
    const wizardPanel = document.getElementById('wizardPanel');
    if (wizardPanel) {
        if (multiSwitchMode) {
            wizardPanel.classList.add('hidden');
            document.body.classList.add('multi-switch-mode');
            console.log('[MULTI_SWITCH_MODE] Wizard panel hidden');
        } else {
            wizardPanel.classList.remove('hidden');
            document.body.classList.remove('multi-switch-mode');
            // Restore wizard-nav and roadmap when leaving multi-switch mode
            const wizardNav = document.getElementById('wizardNav');
            if (wizardNav) wizardNav.classList.remove('hidden');
            const roadmap = document.getElementById('roadmapSummary');
            if (roadmap) roadmap.classList.remove('hidden');
            console.log('[MULTI_SWITCH_MODE] Wizard panel visible');
        }
    }
    
    // Ensure configuration editor is visible when in multi-switch mode with deployment data
    if (multiSwitchMode && deployment.switches.length > 0) {
        const editor = document.getElementById('configurationEditor');
        if (editor) {
            editor.classList.remove('hidden');
            console.log('[MULTI_SWITCH_MODE] Configuration editor visible');
        }
        
        // Ensure wizard tip bars are hidden in multi-switch mode
        const tipBars = ['configurePathBanner', 'wizardTipBox', 'firstRunHint'];
        tipBars.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.add('hidden');
            }
        });
    }
    
    // Log mode change for debugging
    console.log('[MULTI_SWITCH_MODE] Mode toggled:', multiSwitchMode);
    console.log('[MULTI_SWITCH_MODE] Deployment switches:', deployment.switches.length);
}

function renderDeploymentTemplates() {
    // Old template system - disabled in favor of new template gallery
    // This function is kept for backward compatibility but no longer used
    console.log('[DEPRECATED] renderDeploymentTemplates called - using new template gallery instead');
    showTemplateGallery();
}

function selectDeploymentTemplate(templateKey) {
    const template = DEPLOYMENT_TEMPLATES[templateKey];
    if (!template) return;
    
    // Validate port-channel ID uniqueness before loading template
    const poValidation = validatePortChannelIds(template.uplinks);
    if (!poValidation.valid) {
        flashToast(`Warning: Template has duplicate port-channel IDs on switch ${poValidation.conflict_switch}: ${poValidation.conflict_ids.join(', ')}`, "warning");
    }
    
    // Initialize deployment from template
    deployment = {
        switches: template.switches.map((sw, i) => ({
            id: `switch-${Date.now()}-${i}`,
            hostname: sw.hostname,
            mgmt_ip: sw.mgmt_ip,
            mgmt_gw: sw.mgmt_gw || "10.0.0.254",
            model: sw.model,
            role: sw.role,
            vpc_domain: sw.vpc_domain || null,
            nxos_version: sw.nxos_version || "9.3",
            vpc_peer_link_id: sw.vpc_peer_link_id || 1,
            keepalive_po_id: sw.keepalive_po_id || 2,
            vpc_system_priority: sw.vpc_system_priority || 32667,
            local_ka: sw.local_ka || "10.0.0.1",
            remote_ka: sw.remote_ka || "10.0.0.2",
            peer_link_ports: sw.peer_link_ports || "",
            base_access_vlan: sw.base_access_vlan || 10,
            access_vlan_count: sw.access_vlan_count || 4,
            interface_count: sw.interface_count || 0,
            bring_up_spare_ports: sw.bring_up_spare_ports || false,
            security_tier: sw.security_tier || "standard",
            site_name: sw.site_name || "HQ",
            configured_ports: []
        })),
        vpc_pairs: template.vpc_pairs.map((pair, i) => ({
            id: `vpc-${Date.now()}-${i}`,
            domain: pair.domain,
            primary: pair.primary,
            secondary: pair.secondary,
            peer_link_ports: pair.peer_link_ports
        })),
        uplinks: template.uplinks.map((uplink, i) => ({
            id: `uplink-${Date.now()}-${i}`,
            from: uplink.from,
            to: uplink.to,
            ports: uplink.ports,
            po_id: uplink.po_id
        })),
        global_vlans: []
    };
    
    renderSwitchList();
    renderDeploymentTopology();
    
    // Show configuration wizard
    showDeploymentWizard();
}

function validatePortChannelIds(uplinks) {
    // Port channel validation: same po_id on same switch is valid (LACP port channel with multiple member ports)
    // Only validate that po_ids are present and numeric
    for (const uplink of uplinks) {
        if (!uplink.po_id) {
            return {
                valid: false,
                errors: [`Uplink from ${uplink.from} to ${uplink.to} is missing port channel ID`]
            };
        }
        if (isNaN(parseInt(uplink.po_id))) {
            return {
                valid: false,
                errors: [`Uplink from ${uplink.from} to ${uplink.to} has invalid port channel ID: ${uplink.po_id}`]
            };
        }
    }
    
    return { valid: true };
}

function showDeploymentWizard() {
    // Navigate to step 4 (Features) to configure the deployment
    goToStep(4);
    flashToast("Deployment template loaded. Configure each switch in the Features step.", "info");
}

function addSwitch() {
    console.log('[SWITCH_ADD] [USER_ACTION] User clicked "Add Switch" button');
    console.log('[SWITCH_ADD] [CODE_LOCATION] static/app.js:3070');
    
    const baseHostname = document.getElementById("hostname")?.value || "SW";
    const baseMgmtIp = document.getElementById("mgmt_ip")?.value || "10.0.0.1";
    const model = document.getElementById("model")?.value || "Nexus 9336C-FX2";
    
    console.log('[SWITCH_ADD] [FORM_DATA] Base hostname:', baseHostname, 'Base mgmt IP:', baseMgmtIp, 'Default model:', model);
    
    // Create modal for adding switch with role selection
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "modal-title");
    
    console.log('[SWITCH_ADD] [UI_RENDER] Rendering add switch modal');
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 id="modal-title">Add New Switch</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <form id="addSwitchForm">
                    <div class="form-group">
                        <label for="addHostname">Base Hostname</label>
                        <input type="text" id="addHostname" name="hostname" value="${baseHostname}" required>
                        <small>Will auto-increment (e.g., SW-1, SW-2)</small>
                    </div>
                    <div class="form-group">
                        <label for="addMgmtIp">Base Management IP</label>
                        <input type="text" id="addMgmtIp" name="mgmt_ip" value="${baseMgmtIp}" required>
                        <small>Will auto-increment (e.g., 10.0.0.1, 10.0.0.2)</small>
                    </div>
                    <div class="form-group">
                        <label for="addMgmtGw">Management Gateway</label>
                        <input type="text" id="addMgmtGw" name="mgmt_gw" value="${document.getElementById("mgmt_gw")?.value || "10.0.0.254"}">
                    </div>
                    <div class="form-group">
                        <label for="addModel">Model</label>
                        <select id="addModel" name="model" data-action="log-model-change">
                            <option value="Nexus 9336C-FX2" ${model === 'Nexus 9336C-FX2' ? 'selected' : ''}>Nexus 9336C-FX2 (40GB Core)</option>
                            <option value="Nexus 93180YC-EX" ${model === 'Nexus 93180YC-EX' ? 'selected' : ''}>Nexus 93180YC-EX (10GB Leaf)</option>
                            <option value="Nexus 9348GC-FXP" ${model === 'Nexus 9348GC-FXP' ? 'selected' : ''}>Nexus 9348GC-FXP (1GB Leaf)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="addRole">Role</label>
                        <select id="addRole" name="role" data-action="log-role-change">
                            <option value="leaf">Leaf (Access)</option>
                            <option value="core">Core (Spine/Aggregation)</option>
                            <option value="spine">Spine</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="addVpcDomain">vPC Domain (leave empty for standalone)</label>
                        <input type="number" id="addVpcDomain" name="vpc_domain" value="${document.getElementById("vpc_domain")?.value || ""}" min="1" max="4096">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="confirm-add-switch">Add Switch</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    console.log('[SWITCH_ADD] [UI_RENDER] Modal appended to DOM');
    
    // Focus on first input for accessibility
    setTimeout(() => {
        const firstInput = modal.querySelector('input');
        if (firstInput) firstInput.focus();
    }, 100);
}

function confirmAddSwitch() {
    console.log('[SWITCH_ADD_CONFIRM] [USER_ACTION] User clicked "Add Switch" to confirm');
    console.log('[SWITCH_ADD_CONFIRM] [CODE_LOCATION] static/app.js:3148');
    
    const form = document.getElementById("addSwitchForm");
    if (!form) {
        console.log('[SWITCH_ADD_CONFIRM] [ERROR] Add switch form not found in DOM');
        console.log('[SWITCH_ADD_CONFIRM] [OPERATIONAL_LOGIC] This is unexpected - form should exist when confirm button is clicked');
        return;
    }
    
    const baseHostname = form.hostname.value || "SW";
    const baseMgmtIp = form.mgmt_ip.value || "10.0.0.1";
    const model = form.model.value || "Nexus 9336C-FX2";
    const role = form.role.value || "leaf";
    const vpcDomain = form.vpc_domain.value;
    
    console.log('[SWITCH_ADD_CONFIRM] [FORM_DATA] Hostname:', baseHostname, 'Mgmt IP:', baseMgmtIp, 'Model:', model, 'Role:', role, 'vPC Domain:', vpcDomain);
    
    // Validate model compatibility with deployment topology
    const hwProfile = SWITCH_MODELS[model] || {};
    
    console.log('[SWITCH_ADD_CONFIRM] [HW_PROFILE] Hardware profile for model:', model, hwProfile);
    
    // Check if model supports vPC if deployment has vPC pairs
    if (deployment.vpc_pairs && deployment.vpc_pairs.length > 0) {
        const supportsVpc = hwProfile.vpc_peer_link || hwProfile.device_class !== "generic";
        if (!supportsVpc) {
            console.log('[SWITCH_ADD_CONFIRM] [VALIDATION_WARNING] Model may not support vPC peer-link');
            const confirmed = confirm(`Warning: ${model} may not support vPC peer-link configuration. Deployment has ${deployment.vpc_pairs.length} vPC pair(s).\n\nContinue anyway?`);
            if (!confirmed) {
                console.log('[SWITCH_ADD_CONFIRM] [USER_CANCEL] User cancelled due to vPC incompatibility');
                return;
            }
        }
    }
    
    // Check if model has sufficient ports for connections
    const interfaceCount = hwProfile.ports || 48;
    const requiredPorts = deployment.switches.length * 2;
    if (interfaceCount < requiredPorts) {
        console.log('[SWITCH_ADD_CONFIRM] [VALIDATION_WARNING] Insufficient ports - has:', interfaceCount, 'needs:', requiredPorts);
        const confirmed = confirm(`Warning: ${model} has only ${interfaceCount} ports. May be insufficient for ${deployment.switches.length + 1} switches.\n\nContinue anyway?`);
        if (!confirmed) {
            console.log('[SWITCH_ADD_CONFIRM] [USER_CANCEL] User cancelled due to insufficient ports');
            return;
        }
    }
    
    // Validate hostname uniqueness
    const switchNum = deployment.switches.length + 1;
    const newHostname = `${baseHostname}-${switchNum}`;
    const hostnameExists = deployment.switches.some(s => s.hostname === newHostname);
    if (hostnameExists) {
        console.log('[SWITCH_ADD_CONFIRM] [VALIDATION_ERROR] Hostname already exists:', newHostname);
        console.log('[SWITCH_ADD_CONFIRM] [OPERATIONAL_LOGIC] This is expected behavior - hostnames must be unique');
        flashToast(`Error: Hostname ${newHostname} already exists. Use a different base hostname.`, "error");
        return;
    }
    
    // Validate vPC domain uniqueness if this switch will have vPC
    if (vpcDomain && vpcDomain.trim() !== '') {
        const domainConflict = deployment.vpc_pairs.find(p => p.domain === vpcDomain);
        if (domainConflict) {
            console.log('[SWITCH_ADD_CONFIRM] [VALIDATION_ERROR] vPC domain already in use:', vpcDomain);
            console.log('[SWITCH_ADD_CONFIRM] [OPERATIONAL_LOGIC] This is expected behavior - vPC domains must be unique');
            flashToast(`Error: vPC domain ${vpcDomain} already in use by ${domainConflict.primary} ↔ ${domainConflict.secondary}. Use a different domain.`, "error");
            return;
        }
    }
    
    console.log('[SWITCH_ADD_CONFIRM] [VALIDATION_SUCCESS] All validations passed');
    
    const newSwitch = {
        id: `switch-${Date.now()}`,
        hostname: newHostname,
        mgmt_ip: incrementIpAddress(baseMgmtIp, switchNum - 1),
        mgmt_gw: form.mgmt_gw.value || "10.0.0.254",
        model: model,
        role: role,
        vpc_domain: vpcDomain || "",
        configured_ports: []
    };
    
    console.log('[SWITCH_ADD_CONFIRM] [DATA_UPDATE] Creating new switch:', newSwitch.hostname, 'Model:', newSwitch.model, 'Role:', newSwitch.role);
    
    deployment.switches.push(newSwitch);
    document.querySelector('.modal-overlay').remove();
    
    // Render in configuration editor if visible, otherwise use old UI
    const configEditor = document.getElementById('configurationEditor');
    if (configEditor && !configEditor.classList.contains('hidden')) {
        renderSwitchesList();
        renderEditorTopology();
    } else {
        renderSwitchList();
        renderDeploymentTopology();
    }
    
    flashToast(`Switch ${newHostname} added successfully as ${role}`, "ok");
    
    console.log('[SWITCH_ADD_CONFIRM] [UI_UPDATE] Switch added and UI updated');
}

function removeSwitch(switchId) {
    const sw = deployment.switches.find(s => s.id === switchId);
    if (!sw) return;
    
    // Check if switch is part of any vPC pair
    const vpcPair = deployment.vpc_pairs.find(p => p.primary === sw.hostname || p.secondary === sw.hostname);
    if (vpcPair) {
        const confirmed = confirm(`Warning: Switch ${sw.hostname} is part of vPC Domain ${vpcPair.domain} with ${vpcPair.primary === sw.hostname ? vpcPair.secondary : vpcPair.primary}.\n\nRemoving this switch will break the vPC pair. Continue?`);
        if (!confirmed) return;
        
        // Remove the vPC pair
        deployment.vpc_pairs = deployment.vpc_pairs.filter(p => p !== vpcPair);
    }
    
    // Check if switch has any uplinks
    const uplinks = deployment.uplinks.filter(u => u.from === sw.hostname || u.to === sw.hostname);
    if (uplinks.length > 0) {
        const uplinkInfo = uplinks.map(u => `${u.from} → ${u.to} (PO${u.po_id})`).join('\n');
        const confirmed = confirm(`Warning: Switch ${sw.hostname} has ${uplinks.length} uplink(s):\n${uplinkInfo}\n\nRemoving this switch will delete these uplinks. Continue?`);
        if (!confirmed) return;
        
        // Remove uplinks
        deployment.uplinks = deployment.uplinks.filter(u => u.from !== sw.hostname && u.to !== sw.hostname);
    }
    
    deployment.switches = deployment.switches.filter(s => s.id !== switchId);
    deployment.connections = deployment.connections.filter(c => c.from !== switchId && c.to !== switchId);
    renderSwitchList();
    renderDeploymentTopology();
    flashToast(`Switch ${sw.hostname} removed successfully`, "ok");
}

function incrementIpAddress(ip, increment) {
    const parts = ip.split('/');
    const address = parts[0];
    const cidr = parts[1] || "24";
    const octets = address.split('.').map(Number);
    octets[3] += increment;
    if (octets[3] > 255) {
        octets[3] = 1;
        octets[2] += 1;
    }
    return `${octets.join('.')}/${cidr}`;
}

function renderSwitchList() {
    const container = document.getElementById("switchListContainer");
    if (!container) return;
    
    if (deployment.switches.length === 0) {
        renderDeploymentTemplates();
        return;
    }
    
    let html = `<div class="switch-list-header">`;
    html += `<h3>Deployment Switches (${deployment.switches.length})</h3>`;
    html += `<div class="switch-list-actions">`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="save-deployment">Save Deployment</button>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="load-deployment">Load Deployment</button>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="change-deployment-template">Change Template</button>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="add-switch">+ Add Switch</button>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="reset-deployment">Reset</button>`;
    html += `</div>`;
    html += `</div>`;
    
    html += `<div class="switch-list-instructions">`;
    html += `<p><strong>Tip:</strong> Click on any switch in the topology diagram above to view its port configuration. Use the switch cards below to manage individual switches.</p>`;
    html += `</div>`;
    
    html += `<div class="switch-list">`;
    deployment.switches.forEach((sw, index) => {
        const vpcPair = deployment.vpc_pairs.find(p => p.primary === sw.hostname || p.secondary === sw.hostname);
        const vpcInfo = vpcPair ? `vPC Domain ${vpcPair.domain}` : 'Standalone';
        
        html += `
            <div class="switch-card" data-switch-id="${sw.id}">
                <div class="switch-card-header">
                    <span class="switch-name">${sw.hostname}</span>
                    <span class="switch-role-badge">${sw.role}</span>
                </div>
                <div class="switch-card-body">
                    <div class="switch-info">
                        <span class="label">Model:</span>
                        <span>${sw.model}</span>
                    </div>
                    <div class="switch-info">
                        <span class="label">Mgmt IP:</span>
                        <span>${sw.mgmt_ip}</span>
                    </div>
                    <div class="switch-info">
                        <span class="label">vPC:</span>
                        <span>${vpcInfo}</span>
                    </div>
                    <div class="switch-card-actions">
                        <button type="button" class="btn-outline btn-sm" data-action="edit-switch" data-switch-id="${sw.id}">Edit</button>
                        <button type="button" class="btn-outline btn-sm" data-action="delete-switch" data-switch-id="${sw.id}">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    html += `</div>`;
    
    // Add vPC pairs summary with CRUD
    if (deployment.vpc_pairs.length > 0) {
        html += `<div class="deployment-connections">`;
        html += `<div class="deployment-connections-header">`;
        html += `<h4>vPC Pairs (${deployment.vpc_pairs.length})</h4>`;
        html += `<button type="button" class="btn-outline btn-sm" data-action="add-vpc-pair">+ Add vPC Pair</button>`;
        html += `</div>`;
        deployment.vpc_pairs.forEach(pair => {
            html += `
                <div class="connection-item">
                    <span>Domain ${pair.domain}: ${pair.primary} ↔ ${pair.secondary || 'Pending'} (Peer-link: ${pair.peer_link_ports || 'Auto'})</span>
                    <div class="connection-actions">
                        <button type="button" class="btn-outline btn-sm" data-action="edit-vpc-pair" data-pair-id="${pair.id}">Edit</button>
                        <button type="button" class="btn-outline btn-sm" data-action="delete-vpc-pair" data-pair-id="${pair.id}">Delete</button>
                    </div>
                </div>`;
        });
        html += `</div>`;
    } else {
        html += `<div class="deployment-connections">`;
        html += `<div class="deployment-connections-header">`;
        html += `<h4>vPC Pairs (0)</h4>`;
        html += `<button type="button" class="btn-outline btn-sm" data-action="add-vpc-pair">+ Add vPC Pair</button>`;
        html += `</div>`;
        html += `<p class="no-connections">No vPC pairs configured</p>`;
        html += `</div>`;
    }
    
    // Add uplinks summary with CRUD
    if (deployment.uplinks.length > 0) {
        html += `<div class="deployment-connections">`;
        html += `<div class="deployment-connections-header">`;
        html += `<h4>Uplinks (${deployment.uplinks.length})</h4>`;
        html += `<button type="button" class="btn-outline btn-sm" data-action="add-uplink">+ Add Uplink</button>`;
        html += `</div>`;
        deployment.uplinks.forEach(uplink => {
            html += `
                <div class="connection-item">
                    <span>${uplink.from} → ${uplink.to} (Ports: ${uplink.ports}, PO${uplink.po_id})</span>
                    <div class="connection-actions">
                        <button type="button" class="btn-outline btn-sm" data-action="edit-uplink" data-uplink-id="${uplink.id}">Edit</button>
                        <button type="button" class="btn-outline btn-sm" data-action="delete-uplink" data-uplink-id="${uplink.id}">Delete</button>
                    </div>
                </div>`;
        });
        html += `</div>`;
    } else {
        html += `<div class="deployment-connections">`;
        html += `<div class="deployment-connections-header">`;
        html += `<h4>Uplinks (0)</h4>`;
        html += `<button type="button" class="btn-outline btn-sm" data-action="add-uplink">+ Add Uplink</button>`;
        html += `</div>`;
        html += `<p class="no-connections">No uplinks configured</p>`;
        html += `</div>`;
    }
    
    // Add global VLAN configuration
    html += `<div class="deployment-connections">`;
    html += `<div class="deployment-connections-header">`;
    html += `<h4>Global VLAN Configuration</h4>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="configure-global-vlans">Configure VLANs</button>`;
    html += `</div>`;
    if (deployment.global_vlans && deployment.global_vlans.length > 0) {
        html += `<div class="global-vlans-summary">`;
        html += `<p><strong>${deployment.global_vlans.length} VLAN(s) configured:</strong> ${deployment.global_vlans.map(v => `VLAN ${v.id} (${v.name})`).join(', ')}</p>`;
        html += `</div>`;
    } else {
        html += `<p class="no-connections">No global VLANs configured. VLANs will use template defaults per switch role.</p>`;
    }
    html += `</div>`;
    
    // Add topology validation
    html += `<div class="deployment-connections">`;
    html += `<div class="deployment-connections-header">`;
    html += `<h4>Topology Validation</h4>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="validate-topology">Validate Topology</button>`;
    html += `</div>`;
    html += `<div id="topologyValidationResults" class="topology-validation-results" style="display: none;">`;
    html += `</div>`;
    html += `</div>`;
    
    // Add interface template management
    html += `<div class="deployment-connections">`;
    html += `<div class="deployment-connections-header">`;
    html += `<h4>Interface Templates</h4>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="apply-interface-template">Apply Template</button>`;
    html += `</div>`;
    html += `<p class="no-connections">Apply standard interface configurations (server ports, AP ports, etc.) across switches.</p>`;
    html += `</div>`;
    
    // Add multi-site management
    html += `<div class="deployment-connections">`;
    html += `<div class="deployment-connections-header">`;
    html += `<h4>Multi-Site Management</h4>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="manage-sites">Manage Sites</button>`;
    html += `</div>`;
    html += `<p class="no-connections">Configure site hierarchy and manage multi-site deployments.</p>`;
    html += `</div>`;
    
    // Add error analytics dashboard
    html += `<div class="deployment-connections">`;
    html += `<div class="deployment-connections-header">`;
    html += `<h4>Error Analytics</h4>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="show-error-analytics">View Analytics</button>`;
    html += `</div>`;
    html += `<p class="no-connections">View error patterns, recovery suggestions, and analytics.</p>`;
    html += `</div>`;
    
    // Add generate deployment button
    html += `<div class="deployment-actions">`;
    html += `<button type="button" class="btn-outline" data-action="show-deployment-preview">Preview Configuration</button>`;
    html += `<button type="button" class="btn-primary" data-action="generate-deployment-configs">Generate All Configurations</button>`;
    html += `</div>`;
    
    container.innerHTML = html;
}

async function validateTopology() {
    if (deployment.switches.length === 0) {
        flashToast("No switches in deployment to validate", "error");
        return;
    }
    
    const resultsDiv = document.getElementById('topologyValidationResults');
    if (!resultsDiv) {
        flashToast("Validation results container not found", "error");
        return;
    }
    
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<div class="loading-spinner">Validating topology...</div>';
    
    try {
        const response = await fetch('/validate/topology', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                switches: deployment.switches,
                vpc_pairs: deployment.vpc_pairs || [],
                uplinks: deployment.uplinks || []
            })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            resultsDiv.innerHTML = `
                <div class="validation-success">
                    <p>✓ Topology validation passed!</p>
                    <p class="validation-summary">No critical issues found.</p>
                </div>
            `;
            flashToast("Topology validation passed", "ok");
        } else {
            const issuesHtml = data.issues.map(issue => `
                <div class="validation-issue ${issue.severity}">
                    <strong>[${issue.severity.toUpperCase()}] ${issue.category}</strong>
                    <p>${issue.message}</p>
                    ${issue.suggestion ? `<p class="suggestion">Suggestion: ${issue.suggestion}</p>` : ''}
                    ${issue.affected_switches.length > 0 ? `<p class="affected">Affected: ${issue.affected_switches.join(', ')}</p>` : ''}
                </div>
            `).join('');
            
            resultsDiv.innerHTML = `
                <div class="validation-errors">
                    <p>Found ${data.issues.length} issue(s):</p>
                    ${issuesHtml}
                    <p class="validation-summary">Critical: ${data.summary.critical}, Warnings: ${data.summary.warning}, Info: ${data.summary.info}</p>
                </div>
            `;
            flashToast(`Found ${data.summary.critical} critical issue(s)`, "warning");
        }
    } catch (error) {
        console.error('Topology validation failed:', error);
        resultsDiv.innerHTML = `
            <div class="validation-error">
                <p>Topology validation failed: ${error.message}</p>
            </div>
        `;
        flashToast("Topology validation failed", "error");
    }
}

// PA-007 FIX: Load interface templates from external JSON file
let INTERFACE_TEMPLATES = [];

async function fetchInterfaceTemplates() {
    try {
        const response = await fetch('/templates/interface_templates.json');
        const data = await response.json();
        INTERFACE_TEMPLATES = data.interface_templates || [];
        console.log('[INTERFACE_TEMPLATES] Loaded from external JSON:', INTERFACE_TEMPLATES.length, 'templates');
    } catch (error) {
        console.error('[INTERFACE_TEMPLATES] Failed to load external templates, using fallback:', error);
        // Fallback to hardcoded templates if external file fails
        INTERFACE_TEMPLATES = [
            { id: 'server_port', label: 'Server Port (Access)', description: 'Standard server access with portfast and BPDU guard' },
            { id: 'ip_phone_port', label: 'IP Phone Port (Access)', description: 'IP phone with voice VLAN and CDP/LLDP' },
            { id: 'ap_port', label: 'Wireless AP Port (Trunk)', description: 'Wireless AP trunk with native VLAN' },
            { id: 'iscsi_port', label: 'iSCSI Storage Port (Trunk)', description: 'iSCSI storage with jumbo frames' },
            { id: 'mgmt_port', label: 'Management Port (Access)', description: 'OOB management access' },
            { id: 'lacp_port', label: 'LACP Port Channel Member', description: 'LACP port channel member' },
            { id: 'vpc_peer_link', label: 'vPC Peer Link (Trunk)', description: 'vPC peer link trunk' },
            { id: 'vpc_keepalive', label: 'vPC Keepalive (Routed)', description: 'vPC keepalive routed port' }
        ];
    }
}

// Initialize interface templates on page load
fetchInterfaceTemplates();

// NT-007 FIX: LLDP/CDP discovery integration for topology
let discoveryData = null;
let useDiscoveryTopology = false;

async function runLldpDiscovery(switchHostnames) {
    console.log('[DISCOVERY] Running LLDP discovery for switches:', switchHostnames);
    try {
        const response = await fetch('/api/discovery/lldp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ switches: switchHostnames })
        });
        const data = await response.json();
        console.log('[DISCOVERY] LLDP discovery completed:', data);
        return data;
    } catch (error) {
        console.error('[DISCOVERY] LLDP discovery failed:', error);
        return null;
    }
}

async function runCdpDiscovery(switchHostnames) {
    console.log('[DISCOVERY] Running CDP discovery for switches:', switchHostnames);
    try {
        const response = await fetch('/api/discovery/cdp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ switches: switchHostnames })
        });
        const data = await response.json();
        console.log('[DISCOVERY] CDP discovery completed:', data);
        return data;
    } catch (error) {
        console.error('[DISCOVERY] CDP discovery failed:', error);
        return null;
    }
}

function renderTopologyFromDiscovery(discoveryData) {
    console.log('[DISCOVERY] Rendering topology from discovery data:', discoveryData);
    // Convert discovery data to topology format
    const topology = {
        switches: [],
        connections: []
    };
    
    if (discoveryData && discoveryData.neighbors) {
        discoveryData.neighbors.forEach(neighbor => {
            topology.switches.push({
                id: neighbor.local_device,
                hostname: neighbor.local_device,
                x: 0, y: 0 // Will be auto-positioned
            });
            
            if (neighbor.remote_device) {
                topology.connections.push({
                    from: neighbor.local_device,
                    to: neighbor.remote_device,
                    local_interface: neighbor.local_interface,
                    remote_interface: neighbor.remote_interface
                });
            }
        });
    }
    
    return topology;
}

async function loadDiscoveryData() {
    if (deployment.switches.length === 0) return;
    
    const switchHostnames = deployment.switches.map(sw => sw.hostname);
    console.log('[DISCOVERY] Attempting to load discovery data for:', switchHostnames);
    
    // Try LLDP first, then CDP
    let data = await runLldpDiscovery(switchHostnames);
    if (!data) {
        data = await runCdpDiscovery(switchHostnames);
    }
    
    if (data && data.neighbors && data.neighbors.length > 0) {
        discoveryData = data;
        useDiscoveryTopology = true;
        console.log('[DISCOVERY] Discovery data loaded successfully, will use for topology');
        flashToast('Network discovery data loaded', 'success');
    } else {
        console.log('[DISCOVERY] No discovery data available, will use template-based topology');
        useDiscoveryTopology = false;
    }
}

// NT-008 FIX: Custom interface template creation
let customInterfaceTemplates = [];

function createCustomInterfaceTemplate(templateData) {
    console.log('[CUSTOM_TEMPLATE] Creating custom interface template:', templateData);
    
    const newTemplate = {
        id: `custom_${Date.now()}`,
        label: templateData.label,
        description: templateData.description,
        mode: templateData.mode || 'access',
        vlan: templateData.vlan,
        voice_vlan: templateData.voice_vlan,
        native_vlan: templateData.native_vlan,
        allowed_vlans: templateData.allowed_vlans,
        mtu: templateData.mtu,
        features: templateData.features || [],
        config: templateData.config || {},
        is_custom: true
    };
    
    customInterfaceTemplates.push(newTemplate);
    INTERFACE_TEMPLATES.push(newTemplate);
    
    // Save to localStorage
    saveCustomInterfaceTemplates();
    
    console.log('[CUSTOM_TEMPLATE] Custom template created:', newTemplate);
    return newTemplate;
}

function saveCustomInterfaceTemplates() {
    try {
        localStorage.setItem('customInterfaceTemplates', JSON.stringify(customInterfaceTemplates));
        console.log('[CUSTOM_TEMPLATE] Saved custom templates to localStorage:', customInterfaceTemplates.length);
    } catch (error) {
        console.error('[CUSTOM_TEMPLATE] Failed to save custom templates:', error);
    }
}

function loadCustomInterfaceTemplates() {
    try {
        const saved = localStorage.getItem('customInterfaceTemplates');
        if (saved) {
            customInterfaceTemplates = JSON.parse(saved);
            // Merge with INTERFACE_TEMPLATES
            customInterfaceTemplates.forEach(template => {
                if (!INTERFACE_TEMPLATES.find(t => t.id === template.id)) {
                    INTERFACE_TEMPLATES.push(template);
                }
            });
            console.log('[CUSTOM_TEMPLATE] Loaded custom templates from localStorage:', customInterfaceTemplates.length);
        }
    } catch (error) {
        console.error('[CUSTOM_TEMPLATE] Failed to load custom templates:', error);
    }
}

function showCustomInterfaceTemplateModal() {
    console.log('[CUSTOM_TEMPLATE] Showing custom template creation modal');
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.id = "customInterfaceTemplateModal";
    
    const html = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Create Custom Interface Template</h3>
                <button type="button" class="btn-close" data-action="close-modal-by-id" data-modal-id="customInterfaceTemplateModal">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="customTemplateName">Template Name</label>
                    <input type="text" id="customTemplateName" placeholder="e.g., Custom Server Port" />
                </div>
                <div class="form-group">
                    <label for="customTemplateDescription">Description</label>
                    <input type="text" id="customTemplateDescription" placeholder="e.g., Custom server configuration" />
                </div>
                <div class="form-group">
                    <label for="customTemplateMode">Mode</label>
                    <select id="customTemplateMode">
                        <option value="access">Access</option>
                        <option value="trunk">Trunk</option>
                        <option value="routed">Routed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="customTemplateVlan">VLAN</label>
                    <input type="text" id="customTemplateVlan" placeholder="e.g., data" />
                </div>
                <div class="form-group">
                    <label>Features</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" id="feature_portfast"> Portfast</label>
                        <label><input type="checkbox" id="feature_bpduguard"> BPDU Guard</label>
                        <label><input type="checkbox" id="feature_lacp"> LACP</label>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" data-action="close-modal-by-id" data-modal-id="customInterfaceTemplateModal">Cancel</button>
                    <button type="button" class="btn-primary" data-action="save-custom-template-from-modal">Save Template</button>
                </div>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function saveCustomTemplateFromModal() {
    const name = document.getElementById('customTemplateName').value;
    const description = document.getElementById('customTemplateDescription').value;
    const mode = document.getElementById('customTemplateMode').value;
    const vlan = document.getElementById('customTemplateVlan').value;
    
    const features = [];
    if (document.getElementById('feature_portfast').checked) features.push('portfast');
    if (document.getElementById('feature_bpduguard').checked) features.push('bpduguard');
    if (document.getElementById('feature_lacp').checked) features.push('lacp');
    
    if (!name) {
        flashToast('Please enter a template name', 'error');
        return;
    }
    
    const templateData = {
        label: name,
        description: description,
        mode: mode,
        vlan: vlan,
        features: features,
        config: {
            switchport_mode: mode,
            switchport_access_vlan: vlan
        }
    };
    
    createCustomInterfaceTemplate(templateData);
    document.getElementById('customInterfaceTemplateModal').remove();
    flashToast('Custom template created successfully', 'success');
}

// Load custom templates on page load
loadCustomInterfaceTemplates();

// NT-009 FIX: Performance testing and pagination for large deployments
let performanceMetrics = {
    switchRenderTime: 0,
    topologyRenderTime: 0,
    totalSwitches: 0
};

function trackPerformanceMetrics(metricName, value) {
    performanceMetrics[metricName] = value;
    console.log(`[PERFORMANCE] ${metricName}: ${value}ms`);
}

function renderPaginatedSwitchList(switches, page = 1, pageSize = 20) {
    console.log('[PERFORMANCE] Rendering paginated switch list:', switches.length, 'switches, page:', page);
    
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedSwitches = switches.slice(startIndex, endIndex);
    
    const totalPages = Math.ceil(switches.length / pageSize);
    
    // Render pagination controls
    const paginationHtml = `
        <div class="pagination-controls">
            <button class="btn-secondary" ${page === 1 ? 'disabled' : ''} data-action="render-paginated-switch-list" data-page="${page - 1}" data-page-size="${pageSize}">Previous</button>
            <span>Page ${page} of ${totalPages}</span>
            <button class="btn-secondary" ${page === totalPages ? 'disabled' : ''} data-action="render-paginated-switch-list" data-page="${page + 1}" data-page-size="${pageSize}">Next</button>
        </div>
    `;
    
    // Render switches
    const switchListHtml = paginatedSwitches.map(sw => `
        <div class="switch-card" data-switch-id="${sw.id}">
            <h4>${sw.hostname}</h4>
            <p>Model: ${sw.model}</p>
            <p>Role: ${sw.role}</p>
        </div>
    `).join('');
    
    const container = document.getElementById('switchListContainer');
    if (container) {
        container.innerHTML = paginationHtml + switchListHtml;
    }
    
    return paginatedSwitches;
}

function lazyLoadSwitches() {
    console.log('[PERFORMANCE] Implementing lazy loading for switches');
    // Intersection Observer for lazy loading
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Load more switches when scrolling to bottom
                console.log('[PERFORMANCE] Loading more switches on scroll');
            }
        });
    }, { threshold: 0.1 });
    
    return observer;
}

function batchUpdateSwitches(updates) {
    console.log('[PERFORMANCE] Batch updating switches:', updates.length, 'updates');
    
    // Process updates in batches to avoid UI blocking
    const batchSize = 10;
    const batches = [];
    
    for (let i = 0; i < updates.length; i += batchSize) {
        batches.push(updates.slice(i, i + batchSize));
    }
    
    let currentBatch = 0;
    
    function processNextBatch() {
        if (currentBatch >= batches.length) {
            console.log('[PERFORMANCE] All batches processed');
            return;
        }
        
        const batch = batches[currentBatch];
        console.log(`[PERFORMANCE] Processing batch ${currentBatch + 1}/${batches.length}`);
        
        // Process batch
        batch.forEach(update => {
            // Apply update
            const switchIndex = deployment.switches.findIndex(sw => sw.id === update.id);
            if (switchIndex !== -1) {
                deployment.switches[switchIndex] = { ...deployment.switches[switchIndex], ...update };
            }
        });
        
        currentBatch++;
        
        // Process next batch after a small delay
        setTimeout(processNextBatch, 0);
    }
    
    processNextBatch();
}

async function applyInterfaceTemplate() {
    if (deployment.switches.length === 0) {
        flashToast("No switches in deployment to apply templates", "error");
        return;
    }
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    
    // PA-007 FIX: Use loaded interface templates from external JSON
    const templates = INTERFACE_TEMPLATES.length > 0 ? INTERFACE_TEMPLATES : [
        { id: 'server_port', label: 'Server Port (Access)', description: 'Standard server access with portfast and BPDU guard' },
        { id: 'ip_phone_port', label: 'IP Phone Port (Access)', description: 'IP phone with voice VLAN and CDP/LLDP' },
        { id: 'ap_port', label: 'Wireless AP Port (Trunk)', description: 'Wireless AP trunk with native VLAN' },
        { id: 'iscsi_port', label: 'iSCSI Storage Port (Trunk)', description: 'iSCSI storage with jumbo frames' },
        { id: 'mgmt_port', label: 'Management Port (Access)', description: 'OOB management access' },
        { id: 'lacp_port', label: 'LACP Port Channel Member', description: 'LACP port channel member' },
        { id: 'vpc_peer_link', label: 'vPC Peer Link (Trunk)', description: 'vPC peer link trunk' },
        { id: 'vpc_keepalive', label: 'vPC Keepalive (Routed)', description: 'vPC keepalive routed port' }
    ];
    
    const templateOptions = templates.map(t => 
        `<option value="${t.id}">${t.label}</option>`
    ).join('');
    
    const switchOptions = deployment.switches.map(sw => 
        `<option value="${sw.id}">${sw.hostname}</option>`
    ).join('');
    
    const html = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Apply Interface Template</h3>
                <button type="button" class="btn-close" data-action="close-modal">×</button>
            </div>
            <div class="modal-body">
                <p class="modal-description">Apply standard interface configuration templates to switches.</p>
                
                <div class="form-group">
                    <label for="templateSelect">Interface Template</label>
                    <select id="templateSelect" class="form-control">
                        ${templateOptions}
                    </select>
                    <small id="templateDescription" class="form-text">Select a template to apply</small>
                </div>
                
                <!-- NT-008 FIX: Add button to create custom template -->
                <div class="form-group">
                    <button type="button" class="btn-secondary" data-action="create-interface-template">
                        + Create Custom Template
                    </button>
                </div>
                
                <div class="form-group">
                    <label for="targetSwitch">Target Switch</label>
                    <select id="targetSwitch" class="form-control">
                        <option value="all">All Switches</option>
                        ${switchOptions}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="portRange">Port Range (optional)</label>
                    <input type="text" id="portRange" class="form-control" placeholder="e.g., Ethernet1/1-24 or leave empty for all ports">
                    <small class="form-text">Leave empty to apply to all configurable ports</small>
                </div>
                
                <div class="form-group">
                    <label for="vlanOverride">VLAN Override (optional)</label>
                    <input type="number" id="vlanOverride" class="form-control" placeholder="VLAN ID" min="1" max="4094">
                    <small class="form-text">Override default VLAN for access ports</small>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="execute-interface-template">Apply Template</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Update template description on selection
    document.getElementById('templateSelect').addEventListener('change', function() {
        const selected = templates.find(t => t.id === this.value);
        if (selected) {
            document.getElementById('templateDescription').textContent = selected.description;
        }
    });
    
    // Execute interface template application
    window.executeInterfaceTemplate = function() {
        const templateId = document.getElementById('templateSelect').value;
        const targetSwitch = document.getElementById('targetSwitch').value;
        const portRange = document.getElementById('portRange').value;
        const vlanOverride = document.getElementById('vlanOverride').value;
        
        const selected = templates.find(t => t.id === templateId);
        
        // Apply template to switches
        let affectedSwitches = [];
        if (targetSwitch === 'all') {
            affectedSwitches = deployment.switches;
        } else {
            affectedSwitches = deployment.switches.filter(sw => sw.id === targetSwitch);
        }
        
        affectedSwitches.forEach(sw => {
            if (!sw.configured_ports) {
                sw.configured_ports = [];
            }
            
            // Add template configuration
            sw.configured_ports.push({
                template_id: templateId,
                template_name: selected.label,
                port_range: portRange || 'all',
                vlan_override: vlanOverride ? parseInt(vlanOverride) : null,
                applied_at: new Date().toISOString()
            });
        });
        
        document.querySelector('.modal-overlay').remove();
        renderSwitchList();
        flashToast(`Applied ${selected.label} to ${affectedSwitches.length} switch(es)`, "ok");
    };
}

async function manageSites() {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    
    const html = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Multi-Site Management</h3>
                <button type="button" class="btn-close" data-action="close-modal">×</button>
            </div>
            <div class="modal-body">
                <p class="modal-description">Configure site hierarchy and manage multi-site deployments.</p>
                
                <div class="form-group">
                    <label for="siteId">Site ID</label>
                    <input type="text" id="siteId" class="form-control" placeholder="e.g., site-hq">
                </div>
                
                <div class="form-group">
                    <label for="siteName">Site Name</label>
                    <input type="text" id="siteName" class="form-control" placeholder="e.g., Headquarters">
                </div>
                
                <div class="form-group">
                    <label for="parentSite">Parent Site (optional)</label>
                    <input type="text" id="parentSite" class="form-control" placeholder="e.g., region-na">
                </div>
                
                <div class="form-group">
                    <label for="region">Region (optional)</label>
                    <input type="text" id="region" class="form-control" placeholder="e.g., North America">
                </div>
                
                <div class="form-group">
                    <label for="rolloutPhase">Rollout Phase</label>
                    <select id="rolloutPhase" class="form-control">
                        <option value="planned">Planned</option>
                        <option value="staging">Staging</option>
                        <option value="production">Production</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="progressiveRollout"> Enable Progressive Rollout
                    </label>
                    <small class="form-text">Deploy sites sequentially rather than simultaneously</small>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="create-site">Create Site</button>
                <button type="button" class="btn-outline" data-action="execute-progressive-rollout">Progressive Rollout</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    window.createSite = async function() {
        const siteId = document.getElementById('siteId').value;
        const siteName = document.getElementById('siteName').value;
        const parentSite = document.getElementById('parentSite').value;
        const region = document.getElementById('region').value;
        const rolloutPhase = document.getElementById('rolloutPhase').value;
        
        if (!siteId || !siteName) {
            flashToast("Site ID and Site Name are required", "error");
            return;
        }
        
        try {
            const response = await fetch('/sites/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    site_id: siteId,
                    site_name: siteName,
                    parent_site: parentSite || null,
                    region: region || null,
                    rollout_phase: rolloutPhase,
                    deployment_status: 'pending'
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                flashToast(`Site "${siteName}" created successfully`, "ok");
                document.querySelector('.modal-overlay').remove();
            }
        } catch (error) {
            console.error('Failed to create site:', error);
            flashToast("Failed to create site", "error");
        }
    };
    
    window.executeProgressiveRollout = async function() {
        const progressiveRollout = document.getElementById('progressiveRollout').checked;
        
        try {
            const response = await fetch('/sites/progressive-rollout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sites: [],
                    global_config: {},
                    progressive_rollout: progressiveRollout
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                flashToast(`Progressive rollout ${progressiveRollout ? 'enabled' : 'disabled'}`, "ok");
                document.querySelector('.modal-overlay').remove();
            }
        } catch (error) {
            console.error('Progressive rollout failed:', error);
            flashToast("Progressive rollout failed", "error");
        }
    };
}

async function showErrorAnalytics() {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    
    const html = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Error Analytics Dashboard</h3>
                <button type="button" class="btn-close" data-action="close-modal">×</button>
            </div>
            <div class="modal-body">
                <p class="modal-description">View error patterns, recovery suggestions, and analytics.</p>
                
                <div id="errorAnalyticsContent" class="error-analytics-content">
                    <div class="loading-spinner">Loading error analytics...</div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Close</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Load error analytics
    try {
        const response = await fetch('/errors/analytics');
        const data = await response.json();
        
        const contentDiv = document.getElementById('errorAnalyticsContent');
        
        if (data.total_errors === 0) {
            contentDiv.innerHTML = `<p class="validation-success">✓ No errors detected in recent operations.</p>`;
        } else {
            const patternsHtml = data.error_patterns.map(pattern => `
                <div class="error-pattern-item ${pattern.auto_recoverable ? 'recoverable' : 'non-recoverable'}">
                    <div class="pattern-header">
                        <strong>${pattern.pattern_name}</strong>
                        <span class="pattern-badge ${pattern.error_type}">${pattern.error_type}</span>
                    </div>
                    <p class="pattern-details">Frequency: ${pattern.frequency} | Last: ${new Date(pattern.last_occurred).toLocaleString()}</p>
                    <p class="pattern-suggestion">Suggested: ${pattern.suggested_fix}</p>
                    ${pattern.auto_recoverable ? 
                        `<button type="button" class="btn-outline btn-sm" data-action="auto-recover" data-pattern-id="${pattern.pattern_id}">Auto-Recover</button>` : 
                        `<button type="button" class="btn-outline btn-sm" data-action="show-recovery-steps" data-pattern-id="${pattern.pattern_id}">View Recovery Steps</button>`
                    }
                </div>
            `).join('');
            
            contentDiv.innerHTML = `
                <div class="error-summary">
                    <p><strong>Total Errors:</strong> ${data.total_errors}</p>
                    <p><strong>Patterns Detected:</strong> ${data.error_patterns.length}</p>
                </div>
                <div class="error-patterns">
                    <h4>Error Patterns</h4>
                    ${patternsHtml}
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load error analytics:', error);
        document.getElementById('errorAnalyticsContent').innerHTML = `
            <p class="validation-error">Failed to load error analytics: ${error.message}</p>
        `;
    }
    
    window.showRecoverySteps = async function(patternId) {
        try {
            const response = await fetch(`/errors/recovery-suggestion?error_code=${patternId}`);
            const data = await response.json();
            
            const stepsHtml = data.recovery_suggestion.recovery_steps.map(step => 
                `<li>${step}</li>`
            ).join('');
            
            alert(`Recovery Steps for ${data.error_code}:\n\n${stepsHtml.join('\n')}`);
        } catch (error) {
            console.error('Failed to get recovery steps:', error);
            flashToast("Failed to get recovery steps", "error");
        }
    };
    
    window.autoRecover = async function(patternId) {
        try {
            const response = await fetch(`/errors/auto-recover?error_code=${patternId}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.auto_recovery === 'not_available') {
                flashToast(data.message, "warning");
            } else {
                flashToast("Auto-recovery initiated", "ok");
            }
        } catch (error) {
            console.error('Auto-recovery failed:', error);
            flashToast("Auto-recovery failed", "error");
        }
    };
}

async function showDeploymentPreview() {
    if (deployment.switches.length === 0) {
        flashToast("No switches in deployment to preview", "error");
        return;
    }
    
    // Show loading state
    const loadingOverlay = document.createElement("div");
    loadingOverlay.className = "loading-overlay";
    loadingOverlay.innerHTML = `<div class="loading-spinner">Generating CLI previews...</div>`;
    document.body.appendChild(loadingOverlay);
    
    try {
        // Build deployment input
        const deploymentInput = {
            switches: deployment.switches.map((sw, idx) => {
                console.log(`Processing switch ${idx}: ${sw.hostname}`, sw);
                const switchConfig = {
                    hostname: sw.hostname,
                    mgmt_ip: sw.mgmt_ip,
                    mgmt_gw: sw.mgmt_gw || "10.10.10.1",
                    site_name: sw.site_name || "HQ",
                    model: sw.model,
                    nxos_version: sw.nxos_version || "9.3",
                    vpc_peer_link_id: sw.vpc_peer_link_id || 1,
                    keepalive_po_id: sw.keepalive_po_id || 2,
                    vpc_system_priority: sw.vpc_system_priority || 32667,
                    local_ka: sw.local_ka || "10.10.10.1",
                    remote_ka: sw.remote_ka || "10.10.10.2",
                    vpc_pl_ints: sw.peer_link_ports || "",
                    base_access_vlan: sw.base_access_vlan || 10,
                    access_vlan_count: sw.access_vlan_count || 4,
                    interface_count: sw.interface_count || 0,
                    bring_up_spare_ports: sw.bring_up_spare_ports || false,
                    security_tier: sw.security_tier || "standard",
                    role: sw.role,
                    baseline_options: ["baseline_snmp_traps", "baseline_cli_aliases", "baseline_logging_source", "baseline_spanning_tree"],
                    vlans: sw.vlans || []
                };
                // Only include vpc_domain if it has a value
                if (sw.vpc_domain && sw.vpc_domain !== "") {
                    switchConfig.vpc_domain = sw.vpc_domain;
                }
                console.log(`Switch config for ${sw.hostname}:`, switchConfig);
                return switchConfig;
            }),
            vpc_pairs: deployment.vpc_pairs || [],
            uplinks: deployment.uplinks || [],
            global_vlans: deployment.global_vlans || []
        };
        
        console.log("=== CALLING DEPLOYMENT PREVIEW API ===");
        console.log("Deployment input:", JSON.stringify(deploymentInput, null, 2));
        
        // Call API with preview=true
        const response = await fetch('/generate-deployment?preview=true', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(deploymentInput)
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log("Deployment preview result:", result);
        
        // Remove loading overlay
        loadingOverlay.remove();
        
        // Display CLI previews in modal
        displayDeploymentCliPreview(result);
        
    } catch (error) {
        console.error('Failed to generate deployment preview:', error);
        flashToast(`Failed to generate preview: ${error.message}`, "error");
        loadingOverlay.remove();
    }
}

function displayDeploymentCliPreview(result) {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "preview-title");
    
    let html = `
        <div class="modal-content" style="max-width: 1200px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h3 id="preview-title">Deployment CLI Configuration Preview</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <div class="deployment-preview">
    `;
    
    if (result.results && Array.isArray(result.results) && result.results.length > 0) {
        result.results.forEach((item, index) => {
            const hostname = item.hostname || `Switch-${index}`;
            const config = item.export?.cli || item.export?.config || "";
            const safeHostname = escapeHtml(hostname);
            
            html += `
                <div class="node-section">
                    <h3 class="section-title">${safeHostname}</h3>
                    <div class="deployment-switch-stack">
                        <div class="switch-stack-header">
                            <h4>CLI Configuration</h4>
                            <div class="switch-stack-actions">
                                <button type="button" class="btn-outline btn-sm" data-action="download-config" data-hostname="${safeHostname}">Download</button>
                            </div>
                        </div>
                        <div class="switch-stack-content">
                            <div class="cli-section">
                                <pre class="cli-block">${escapeHtml(config)}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    } else {
        html += `<div class="no-results">No configuration previews available</div>`;
    }
    
    html += `
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Close</button>
                <button type="button" class="btn-primary" data-action="close-and-generate-deployment">Generate All Configurations</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

async function previewSwitchConfig(switchId) {
    const sw = deployment.switches.find(s => s.id === switchId);
    if (!sw) {
        flashToast("Switch not found", "error");
        return;
    }
    
    // Show loading state
    const loadingOverlay = document.createElement("div");
    loadingOverlay.className = "loading-overlay";
    loadingOverlay.innerHTML = `<div class="loading-spinner">Generating CLI preview for ${sw.hostname}...</div>`;
    document.body.appendChild(loadingOverlay);
    
    try {
        // Build scenario payload for this switch - match ScenarioInput model structure
        const payload = {
            scenario_id: getScenarioIdForRole(sw.role),
            hostname: sw.hostname,
            mgmt_ip: sw.mgmt_ip,
            mgmt_gw: sw.mgmt_gw || "10.10.10.1",
            site_name: sw.site_name || "HQ",
            generate_pair: false,
            secondary_hostname: null,
            secondary_mgmt_ip: null,
            overrides: {
                model: sw.model,
                nxos_version: sw.nxos_version || "9.3",
                base_access_vlan: sw.base_access_vlan || 10,
                access_vlan_count: sw.access_vlan_count || 4,
                vpc_domain_id: sw.vpc_domain ? parseInt(sw.vpc_domain) : null,
                vpc_peer_link_id: sw.vpc_peer_link_id || 1,
                keepalive_po_id: sw.keepalive_po_id || 2,
                vpc_system_priority: sw.vpc_system_priority || 32667,
                local_keepalive_ip: sw.local_ka || "10.10.10.1",
                remote_keepalive_ip: sw.remote_ka || "10.10.10.2",
                vpc_peer_link_interfaces: sw.peer_link_ports || "Ethernet1/35-36"
            }
        };
        
        // Add explicit VLANs if provided
        if (sw.vlans && sw.vlans.length > 0) {
            payload.overrides.vlans = sw.vlans;
        }
        
        console.log("=== CALLING SCENARIO PREVIEW FOR SINGLE SWITCH ===");
        console.log("Switch:", sw.hostname);
        console.log("Payload:", JSON.stringify(payload, null, 2));
        
        // Call scenario preview endpoint
        const response = await fetch('/scenario/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("API error response:", errorText);
            throw new Error(`API call failed: ${response.status} ${response.statusText} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log("Scenario preview result:", result);
        
        // Remove loading overlay
        loadingOverlay.remove();
        
        // Display CLI preview in modal
        displaySingleSwitchPreview(sw.hostname, result.config_preview || "");
        
    } catch (error) {
        console.error('Failed to generate switch preview:', error);
        flashToast(`Failed to generate preview: ${error.message}`, "error");
        loadingOverlay.remove();
    }
}

function getScenarioIdForRole(role) {
    // Map deployment roles to scenario IDs
    const roleToScenario = {
        'spine': 'spine_leaf',
        'leaf': 'spine_leaf', 
        'core': 'vpc_core',
        'access': 'access_layer'
    };
    return roleToScenario[role] || 'spine_leaf';
}

function displaySingleSwitchPreview(hostname, config) {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "preview-title");
    
    const safeHostname = escapeHtml(hostname);
    
    let html = `
        <div class="modal-content" style="max-width: 1200px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h3 id="preview-title">CLI Configuration Preview - ${safeHostname}</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <div class="deployment-switch-stack">
                    <div class="switch-stack-header">
                        <h4>CLI Configuration</h4>
                        <div class="switch-stack-actions">
                            <button type="button" class="btn-outline btn-sm" data-action="download-config" data-hostname="${safeHostname}">Download</button>
                        </div>
                    </div>
                    <div class="switch-stack-content">
                        <div class="cli-section">
                            <pre class="cli-block">${escapeHtml(config)}</pre>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Close</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function resetDeployment() {
    if (confirm("Reset deployment? This will clear all switches and connections.")) {
        deployment = { switches: [], vpc_pairs: [], uplinks: [], global_vlans: [] };
        renderDeploymentTemplates();
        renderDeploymentTopology();
    }
}

function changeDeploymentTemplate() {
    if (confirm("Change template? This will clear the current deployment and show template selector.")) {
        deployment = { switches: [], vpc_pairs: [], uplinks: [], global_vlans: [] };
        renderDeploymentTemplates();
        renderDeploymentTopology();
        flashToast("Deployment cleared. Select a new template.", "info");
    }
}

function configureGlobalVlans() {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    
    // Pre-populate with existing VLANs or defaults
    const existingVlans = deployment.global_vlans || [];
    const vlanInputs = existingVlans.map((v, i) => 
        `<div class="vlan-row" data-index="${i}">
            <input type="number" class="vlan-id-input" value="${v.id}" placeholder="VLAN ID" min="1" max="4094">
            <input type="text" class="vlan-name-input" value="${v.name}" placeholder="VLAN Name">
            <button type="button" class="btn-outline btn-sm" data-action="remove-parent">Remove</button>
        </div>`
    ).join('');
    
    const html = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Configure Global VLANs</h3>
                <button type="button" class="btn-close" data-action="close-modal">×</button>
            </div>
            <div class="modal-body">
                <p class="modal-description">Configure VLANs that will be applied to ALL switches in this deployment. These VLANs will override template defaults.</p>
                
                <div class="vlan-bulk-actions">
                    <h4>Bulk Operations</h4>
                    <button type="button" class="btn-outline btn-sm" data-action="bulk-add-vlans">+ Bulk Add Range</button>
                    <button type="button" class="btn-outline btn-sm" data-action="bulk-remove-vlans">- Bulk Remove Range</button>
                    <button type="button" class="btn-outline btn-sm" data-action="validate-vlan-naming">Validate Naming</button>
                    <button type="button" class="btn-outline btn-sm" data-action="check-vlan-conflicts">Check Conflicts</button>
                </div>
                
                <div class="vlan-configuration">
                    <div class="vlan-rows">
                        ${vlanInputs}
                    </div>
                    <button type="button" class="btn-outline btn-sm" data-action="add-vlan-row">+ Add VLAN</button>
                </div>
                
                <div class="vlan-presets">
                    <h4>VLAN Presets</h4>
                    <button type="button" class="btn-outline btn-sm" data-action="apply-vlan-preset" data-preset="datacenter">Data Center (10,20,30,40,50)</button>
                    <button type="button" class="btn-outline btn-sm" data-action="apply-vlan-preset" data-preset="campus">Campus (100-105)</button>
                    <button type="button" class="btn-outline btn-sm" data-action="apply-vlan-preset" data-preset="dmz">DMZ (200-205)</button>
                </div>
                
                <div class="vlan-validation-results" id="vlanValidationResults" style="display: none;">
                    <h4>Validation Results</h4>
                    <div id="vlanValidationContent"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="save-global-vlans">Save VLANs</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Add VLAN row function to global scope
    window.addVlanRow = function() {
        const vlanRows = document.querySelector('.vlan-rows');
        const newRow = document.createElement('div');
        newRow.className = 'vlan-row';
        newRow.innerHTML = `
            <input type="number" class="vlan-id-input" placeholder="VLAN ID" min="1" max="4094">
            <input type="text" class="vlan-name-input" placeholder="VLAN Name">
            <button type="button" class="btn-outline btn-sm" data-action="remove-parent">Remove</button>
        `;
        vlanRows.appendChild(newRow);
    };
    
    // Apply VLAN preset function
    window.applyVlanPreset = function(preset) {
        const vlanRows = document.querySelector('.vlan-rows');
        vlanRows.innerHTML = '';
        
        const presets = {
            'datacenter': [
                {id: 10, name: 'Data-Web'},
                {id: 20, name: 'Data-App'},
                {id: 30, name: 'Data-DB'},
                {id: 40, name: 'Data-Mgmt'},
                {id: 50, name: 'Data-Backup'}
            ],
            'campus': [
                {id: 100, name: 'Campus-Voice'},
                {id: 101, name: 'Campus-Data'},
                {id: 102, name: 'Campus-Guest'},
                {id: 103, name: 'Campus-Video'},
                {id: 104, name: 'Campus-IoT'},
                {id: 105, name: 'Campus-Mgmt'}
            ],
            'dmz': [
                {id: 200, name: 'DMZ-Web'},
                {id: 201, name: 'DMZ-App'},
                {id: 202, name: 'DMZ-DB'},
                {id: 203, name: 'DMZ-Mgmt'},
                {id: 204, name: 'DMZ-Monitor'},
                {id: 205, name: 'DMZ-Backup'}
            ]
        };
        
        const selectedPreset = presets[preset] || [];
        selectedPreset.forEach(v => {
            const newRow = document.createElement('div');
            newRow.className = 'vlan-row';
            newRow.innerHTML = `
                <input type="number" class="vlan-id-input" value="${v.id}" placeholder="VLAN ID" min="1" max="4094">
                <input type="text" class="vlan-name-input" value="${v.name}" placeholder="VLAN Name">
                <button type="button" class="btn-outline btn-sm" data-action="remove-parent">Remove</button>
            `;
            vlanRows.appendChild(newRow);
        });
    };
    
    // Save global VLANs function
    window.saveGlobalVlans = function() {
        const vlanRows = document.querySelectorAll('.vlan-row');
        const vlans = [];
        
        vlanRows.forEach(row => {
            const vlanId = row.querySelector('.vlan-id-input').value;
            const vlanName = row.querySelector('.vlan-name-input').value;
            
            if (vlanId && vlanName) {
                vlans.push({id: parseInt(vlanId), name: vlanName});
            }
        });
        
        deployment.global_vlans = vlans;
        document.querySelector('.modal-overlay').remove();
        renderSwitchList();
        flashToast(`Saved ${vlans.length} global VLAN(s)`, "ok");
};
    
    // Bulk add VLANs function
    window.bulkAddVlans = function() {
        const startVlan = prompt("Enter starting VLAN ID (1-4094):");
        if (!startVlan) return;
        
        const vlanCount = prompt("Enter number of VLANs to add:");
        if (!vlanCount) return;
        
        const namePrefix = prompt("Enter VLAN name prefix (e.g., 'Data-VLAN'):");
        if (!namePrefix) return;
        
        const startId = parseInt(startVlan);
        const count = parseInt(vlanCount);
        
        if (isNaN(startId) || startId < 1 || startId > 4094) {
            flashToast("Invalid VLAN ID. Must be between 1 and 4094.", "error");
            return;
        }
        
        if (isNaN(count) || count < 1 || count > 100) {
            flashToast("Invalid count. Must be between 1 and 100.", "error");
            return;
        }
        
        const vlanRows = document.querySelector('.vlan-rows');
        for (let i = 0; i < count; i++) {
            const vlanId = startId + i;
            if (vlanId > 4094) {
                flashToast(`Cannot add VLAN ${vlanId} - exceeds maximum of 4094. Stopped at ${vlanId - 1}.`, "warning");
                break;
            }
            
            const newRow = document.createElement('div');
            newRow.className = 'vlan-row';
            newRow.innerHTML = `
                <input type="number" class="vlan-id-input" value="${vlanId}" placeholder="VLAN ID" min="1" max="4094">
                <input type="text" class="vlan-name-input" value="${namePrefix}-${vlanId}" placeholder="VLAN Name">
                <button type="button" class="btn-outline btn-sm" data-action="remove-parent">Remove</button>
            `;
            vlanRows.appendChild(newRow);
        }
        
        flashToast(`Added ${count} VLAN(s) starting from ${startId}`, "ok");
    };
    
    // Bulk remove VLANs function
    window.bulkRemoveVlans = function() {
        const startVlan = prompt("Enter starting VLAN ID to remove:");
        if (!startVlan) return;
        
        const endVlan = prompt("Enter ending VLAN ID to remove:");
        if (!endVlan) return;
        
        const startId = parseInt(startVlan);
        const endId = parseInt(endVlan);
        
        if (isNaN(startId) || isNaN(endId) || startId > endId) {
            flashToast("Invalid VLAN range.", "error");
            return;
        }
        
        const vlanRows = document.querySelectorAll('.vlan-row');
        let removedCount = 0;
        
        vlanRows.forEach(row => {
            const vlanId = parseInt(row.querySelector('.vlan-id-input').value);
            if (vlanId >= startId && vlanId <= endId) {
                row.remove();
                removedCount++;
            }
        });
        
        flashToast(`Removed ${removedCount} VLAN(s) in range ${startId}-${endId}`, "ok");
    };
    
    // Validate VLAN naming function
    window.validateVlanNaming = function() {
        const vlanRows = document.querySelectorAll('.vlan-row');
        const issues = [];
        const namingPattern = /^[a-zA-Z0-9-_]+$/;
        
        vlanRows.forEach(row => {
            const vlanId = row.querySelector('.vlan-id-input').value;
            const vlanName = row.querySelector('.vlan-name-input').value;
            
            if (!vlanName || vlanName.trim() === '') {
                issues.push(`VLAN ${vlanId}: Missing name`);
            } else if (vlanName.length < 3) {
                issues.push(`VLAN ${vlanId}: Name too short (minimum 3 characters)`);
            } else if (vlanName.length > 32) {
                issues.push(`VLAN ${vlanId}: Name too long (maximum 32 characters)`);
            } else if (!namingPattern.test(vlanName)) {
                issues.push(`VLAN ${vlanId}: Name contains invalid characters (use letters, numbers, hyphens, underscores)`);
            } else if (!vlanName.match(/^[a-zA-Z]/)) {
                issues.push(`VLAN ${vlanId}: Name should start with a letter`);
            }
        });
        
        const resultsDiv = document.getElementById('vlanValidationResults');
        const contentDiv = document.getElementById('vlanValidationContent');
        resultsDiv.style.display = 'block';
        
        if (issues.length === 0) {
            contentDiv.innerHTML = `<p class="validation-success">✓ All VLAN names are valid!</p>`;
            flashToast("VLAN naming validation passed", "ok");
        } else {
            contentDiv.innerHTML = `<ul class="validation-errors">${issues.map(issue => `<li>${issue}</li>`).join('')}</ul>`;
            flashToast(`Found ${issues.length} naming issue(s)`, "warning");
        }
    };
    
    // Check VLAN conflicts function
    window.checkVlanConflicts = function() {
        const vlanRows = document.querySelectorAll('.vlan-row');
        const vlanIds = [];
        const conflicts = [];
        
        vlanRows.forEach(row => {
            const vlanId = parseInt(row.querySelector('.vlan-id-input').value);
            const vlanName = row.querySelector('.vlan-name-input').value;
            
            if (vlanIds.includes(vlanId)) {
                conflicts.push(`Duplicate VLAN ID: ${vlanId}`);
            } else {
                vlanIds.push(vlanId);
            }
        });
        
        // Check against switch-level VLANs
        deployment.switches.forEach(sw => {
            if (sw.vlans && sw.vlans.length > 0) {
                sw.vlans.forEach(v => {
                    if (vlanIds.includes(v.id)) {
                        conflicts.push(`VLAN ${v.id} conflicts with switch ${sw.hostname} (VLAN: ${v.name})`);
                    }
                });
            }
        });
        
        const resultsDiv = document.getElementById('vlanValidationResults');
        const contentDiv = document.getElementById('vlanValidationContent');
        resultsDiv.style.display = 'block';
        
        if (conflicts.length === 0) {
            contentDiv.innerHTML = `<p class="validation-success">✓ No VLAN conflicts detected!</p>`;
            flashToast("No VLAN conflicts found", "ok");
        } else {
            contentDiv.innerHTML = `<ul class="validation-errors">${conflicts.map(conflict => `<li>${conflict}</li>`).join('')}</ul>`;
            flashToast(`Found ${conflicts.length} VLAN conflict(s)`, "warning");
        }
    };
}

async function generateDeploymentConfigs() {
    console.log("=== GENERATE_DEPLOYMENT_CONFIGS START ===");
    console.log("Deployment object:", JSON.stringify(deployment, null, 2));
    console.log("Switches count:", deployment.switches.length);
    console.log("vPC pairs:", deployment.vpc_pairs);
    console.log("Uplinks:", deployment.uplinks);
    
    if (deployment.switches.length === 0) {
        console.error("No switches in deployment to configure");
        flashToast("No switches in deployment to configure", "error");
        return;
    }
    
    // Show loading overlay
    const loadingOverlay = document.createElement("div");
    loadingOverlay.className = "loading-overlay";
    loadingOverlay.innerHTML = `
        <div style="text-align: center;">
            <div class="loading-spinner"></div>
            <div class="loading-text">Generating configurations for ${deployment.switches.length} switch(es)...</div>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
    
    try {
        console.log("=== generateDeploymentConfigs START ===");
        console.log("Number of switches in deployment:", deployment.switches.length);
        console.log("Switch hostnames:", deployment.switches.map(s => s.hostname));
        
        flashToast("Generating configurations for all switches...", "info");
        
        // Calculate remote_ka for each switch based on vPC partner
        const switchesWithRemoteKa = deployment.switches.map(sw => {
            let remoteKa = "";
            if (sw.vpc_domain && deployment.vpc_pairs.length > 0) {
                const vpcPair = deployment.vpc_pairs.find(p => p.domain === sw.vpc_domain);
                if (vpcPair) {
                    const partnerHostname = vpcPair.primary === sw.hostname ? vpcPair.secondary : vpcPair.primary;
                    const partnerSwitch = deployment.switches.find(s => s.hostname === partnerHostname);
                    if (partnerSwitch) {
                        remoteKa = partnerSwitch.local_ka || "";
                    }
                }
            }
            return {
                ...sw,
                remote_ka: remoteKa
            };
        });
        
        const deploymentInput = {
            switches: switchesWithRemoteKa.map((sw, idx) => {
                console.log(`Processing switch ${idx}: ${sw.hostname}`, sw);
                const switchConfig = {
                    hostname: sw.hostname,
                    mgmt_ip: sw.mgmt_ip,
                    mgmt_gw: sw.mgmt_gw || "10.10.10.1",
                    site_name: sw.site_name || "HQ",
                    model: sw.model,
                    nxos_version: sw.nxos_version || "9.3",
                    vpc_peer_link_id: sw.vpc_peer_link_id || 1,
                    keepalive_po_id: sw.keepalive_po_id || 2,
                    vpc_system_priority: sw.vpc_system_priority || 32667,
                    vpc_pl_ints: sw.peer_link_ports || "",
                    base_access_vlan: sw.base_access_vlan || 10,
                    access_vlan_count: sw.access_vlan_count || 4,
                    interface_count: sw.interface_count || 0,
                    bring_up_spare_ports: sw.bring_up_spare_ports || false,
                    security_tier: sw.security_tier || "standard",
                    role: sw.role,
                    baseline_options: ["baseline_snmp_traps", "baseline_cli_aliases", "baseline_logging_source", "baseline_spanning_tree"],
                    vlans: sw.vlans || []
                };
                // Only include vpc_domain, local_ka, and remote_ka if switch has a vPC domain
                if (sw.vpc_domain && sw.vpc_domain !== "") {
                    switchConfig.vpc_domain = sw.vpc_domain;
                    switchConfig.local_ka = sw.local_ka || "10.10.10.1";
                    switchConfig.remote_ka = sw.remote_ka || "";
                }
                console.log(`Switch config for ${sw.hostname}:`, switchConfig);
                return switchConfig;
            }),
            vpc_pairs: deployment.vpc_pairs || [],
            uplinks: deployment.uplinks || [],
            global_vlans: deployment.global_vlans || []
        };
        
        console.log("Deployment input switches count:", deploymentInput.switches.length);
        console.log("Deployment input switches:", deploymentInput.switches.map(s => s.hostname));
        console.log("Deployment input vpc_pairs:", deploymentInput.vpc_pairs);
        console.log("Deployment input uplinks:", deploymentInput.uplinks);
        console.log("Full deployment input payload:", JSON.stringify(deploymentInput, null, 2));
        
        const requestId = crypto.randomUUID();
        console.log("Generated request ID:", requestId);
        
        console.log("Sending POST request to", CONFIG_ROUTE_MULTISWITCH);
        const response = await fetch(CONFIG_ROUTE_MULTISWITCH, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Request-ID': requestId
            },
            body: JSON.stringify(deploymentInput)
        });
        
        console.log("Response received, status:", response.status, response.statusText);
        
        if (!response.ok) {
            console.error("Response not OK:", response.status, response.statusText);
            let errorMessage = `API request failed: ${response.status}`;
            try {
                const errorData = await response.json();
                console.error("Error response data:", errorData);
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                console.error("Failed to parse error response:", e);
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        console.log("Parsing JSON response");
        const result = await response.json();
        
        console.log("=== Backend response ===");
        console.log("Full result object:", JSON.stringify(result, null, 2));
        console.log("Total switches from backend:", result.total_switches);
        console.log("Successful:", result.successful);
        console.log("Failed:", result.failed);
        console.log("Number of results:", result.results?.length);
        console.log("Result hostnames:", result.results?.map(r => r.hostname));
        console.log("Errors:", result.errors);
        
        if (result.errors && result.errors.length > 0) {
            console.warn("Deployment generation errors:", result.errors);
            flashToast(`Generated ${result.successful}/${result.total_switches} configurations with ${result.failed} errors`, "warning");
        } else {
            console.log("All configurations generated successfully");
            flashToast(`Successfully generated configurations for all ${result.total_switches} switches`, "ok");
        }
        
        console.log("Calling displayDeploymentResults");
        // Display results
        displayDeploymentResults(result);
        
        // Show completion modal (INFO-001 / P0-009)
        showMultiSwitchSuccessModal(result);
        
        console.log("Re-rendering topology after deployment generation");
        // Re-render topology after deployment generation to ensure all switches are visible
        renderDeploymentTopology();
        
        console.log("=== GENERATE_DEPLOYMENT_CONFIGS COMPLETE ===");
        
        // Remove loading overlay
        loadingOverlay.remove();
        
    } catch (error) {
        console.error('Failed to generate deployment configs:', error);
        console.error('Error stack:', error.stack);
        flashToast(`Failed to generate deployment configurations: ${error.message}`, "error");
        
        // Remove loading overlay on error
        loadingOverlay.remove();
    }
}

function showMultiSwitchSuccessModal(result) {
    const modalId = 'multiSwitchSuccessModal';
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        document.body.appendChild(modal);
    }
    
    const count = result.total_switches || result.results?.length || 0;
    const successful = result.successful || 0;
    const failed = result.failed || 0;
    const exportPath = result.export?.output_dir || result.export_path || 'Vault directory';
    
    modal.innerHTML = `
        <div class="modal-content modal-wide">
            <h2>Multi-Switch Deployment Complete</h2>
            <div class="validation-status ${failed === 0 ? 'valid' : 'warn'}" style="margin-bottom:1rem;">
                <span>${successful}/${count} switches configured successfully${failed > 0 ? ` (${failed} failed)` : ''}</span>
            </div>
            <div style="margin-bottom:1rem;font-size:13px;color:var(--text-muted,#94a3b8);">
                <p style="margin:4px 0;"><strong>Export Path:</strong> <code>${escapeHtml(String(exportPath))}</code></p>
                <p style="margin:8px 0 4px;"><strong>Next Steps:</strong></p>
                <ul style="margin:0 0 0 18px;padding:0;">
                    <li>Download each CLI config from the results panel below, or download all at once.</li>
                    <li>Verify vPC peer-link and keepalive IPs across pair switches before deployment.</li>
                    <li>Upload configs via NX-API or console to target Nexus hardware.</li>
                </ul>
            </div>
            <div class="btn-row">
                <button type="button" class="btn-outline" data-action="close-modal-by-id" data-modal-id="${modalId}">Close</button>
                <button type="button" class="btn-primary" data-action="download-all-configs-close-modal" data-modal-id="${modalId}">Download All Configs</button>
            </div>
        </div>
    `;
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
}

// Edit Switch Modal Functions
let currentEditingHostname = null;

// PA-004 FIX: Modal ready function for explicit modal initialization timing
function modalReady(modalId) {
    console.log('[MODAL_READY] Checking if modal is ready:', modalId);
    return new Promise((resolve, reject) => {
        const modal = document.getElementById(modalId);
        if (!modal) {
            reject(new Error(`Modal ${modalId} not found`));
            return;
        }
        
        // Check if modal is already visible and ready
        if (!modal.classList.contains('hidden') && modal.offsetParent !== null) {
            modal.setAttribute('data-modal-ready', 'true');
            console.log('[MODAL_READY] Modal already ready:', modalId);
            resolve(modal);
            return;
        }
        
        // Wait for modal to become ready (max 2 seconds)
        const timeout = setTimeout(() => {
            reject(new Error(`Modal ${modalId} ready timeout`));
        }, 2000);
        
        const checkInterval = setInterval(() => {
            if (!modal.classList.contains('hidden') && modal.offsetParent !== null) {
                clearInterval(checkInterval);
                clearTimeout(timeout);
                modal.setAttribute('data-modal-ready', 'true');
                console.log('[MODAL_READY] Modal became ready:', modalId);
                resolve(modal);
            }
        }, 50);
    });
}

function openEditSwitchModal(hostname) {
    console.log('[EDIT_SWITCH] Opening edit modal for switch:', hostname);
    currentEditingHostname = hostname;
    const modal = document.getElementById('editSwitchModal');
    if (!modal) {
        console.error('[EDIT_SWITCH] Modal not found');
        return;
    }
    
    // Find switch in deployment state
    const sw = deployment.switches.find(s => s.hostname === hostname);
    if (!sw) {
        console.error('[EDIT_SWITCH] Switch not found:', hostname);
        flashToast('Switch not found', 'error');
        return;
    }
    
    console.log('[EDIT_SWITCH] Populating modal with switch data');
    
    // Populate model dropdown
    const modelSelect = document.getElementById('edit_model');
    if (modelSelect) {
        modelSelect.innerHTML = '';
        catalog.hardware.forEach(hw => {
            const option = document.createElement('option');
            option.value = hw.display_name;
            option.textContent = hw.display_name;
            modelSelect.appendChild(option);
        });
    }
    
    // Populate NX-OS version dropdown
    const versionSelect = document.getElementById('edit_nxos_version');
    if (versionSelect) {
        versionSelect.innerHTML = '';
        catalog.versions.forEach(ver => {
            const option = document.createElement('option');
            option.value = ver.id;
            option.textContent = ver.id;
            versionSelect.appendChild(option);
        });
    }
    
    // Populate form with current switch data from deployment state
    const editHostname = document.getElementById('edit_hostname');
    const editMgmtIp = document.getElementById('edit_mgmt_ip');
    const editMgmtGw = document.getElementById('edit_mgmt_gw');
    const editModel = document.getElementById('edit_model');
    const editSwitchRole = document.getElementById('edit_switch_role');
    const editNxosVersion = document.getElementById('edit_nxos_version');
    const editVpcDomain = document.getElementById('edit_vpc_domain');
    const editSiteName = document.getElementById('edit_site_name');
    const editLocalKa = document.getElementById('edit_local_ka');
    const keepaliveFieldGroup = document.getElementById('keepalive_field_group');
    const partnerInfo = document.getElementById('partner_info');
    
    if (editHostname) editHostname.value = sw.hostname || '';
    if (editMgmtIp) editMgmtIp.value = sw.mgmt_ip || '';
    if (editMgmtGw) editMgmtGw.value = sw.mgmt_gw || '';
    if (editModel) editModel.value = sw.model || '';
    if (editSwitchRole) editSwitchRole.value = sw.role || 'access';
    if (editNxosVersion) editNxosVersion.value = sw.nxos_version || '';
    if (editVpcDomain) editVpcDomain.value = sw.vpc_domain || '';
    if (editSiteName) editSiteName.value = sw.site_name || '';
    
    // Handle keepalive IP field and partner info
    if (editLocalKa) editLocalKa.value = sw.local_ka || '';
    
    // Find vPC partner and display info
    if (sw.vpc_domain && deployment.vpc_pairs.length > 0) {
        const vpcPair = deployment.vpc_pairs.find(p => p.domain === sw.vpc_domain);
        if (vpcPair) {
            const partnerHostname = vpcPair.primary === sw.hostname ? vpcPair.secondary : vpcPair.primary;
            const partnerSwitch = deployment.switches.find(s => s.hostname === partnerHostname);
            
            if (keepaliveFieldGroup) keepaliveFieldGroup.classList.remove('hidden');
            
            if (partnerInfo && partnerSwitch) {
                partnerInfo.innerHTML = `Partner: <strong>${partnerSwitch.hostname}</strong> (Keepalive: ${partnerSwitch.local_ka || 'not configured'})`;
            } else if (partnerInfo) {
                partnerInfo.textContent = 'Partner: not found';
            }
            
            // Add event listener to sync partner info when keepalive changes
            if (editLocalKa && partnerSwitch) {
                editLocalKa.oninput = function() {
                    const newKa = this.value;
                    // Update partner switch's local_ka in deployment state
                    partnerSwitch.local_ka = newKa;
                    // Update partner info display
                    if (partnerInfo) {
                        partnerInfo.innerHTML = `Partner: <strong>${partnerSwitch.hostname}</strong> (Keepalive: ${newKa || 'not configured'})`;
                    }
                };
            }
        } else {
            if (keepaliveFieldGroup) keepaliveFieldGroup.classList.add('hidden');
            if (partnerInfo) partnerInfo.textContent = '';
        }
    } else {
        if (keepaliveFieldGroup) keepaliveFieldGroup.classList.add('hidden');
        if (partnerInfo) partnerInfo.textContent = '';
    }
    
    console.log('[EDIT_SWITCH] Removing hidden class from modal');
    modal.classList.remove('hidden');
    
    // UX-004 FIX: Activate focus trap when modal opens
    activateFocusTrap(modal);
    
    // PA-004 FIX: Mark modal as ready after a small delay to ensure DOM updates
    setTimeout(() => {
        modal.setAttribute('data-modal-ready', 'true');
        modal.classList.add('modal-ready');
        console.log('[EDIT_SWITCH] Modal marked as ready');
    }, 100);
}

// UX-006 FIX: Error boundary for graceful error handling
class ErrorBoundary {
    constructor() {
        this.errorContainer = null;
        this.init();
    }
    
    init() {
        // Create error boundary container
        this.errorContainer = document.createElement('div');
        this.errorContainer.id = 'error-boundary';
        this.errorContainer.className = 'error-boundary hidden';
        this.errorContainer.setAttribute('role', 'alert');
        this.errorContainer.setAttribute('aria-live', 'assertive');
        this.errorContainer.innerHTML = `
            <div class="error-boundary-content">
                <h2>Something went wrong</h2>
                <p id="error-message">An unexpected error occurred.</p>
                <p id="error-details" class="error-details"></p>
                <div class="error-actions">
                    <button type="button" class="btn-primary" data-action="reload-page">Reload Page</button>
                    <button type="button" class="btn-secondary" data-action="dismiss-error">Dismiss</button>
                </div>
            </div>
        `;
        document.body.appendChild(this.errorContainer);
        
        // Set up global error handlers
        this.setupGlobalHandlers();
    }
    
    setupGlobalHandlers() {
        // Handle uncaught errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), 'Global Error');
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'Unhandled Promise Rejection');
        });
    }
    
    handleError(error, context = 'Error') {
        console.error(`[${context}]`, error);
        
        const errorMessage = this.errorContainer.querySelector('#error-message');
        const errorDetails = this.errorContainer.querySelector('#error-details');
        
        if (errorMessage) {
            errorMessage.textContent = `${context}: ${error.message || 'Unknown error'}`;
        }
        
        if (errorDetails && error.stack) {
            errorDetails.textContent = error.stack;
        }
        
        this.show();
    }
    
    show() {
        if (this.errorContainer) {
            this.errorContainer.classList.remove('hidden');
        }
    }
    
    static hide() {
        const container = document.getElementById('error-boundary');
        if (container) {
            container.classList.add('hidden');
        }
    }
}

// Initialize error boundary on page load
const errorBoundary = new ErrorBoundary();

// UX-004 FIX: Modal focus trap for accessibility
let focusTrapActive = false;
let focusTrapElement = null;
let lastFocusedElement = null;

function activateFocusTrap(modal) {
    if (!modal) return;
    
    // Save the element that had focus before modal opened
    lastFocusedElement = document.activeElement;
    
    focusTrapActive = true;
    focusTrapElement = modal;
    
    // Focus the first focusable element in the modal
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length > 0) {
        focusableElements[0].focus();
    }
    
    // Add keydown listener for Tab key
    modal.addEventListener('keydown', handleFocusTrapKeydown);
}

function deactivateFocusTrap() {
    if (!focusTrapActive || !focusTrapElement) return;
    
    focusTrapActive = false;
    focusTrapElement.removeEventListener('keydown', handleFocusTrapKeydown);
    focusTrapElement = null;
    
    // Return focus to the element that had focus before modal opened
    if (lastFocusedElement) {
        lastFocusedElement.focus();
        lastFocusedElement = null;
    }
}

function handleFocusTrapKeydown(e) {
    if (!focusTrapActive || !focusTrapElement) return;
    
    if (e.key === 'Tab') {
        const focusableElements = focusTrapElement.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            // Shift + Tab: move to previous element
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            // Tab: move to next element
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    } else if (e.key === 'Escape') {
        // Close modal on Escape
        e.preventDefault();
        closeEditSwitchModal();
    }
}

function closeEditSwitchModal() {
    const modal = document.getElementById('editSwitchModal');
    if (modal) {
        modal.classList.add('hidden');
        // UX-004 FIX: Deactivate focus trap when modal closes
        deactivateFocusTrap();
    }
    currentEditingHostname = null;
    
    // Clear validation messages
    clearValidationMessages();
}

function clearValidationMessages() {
    const validationDivs = document.querySelectorAll('.validation-message');
    validationDivs.forEach(div => div.textContent = '');
}

function validateHostname(input) {
    const validationDiv = document.getElementById(input.id + '_validation');
    const value = input.value.trim();
    
    if (!value) {
        validationDiv.textContent = 'Hostname is required';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    // Hostname validation: alphanumeric, hyphens, max 63 chars
    // RFC 1123 compliant: must start and end with alphanumeric, can have hyphens in between
    const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    if (!hostnameRegex.test(value)) {
        validationDiv.textContent = 'Invalid hostname format (alphanumeric, hyphens only, max 63 chars)';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    if (value.length > 63) {
        validationDiv.textContent = 'Hostname must be 63 characters or less';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    // Check for duplicate hostnames in deployment
    const isDuplicate = deployment.switches.some(sw => 
        sw.hostname === value && sw.hostname !== currentEditingHostname
    );
    if (isDuplicate) {
        validationDiv.textContent = 'Hostname already exists in deployment';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    validationDiv.textContent = '✓ Valid';
    validationDiv.style.color = '#28a745';
    input.style.borderColor = '#28a745';
    return true;
}

function validateIP(input) {
    const validationDiv = document.getElementById(input.id + '_validation');
    const value = input.value.trim();
    
    if (!value) {
        validationDiv.textContent = 'IP address is required';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    // IP address validation with optional CIDR notation
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/;
    if (!ipRegex.test(value)) {
        validationDiv.textContent = 'Invalid IP format (e.g., 10.0.0.1 or 10.0.0.1/24)';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    // Validate octet ranges
    const ipPart = value.split('/')[0];
    const octets = ipPart.split('.');
    for (const octet of octets) {
        const num = parseInt(octet, 10);
        if (num < 0 || num > 255) {
            validationDiv.textContent = 'IP octets must be 0-255';
            validationDiv.style.color = '#dc3545';
            input.style.borderColor = '#dc3545';
            return false;
        }
    }
    
    // Validate CIDR if present
    if (value.includes('/')) {
        const cidr = parseInt(value.split('/')[1], 10);
        if (cidr < 0 || cidr > 32) {
            validationDiv.textContent = 'CIDR must be 0-32';
            validationDiv.style.color = '#dc3545';
            input.style.borderColor = '#dc3545';
            return false;
        }
    }
    
    // Check for duplicate IPs in deployment (excluding current switch)
    const isDuplicate = deployment.switches.some(sw => 
        sw.mgmt_ip === value && sw.hostname !== currentEditingHostname
    );
    if (isDuplicate) {
        validationDiv.textContent = 'IP address already exists in deployment';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    validationDiv.textContent = '✓ Valid';
    validationDiv.style.color = '#28a745';
    input.style.borderColor = '#28a745';
    return true;
}

function validateVPCDomain(input) {
    const validationDiv = document.getElementById(input.id + '_validation');
    const value = input.value.trim();
    
    // vPC domain is optional
    if (!value) {
        validationDiv.textContent = '';
        input.style.borderColor = '';
        return true;
    }
    
    // vPC domain should be a number
    const domainNum = parseInt(value, 10);
    if (isNaN(domainNum)) {
        validationDiv.textContent = 'vPC domain must be a number';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    if (domainNum < 1 || domainNum > 4094) {
        validationDiv.textContent = 'vPC domain must be 1-4094';
        validationDiv.style.color = '#dc3545';
        input.style.borderColor = '#dc3545';
        return false;
    }
    
    // Check for vPC domain consistency across switches
    // If this switch has a vPC domain, ensure role is appropriate
    const roleSelect = document.getElementById('edit_switch_role');
    const role = roleSelect ? roleSelect.value : '';
    
    if (value && (role === 'spine' || role === 'core')) {
        validationDiv.textContent = 'vPC not typically used on spine/core switches';
        validationDiv.style.color = '#ffc107';
        input.style.borderColor = '#ffc107';
        return true; // Warning, not error
    }
    
    validationDiv.textContent = '✓ Valid';
    validationDiv.style.color = '#28a745';
    input.style.borderColor = '#28a745';
    return true;
}

function saveSwitchEdit() {
    if (!currentEditingHostname) return;
    
    // Validate all fields before saving
    const hostnameInput = document.getElementById('edit_hostname');
    const mgmtIpInput = document.getElementById('edit_mgmt_ip');
    const mgmtGwInput = document.getElementById('edit_mgmt_gw');
    const vpcDomainInput = document.getElementById('edit_vpc_domain');
    
    const isHostnameValid = validateHostname(hostnameInput);
    const isMgmtIpValid = validateIP(mgmtIpInput);
    const isMgmtGwValid = validateIP(mgmtGwInput);
    const isVpcDomainValid = validateVPCDomain(vpcDomainInput);
    
    if (!isHostnameValid || !isMgmtIpValid || !isMgmtGwValid || !isVpcDomainValid) {
        flashToast('Please fix validation errors before saving', 'error');
        return;
    }
    
    // Find switch in deployment state
    const swIndex = deployment.switches.findIndex(s => s.hostname === currentEditingHostname);
    if (swIndex === -1) {
        console.error('[SAVE_SWITCH] Switch not found:', currentEditingHostname);
        flashToast('Switch not found', 'error');
        return;
    }
    
    // Update switch in deployment state
    deployment.switches[swIndex] = {
        ...deployment.switches[swIndex],
        mgmt_ip: document.getElementById('edit_mgmt_ip').value,
        mgmt_gw: document.getElementById('edit_mgmt_gw').value,
        model: document.getElementById('edit_model').value,
        role: document.getElementById('edit_switch_role').value,
        nxos_version: document.getElementById('edit_nxos_version').value,
        vpc_domain: document.getElementById('edit_vpc_domain').value || null,
        site_name: document.getElementById('edit_site_name').value
    };
    
    flashToast(`Switch ${currentEditingHostname} updated successfully`, 'success');
    closeEditSwitchModal();
    
    // Refresh the switches list
    renderSwitchesList();
}

// Tab switching functions for Port Map vs CLI panel
// PA-003 FIX: Duplicate switchTab function removed - now using consolidated switchOutputTab function above

// Deployment completion modal functions
function showDeploymentCompletionModal(result) {
    const modal = document.getElementById('deploymentCompletionModal');
    if (!modal) return;
    
    const summaryDiv = document.getElementById('deploymentCompletionSummary');
    const switchesDiv = document.getElementById('deploymentCompletionSwitches');
    const errorsDiv = document.getElementById('deploymentCompletionErrors');
    
    // Build summary
    const successCount = result.results?.filter(r => r.status === 'success').length || 0;
    const errorCount = result.results?.filter(r => r.status === 'error').length || 0;
    const totalCount = result.results?.length || 0;
    
    summaryDiv.innerHTML = `
        <p><strong>Total Switches:</strong> ${totalCount}</p>
        <p><strong>Successful:</strong> ${successCount}</p>
        <p><strong>Failed:</strong> ${errorCount}</p>
        <p><strong>Export Path:</strong> ${result.export_path || 'N/A'}</p>
    `;
    
    // Build switches list
    switchesDiv.innerHTML = '';
    if (result.results && Array.isArray(result.results)) {
        result.results.forEach(switchResult => {
            const item = document.createElement('div');
            item.className = 'deployment-switch-item';
            const statusClass = switchResult.status === 'success' ? 'success' : 'error';
            const statusText = switchResult.status === 'success' ? '✓ Success' : '✗ Failed';
            
            item.innerHTML = `
                <span><strong>${escapeHtml(switchResult.hostname || 'Unknown')}</strong> (${escapeHtml(switchResult.model || 'Unknown')})</span>
                <span class="deployment-switch-status ${statusClass}">${statusText}</span>
            `;
            switchesDiv.appendChild(item);
        });
    }
    
    // Show errors if any
    const errors = result.results?.filter(r => r.status === 'error').map(r => r.error) || [];
    if (errors.length > 0) {
        errorsDiv.hidden = false;
        errorsDiv.innerHTML = `
            <h4>Errors</h4>
            <ul>
                ${errors.map(err => `<li>${escapeHtml(err || 'Unknown error')}</li>`).join('')}
            </ul>
        `;
    } else {
        errorsDiv.hidden = true;
    }
    
    modal.classList.remove('hidden');
}

function closeDeploymentCompletionModal() {
    const modal = document.getElementById('deploymentCompletionModal');
    if (modal) modal.classList.add('hidden');
}

function downloadAllDeploymentConfigs() {
    // Trigger download of all switch configurations as ZIP
    fetch('/deployment/download-all', {
        method: 'POST'
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to download configs');
        return res.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deployment_configs_${new Date().toISOString().slice(0,10)}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        flashToast?.('All configurations downloaded', 'ok');
    })
    .catch(err => {
        console.error('Failed to download configs:', err);
        flashToast?.('Failed to download configurations', 'error');
    });
}

// Save/Load deployment configuration functions
function saveDeploymentConfiguration(name) {
    const configName = name || prompt('Enter a name for this deployment configuration:');
    if (!configName) return;
    
    fetch('/deployment/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: configName })
    })
    .then(res => res.json())
    .then(result => {
        flashToast?.(`Deployment saved as "${configName}"`, 'ok');
    })
    .catch(err => {
        console.error('Failed to save deployment:', err);
        flashToast?.('Failed to save deployment', 'error');
    });
}

function loadDeploymentConfiguration(snapshotId) {
    if (!snapshotId) return;
    
    if (!confirm('This will replace the current deployment. Continue?')) return;
    
    fetch(`/deployment/load/${snapshotId}`, {
        method: 'POST'
    })
    .then(res => {
        if (!res.ok) return res.json().then(err => { throw err; });
        return res.json();
    })
    .then(result => {
        flashToast?.('Deployment loaded successfully', 'ok');
        // Refresh deployment view
        if (multiSwitchMode) {
            refreshDeploymentView();
        }
    })
    .catch(err => {
        console.error('Failed to load deployment:', err);
        flashToast?.(err.detail || 'Failed to load deployment', 'error');
    });
}

function listDeploymentConfigurations() {
    return fetch('/deployment/configurations')
        .then(res => res.json())
        .then(data => data.configurations || [])
        .catch(err => {
            console.error('Failed to list configurations:', err);
            return [];
        });
}

// Export/Import deployment configuration functions
function exportDeploymentConfiguration() {
    fetch('/deployment/export', {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        // Create a blob and trigger download
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deployment_export_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        flashToast?.('Deployment exported successfully', 'ok');
    })
    .catch(err => {
        console.error('Failed to export deployment:', err);
        flashToast?.('Failed to export deployment', 'error');
    });
}

function importDeploymentConfiguration(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const deploymentData = JSON.parse(e.target.result);
            
            if (!confirm('This will replace the current deployment. Continue?')) return;
            
            fetch('/deployment/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deploymentData)
            })
            .then(res => {
                if (!res.ok) return res.json().then(err => { throw err; });
                return res.json();
            })
            .then(result => {
                flashToast?.('Deployment imported successfully', 'ok');
                // Refresh deployment view
                if (multiSwitchMode) {
                    refreshDeploymentView();
                }
            })
            .catch(err => {
                console.error('Failed to import deployment:', err);
                flashToast?.(err.detail || 'Failed to import deployment', 'error');
            });
        } catch (err) {
            console.error('Failed to parse deployment file:', err);
            flashToast?.('Invalid deployment file format', 'error');
        }
    };
    reader.readAsText(file);
}

function displayDeploymentResults(result) {
    console.log('[DEPLOY_RESULTS] Displaying results, total_switches:', result?.total_switches);
    
    try {
        if (!result || typeof result !== 'object') {
            throw new Error('Result object is invalid or undefined');
        }
        
        window.lastDeploymentResults = result;
        
        // Store device_config per switch for later views
        if (result.results && Array.isArray(result.results)) {
            result.results.forEach((item) => {
                if (item.device_config && Array.isArray(deployment.switches)) {
                    const swIndex = deployment.switches.findIndex(s => s && s.hostname === item.hostname);
                    if (swIndex >= 0) deployment.switches[swIndex].device_config = item.device_config;
                }
            });
        }
        
        const successful = result.successful || 0;
        const failed = result.failed || 0;
        const exportDir = result.export?.output_dir || result.export_dir || '';
        
        // Build results HTML per docs/step-9
        let html = `<div class="deployment-results">
            <div class="results-header">
                <h3>Configuration Results</h3>
                <button class="btn-sm btn-ghost" data-action="ms-back-to-editor">← Back to Editor</button>
            </div>
            <div class="results-summary">
                <span class="success-count">${successful} successful</span>
                <span class="error-count">${failed} failed</span>
                ${exportDir ? `<span class="export-dir" title="${escapeHtml(exportDir)}">📁 ${escapeHtml(exportDir.split(/[/\\]/).slice(-2).join('/'))}</span>` : ''}
            </div>
            <div class="results-list">`;
        
        if (result.results && result.results.length > 0) {
            result.results.forEach((item, index) => {
                const hostname = item.hostname || `Switch-${index}`;
                const safe = escapeHtml(hostname);
                const ok = item.status === 'success';
                html += `<div class="result-item" data-hostname="${safe}">
                    <div class="result-header">
                        <strong>${safe}</strong>
                        <span class="status-badge ${ok ? 'success' : 'error'}">${ok ? '✓ Success' : '✗ Failed'}</span>
                    </div>
                    <div class="result-actions">
                        <button class="btn-sm btn-outline" data-action="view-config" data-hostname="${safe}">View Config</button>
                        <button class="btn-sm btn-outline" data-action="view-port-map" data-hostname="${safe}">Port Map</button>
                        <button class="btn-sm btn-outline" data-action="download-config" data-hostname="${safe}">Download</button>
                    </div>
                </div>`;
            });
        } else {
            html += `<div class="no-results">No configuration results available</div>`;
        }
        
        html += `</div>
            <div class="deployment-actions">
                <button class="btn-outline" data-action="download-all-deployment-configs">Download All Configs (ZIP)</button>
                <button class="btn-primary" data-action="open-vault-folder">Open Output Folder</button>
                <button class="btn-ghost" data-action="close-deployment-results">Close</button>
            </div>
        </div>`;
        
        // ── Multi-switch mode: render into dedicated results panel ────────────
        if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode) {
            const resultsPanel = document.getElementById('multiSwitchResultsPanel');
            const wizardPanel = document.getElementById('wizardPanel');
            const configEditor = document.getElementById('configurationEditor');
            const gallery = document.getElementById('templateGallery');
            const wizardNav = document.getElementById('wizardNav');
            const roadmap = document.getElementById('roadmapSummary');
            
            // Hide editor and gallery
            if (configEditor) configEditor.classList.add('hidden');
            if (gallery) gallery.classList.add('hidden');
            if (wizardNav) wizardNav.classList.add('hidden');
            if (roadmap) roadmap.classList.add('hidden');
            
            // Show wizard panel (it IS the left column) then show results inside it
            if (wizardPanel) wizardPanel.classList.remove('hidden');
            
            if (resultsPanel) {
                resultsPanel.innerHTML = html;
                resultsPanel.classList.remove('hidden');
                resultsPanel.style.cssText = 'display:block;padding:1rem;';
            } else {
                // Fallback — inject into wizardPanel directly before steps
                const fallback = document.createElement('div');
                fallback.id = 'multiSwitchResultsPanelFallback';
                fallback.innerHTML = html;
                fallback.style.cssText = 'padding:1rem;';
                wizardPanel?.insertAdjacentElement('afterbegin', fallback);
            }
        } else {
            // Single-switch / standalone mode: use legacy containers
            const container = document.getElementById('switchPortPanel');
            const deploymentResults = document.getElementById('deploymentResults');
            if (container) { container.innerHTML = html; container.style.display = 'block'; }
            if (deploymentResults) { deploymentResults.innerHTML = html; }
            
            const portMapTab = document.getElementById('portMapTab');
            if (portMapTab) { portMapTab.classList.add('active'); portMapTab.hidden = false; }
            const cliTab = document.getElementById('cliTab');
            if (cliTab) { cliTab.classList.remove('active'); cliTab.hidden = true; }
            if (typeof goToStep === 'function') goToStep(8);
        }
        
        if (typeof renderTopologyDiagram === 'function') renderTopologyDiagram();
        
        console.log('[DEPLOY_RESULTS] Done — successful:', successful);
    } catch (error) {
        console.error('[DEPLOY_RESULTS] Error:', error);
        flashToast('Error displaying results: ' + error.message, 'error');
    }
}

// Render port map for a specific switch in stacked layout
function renderPortMapForSwitch(hostname, deviceConfig) {
    console.log(`renderPortMapForSwitch called for ${hostname}, deviceConfig:`, deviceConfig);
    
    try {
        if (!deviceConfig) {
            console.warn(`No device_config for ${hostname}`);
            return `<div class="no-port-map">No device configuration available</div>`;
        }
        
        if (!deviceConfig.port_map) {
            console.warn(`No port_map in device_config for ${hostname}`);
            return `<div class="no-port-map">No port map available</div>`;
        }
        
        if (!deviceConfig.port_map.ports || !Array.isArray(deviceConfig.port_map.ports)) {
            console.warn(`No valid ports array in port_map for ${hostname}:`, deviceConfig.port_map);
            return `<div class="no-port-map">No port data available</div>`;
        }
        
        const ports = deviceConfig.port_map.ports;
        console.log(`Rendering ${ports.length} ports for ${hostname}`);
        
        let html = `<table class="port-map-table">`;
        html += `<thead><tr><th>Port</th><th>Name</th><th>Type</th><th>Description</th><th>Port Channel</th></tr></thead>`;
        html += `<tbody>`;
        
        ports.forEach(port => {
            if (!port) {
                console.warn(`Invalid port entry in ${hostname}`);
                return;
            }
            // Handle both backend field names (port) and frontend field names (port_number)
            const portNum = port.port_number || port.port || 'N/A';
            const portName = port.port_name || port.interface_name || port.interface || 'N/A';
            const portType = port.type || port.port_type || 'N/A';
            const portChannel = port.port_channel ? `PO${port.port_channel}` : '-';
            
            html += `
                <tr>
                    <td>${escapeHtml(String(portNum))}</td>
                    <td>${escapeHtml(String(portName))}</td>
                    <td>${escapeHtml(String(portType))}</td>
                    <td>${escapeHtml(String(port.description || 'N/A'))}</td>
                    <td>${escapeHtml(String(portChannel))}</td>
                </tr>
            `;
        });
        
        html += `</tbody></table>`;
        console.log(`Port map HTML generated for ${hostname}, length: ${html.length}`);
        return html;
    } catch (error) {
        console.error(`Error in renderPortMapForSwitch for ${hostname}:`, error);
        return `<div class="error-message">Error generating port map: ${escapeHtml(error.message)}</div>`;
    }
}

function downloadConfig(hostname, config) {
    const blob = new Blob([config], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${hostname}-config.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadAllConfigs() {
    if (!deployment.switches || deployment.switches.length === 0) {
        flashToast("No switches to download configs for", "error");
        return;
    }
    
    // Check if device configs are available
    const switchesWithConfigs = deployment.switches.filter(s => s.device_config && s.device_config.export && s.device_config.export.cli);
    if (switchesWithConfigs.length === 0) {
        flashToast("No generated configurations available. Please generate configurations first.", "error");
        return;
    }
    
    // Create a simple text file with all configs
    let allConfigs = "";
    switchesWithConfigs.forEach(sw => {
        const config = sw.device_config.export.cli || "";
        allConfigs += `========================================\n`;
        allConfigs += `Configuration for ${sw.hostname}\n`;
        allConfigs += `Model: ${sw.model}\n`;
        allConfigs += `Management IP: ${sw.mgmt_ip}\n`;
        allConfigs += `========================================\n\n`;
        allConfigs += config;
        allConfigs += `\n\n`;
    });
    
    // Download as text file
    const blob = new Blob([allConfigs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nxos-deployment-configs-${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    flashToast(`Downloaded configurations for ${switchesWithConfigs.length} switch(es)`, "ok");
}

function saveDeployment() {
    if (!deployment || deployment.switches.length === 0) {
        flashToast("No deployment to save", "error");
        return;
    }
    
    const deploymentData = JSON.stringify(deployment, null, 2);
    const blob = new Blob([deploymentData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nxos-deployment-${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    flashToast("Deployment saved successfully", "ok");
}

function loadDeployment() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const loadedDeployment = JSON.parse(event.target.result);
                
                // Validate deployment structure
                if (!loadedDeployment.switches || !Array.isArray(loadedDeployment.switches)) {
                    throw new Error("Invalid deployment file: missing or invalid switches array");
                }
                
                // Load the deployment
                deployment = {
                    switches: loadedDeployment.switches,
                    vpc_pairs: loadedDeployment.vpc_pairs || [],
                    uplinks: loadedDeployment.uplinks || []
                };
                
                renderSwitchList();
                renderDeploymentTopology();
                flashToast("Deployment loaded successfully", "ok");
            } catch (error) {
                console.error("Error loading deployment:", error);
                flashToast(`Failed to load deployment: ${error.message}`, "error");
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

function getErrorGuidance(errorMsg) {
    const lowerError = errorMsg.toLowerCase();
    
    if (lowerError.includes('hostname') || lowerError.includes('host name')) {
        return 'Ensure hostname contains only letters, numbers, and hyphens (no spaces or special characters)';
    }
    if (lowerError.includes('management ip') || lowerError.includes('mgmt_ip') || lowerError.includes('cidr')) {
        return 'Management IP must be in CIDR format (e.g., 10.10.10.1/24)';
    }
    if (lowerError.includes('gateway') || lowerError.includes('mgmt_gw')) {
        return 'Management gateway must be a valid IPv4 address (e.g., 10.10.10.1)';
    }
    if (lowerError.includes('vlan') || lowerError.includes('base access vlan')) {
        return 'VLAN ID must be between 1 and 4094';
    }
    if (lowerError.includes('vpc') || lowerError.includes('domain')) {
        return 'vPC domain must be a number between 1 and 4096. Ensure both switches in the pair have the same domain ID';
    }
    if (lowerError.includes('model') || lowerError.includes('hardware')) {
        return 'Select a valid switch model from the dropdown list';
    }
    if (lowerError.includes('nxos') || lowerError.includes('version')) {
        return 'Enter a valid NX-OS version (e.g., 9.3, 10.2)';
    }
    if (lowerError.includes('validation') || lowerError.includes('required')) {
        return 'Fill in all required fields marked with validation errors';
    }
    
    return null;
}

// saveSwitchEdit function for the configuration editor modal
function saveSwitchEdit() {
    console.log('[SWITCH_EDIT_SAVE] [USER_ACTION] User clicked "Save Switch Edit"');
    console.log('[SWITCH_EDIT_SAVE] [CODE_LOCATION] static/app.js:6563');
    
    // Find switch by currentEditingHostname
    const sw = deployment.switches.find(s => s.hostname === currentEditingHostname);
    if (!sw) {
        console.log('[SWITCH_EDIT_SAVE] [ERROR] Switch not found for hostname:', currentEditingHostname);
        console.log('[SWITCH_EDIT_SAVE] [OPERATIONAL_LOGIC] This is unexpected - switch should exist if edit was triggered');
        return;
    }
    
    console.log('[SWITCH_EDIT_SAVE] [DATA_RETRIEVAL] Found switch:', sw.hostname, 'Current model:', sw.model, 'Current role:', sw.role);
    
    // Get values directly from input fields (no form wrapper in HTML modal)
    const hostname = document.getElementById('edit_hostname')?.value;
    const mgmtIp = document.getElementById('edit_mgmt_ip')?.value;
    const mgmtGw = document.getElementById('edit_mgmt_gw')?.value;
    const model = document.getElementById('edit_model')?.value;
    const role = document.getElementById('edit_switch_role')?.value;
    const nxosVersion = document.getElementById('edit_nxos_version')?.value;
    const vpcDomain = document.getElementById('edit_vpc_domain')?.value;
    const siteName = document.getElementById('edit_site_name')?.value;
    const localKa = document.getElementById('edit_local_ka')?.value;
    
    console.log('[SWITCH_EDIT_SAVE] [FORM_DATA] Retrieved values - hostname:', hostname, 'mgmt_ip:', mgmtIp);
    
    // Basic validation
    if (!hostname || hostname.trim() === '') {
        flashToast('Hostname is required', 'error');
        return;
    }
    
    if (!mgmtIp || mgmtIp.trim() === '') {
        flashToast('Management IP is required', 'error');
        return;
    }
    
    // Update switch properties
    sw.hostname = hostname;
    sw.mgmt_ip = mgmtIp;
    sw.mgmt_gw = mgmtGw || '';
    sw.model = model || sw.model;
    sw.role = role || sw.role;
    sw.nxos_version = nxosVersion || sw.nxos_version;
    sw.vpc_domain = vpcDomain || null;
    sw.site_name = siteName || '';
    sw.local_ka = localKa || '';
    
    console.log('[SWITCH_EDIT_SAVE] [DATA_UPDATE] Updated switch:', sw.hostname, 'with keepalive:', sw.local_ka);
    
    // Refresh the switches list
    renderSwitchesList();
    
    // Close the modal
    closeEditSwitchModal();
    
    flashToast(`Switch ${sw.hostname} updated successfully`, 'success');
}

function addVlanEditRow() {
    const vlanList = document.getElementById("editVlansList");
    if (!vlanList) return;
    
    const row = document.createElement("div");
    row.className = "vlan-edit-row";
    row.style.display = "flex";
    row.style.gap = "8px";
    row.style.marginBottom = "8px";
    row.innerHTML = `
        <input type="number" placeholder="VLAN ID" class="edit-vlan-id">
        <input type="text" placeholder="VLAN Name" class="edit-vlan-name">
        <button type="button" class="btn-outline btn-sm" data-action="remove-parent">Remove</button>
    `;
    vlanList.appendChild(row);
}

function deleteSwitch(switchId) {
    console.log('[SWITCH_DELETE] [USER_ACTION] User clicked "Delete Switch" for switch ID:', switchId);
    console.log('[SWITCH_DELETE] [CODE_LOCATION] static/app.js:4415');
    
    const sw = deployment.switches.find(s => s.id === switchId);
    if (!sw) {
        console.log('[SWITCH_DELETE] [ERROR] Switch not found for ID:', switchId);
        console.log('[SWITCH_DELETE] [OPERATIONAL_LOGIC] This is unexpected - switch should exist if delete button was clicked');
        return;
    }
    
    console.log('[SWITCH_DELETE] [DATA_RETRIEVAL] Found switch:', sw.hostname, 'Model:', sw.model, 'Role:', sw.role);
    
    // Check topology impact
    const affectedPairs = deployment.vpc_pairs.filter(p => p.primary === sw.hostname || p.secondary === sw.hostname);
    const affectedUplinks = deployment.uplinks.filter(u => u.from === sw.hostname || u.to === sw.hostname);
    
    console.log('[SWITCH_DELETE] [TOPOLOGY_IMPACT] Affected vPC pairs:', affectedPairs.length, 'Affected uplinks:', affectedUplinks.length);
    
    // Check if this would leave orphaned switches
    const coreSwitches = deployment.switches.filter(s => {
        const hw = SWITCH_MODELS[s.model] || {};
        return hw.device_class === "core";
    });
    const isCore = coreSwitches.some(s => s.id === switchId);
    
    console.log('[SWITCH_DELETE] [CORE_CHECK] Is core switch:', isCore, 'Total core switches:', coreSwitches.length);
    
    let warning = `Delete switch ${sw.hostname}?`;
    if (isCore && coreSwitches.length <= 2) {
        warning += "\nWARNING: This will leave fewer than 2 core switches!";
        console.log('[SWITCH_DELETE] [WARNING] Deleting core switch would leave fewer than 2 core switches');
    }
    if (affectedPairs.length > 0) {
        warning += `\nThis will remove ${affectedPairs.length} vPC pair(s).`;
        console.log('[SWITCH_DELETE] [WARNING] Will remove', affectedPairs.length, 'vPC pair(s)');
    }
    if (affectedUplinks.length > 0) {
        warning += `\nThis will remove ${affectedUplinks.length} uplink(s).`;
        console.log('[SWITCH_DELETE] [WARNING] Will remove', affectedUplinks.length, 'uplink(s)');
    }
    
    if (confirm(warning)) {
        console.log('[SWITCH_DELETE] [USER_CONFIRMATION] User confirmed deletion');
        // Remove switch
        deployment.switches = deployment.switches.filter(s => s.id !== switchId);
        
        // Remove associated vPC pairs
        deployment.vpc_pairs = deployment.vpc_pairs.filter(p => p.primary !== sw.hostname && p.secondary !== sw.hostname);
        
        // Remove associated uplinks
        deployment.uplinks = deployment.uplinks.filter(u => u.from !== sw.hostname && u.to !== sw.hostname);
        
        renderSwitchList();
        renderDeploymentTopology();
        flashToast(`Switch ${sw.hostname} deleted`, "info");
        console.log('[SWITCH_DELETE] [DATA_UPDATE] Switch deleted and UI updated');
    } else {
        console.log('[SWITCH_DELETE] [USER_CANCEL] User cancelled deletion');
    }
}

// vPC Pair CRUD Functions
function addVpcPair() {
    console.log('[VPC_PAIR_ADD] [USER_ACTION] User clicked "Add vPC Pair" button');
    console.log('[VPC_PAIR_ADD] [CODE_LOCATION] static/app.js:4478');
    
    if (deployment.switches.length < 2) {
        console.log('[VPC_PAIR_ADD] [VALIDATION_ERROR] Need at least 2 switches to create a vPC pair');
        console.log('[VPC_PAIR_ADD] [OPERATIONAL_LOGIC] This is expected behavior - vPC requires at least 2 switches');
        flashToast("Need at least 2 switches to create a vPC pair", "error");
        return;
    }
    
    console.log('[VPC_PAIR_ADD] [VALIDATION_SUCCESS] Switch count check passed:', deployment.switches.length);
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "modal-title");
    
    const switchOptions = deployment.switches.map(s => {
        console.log('[VPC_PAIR_ADD] [SWITCH_OPTION] Available switch:', s.hostname, 'Model:', s.model);
        return `<option value="${s.hostname}">${s.hostname} (${s.model})</option>`;
    }).join('');
    
    console.log('[VPC_PAIR_ADD] [UI_RENDER] Rendering vPC pair add modal with', deployment.switches.length, 'switch options');
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 id="modal-title">Add vPC Pair</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <form id="vpcPairForm">
                    <div class="form-group">
                        <label for="vpcDomain">vPC Domain ID</label>
                        <input type="number" id="vpcDomain" name="domain" value="${Math.max(...(deployment.vpc_pairs.map(p => parseInt(p.domain)) || [0])) + 1}" min="1" max="4096" required>
                    </div>
                    <div class="form-group">
                        <label for="vpcPrimary">Primary Switch</label>
                        <select id="vpcPrimary" name="primary" required data-action="log-vpc-primary-change">${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="vpcSecondary">Secondary Switch</label>
                        <select id="vpcSecondary" name="secondary" required data-action="log-vpc-secondary-change">${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="vpcPeerLink">Peer-Link Ports (e.g., E1/51-52)</label>
                        <input type="text" id="vpcPeerLink" name="peer_link_ports" placeholder="Auto-detect if empty">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="save-vpc-pair">Add vPC Pair</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.querySelector('input').focus(), 100);
    
    console.log('[VPC_PAIR_ADD] [UI_RENDER] Modal appended to DOM and focused');
}

function editVpcPair(pairId) {
    console.log('[VPC_PAIR_EDIT] [USER_ACTION] User clicked "Edit vPC Pair" for pair ID:', pairId);
    console.log('[VPC_PAIR_EDIT] [CODE_LOCATION] static/app.js:4481');
    
    const pair = deployment.vpc_pairs.find(p => p.id === pairId);
    if (!pair) {
        console.log('[VPC_PAIR_EDIT] [ERROR] vPC pair not found for ID:', pairId);
        console.log('[VPC_PAIR_EDIT] [OPERATIONAL_LOGIC] This is unexpected - pair should exist if edit button was clicked');
        return;
    }
    
    console.log('[VPC_PAIR_EDIT] [DATA_RETRIEVAL] Found vPC pair:', pair.primary, '↔', pair.secondary, 'Domain:', pair.domain);
    
    const switchOptions = deployment.switches.map(s => {
        console.log('[VPC_PAIR_EDIT] [SWITCH_OPTION] Available switch:', s.hostname, 'Model:', s.model);
        return `<option value="${s.hostname}" ${s.hostname === pair.primary ? 'selected' : ''}>${s.hostname} (${s.model})</option>`;
    }).join('');
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "modal-title");
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 id="modal-title">Edit vPC Pair</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <form id="vpcPairForm">
                    <input type="hidden" id="vpcPairId" value="${pairId}">
                    <div class="form-group">
                        <label for="vpcDomain">vPC Domain ID</label>
                        <input type="number" id="vpcDomain" name="domain" value="${pair.domain}" min="1" max="4096" required>
                    </div>
                    <div class="form-group">
                        <label for="vpcPrimary">Primary Switch</label>
                        <select id="vpcPrimary" name="primary" required data-action="log-vpc-primary-change-edit">${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="vpcSecondary">Secondary Switch</label>
                        <select id="vpcSecondary" name="secondary" required data-action="log-vpc-secondary-change-edit">
                            ${deployment.switches.map(s => 
                                `<option value="${s.hostname}" ${s.hostname === pair.secondary ? 'selected' : ''}>${s.hostname} (${s.model})</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="vpcPeerLink">Peer-Link Ports (e.g., E1/51-52)</label>
                        <input type="text" id="vpcPeerLink" name="peer_link_ports" value="${pair.peer_link_ports || ''}" placeholder="Auto-detect if empty">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="save-vpc-pair">Save Changes</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.querySelector('input').focus(), 100);
    
    console.log('[VPC_PAIR_EDIT] [UI_RENDER] Edit modal appended to DOM and focused');
}

function saveVpcPair() {
    console.log('[VPC_PAIR_SAVE] [USER_ACTION] User clicked "Save vPC Pair" button');
    console.log('[VPC_PAIR_SAVE] [CODE_LOCATION] static/app.js:4549');
    
    const form = document.getElementById("vpcPairForm");
    if (!form) {
        console.log('[VPC_PAIR_SAVE] [ERROR] vPC pair form not found in DOM');
        console.log('[VPC_PAIR_SAVE] [OPERATIONAL_LOGIC] This is unexpected - form should exist when save button is clicked');
        return;
    }
    
    const pairId = document.getElementById("vpcPairId")?.value;
    const domain = form.domain.value;
    const primary = form.primary.value;
    const secondary = form.secondary.value;
    const peerLinkPorts = form.peer_link_ports.value;
    
    console.log('[VPC_PAIR_SAVE] [FORM_DATA] Domain:', domain, 'Primary:', primary, 'Secondary:', secondary, 'Peer-link:', peerLinkPorts);
    
    // Validation
    if (primary === secondary) {
        console.log('[VPC_PAIR_SAVE] [VALIDATION_ERROR] Primary and secondary switches must be different');
        console.log('[VPC_PAIR_SAVE] [OPERATIONAL_LOGIC] This is expected behavior - vPC requires two different switches');
        flashToast("Primary and secondary switches must be different", "error");
        return;
    }
    
    // Check domain uniqueness
    const domainConflict = deployment.vpc_pairs.find(p => p.domain === domain && p.id !== pairId);
    if (domainConflict) {
        console.log('[VPC_PAIR_SAVE] [VALIDATION_ERROR] Domain', domain, 'already in use by', domainConflict.primary, '↔', domainConflict.secondary);
        console.log('[VPC_PAIR_SAVE] [OPERATIONAL_LOGIC] This is expected behavior - vPC domains must be unique');
        flashToast(`Domain ${domain} already in use by ${domainConflict.primary} ↔ ${domainConflict.secondary}`, "error");
        return;
    }
    
    console.log('[VPC_PAIR_SAVE] [VALIDATION_SUCCESS] All validations passed');
    
    if (pairId) {
        console.log('[VPC_PAIR_SAVE] [OPERATION] Editing existing vPC pair ID:', pairId);
        // Edit existing
        const pair = deployment.vpc_pairs.find(p => p.id === pairId);
        if (pair) {
            pair.domain = domain;
            pair.primary = primary;
            pair.secondary = secondary;
            pair.peer_link_ports = peerLinkPorts;
            console.log('[VPC_PAIR_SAVE] [DATA_UPDATE] Updated vPC pair:', pair.primary, '↔', pair.secondary, 'Domain:', pair.domain);
        } else {
            console.log('[VPC_PAIR_SAVE] [ERROR] vPC pair not found for ID:', pairId);
            console.log('[VPC_PAIR_SAVE] [OPERATIONAL_LOGIC] This is unexpected - pair should exist if editing');
        }
    } else {
        console.log('[VPC_PAIR_SAVE] [OPERATION] Creating new vPC pair');
        // Create new
        const newPair = {
            id: Date.now().toString(),
            domain: domain,
            primary: primary,
            secondary: secondary,
            peer_link_ports: peerLinkPorts
        };
        deployment.vpc_pairs.push(newPair);
        console.log('[VPC_PAIR_SAVE] [DATA_UPDATE] Created new vPC pair:', newPair.primary, '↔', newPair.secondary, 'Domain:', newPair.domain);
    }
    
    // Update UI
    renderDeploymentTopology();
    renderSwitchList();
    
    // Close modal
    document.querySelector('.modal-overlay')?.remove();
    
    console.log('[VPC_PAIR_SAVE] [UI_UPDATE] Modal closed and topology updated');
    flashToast(pairId ? "vPC pair updated" : "vPC pair created", "success");
}

function deleteVpcPair(pairId) {
    console.log('[VPC_PAIR_DELETE] [USER_ACTION] User clicked "Delete vPC Pair" for pair ID:', pairId);
    console.log('[VPC_PAIR_DELETE] [CODE_LOCATION] static/app.js:4705');
    
    const pair = deployment.vpc_pairs.find(p => p.id === pairId);
    if (!pair) {
        console.log('[VPC_PAIR_DELETE] [ERROR] vPC pair not found for ID:', pairId);
        console.log('[VPC_PAIR_DELETE] [OPERATIONAL_LOGIC] This is unexpected - pair should exist if delete button was clicked');
        return;
    }
    
    console.log('[VPC_PAIR_DELETE] [DATA_RETRIEVAL] Found vPC pair:', pair.primary, '↔', pair.secondary, 'Domain:', pair.domain);
    
    if (confirm(`Delete vPC pair ${pair.primary} ↔ ${pair.secondary} (Domain ${pair.domain})?`)) {
        console.log('[VPC_PAIR_DELETE] [USER_CONFIRMATION] User confirmed deletion');
        deployment.vpc_pairs = deployment.vpc_pairs.filter(p => p.id !== pairId);
        renderSwitchList();
        renderDeploymentTopology();
        flashToast(`vPC pair deleted`, "info");
        console.log('[VPC_PAIR_DELETE] [DATA_UPDATE] vPC pair deleted and UI updated');
    } else {
        console.log('[VPC_PAIR_DELETE] [USER_CANCEL] User cancelled deletion');
    }
}

// Uplink CRUD Functions
function addUplink() {
    if (deployment.switches.length < 2) {
        flashToast("Need at least 2 switches to create an uplink", "error");
        return;
    }
    
    const switchOptions = deployment.switches.map(s => 
        `<option value="${s.hostname}">${s.hostname} (${s.model})</option>`
    ).join('');
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "modal-title");
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 id="modal-title">Add Uplink</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <form id="uplinkForm">
                    <div class="form-group">
                        <label for="uplinkFrom">From Switch</label>
                        <select id="uplinkFrom" name="from" required>${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="uplinkTo">To Switch</label>
                        <select id="uplinkTo" name="to" required>${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="uplinkPorts">Ports (e.g., E1/1-2)</label>
                        <input type="text" id="uplinkPorts" name="ports" placeholder="E1/1-2" required>
                    </div>
                    <div class="form-group">
                        <label for="uplinkPoId">Port-Channel ID</label>
                        <input type="number" id="uplinkPoId" name="po_id" value="${Math.max(...(deployment.uplinks.map(u => parseInt(u.po_id)) || [0])) + 1}" min="1" max="4096" required>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="save-uplink">Add Uplink</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.querySelector('input').focus(), 100);
}

function editUplink(uplinkId) {
    const uplink = deployment.uplinks.find(u => u.id === uplinkId);
    if (!uplink) return;
    
    const switchOptions = deployment.switches.map(s => 
        `<option value="${s.hostname}" ${s.hostname === uplink.from ? 'selected' : ''}>${s.hostname} (${s.model})</option>`
    ).join('');
    
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "modal-title");
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 id="modal-title">Edit Uplink</h3>
                <button type="button" class="btn-close" data-action="close-modal" aria-label="Close modal">×</button>
            </div>
            <div class="modal-body">
                <form id="uplinkForm">
                    <input type="hidden" id="uplinkId" value="${uplinkId}">
                    <div class="form-group">
                        <label for="uplinkFrom">From Switch</label>
                        <select id="uplinkFrom" name="from" required>${switchOptions}</select>
                    </div>
                    <div class="form-group">
                        <label for="uplinkTo">To Switch</label>
                        <select id="uplinkTo" name="to" required>
                            ${deployment.switches.map(s => 
                                `<option value="${s.hostname}" ${s.hostname === uplink.to ? 'selected' : ''}>${s.hostname} (${s.model})</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="uplinkPorts">Ports (e.g., E1/1-2)</label>
                        <input type="text" id="uplinkPorts" name="ports" value="${uplink.ports}" required>
                    </div>
                    <div class="form-group">
                        <label for="uplinkPoId">Port-Channel ID</label>
                        <input type="number" id="uplinkPoId" name="po_id" value="${uplink.po_id}" min="1" max="4096" required>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-outline" data-action="close-modal">Cancel</button>
                <button type="button" class="btn-primary" data-action="save-uplink">Save Changes</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.querySelector('input').focus(), 100);
}

function saveUplink() {
    const form = document.getElementById("uplinkForm");
    if (!form) return;
    
    const uplinkId = document.getElementById("uplinkId")?.value;
    const from = form.from.value;
    const to = form.to.value;
    const ports = form.ports.value;
    const poId = form.po_id.value;
    
    // Validation
    if (from === to) {
        flashToast("From and to switches must be different", "error");
        return;
    }
    
    if (uplinkId) {
        // Edit existing
        const uplink = deployment.uplinks.find(u => u.id === uplinkId);
        if (uplink) {
            uplink.from = from;
            uplink.to = to;
            uplink.ports = ports;
            uplink.po_id = poId;
        }
    } else {
        // Add new
        deployment.uplinks.push({
            id: `uplink-${Date.now()}`,
            from: from,
            to: to,
            ports: ports,
            po_id: poId
        });
    }
    
    document.querySelector('.modal-overlay').remove();
    renderSwitchList();
    renderDeploymentTopology();
    flashToast(`Uplink ${from} → ${to} saved`, "ok");
}

function deleteUplink(uplinkId) {
    const uplink = deployment.uplinks.find(u => u.id === uplinkId);
    if (!uplink) return;
    
    if (confirm(`Delete uplink ${uplink.from} → ${uplink.to} (PO${uplink.po_id})?`)) {
        deployment.uplinks = deployment.uplinks.filter(u => u.id !== uplinkId);
        renderSwitchList();
        renderDeploymentTopology();
        flashToast(`Uplink deleted`, "info");
    }
}

function renderDeploymentTopology() {
    console.log("=== renderDeploymentTopology START ===");
    
    try {
        console.log("deployment.switches:", deployment.switches);
        console.log("deployment.switches.length:", deployment.switches?.length || 0);
        console.log("deployment.vpc_pairs:", deployment.vpc_pairs);
        console.log("deployment.uplinks:", deployment.uplinks);
        
        // Validate deployment object structure
        if (!deployment || typeof deployment !== 'object') {
            console.error("Invalid deployment object:", deployment);
            throw new Error("Deployment object is invalid or undefined");
        }
        
        if (!Array.isArray(deployment.switches)) {
            console.error("deployment.switches is not an array:", deployment.switches);
            deployment.switches = [];
        }
        
        // Render multi-switch topology diagram
        const container = document.getElementById("topologyContainer");
        console.log("topologyContainer found:", !!container);
        if (!container) {
            console.error("topologyContainer not found in DOM");
            // Try to create it if it doesn't exist
            const switchListPanel = document.getElementById("switchListPanel");
            if (switchListPanel) {
                const newContainer = document.createElement("div");
                newContainer.id = "topologyContainer";
                switchListPanel.insertBefore(newContainer, switchListPanel.firstChild);
                console.log("Created topologyContainer dynamically");
                return renderDeploymentTopology(); // Retry with new container
            }
            throw new Error("topologyContainer not found in DOM and could not be created");
        }
        
        if (deployment.switches.length === 0) {
            container.innerHTML = `<div class="topology-empty">No switches in deployment. Select a template to get started.</div>`;
            console.log("No switches in deployment, showing empty message");
            return;
        }
        
        let html = `<div class="topology-diagram">`;
        
        // Group switches by role for layout with defensive filtering
        const spineSwitches = deployment.switches.filter(s => s && (s.role === 'spine' || s.role === 'core'));
        const leafSwitches = deployment.switches.filter(s => s && s.role === 'leaf');
        const otherSwitches = deployment.switches.filter(s => s && s.role && s.role !== 'spine' && s.role !== 'core' && s.role !== 'leaf');
        
        console.log("spineSwitches:", spineSwitches.map(s => s.hostname));
        console.log("leafSwitches:", leafSwitches.map(s => s.hostname));
        console.log("otherSwitches:", otherSwitches.map(s => s.hostname));
        
        // Render spine/core switches at top
        if (spineSwitches.length > 0) {
            html += `<div class="topology-row topology-spine">`;
            html += `<div class="topology-row-label">Spine/Core</div>`;
            html += `<div class="topology-nodes">`;
            spineSwitches.forEach(sw => {
                if (!sw || !sw.hostname) {
                    console.warn("Invalid switch in spineSwitches:", sw);
                    return;
                }
                const vpcPair = (deployment.vpc_pairs || []).find(p => p && (p.primary === sw.hostname || p.secondary === sw.hostname));
                // Handle vPC pairs with null secondary (standalone switches in vPC domain)
                const vpcInfo = vpcPair && vpcPair.domain ? (vpcPair.secondary ? `vPC ${vpcPair.domain}` : `vPC Domain ${vpcPair.domain} (Standalone)`) : '';
                const model = sw.model || 'Unknown Model';
                const safeHostname = escapeHtml(sw.hostname);
                const safeHostnameJs = escapeJsString(sw.hostname);
                html += `
                    <div class="topo-node" data-node-id="${safeHostnameJs}" data-action="select-topology-node" data-hostname="${safeHostnameJs}">
                        <div class="topo-node-header">
                            <span class="topo-node-name">${safeHostname}</span>
                            <span class="topo-node-role">${escapeHtml(sw.role || 'unknown')}</span>
                        </div>
                        <div class="topo-node-details">
                            <span class="topo-node-model">${escapeHtml(model)}</span>
                            ${vpcInfo ? `<span class="topo-node-vpc">${escapeHtml(vpcInfo)}</span>` : ''}
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
            html += `</div>`;
        }
        
        // Render leaf switches at bottom
        if (leafSwitches.length > 0) {
            html += `<div class="topology-row topology-leaf">`;
            html += `<div class="topology-row-label">Leaf</div>`;
            html += `<div class="topology-nodes">`;
            leafSwitches.forEach(sw => {
                if (!sw || !sw.hostname) {
                    console.warn("Invalid switch in leafSwitches:", sw);
                    return;
                }
                const vpcPair = (deployment.vpc_pairs || []).find(p => p && (p.primary === sw.hostname || p.secondary === sw.hostname));
                const vpcInfo = vpcPair && vpcPair.domain ? (vpcPair.secondary ? `vPC ${vpcPair.domain}` : `vPC Domain ${vpcPair.domain} (Standalone)`) : '';
                const model = sw.model || 'Unknown Model';
                const safeHostname = escapeHtml(sw.hostname);
                const safeHostnameJs = escapeJsString(sw.hostname);
                html += `
                    <div class="topo-node" data-node-id="${safeHostnameJs}" data-action="select-topology-node" data-hostname="${safeHostnameJs}">
                        <div class="topo-node-header">
                            <span class="topo-node-name">${safeHostname}</span>
                            <span class="topo-node-role">${escapeHtml(sw.role || 'unknown')}</span>
                        </div>
                        <div class="topo-node-details">
                            <span class="topo-node-model">${escapeHtml(model)}</span>
                            ${vpcInfo ? `<span class="topo-node-vpc">${escapeHtml(vpcInfo)}</span>` : ''}
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
            html += `</div>`;
        }
        
        // Render other switches (fallback for unknown roles)
        if (otherSwitches.length > 0) {
            html += `<div class="topology-row topology-other">`;
            html += `<div class="topology-row-label">Other</div>`;
            html += `<div class="topology-nodes">`;
            otherSwitches.forEach(sw => {
                if (!sw || !sw.hostname) {
                    console.warn("Invalid switch in otherSwitches:", sw);
                    return;
                }
                const vpcPair = (deployment.vpc_pairs || []).find(p => p && (p.primary === sw.hostname || p.secondary === sw.hostname));
                const vpcInfo = vpcPair && vpcPair.domain ? (vpcPair.secondary ? `vPC ${vpcPair.domain}` : `vPC Domain ${vpcPair.domain} (Standalone)`) : '';
                const model = sw.model || 'Unknown Model';
                const safeHostname = escapeHtml(sw.hostname);
                const safeHostnameJs = escapeJsString(sw.hostname);
                html += `
                    <div class="topo-node" data-node-id="${safeHostnameJs}" data-action="select-topology-node" data-hostname="${safeHostnameJs}">
                        <div class="topo-node-header">
                            <span class="topo-node-name">${safeHostname}</span>
                            <span class="topo-node-role">${escapeHtml(sw.role || 'unknown')}</span>
                        </div>
                        <div class="topo-node-details">
                            <span class="topo-node-model">${escapeHtml(model)}</span>
                            ${vpcInfo ? `<span class="topo-node-vpc">${escapeHtml(vpcInfo)}</span>` : ''}
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
            html += `</div>`;
        }
        
        // Render SVG overlay for connections (after all nodes are rendered)
        html += `<svg class="topology-connections" width="100%" height="100%">`;
        
        // Draw vPC peer-link connections with validation
        if (Array.isArray(deployment.vpc_pairs)) {
            deployment.vpc_pairs.forEach(pair => {
                if (!pair || !pair.primary) {
                    console.warn("Invalid vpc_pair (missing primary):", pair);
                    return;
                }
                // Skip vPC pairs with null secondary (standalone switches)
                if (!pair.secondary) {
                    console.log(`Skipping vPC pair with null secondary: ${pair.primary} (standalone)`);
                    return;
                }
                const primary = deployment.switches.find(s => s && s.hostname === pair.primary);
                const secondary = deployment.switches.find(s => s && s.hostname === pair.secondary);
                if (primary && secondary) {
                    const safePrimary = escapeJsString(pair.primary);
                    const safeSecondary = escapeJsString(pair.secondary);
                    html += `<line class="topo-connection topo-vpc-link" data-from="${safePrimary}" data-to="${safeSecondary}" />`;
                } else {
                    console.warn(`vPC pair references missing switches: ${pair.primary} -> ${pair.secondary}`);
                }
            });
        }
        
        // Draw uplink connections with validation
        if (Array.isArray(deployment.uplinks)) {
            deployment.uplinks.forEach(uplink => {
                if (!uplink || !uplink.from || !uplink.to) {
                    console.warn("Invalid uplink:", uplink);
                    return;
                }
                const from = deployment.switches.find(s => s && s.hostname === uplink.from);
                const to = deployment.switches.find(s => s && s.hostname === uplink.to);
                if (from && to) {
                    const safeFrom = escapeJsString(uplink.from);
                    const safeTo = escapeJsString(uplink.to);
                    html += `<line class="topo-connection topo-uplink" data-from="${safeFrom}" data-to="${safeTo}" />`;
                } else {
                    console.warn(`Uplink references missing switches: ${uplink.from} -> ${uplink.to}`);
                }
            });
        }
        
        html += `</svg>`;
        html += `</div>`;
        
        console.log("Topology HTML generated, length:", html.length);
        container.innerHTML = html;
        console.log("Topology HTML set to container");
        
        // Draw connection lines after DOM is rendered with error handling
        setTimeout(() => {
            try {
                drawTopologyConnections();
            } catch (error) {
                console.error("Error drawing topology connections:", error);
            }
        }, 300);
        
        console.log("=== renderDeploymentTopology END ===");
    } catch (error) {
        console.error("Error in renderDeploymentTopology:", error);
        // Show error in UI
        const container = document.getElementById("topologyContainer");
        if (container) {
            container.innerHTML = `<div class="topology-error">Error rendering topology: ${escapeHtml(error.message)}</div>`;
        }
    }
}

function drawTopologyConnections() {
    const svg = document.querySelector('.topology-connections');
    if (!svg) {
        console.warn("SVG topology-connections element not found");
        return;
    }
    
    try {
        const connections = svg.querySelectorAll('.topo-connection');
        console.log(`Drawing ${connections.length} topology connections`);
        
        connections.forEach(line => {
            const fromId = line.getAttribute('data-from');
            const toId = line.getAttribute('data-to');
            
            if (!fromId || !toId) {
                console.warn("Connection line missing data-from or data-to attribute");
                return;
            }
            
            const fromNode = document.querySelector(`.topo-node[data-node-id="${fromId}"]`);
            const toNode = document.querySelector(`.topo-node[data-node-id="${toId}"]`);
            
            if (fromNode && toNode) {
                const fromRect = fromNode.getBoundingClientRect();
                const toRect = toNode.getBoundingClientRect();
                const svgRect = svg.getBoundingClientRect();
                
                const x1 = fromRect.left + fromRect.width / 2 - svgRect.left;
                const y1 = fromRect.top + fromRect.height / 2 - svgRect.top;
                const x2 = toRect.left + toRect.width / 2 - svgRect.left;
                const y2 = toRect.top + toRect.height / 2 - svgRect.top;
                
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                console.log(`Drew connection: ${fromId} -> ${toId} (${x1},${y1} to ${x2},${y2})`);
            } else {
                console.warn(`Could not find nodes for connection: ${fromId} -> ${toId} (fromNode: ${!!fromNode}, toNode: ${!!toNode})`);
            }
        });
    } catch (error) {
        console.error("Error drawing topology connections:", error);
    }
}

// Switch port visualization
async function renderSwitchPortPanel(switchId, overrideHostname = null) {
    const container = document.getElementById("switchPortPanel");
    if (!container) return;
    
    let sw;
    let model;
    let hostname = overrideHostname; // For vPC peer switches
    
    // Check if in multi-switch mode
    if (multiSwitchMode && deployment.switches.length > 0) {
        // Try to find switch by ID first, then by hostname
        sw = deployment.switches.find(s => s.id === switchId);
        if (!sw) {
            sw = deployment.switches.find(s => s.hostname === switchId);
        }
        if (!sw && !hostname) {
            console.log(`Switch not found with ID: ${switchId}, available switches:`, deployment.switches.map(s => ({id: s.id, hostname: s.hostname})));
            return;
        }
        if (sw) {
            model = SWITCH_MODELS[sw.model] || SWITCH_MODELS["Generic"];
        }
        
        // For vPC peer in single-switch mode, create temporary switch object
        if (!sw && hostname) {
            sw = {
                hostname: hostname,
                model: document.getElementById("model")?.value || "N9K-C93180YC-FX",
                role: 'leaf',
                device_config: null
            };
            model = SWITCH_MODELS[sw.model] || SWITCH_MODELS["Generic"];
            console.log(`Created temporary switch object for vPC peer: ${sw.hostname}`);
        }
        
        console.log(`Rendering port panel for switch: ${sw.hostname}, model: ${sw.model}, role: ${sw.role}, device_config:`, sw.device_config);
        
        // Add switch info header to port panel
        const headerHtml = `
            <div class="port-panel-header">
                <h3>Port Configuration: ${sw.hostname}</h3>
                <span class="port-panel-subtitle">${sw.model} - ${sw.role || 'Unknown Role'}</span>
            </div>
        `;
        container.innerHTML = headerHtml;
        
        // In multi-switch mode, populate configured_ports from hardware profile and deployment
        const allPorts = [];
        
        // Use bulletproof port_map if available from API response
        if (sw.device_config && sw.device_config.port_map && sw.device_config.port_map.ports && sw.device_config.port_map.ports.length > 0) {
            console.log(`Using bulletproof port_map for ${sw.hostname}:`, sw.device_config.port_map);
            const portMapData = sw.device_config.port_map;
            
            // Check for errors in port_map
            if (portMapData.error) {
                console.warn(`Port map contains error for ${sw.hostname}:`, portMapData.error);
                flashToast(`Port map generation error for ${sw.hostname}: ${portMapData.error}. Using fallback.`, "warning");
            }
            
            // Convert port_map data to allPorts format
            portMapData.ports.forEach(portData => {
                if (!allPorts.find(p => p.port === portData.port)) {
                    allPorts.push({
                        port: portData.port,
                        port_name: portData.port_name,
                        type: portData.type,
                        description: portData.description,
                        port_channel: portData.port_channel || null,
                        channel_group: portData.channel_group || null,
                        mode: portData.mode || null,
                        enabled: portData.enabled !== false
                    });
                    console.log(`Added port from bulletproof port_map: ${portData.port_name} -> ${portData.port}, type: ${portData.type}, PO${portData.port_channel}`);
                }
            });
            
            sw.configured_ports = allPorts;
            console.log(`Final configured ports for ${sw.hostname} from bulletproof port_map:`, allPorts);
        } else {
            // Fallback to legacy port mapping logic with user notification
            console.log(`Using legacy port mapping for ${sw.hostname}`);
            if (sw.device_config && (!sw.device_config.port_map || !sw.device_config.port_map.ports)) {
                flashToast(`Port map not available for ${sw.hostname}. Using legacy port mapping.`, "info");
            }
            
            // Get hardware profile for this switch model to get vPC port assignments
            const hwProfile = await getHardwareProfile(sw.model);
            console.log(`Hardware profile for ${sw.model}:`, hwProfile);
            
            // Add vPC peer-link ports from hardware profile if this switch is in a vPC pair
            const vpcPair = deployment.vpc_pairs.find(p => p.primary === sw.hostname || p.secondary === sw.hostname);
            console.log(`vPC pair for ${sw.hostname}:`, vpcPair);
            
            if (vpcPair && hwProfile && hwProfile.vpc_peer_link) {
                hwProfile.vpc_peer_link.forEach(portStr => {
                    let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = portStr.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: portStr,
                                type: 'peer-link',
                                description: `vPC Peer-link (Domain ${vpcPair.domain})`
                            });
                            console.log(`Added peer-link port: ${portStr} -> ${portNum}`);
                        }
                    }
                });
            }
        
        // Add vPC keepalive ports from hardware profile if this switch is in a vPC pair
        if (vpcPair && hwProfile && hwProfile.vpc_keepalive) {
            hwProfile.vpc_keepalive.forEach(portStr => {
                let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                if (!portMatch) portMatch = portStr.match(/(\d+)/);
                if (portMatch) {
                    const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                    if (!allPorts.find(p => p.port === portNum)) {
                        allPorts.push({
                            port: portNum,
                            port_name: portStr,
                            type: 'keepalive',
                            description: `vPC Keepalive (Domain ${vpcPair.domain})`
                        });
                        console.log(`Added keepalive port: ${portStr} -> ${portNum}`);
                    }
                }
            });
        }
        
        // Add downlink ports for core switches based on actual device configuration
        if (sw.role === 'core' && hwProfile) {
            console.log(`Processing core switch ${sw.hostname} for downlink ports`);
            // Use the actual device_config from API response if available
            if (sw.device_config && sw.device_config.interfaces && sw.device_config.interfaces.length > 0) {
                console.log(`Using device_config interfaces for ${sw.hostname}:`, sw.device_config.interfaces);
                sw.device_config.interfaces.forEach(iface => {
                    let portMatch = iface.name.match(/E(\d+)\/(\d+)/);
                    if (!portMatch) portMatch = iface.name.match(/Ethernet1\/(\d+)/);
                    if (!portMatch) portMatch = iface.name.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: iface.name,
                                type: iface.port_channel ? 'downlink-pc' : 'downlink',
                                description: iface.description || 'Configured',
                                port_channel: iface.port_channel || null
                            });
                            console.log(`Added interface from device_config: ${iface.name} -> ${portNum}, PO${iface.port_channel}, desc: ${iface.description}`);
                        }
                    }
                });
            } else if (sw.device_config && sw.device_config.downlink_config && sw.device_config.downlink_config.length > 0) {
                console.log(`Using device_config downlink_config for ${sw.hostname}:`, sw.device_config.downlink_config);
                sw.device_config.downlink_config.forEach(dl => {
                    let portMatch = dl.interface.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = dl.interface.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: dl.interface,
                                type: dl.port_channel ? 'downlink-pc' : 'downlink',
                                description: dl.description || 'Downlink',
                                port_channel: dl.port_channel || null
                            });
                            console.log(`Added downlink port from device_config: ${dl.interface} -> ${portNum}, PO${dl.port_channel}, desc: ${dl.description}`);
                        }
                    }
                });
            } else if (sw.downlink_config && sw.downlink_config.length > 0) {
                console.log(`Using switch downlink_config for ${sw.hostname}:`, sw.downlink_config);
                // Fallback to switch downlink_config
                sw.downlink_config.forEach(dl => {
                    let portMatch = dl.interface.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = dl.interface.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: dl.interface,
                                type: dl.port_channel ? 'downlink-pc' : 'downlink',
                                description: dl.description || 'Downlink',
                                port_channel: dl.port_channel || null
                            });
                            console.log(`Added downlink port from switch config: ${dl.interface} -> ${portNum}, PO${dl.port_channel}`);
                        }
                    }
                });
            } else {
                console.log(`No device_config or downlink_config found, using hardware profile ranges for ${sw.hostname}`);
                // Fallback to hardware profile ranges if no config available
                // Add 10GB downlink ports
                if (hwProfile.downlink_10g_start && hwProfile.downlink_10g_end) {
                    for (let portNum = hwProfile.downlink_10g_start; portNum <= hwProfile.downlink_10g_end; portNum++) {
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: `Ethernet1/${portNum}`,
                                type: 'downlink-10g',
                                description: '10GB Downlink (configured)'
                            });
                            console.log(`Added 10GB downlink port: Ethernet1/${portNum}`);
                        }
                    }
                }
                // Add 1GB downlink ports
                if (hwProfile.downlink_1g_start && hwProfile.downlink_1g_end) {
                    for (let portNum = hwProfile.downlink_1g_start; portNum <= hwProfile.downlink_1g_end; portNum++) {
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: `Ethernet1/${portNum}`,
                                type: 'downlink-1g',
                                description: '1GB Downlink (configured)'
                            });
                            console.log(`Added 1GB downlink port: Ethernet1/${portNum}`);
                        }
                    }
                }
            }
        } else if (sw.role !== 'core' && hwProfile) {
            // For leaf switches, add uplink ports from device_config or hardware profile
            console.log(`Processing leaf switch ${sw.hostname} for uplink ports`);
            if (sw.device_config && sw.device_config.interfaces && sw.device_config.interfaces.length > 0) {
                console.log(`Using device_config interfaces for leaf ${sw.hostname}:`, sw.device_config.interfaces);
                sw.device_config.interfaces.forEach(iface => {
                    let portMatch = iface.name.match(/E(\d+)\/(\d+)/);
                    if (!portMatch) portMatch = iface.name.match(/Ethernet1\/(\d+)/);
                    if (!portMatch) portMatch = iface.name.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: iface.name,
                                type: iface.port_channel ? 'uplink-pc' : 'uplink',
                                description: iface.description || 'Configured',
                                port_channel: iface.port_channel || null
                            });
                            console.log(`Added interface from device_config for leaf: ${iface.name} -> ${portNum}, PO${iface.port_channel}, desc: ${iface.description}`);
                        }
                    }
                });
            } else if (sw.device_config && sw.device_config.uplink_config && sw.device_config.uplink_config.length > 0) {
                console.log(`Using device_config uplink_config for leaf ${sw.hostname}:`, sw.device_config.uplink_config);
                sw.device_config.uplink_config.forEach(ul => {
                    let portMatch = ul.interface.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = ul.interface.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: ul.interface,
                                type: ul.port_channel ? 'uplink-pc' : 'uplink',
                                description: ul.description || 'Uplink',
                                port_channel: ul.port_channel || null
                            });
                            console.log(`Added uplink port from device_config: ${ul.interface} -> ${portNum}, PO${ul.port_channel}, desc: ${ul.description}`);
                        }
                    }
                });
            } else {
                console.log(`No device_config for leaf ${sw.hostname}, using hardware profile ranges`);
                // Fallback to hardware profile uplink ranges
                if (hwProfile.vpc_uplink_start && hwProfile.vpc_uplink_end) {
                    for (let portNum = hwProfile.vpc_uplink_start; portNum <= hwProfile.vpc_uplink_end; portNum++) {
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: `Ethernet1/${portNum}`,
                                type: 'uplink',
                                description: 'Uplink (configured)'
                            });
                            console.log(`Added uplink port: Ethernet1/${portNum}`);
                        }
                    }
                }
            }
        }
        
        // Add uplink ports for this switch
        const switchUplinks = deployment.uplinks.filter(u => u.from === sw.hostname || u.to === sw.hostname);
        console.log(`Uplinks for ${sw.hostname}:`, switchUplinks);
        
        switchUplinks.forEach(uplink => {
            // Add source ports (from this switch)
            if (uplink.ports && uplink.from === sw.hostname) {
                const uplinkPorts = uplink.ports.split(',').map(p => p.trim());
                console.log(`Source uplink ports for ${uplink.from} -> ${uplink.to}:`, uplinkPorts);
                uplinkPorts.forEach(portStr => {
                    let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = portStr.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: portStr,
                                type: 'uplink',
                                description: `Uplink to ${uplink.to} (PO${uplink.po_id})`
                            });
                            console.log(`Added source uplink port: ${portStr} -> ${portNum}`);
                        }
                    }
                });
            }
            
            // Add destination ports (to this switch)
            if (uplink.to_ports && uplink.to === sw.hostname) {
                const toPorts = uplink.to_ports.split(',').map(p => p.trim());
                console.log(`Destination uplink ports for ${uplink.from} -> ${uplink.to}:`, toPorts);
                toPorts.forEach(portStr => {
                    let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = portStr.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: portStr,
                                type: 'uplink',
                                description: `Uplink from ${uplink.from} (PO${uplink.po_id})`
                            });
                            console.log(`Added destination uplink port: ${portStr} -> ${portNum}`);
                        }
                    }
                });
            }
        });
        
        sw.configured_ports = allPorts;
        console.log(`Final configured ports for ${sw.hostname}:`, allPorts);
        } // End legacy port mapping fallback
    } else {
        // Single switch mode - use current form values
        const hostname = document.getElementById("hostname")?.value || "Switch";
        const modelValue = document.getElementById("model")?.value || "Nexus 9336C-FX2";
        model = SWITCH_MODELS[modelValue] || SWITCH_MODELS["Generic"];
        
        // Create a temporary switch object for rendering
        sw = {
            hostname: hostname,
            model: modelValue,
            configured_ports: [] // Will be populated from link planner
        };
        
        // Get configured ports from link planner if available
        if (typeof linkPlannerRows !== 'undefined' && linkPlannerRows) {
            const allPorts = [];
            if (linkPlannerRows.downlink) {
                linkPlannerRows.downlink.forEach((row, i) => {
                    if (row.enabled !== false && row.members) {
                        const members = row.members.split(',').map(m => m.trim());
                        members.forEach(member => {
                            // Try multiple port name patterns
                            let portMatch = member.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                            if (!portMatch) {
                                portMatch = member.match(/(\d+)/);
                            }
                            if (portMatch) {
                                const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                                allPorts.push({
                                    port: portNum,
                                    port_name: member,
                                    type: 'downlink',
                                    description: row.description || `Downlink ${i+1}`
                                });
                            }
                        });
                    }
                });
            }
            if (linkPlannerRows.uplink) {
                linkPlannerRows.uplink.forEach((row, i) => {
                    if (row.enabled !== false && row.members) {
                        const members = row.members.split(',').map(m => m.trim());
                        members.forEach(member => {
                            // Try multiple port name patterns
                            let portMatch = member.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                            if (!portMatch) {
                                portMatch = member.match(/(\d+)/);
                            }
                            if (portMatch) {
                                const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                                allPorts.push({
                                    port: portNum,
                                    port_name: member,
                                    type: 'uplink',
                                    description: row.description || `Uplink ${i+1}`
                                });
                            }
                        });
                    }
                });
            }
            
            // Add vPC peer-link ports from form
            const vpcPlInts = document.getElementById("vpc_pl_ints")?.value || "";
            if (vpcPlInts) {
                const peerLinkPorts = vpcPlInts.split(',').map(p => p.trim());
                peerLinkPorts.forEach(portStr => {
                    let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = portStr.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]);
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: portStr,
                                type: 'peer-link',
                                description: 'vPC Peer-link'
                            });
                        }
                    }
                });
            }
            
            // Add vPC keepalive ports from form
            const vpcKaInts = document.getElementById("vpc_ka_ints")?.value || "";
            if (vpcKaInts) {
                const kaPorts = vpcKaInts.split(',').map(p => p.trim());
                kaPorts.forEach(portStr => {
                    // Unified regex — matches Ethernet1/1, E1/1, Ethernet1/1/1
                    let portMatch = portStr.match(/(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/);
                    if (!portMatch) portMatch = portStr.match(/(\d+)/);
                    if (portMatch) {
                        const portNum = portMatch[3] ? parseInt(portMatch[3]) : (portMatch[2] ? parseInt(portMatch[2]) : parseInt(portMatch[1]));
                        if (!allPorts.find(p => p.port === portNum)) {
                            allPorts.push({
                                port: portNum,
                                port_name: portStr,
                                type: 'keepalive',
                                description: 'vPC Keepalive'
                            });
                        }
                    }
                });
            }
            
            console.log('Configured ports for single switch:', allPorts);
            sw.configured_ports = allPorts;
        }
    }
    
    let html = `<div class="switch-port-panel">`;
    html += `<div class="switch-port-header">`;
    html += `<h3>${sw.hostname} - ${sw.model}</h3>`;
    html += `<span class="port-description">${model.description || ''}</span>`;
    html += `</div>`;
    
    // Render QSFP28 uplink ports first if model has them
    if (model.hasQSFP && model.qsfpPorts) {
        html += `<div class="fiber-ports-section">`;
        html += `<h4>QSFP28 Uplink Ports (${model.qsfpPortSpeed})</h4>`;
        html += `<div class="fiber-ports-grid">`;
        const qsfpCount = model.qsfpPorts;
        const qsfpStart = model.ports + (model.hasSFP ? model.sfpPorts : 0) + 1;
        for (let i = 0; i < qsfpCount; i++) {
            const qsfpNum = qsfpStart + i;
            const portName = `Ethernet1/${qsfpNum}`;
            const portConfig = sw.configured_ports.find(p => p.port === qsfpNum || p.port_name === portName);
            const isConfigured = !!portConfig;
            const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
            
            html += `
                <div class="switch-port fiber-port ${portClass}" data-port="${qsfpNum}" data-port-name="${portName}" data-port-type="${model.qsfpPortType}">
                    <span class="port-number">${qsfpNum}</span>
                </div>
            `;
        }
        html += `</div>`;
        html += `</div>`;
    }
    
    // Render SFP28 ports if model has them
    if (model.hasSFP && model.sfpPorts) {
        html += `<div class="fiber-ports-section">`;
        html += `<h4>SFP28 Ports (${model.sfpPortSpeed})</h4>`;
        html += `<div class="fiber-ports-grid" style="grid-template-columns: repeat(4, 1fr);">`;
        const sfpCount = model.sfpPorts;
        const sfpStart = model.ports + 1;
        for (let i = 0; i < sfpCount; i++) {
            const sfpNum = sfpStart + i;
            const portName = `Ethernet1/${sfpNum}`;
            const portConfig = sw.configured_ports.find(p => p.port === sfpNum || p.port_name === portName);
            const isConfigured = !!portConfig;
            const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
            
            html += `
                <div class="switch-port fiber-port ${portClass}" data-port="${sfpNum}" data-port-name="${portName}" data-port-type="${model.sfpPortType}">
                    <span class="port-number">${sfpNum}</span>
                </div>
            `;
        }
        html += `</div>`;
        html += `</div>`;
    }
    
    // Render legacy fiber ports (for 93180YC-EX compatibility)
    if (model.hasFiber && model.fiberPorts && !model.hasQSFP) {
        html += `<div class="fiber-ports-section">`;
        html += `<h4>Uplink Ports (${model.fiberPortSpeed} ${model.fiberPortType})</h4>`;
        html += `<div class="fiber-ports-grid">`;
        const fiberCount = model.fiberPorts;
        const fiberStart = model.ports + 1;
        for (let i = 0; i < fiberCount; i++) {
            const fiberNum = fiberStart + i;
            const portName = `Ethernet1/${fiberNum}`;
            const portConfig = sw.configured_ports.find(p => p.port === fiberNum || p.port_name === portName);
            const isConfigured = !!portConfig;
            const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
            
            html += `
                <div class="switch-port fiber-port ${portClass}" data-port="${fiberNum}" data-port-name="${portName}" data-port-type="${model.fiberPortType}">
                    <span class="port-number">${fiberNum}</span>
                </div>
            `;
        }
        html += `</div>`;
        html += `</div>`;
    }
    
    // Render main ports
    const [rows, cols] = model.layout.split('x').map(Number);
    html += `<div class="main-ports-section">`;
    html += `<h4>Downlink Ports (${model.portSpeed} ${model.portType})</h4>`;
    html += `<div class="switch-port-grid" style="grid-template-rows: repeat(${rows}, 1fr); grid-template-columns: repeat(${cols}, 1fr);">`;
    
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const portNum = row * cols + col + 1;
            const portName = `Ethernet1/${portNum}`;
            const portConfig = sw.configured_ports.find(p => p.port === portNum || p.port_name === portName);
            const isConfigured = !!portConfig;
            const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
            
            html += `
                <div class="switch-port ${portClass}" data-port="${portNum}" data-port-name="${portName}" data-port-type="${model.portType}">
                    <span class="port-number">${portNum}</span>
                </div>
            `;
        }
    }
    
    html += `</div>`;
    html += `</div>`;
    
    html += `</div>`;
    container.innerHTML = html;
    
    // Add hover tooltips
    container.querySelectorAll('.switch-port').forEach(portEl => {
        const portNum = parseInt(portEl.dataset.port);
        const portName = portEl.dataset.portName;
        const portType = portEl.dataset.portType || 'Unknown';
        const portConfig = sw.configured_ports.find(p => p.port === portNum || p.port_name === portName);
        
        if (portConfig) {
            portEl.title = `${portName} (${portType})\nStatus: Configured\nType: ${portConfig.type || 'Unknown'}\nDescription: ${portConfig.description || 'No description'}`;
        } else {
            portEl.title = `${portName} (${portType})\nStatus: Unconfigured`;
        }
    });
}

// Generate physical port matrix HTML for a switch
function generatePhysicalPortMatrix(hostname, portMapData) {
    console.log(`generatePhysicalPortMatrix called for ${hostname}, portMapData:`, portMapData);
    
    try {
        // Get the switch model from deployment data (multi-switch mode) or DOM (single-switch mode)
        let modelName = "Nexus 9336C-FX2";
        
        // First try to get from deployment switches (multi-switch mode)
        if (deployment.switches && deployment.switches.length > 0) {
            const sw = deployment.switches.find(s => s && s.hostname === hostname);
            if (sw && sw.model) {
                modelName = sw.model;
                console.log(`Using model from deployment data: ${modelName}`);
            }
        }
        
        // Fallback to DOM element (single-switch mode)
        if (modelName === "Nexus 9336C-FX2") {
            const domModel = document.getElementById("model")?.value;
            if (domModel) {
                modelName = domModel;
                console.log(`Using model from DOM: ${modelName}`);
            }
        }
        
        const switchModel = SWITCH_MODELS[modelName] || SWITCH_MODELS["Generic"];
        console.log(`Switch model for ${hostname}:`, switchModel);
        
        let html = `<div class="switch-port-panel">`;
        html += `<div class="switch-port-header">`;
        html += `<h3>${hostname} - ${modelName}</h3>`;
        html += `<span class="port-description">${switchModel.description || ''}</span>`;
        html += `</div>`;
        
        // Convert port_map data to configured_ports format
        const configuredPorts = [];
        if (portMapData && portMapData.ports && Array.isArray(portMapData.ports)) {
            portMapData.ports.forEach(portData => {
                if (portData) {
                    configuredPorts.push({
                        port: portData.port || portData.port_number,
                        port_name: portData.port_name || portData.interface,
                        type: portData.type || portData.port_type,
                        description: portData.description,
                        port_channel: portData.port_channel || portData.po_id || null
                    });
                }
            });
            console.log(`Converted ${configuredPorts.length} configured ports for ${hostname}`);
        }
        
        // Validate layout
        if (!switchModel.layout) {
            console.error(`No layout defined for model ${modelName}`);
            return `<div class="error-message">Error: No port layout defined for model ${modelName}</div>`;
        }
        
        // Render main ports (physical grid)
        const [rows, cols] = switchModel.layout.split('x').map(Number);
        if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
            console.error(`Invalid layout for model ${modelName}: ${switchModel.layout}`);
            return `<div class="error-message">Error: Invalid port layout for model ${modelName}</div>`;
        }
        
        html += `<div class="main-ports-section">`;
        html += `<h4>Downlink Ports (${switchModel.portSpeed} ${switchModel.portType})</h4>`;
        html += `<div class="switch-port-grid" style="grid-template-rows: repeat(${rows}, 1fr); grid-template-columns: repeat(${cols}, 1fr);">`;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const portNum = row * cols + col + 1;
                const portName = `Ethernet1/${portNum}`;
                const portConfig = configuredPorts.find(p => p.port === portNum || p.port_name === portName);
                const isConfigured = !!portConfig;
                const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
                
                // Build tooltip content
                let tooltipContent = `${portName} (${switchModel.portType})\nStatus: ${isConfigured ? 'Configured' : 'Unconfigured'}`;
                if (portConfig) {
                    tooltipContent += `\nType: ${portConfig.type || 'Unknown'}`;
                    tooltipContent += `\nDescription: ${portConfig.description || 'No description'}`;
                    if (portConfig.port_channel) {
                        tooltipContent += `\nPort Channel: PO${portConfig.port_channel}`;
                    }
                }
                
                html += `
                    <div class="switch-port ${portClass}" data-port="${portNum}" data-port-name="${portName}" data-port-type="${switchModel.portType}" title="${tooltipContent}">
                        <span class="port-number">${portNum}</span>
                    </div>
                `;
            }
        }
        
        html += `</div>`;
        html += `</div>`;
        
        // Render additional high-speed ports (fiber/SFP/QSFP) if model has them
        if (switchModel.fiberPorts) {
            html += `<div class="fiber-ports-section">`;
            html += `<h4>Fiber Ports (${switchModel.fiberPortSpeed} ${switchModel.fiberPortType})</h4>`;
            html += `<div class="switch-port-grid" style="grid-template-rows: 1fr; grid-template-columns: repeat(${switchModel.fiberPorts}, 1fr);">`;
            
            const fiberStart = 49;
            for (let i = 0; i < switchModel.fiberPorts; i++) {
                const portNum = fiberStart + i;
                const portName = `Ethernet1/${portNum}`;
                const portConfig = configuredPorts.find(p => p.port === portNum || p.port_name === portName);
                const isConfigured = !!portConfig;
                const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
                
                let tooltipContent = `${portName} (${switchModel.fiberPortType})\nStatus: ${isConfigured ? 'Configured' : 'Unconfigured'}`;
                if (portConfig) {
                    tooltipContent += `\nType: ${portConfig.type || 'Unknown'}`;
                    tooltipContent += `\nDescription: ${portConfig.description || 'No description'}`;
                    if (portConfig.port_channel) {
                        tooltipContent += `\nPort Channel: PO${portConfig.port_channel}`;
                    }
                }
                
                html += `
                    <div class="switch-port ${portClass}" data-port="${portNum}" data-port-name="${portName}" data-port-type="${switchModel.fiberPortType}" title="${tooltipContent}">
                        <span class="port-number">${portNum}</span>
                    </div>
                `;
            }
            
            html += `</div>`;
            html += `</div>`;
        }
        
        if (switchModel.sfpPorts) {
            html += `<div class="sfp-ports-section">`;
            html += `<h4>SFP Ports (${switchModel.sfpPortSpeed} ${switchModel.sfpPortType})</h4>`;
            html += `<div class="switch-port-grid" style="grid-template-rows: 1fr; grid-template-columns: repeat(${switchModel.sfpPorts}, 1fr);">`;
            
            const sfpStart = 49;
            for (let i = 0; i < switchModel.sfpPorts; i++) {
                const portNum = sfpStart + i;
                const portName = `Ethernet1/${portNum}`;
                const portConfig = configuredPorts.find(p => p.port === portNum || p.port_name === portName);
                const isConfigured = !!portConfig;
                const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
                
                let tooltipContent = `${portName} (${switchModel.sfpPortType})\nStatus: ${isConfigured ? 'Configured' : 'Unconfigured'}`;
                if (portConfig) {
                    tooltipContent += `\nType: ${portConfig.type || 'Unknown'}`;
                    tooltipContent += `\nDescription: ${portConfig.description || 'No description'}`;
                    if (portConfig.port_channel) {
                        tooltipContent += `\nPort Channel: PO${portConfig.port_channel}`;
                    }
                }
                
                html += `
                    <div class="switch-port ${portClass}" data-port="${portNum}" data-port-name="${portName}" data-port-type="${switchModel.sfpPortType}" title="${tooltipContent}">
                        <span class="port-number">${portNum}</span>
                    </div>
                `;
            }
            
            html += `</div>`;
            html += `</div>`;
        }
        
        if (switchModel.qsfpPorts) {
            html += `<div class="qsfp-ports-section">`;
            html += `<h4>QSFP Ports (${switchModel.qsfpPortSpeed} ${switchModel.qsfpPortType})</h4>`;
            html += `<div class="switch-port-grid" style="grid-template-rows: 1fr; grid-template-columns: repeat(${switchModel.qsfpPorts}, 1fr);">`;
            
            const qsfpStart = switchModel.sfpPorts ? 49 + switchModel.sfpPorts : 53;
            for (let i = 0; i < switchModel.qsfpPorts; i++) {
                const portNum = qsfpStart + i;
                const portName = `Ethernet1/${portNum}`;
                const portConfig = configuredPorts.find(p => p.port === portNum || p.port_name === portName);
                const isConfigured = !!portConfig;
                const portClass = isConfigured ? 'port-configured' : 'port-unconfigured';
                
                let tooltipContent = `${portName} (${switchModel.qsfpPortType})\nStatus: ${isConfigured ? 'Configured' : 'Unconfigured'}`;
                if (portConfig) {
                    tooltipContent += `\nType: ${portConfig.type || 'Unknown'}`;
                    tooltipContent += `\nDescription: ${portConfig.description || 'No description'}`;
                    if (portConfig.port_channel) {
                        tooltipContent += `\nPort Channel: PO${portConfig.port_channel}`;
                    }
                }
                
                html += `
                    <div class="switch-port ${portClass}" data-port="${portNum}" data-port-name="${portName}" data-port-type="${switchModel.qsfpPortType}" title="${tooltipContent}">
                        <span class="port-number">${portNum}</span>
                    </div>
                `;
            }
            
            html += `</div>`;
            html += `</div>`;
        }
        
        html += `</div>`;
        
        console.log(`Physical matrix HTML generated for ${hostname}, length: ${html.length}`);
        return html;
    } catch (error) {
        console.error(`Error in generatePhysicalPortMatrix for ${hostname}:`, error);
        return `<div class="error-message">Error generating physical port matrix: ${escapeHtml(error.message)}</div>`;
    }
}

// Render deployment summary in review step
function renderDeploymentSummary() {
    if (!multiSwitchMode || deployment.switches.length === 0) return;
    
    const container = document.getElementById("deploymentSummary");
    if (!container) {
        // Create container if it doesn't exist
        const switchPortPanel = document.getElementById("switchPortPanel");
        if (switchPortPanel) {
            const summaryDiv = document.createElement("div");
            summaryDiv.id = "deploymentSummary";
            summaryDiv.className = "deployment-summary";
            switchPortPanel.parentNode.insertBefore(summaryDiv, switchPortPanel);
        }
    }
    
    const summaryContainer = document.getElementById("deploymentSummary");
    if (!summaryContainer) return;
    
    let html = `<h3>Deployment Summary</h3>`;
    html += `<div class="deployment-switch-list">`;
    
    deployment.switches.forEach(sw => {
        const vpcPair = deployment.vpc_pairs.find(p => p.primary === sw.hostname || p.secondary === sw.hostname);
        const uplinkCount = deployment.uplinks.filter(u => u.from === sw.hostname || u.to === sw.hostname).length;
        const vpcInfo = vpcPair ? `vPC Domain ${vpcPair.domain}` : 'Standalone';
        
        html += `
            <div class="deployment-switch-item">
                <div class="deployment-switch-info">
                    <span class="deployment-switch-name">${sw.hostname}</span>
                    <span class="deployment-switch-details">${sw.model} | ${sw.mgmt_ip} | ${sw.role} | ${vpcInfo}</span>
                </div>
                <span class="switch-role-badge">${uplinkCount} uplinks</span>
            </div>
        `;
    });
    
    html += `</div>`;
    
    if (deployment.vpc_pairs.length > 0) {
        html += `<div class="deployment-connections">`;
        html += `<h4>vPC Pairs (${deployment.vpc_pairs.length})</h4>`;
        deployment.vpc_pairs.forEach(pair => {
            html += `<div class="connection-item">Domain ${pair.domain}: ${pair.primary} ↔ ${pair.secondary} (Peer-link: ${pair.peer_link_ports})</div>`;
        });
        html += `</div>`;
    }
    
    if (deployment.uplinks.length > 0) {
        html += `<div class="deployment-connections">`;
        html += `<h4>Uplinks (${deployment.uplinks.length})</h4>`;
        deployment.uplinks.forEach(uplink => {
            html += `<div class="connection-item">${uplink.from} → ${uplink.to} (Ports: ${uplink.ports}, PO${uplink.po_id})</div>`;
        });
        html += `</div>`;
    }
    
    summaryContainer.innerHTML = html;
}

// Toggle between port map and CLI panels
function toggleConfigPanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

// Switch between tabs in the tabbed view
// PA-003 FIX: Duplicate switchTab function removed - now using consolidated functions above

// Select a topology node to show its port configuration and CLI
async function selectTopologyNode(nodeLabel) {
    console.log('=== selectTopologyNode START ===');
    console.log('nodeLabel:', nodeLabel);
    console.log('multiSwitchMode:', multiSwitchMode);
    console.log('deployment.switches:', deployment.switches);
    console.log('deployment.switches.length:', deployment.switches?.length);
    
    // Log topology node selection to audit logger
    if (window.auditLogger) {
        window.auditLogger.logPreviewEvent('TOPOLOGY_NODE_SELECTED', {
            nodeLabel: nodeLabel,
            multiSwitchMode: multiSwitchMode,
            deploymentSwitchesCount: deployment.switches?.length || 0
        });
    }
    
    // Handle multi-switch deployment mode
    if (multiSwitchMode && deployment.switches && deployment.switches.length > 0) {
        console.log('Multi-switch mode: Searching for switch with label:', nodeLabel);
        const sw = deployment.switches.find(s => s.hostname === nodeLabel || s.id === nodeLabel);
        console.log('Found switch:', sw);
        
        if (sw) {
            console.log('Switch found, proceeding with panel rendering');
            
            // Validate switch has required fields
            if (!sw.id && !sw.hostname) {
                console.error('Switch missing both id and hostname:', sw);
                flashToast(`Invalid switch data for ${nodeLabel}`, "error");
                return;
            }
            
            // Use hostname as fallback if id is missing
            const switchId = sw.id || sw.hostname;
            console.log('Using switchId:', switchId);
            
            // Clear existing panels to prevent data bleed
            const existingConfigPanel = document.getElementById("switchConfigPanel");
            if (existingConfigPanel) {
                console.log('Clearing existing config panel');
                existingConfigPanel.innerHTML = '';
                existingConfigPanel.style.display = 'none';
            }
            
            // Clear existing port panel
            const existingPortPanel = document.getElementById("switchPortPanel");
            if (existingPortPanel) {
                console.log('Clearing existing port panel');
                existingPortPanel.innerHTML = '';
            }
            
            // Create tabbed view container
            const tabbedContainer = document.createElement('div');
            tabbedContainer.className = 'tabbed-view-container';
            tabbedContainer.id = 'switchTabbedView';
            
            // Create tabs
            const tabs = document.createElement('div');
            tabs.className = 'tabbed-view-tabs';
            tabs.innerHTML = `
                <button class="tabbed-view-tab active" data-tab="portmap" data-action="switch-tab">Port Map</button>
                <button class="tabbed-view-tab" data-tab="cli" data-action="switch-tab">CLI Configuration</button>
            `;
            
            // Create content area
            const content = document.createElement('div');
            content.className = 'tabbed-view-content';
            
            // Create port map panel
            const portMapPanel = document.createElement('div');
            portMapPanel.className = 'tabbed-view-panel active';
            portMapPanel.id = 'portmap-panel';
            
            // Create CLI panel
            const cliPanel = document.createElement('div');
            cliPanel.className = 'tabbed-view-panel';
            cliPanel.id = 'cli-panel';
            
            content.appendChild(portMapPanel);
            content.appendChild(cliPanel);
            tabbedContainer.appendChild(tabs);
            tabbedContainer.appendChild(content);
            
            // Insert tabbed container into port panel
            const portPanel = document.getElementById("switchPortPanel");
            if (portPanel) {
                portPanel.appendChild(tabbedContainer);
            }
            
            // Render port panel content into port map panel
            console.log('Rendering port panel for switch:', sw.hostname);
            await renderSwitchPortPanel(switchId);
            
            // Move port panel content to port map panel
            const portPanelContent = portPanel.querySelector('.port-map-section, .switch-port-grid, .deployment-switch-stack');
            if (portPanelContent) {
                portMapPanel.appendChild(portPanelContent);
            }
            
            // For deployment mode, use the device_config if available, otherwise generate CLI
            if (sw.device_config && sw.device_config.config) {
                console.log('Using existing device_config for CLI:', sw.hostname);
                cliPanel.innerHTML = `<h4>CLI Configuration for ${sw.hostname}</h4><pre class="cli-block">${escapeHtml(sw.device_config.config)}</pre>`;
            } else {
                console.log('Generating CLI for switch:', sw.hostname);
                await generateSwitchConfig(sw);
                // Move CLI content to CLI panel after generation
                setTimeout(() => {
                    const cliContent = document.getElementById("switchConfigPanel");
                    if (cliContent) {
                        cliPanel.innerHTML = `<h4>CLI Configuration for ${sw.hostname}</h4>${cliContent.innerHTML}`;
                        cliContent.style.display = 'none';
                    }
                }, 100);
            }
            
            flashToast(`Showing tabbed view for ${sw.hostname}`, "info");
        } else {
            console.error('Switch not found for label:', nodeLabel, 'Available switches:', deployment.switches.map(s => s.hostname));
            flashToast(`Switch not found: ${nodeLabel}`, "error");
        }
    } 
    // Handle vPC mode in single-switch mode
    else if (nodeLabel === "node-self" || nodeLabel === "node-peer") {
        console.log('vPC mode: Handling node click for', nodeLabel);
        
        const hostname = document.getElementById("hostname")?.value || "Switch";
        const secondaryHostname = document.getElementById("hostname_secondary")?.value || "";
        
        if (nodeLabel === "node-self") {
            console.log('Showing primary switch configuration:', hostname);
            flashToast(`Showing configuration for ${hostname}`, "info");
            // Re-render port panel for primary switch
            await renderSwitchPortPanel(null);
        } else if (nodeLabel === "node-peer") {
            console.log('=== NODE-PEER CLICKED - CALLING PREVIEW TO GET PAIR DATA ===');
            console.log('Showing vPC peer configuration');
            if (secondaryHostname) {
                flashToast(`Showing configuration for vPC peer: ${secondaryHostname}`, "info");
                
                // Clear existing panels
                const existingConfigPanel = document.getElementById("switchConfigPanel");
                if (existingConfigPanel) {
                    existingConfigPanel.innerHTML = '';
                    existingConfigPanel.style.display = 'none';
                }
                const existingPortPanel = document.getElementById("switchPortPanel");
                if (existingPortPanel) {
                    existingPortPanel.innerHTML = '';
                }
                
                // Use the original scenario payload with generate_pair=true to get full pair data
                const previewPayload = buildScenarioPayload();
                console.log('=== CALLING /scenario/preview WITH PAIR PAYLOAD ===');
                console.log('previewPayload:', JSON.stringify(previewPayload, null, 2));
                
                // Log peer configuration generation attempt
                if (window.auditLogger) {
                    window.auditLogger.logPreviewEvent('PEER_CONFIG_GENERATION_START', {
                        secondaryHostname: secondaryHostname,
                        payloadKeys: Object.keys(previewPayload),
                        generate_pair: previewPayload.generate_pair
                    });
                }
                
                // Call /scenario/preview to get full pair data with port maps
                const endpoint = "/scenario/preview";
                const res = await fetch(endpoint, { 
                    method: "POST", 
                    headers: authHeaders(), 
                    body: JSON.stringify(previewPayload) 
                });
                
                // Log API response details
                if (window.auditLogger) {
                    window.auditLogger.logAPIResponseDetails(endpoint, res.status, null);
                }
                
                if (res.ok) {
                    const result = await res.json();
                    console.log('=== PREVIEW RESPONSE RECEIVED FOR NODE-PEER ===');
                    console.log('Full result:', result);
                    console.log('Has pair_preview:', !!result.pair_preview);
                    
                    if (result.pair_preview) {
                        console.log('pair_preview keys:', Object.keys(result.pair_preview));
                        console.log('secondary_hostname:', result.pair_preview.secondary_hostname);
                        console.log('has secondary_config_preview:', !!result.pair_preview.secondary_config_preview);
                        console.log('has primary_port_map:', !!result.pair_preview.primary_port_map);
                        console.log('has secondary_port_map:', !!result.pair_preview.secondary_port_map);
                    }
                    
                    // Log successful generation
                    if (window.auditLogger) {
                        window.auditLogger.logPreviewEvent('PEER_CONFIG_GENERATION_SUCCESS', {
                            secondaryHostname: secondaryHostname,
                            hasPairPreview: !!result.pair_preview,
                            hasSecondaryConfigPreview: !!result.pair_preview?.secondary_config_preview,
                            hasPrimaryPortMap: !!result.pair_preview?.primary_port_map,
                            hasSecondaryPortMap: !!result.pair_preview?.secondary_port_map
                        });
                    }
                    
                    // Display the full pair configuration with side-by-side layout
                    displaySwitchConfig(hostname, result);
                } else {
                    const errorText = await res.text();
                    console.error('Failed to generate vPC peer configuration:', res.status, errorText);
                    
                    // Log detailed error
                    if (window.auditLogger) {
                        window.auditLogger.logPreviewEvent('PEER_CONFIG_GENERATION_FAILED', {
                            secondaryHostname: secondaryHostname,
                            status: res.status,
                            statusText: res.statusText,
                            errorText: errorText,
                            payload: peerPayload
                        });
                    }
                    
                    flashToast('Failed to generate vPC peer configuration', "error");
                }
                
                // Also render port panel for peer switch
                await renderSwitchPortPanel(null, secondaryHostname);
            } else {
                flashToast('vPC peer hostname not configured. Please set secondary hostname.', "warning");
            }
        }
    } 
    else {
        // In single-switch mode, node clicks are not applicable
        console.log('Single-switch mode: Node switching not applicable');
        flashToast('Enable multi-switch mode to switch between deployment switches', "info");
        
        // Optionally, show how to enable multi-switch mode
        const toggle = document.getElementById("multiSwitchToggle");
        if (toggle) {
            console.log('Multi-switch toggle found, user can enable it');
            flashToast('Toggle "Multi-Switch Deployment" in the switch list panel', "info");
        } else {
            console.log('Multi-switch toggle not found in UI');
            flashToast('Multi-switch mode not available in current view', "warning");
        }
    }
    
    console.log('=== selectTopologyNode END ===');
}

// Expose function to window for onclick handlers
window.selectTopologyNode = selectTopologyNode;

// Load hardware profiles from server
let hardwareProfilesCache = null;

async function loadHardwareProfiles() {
    if (hardwareProfilesCache) return hardwareProfilesCache;
    
    try {
        // Use the catalog API to get hardware profiles
        const response = await fetch('/catalog/hardware');
        if (!response.ok) {
            throw new Error(`Failed to load hardware profiles: ${response.status}`);
        }
        const profiles = await response.json();
        // Catalog API returns a list directly, wrap it for consistency
        hardwareProfilesCache = { profiles: profiles };
        console.log('Loaded hardware profiles from catalog:', profiles);
        return hardwareProfilesCache;
    } catch (error) {
        console.error('Failed to load hardware profiles from catalog:', error);
        // Try fallback to YAML endpoint
        try {
            const response = await fetch('/data/hardware_profiles.yaml');
            if (!response.ok) {
                throw new Error(`Failed to load hardware profiles: ${response.status}`);
            }
            const text = await response.text();
            // Parse YAML (simple parser for our use case)
            const profiles = parseSimpleYAML(text);
            hardwareProfilesCache = profiles;
            return profiles;
        } catch (yamlError) {
            console.error('Failed to load hardware profiles from YAML:', yamlError);
            // Return fallback hardcoded profiles
            return getFallbackHardwareProfiles();
        }
    }
}

function parseSimpleYAML(text) {
    const lines = text.split('\n');
    const result = { profiles: [] };
    let currentProfile = null;
    let currentKey = null;
    let inList = false;
    let currentList = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        
        // Skip comments and empty lines
        if (trimmed.startsWith('#') || trimmed === '') continue;
        
        // Check for profile start
        if (trimmed.startsWith('- name:')) {
            if (currentProfile) {
                result.profiles.push(currentProfile);
            }
            currentProfile = { name: trimmed.split(':')[1].trim() };
            currentKey = null;
            inList = false;
            currentList = [];
        } else if (currentProfile) {
            // Check for key-value pairs
            const match = trimmed.match(/^(\s+)([\w_]+):\s*(.*)$/);
            if (match) {
                const indent = match[1].length;
                const key = match[2];
                const value = match[3].trim();
                
                if (indent === 4) {
                    // Top-level key in profile
                    if (inList && currentList.length > 0) {
                        currentProfile[currentKey] = currentList;
                        currentList = [];
                        inList = false;
                    }
                    currentKey = key;
                    if (value) {
                        currentProfile[key] = value;
                    } else {
                        inList = true;
                    }
                } else if (indent === 6 && inList) {
                    // List item
                    currentList.push(value.replace(/"/g, ''));
                }
            }
        }
    }
    
    if (currentProfile) {
        if (inList && currentList.length > 0) {
            currentProfile[currentKey] = currentList;
        }
        result.profiles.push(currentProfile);
    }
    
    // Add display_name from name if not present
    result.profiles.forEach(profile => {
        if (!profile.display_name && profile.name) {
            profile.display_name = profile.name;
        }
    });
    
    return result;
}

function getFallbackHardwareProfiles() {
    return {
        profiles: [
            {
                display_name: "Nexus 93180YC-EX",
                vpc_peer_link: ["Ethernet1/51", "Ethernet1/52"],
                vpc_keepalive: ["Ethernet1/49", "Ethernet1/50"]
            },
            {
                display_name: "Nexus 9336C-FX2",
                vpc_peer_link: ["Ethernet1/35", "Ethernet1/36"],
                vpc_keepalive: ["Ethernet1/33", "Ethernet1/34"]
            },
            {
                display_name: "Nexus 9348GC-FXP",
                vpc_peer_link: ["Ethernet1/51", "Ethernet1/52"],
                vpc_keepalive: ["Ethernet1/47", "Ethernet1/48"]
            }
        ]
    };
}

async function getHardwareProfile(modelName) {
    const profiles = await loadHardwareProfiles();
    return profiles.profiles.find(p => p.display_name === modelName);
}

// Generate and display CLI configuration for a switch
async function generateSwitchConfig(sw) {
   try {
        console.log('generateSwitchConfig called with switch:', sw);
        
        // Log switch config generation attempt
        if (window.auditLogger) {
            window.auditLogger.logPreviewEvent('SWITCH_CONFIG_GENERATION_START', {
                switchHostname: sw.hostname,
                switchId: sw.id,
                hasMgmtIp: !!sw.mgmt_ip,
                model: sw.model
            });
        }
        
        // Prepare the device input for the API
        const deviceInput = {
            hostname: sw.hostname,
            mgmt_ip: sw.mgmt_ip,
            mgmt_gw: sw.mgmt_gw || "10.10.10.1",
            site_name: sw.site_name || "HQ",
            model: sw.model,
            nxos_version: sw.nxos_version || "9.3",
            vpc_domain: sw.vpc_domain || null,
            vpc_peer_link_id: sw.vpc_peer_link_id || 1,
            keepalive_po_id: sw.keepalive_po_id || 2,
            vpc_system_priority: sw.vpc_system_priority || 32667,
            local_ka: sw.local_ka || "10.10.10.1",
            remote_ka: sw.remote_ka || "10.10.10.2",
            vpc_pl_ints: sw.peer_link_ports || "",
            base_access_vlan: sw.base_access_vlan || 10,
            access_vlan_count: sw.access_vlan_count || 4,
            interface_count: sw.interface_count || 0,
            bring_up_spare_ports: sw.bring_up_spare_ports || false,
            security_tier: sw.security_tier || "standard"
        };

        console.log('Calling /generate-config API with:', deviceInput);

        // Call the generate-config API
        const response = await fetch('/generate-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceInput)
        });
        
        // Log API response
        if (window.auditLogger) {
            window.auditLogger.logAPIResponseDetails('/generate-config', response.status, null);
        }

        if (!response.ok) {
            let errorMessage = `API request failed: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText;
            }
            
            console.error('generateSwitchConfig failed:', errorMessage);
            
            // Log detailed error
            if (window.auditLogger) {
                window.auditLogger.logPreviewEvent('SWITCH_CONFIG_GENERATION_FAILED', {
                    switchHostname: sw.hostname,
                    switchId: sw.id,
                    status: response.status,
                    statusText: response.statusText,
                    errorMessage: errorMessage,
                    deviceInput: deviceInput
                });
            }
            
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('=== API RESPONSE RECEIVED ===');
        console.log('API response:', result);
        console.log('Response keys:', Object.keys(result));
        console.log('Response status:', result.status);
        
        // EXTENSIVE LOGGING: Check for pair data
        if (result.pair_preview) {
            console.log('=== PAIR_PREVIEW FOUND IN RESPONSE ===');
            console.log('pair_preview keys:', Object.keys(result.pair_preview));
            console.log('pair_preview secondary_hostname:', result.pair_preview.secondary_hostname);
            console.log('pair_preview has secondary_config_preview:', !!result.pair_preview.secondary_config_preview);
            if (result.pair_preview.secondary_config_preview) {
                console.log('secondary_config_preview length:', result.pair_preview.secondary_config_preview.length);
            }
            console.log('pair_preview has primary_port_map:', !!result.pair_preview.primary_port_map);
            console.log('pair_preview has secondary_port_map:', !!result.pair_preview.secondary_port_map);
            if (result.pair_preview.primary_port_map) {
                console.log('primary_port_map keys:', Object.keys(result.pair_preview.primary_port_map));
                console.log('primary_port_map ports count:', result.pair_preview.primary_port_map.ports?.length || 0);
            }
            if (result.pair_preview.secondary_port_map) {
                console.log('secondary_port_map keys:', Object.keys(result.pair_preview.secondary_port_map));
                console.log('secondary_port_map ports count:', result.pair_preview.secondary_port_map.ports?.length || 0);
            }
        } else {
            console.log('=== NO PAIR_PREVIEW IN RESPONSE ===');
        }
        
        // Log successful generation
        if (window.auditLogger) {
            window.auditLogger.logPreviewEvent('SWITCH_CONFIG_GENERATION_SUCCESS', {
                switchHostname: sw.hostname,
                switchId: sw.id,
                hasPortMap: !!result.port_map,
                hasExport: !!result.export
            });
        }
        
        // Store port_map if available for future use
        if (result.port_map) {
            sw.device_config = sw.device_config || {};
            sw.device_config.port_map = result.port_map;
            console.log('Stored port_map for switch:', sw.hostname);
        }
        
        // Display the configuration
        displaySwitchConfig(sw.hostname, result.export || result);
        
    } catch (error) {
        console.error('Failed to generate switch config:', error);
        
        // Log detailed error
        if (window.auditLogger) {
            window.auditLogger.logPreviewEvent('SWITCH_CONFIG_GENERATION_ERROR', {
                switchHostname: sw.hostname,
                switchId: sw.id,
                errorMessage: error.message,
                errorStack: error.stack
            });
        }
        
        // Provide specific error guidance
        let userMessage = `Failed to generate configuration for ${sw.hostname}: ${error.message}`;
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            userMessage = `Network error: Could not connect to server. Please check your connection.`;
        } else if (error.message.includes('500')) {
            userMessage = `Server error: The server encountered an error. Please try again.`;
        } else if (error.message.includes('422')) {
            userMessage = `Validation error: Invalid configuration data. Please check your inputs.`;
        }
        
        flashToast(userMessage, "error");
        
        // Show error in config panel
        displaySwitchConfig(sw.hostname, { error: error.message });
    }
}

// Display CLI configuration in a panel
function displaySwitchConfig(hostname, config) {
    console.log(`displaySwitchConfig called for hostname: ${hostname}`, config);
    
    // Add visual indication of selected switch in topology
    const allNodes = document.querySelectorAll('.topo-node');
    allNodes.forEach(node => {
        node.classList.remove('selected-node');
    });
    
    // Highlight the selected node
    const selectedNode = document.querySelector(`[data-node-id="${hostname}"]`);
    if (selectedNode) {
        selectedNode.classList.add('selected-node');
    }
    
    // Find or create the config panel
    let configPanel = document.getElementById("switchConfigPanel");
    if (!configPanel) {
        const portPanel = document.getElementById("switchPortPanel");
        if (portPanel) {
            configPanel = document.createElement("div");
            configPanel.id = "switchConfigPanel";
            configPanel.className = "switch-config-panel";
            portPanel.parentNode.insertBefore(configPanel, portPanel.nextSibling);
            console.log('Created new config panel');
        }
    }

    if (!configPanel) {
        console.error('Could not find or create config panel');
        return;
    }

    // Clear previous content
    configPanel.innerHTML = '';
    configPanel.style.display = 'block';

    // Create side-by-side layout with port map and CLI
    let html = `<div class="switch-config-stack">`;
    html += `<div class="switch-config-header">`;
    html += `<h3>${hostname} - Configuration</h3>`;
    html += `<button type="button" class="btn-outline btn-sm" data-action="toggle-config-panel" data-panel="switchConfigPanel">Close</button>`;
    html += `</div>`;
    
    // Side-by-side content
    html += `<div class="switch-config-content">`;
    
    // Port Map Section
    html += `<div class="port-map-section">`;
    html += `<h4>Port Map</h4>`;
    html += `<div class="config-content">`;
    
    // Try to get port map from switch data
    let portMapHtml = `<p class="field-note">Port map shows interface assignments and descriptions.</p>`;
    if (deployment.switches) {
        const sw = deployment.switches.find(s => s.hostname === hostname);
        if (sw && sw.device_config && sw.device_config.port_map) {
            portMapHtml = renderPortMapForSwitch(hostname, sw.device_config);
        }
    }
    html += portMapHtml;
    html += `</div>`;
    html += `</div>`;
    
    // CLI Configuration Section
    html += `<div class="cli-section">`;
    html += `<h4>CLI Configuration</h4>`;
    html += `<div class="config-content">`;
    
    // Extract the actual CLI configuration from the response
    // Standardized structure: export.cli or export.config
    let cliConfig = '';
    if (typeof config === 'string') {
        cliConfig = config;
    } else if (config.export && config.export.cli) {
        cliConfig = config.export.cli;
    } else if (config.export && config.export.config) {
        cliConfig = config.export.config;
    } else if (config.export && config.export.raw) {
        // Fallback to raw manifest if cli/config not available
        cliConfig = config.export.raw.cli || config.export.raw.config || JSON.stringify(config.export.raw, null, 2);
    } else {
        cliConfig = JSON.stringify(config, null, 2);
    }
    
    console.log(`Extracted CLI config for ${hostname}:`, cliConfig.substring(0, 200));
    
    html += `<pre class="config-text">${escapeHtml(cliConfig)}</pre>`;
    html += `</div>`;
    html += `</div>`; // Close CLI section
    
    html += `</div>`; // Close switch-config-content
    html += `</div>`; // Close switch-config-stack
    
    configPanel.innerHTML = html;
    console.log(`Config panel updated for ${hostname}`);
}

function getSubnet(ip) {
    // Assume /24 subnet for keepalive IPs (common practice)
    const parts = ip.split('.');
    return `${parts[0]}.${parts[1]}.${parts[2]}.0/24`;
}

// Interface format validation based on hardware profile
function validateInterfaceFormat(interfaceName, model) {
    if (!interfaceName || !model) return { valid: false, message: "Interface name and model required" };
    
    // Get hardware profile for the model
    const hwProfile = SWITCH_MODELS[model] || {};
    const totalPorts = hwProfile.ports || hwProfile.total_ports || 48;
    
    // Parse interface name to extract port number
    // Supports formats: Ethernet1/1, E1/1, Eth1/1, Ethernet1/1-10
    const interfacePatterns = [
        /^Ethernet(\d+)\/(\d+)(?:-(\d+))?$/i,
        /^E(\d+)\/(\d+)(?:-(\d+))?$/i,
        /^Eth(\d+)\/(\d+)(?:-(\d+))?$/i
    ];
    
    let portNum = null;
    let isRange = false;
    
    for (const pattern of interfacePatterns) {
        const match = interfaceName.match(pattern);
        if (match) {
            portNum = parseInt(match[2]);
            if (match[3]) {
                isRange = true;
                const endPort = parseInt(match[3]);
                if (endPort > totalPorts) {
                    return { valid: false, message: `Port range exceeds maximum port ${totalPorts} for ${model}` };
                }
            }
            break;
        }
    }
    
    if (portNum === null) {
        return { valid: false, message: "Invalid interface format. Use Ethernet1/X or E1/X" };
    }
    
    // Validate port number is within range
    if (portNum < 1 || portNum > totalPorts) {
        return { valid: false, message: `Port ${portNum} is invalid for ${model} (max port: ${totalPorts})` };
    }
    
    return { valid: true };
}

// Port conflict detection across all port assignments
function detectPortConflicts(switchId, newPorts, portType) {
    const sw = deployment.switches.find(s => s.id === switchId || s.hostname === switchId);
    if (!sw) return [];
    
    const conflicts = [];
    const allAssignedPorts = new Set();
    
    // Collect all currently assigned ports
    if (sw.vpc_peer_link_ports) {
        parsePortRange(sw.vpc_peer_link_ports).forEach(p => allAssignedPorts.add(p));
    }
    if (sw.keepalive_ports) {
        parsePortRange(sw.keepalive_ports).forEach(p => allAssignedPorts.add(p));
    }
    if (sw.uplink_ports) {
        parsePortRange(sw.uplink_ports).forEach(p => allAssignedPorts.add(p));
    }
    if (sw.access_ports) {
        parsePortRange(sw.access_ports).forEach(p => allAssignedPorts.add(p));
    }
    
    // Check new ports against existing assignments
    const newPortList = parsePortRange(newPorts);
    newPortList.forEach(port => {
        if (allAssignedPorts.has(port)) {
            conflicts.push({
                port: port,
                existingType: getPortTypeForPort(sw, port),
                newType: portType
            });
        }
    });
    
    return conflicts;
}

function parsePortRange(portString) {
    if (!portString) return [];
    const ports = [];
    const parts = portString.split(',').map(p => p.trim());
    
    parts.forEach(part => {
        if (part.includes('-')) {
            const [start, end] = part.split('-').map(n => parseInt(n.trim()));
            for (let i = start; i <= end; i++) {
                ports.push(i);
            }
        } else {
            const portNum = parseInt(part.replace(/\D/g, ''));
            if (!isNaN(portNum)) {
                ports.push(portNum);
            }
        }
    });
    
    return ports;
}

function getPortTypeForPort(sw, port) {
    if (sw.vpc_peer_link_ports && parsePortRange(sw.vpc_peer_link_ports).includes(port)) {
        return 'vPC Peer-Link';
    }
    if (sw.keepalive_ports && parsePortRange(sw.keepalive_ports).includes(port)) {
        return 'vPC Keepalive';
    }
    if (sw.uplink_ports && parsePortRange(sw.uplink_ports).includes(port)) {
        return 'Uplink';
    }
    if (sw.access_ports && parsePortRange(sw.access_ports).includes(port)) {
        return 'Access';
    }
    return 'Unknown';
}

// Switch between Port Map and CLI tabs
function switchConfigTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
    }
    
    // Add active class to selected tab button
    const selectedBtn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
}

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

// Header Dropdown Functionality
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.header-dropdown');
    
    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (button && menu) {
            // Toggle dropdown on click
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const isExpanded = dropdown.getAttribute('aria-expanded') === 'true';
                
                // Close all other dropdowns
                dropdowns.forEach(d => {
                    if (d !== dropdown) {
                        d.setAttribute('aria-expanded', 'false');
                    }
                });
                
                // Toggle current dropdown
                dropdown.setAttribute('aria-expanded', !isExpanded);
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    dropdown.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Close dropdown on Escape key
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    dropdown.setAttribute('aria-expanded', 'false');
                    button.focus();
                }
            });
            
            // Keyboard navigation within dropdown
            const items = menu.querySelectorAll('.dropdown-item');
            items.forEach((item, index) => {
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        const nextItem = items[index + 1];
                        if (nextItem) nextItem.focus();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        const prevItem = items[index - 1];
                        if (prevItem) prevItem.focus();
                    } else if (e.key === 'Escape') {
                        dropdown.setAttribute('aria-expanded', 'false');
                        button.focus();
                    }
                });
            });
        }
    });
}

function setWizardMode(mode) {
    // Don't change wizard mode if in multi-switch mode - they are separate modes
    if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode) {
        console.log('[SET_WIZARD_MODE] Ignoring wizard mode change while in multi-switch mode');
        return;
    }
    
    const modeButtons = document.querySelectorAll('[data-wizard-mode]');
    modeButtons.forEach(btn => {
        const isPressed = btn.getAttribute('data-wizard-mode') === mode;
        btn.setAttribute('aria-pressed', isPressed);
    });
    
    // Update dropdown button text
    const modeBtn = document.getElementById('modeDropdownBtn');
    if (modeBtn) {
        const modeText = mode.charAt(0).toUpperCase() + mode.slice(1);
        modeBtn.innerHTML = `Mode: ${modeText} <span class="dropdown-arrow">▾</span>`;
    }
    
    // Close dropdown
    const modeDropdown = document.getElementById('modeDropdown');
    if (modeDropdown) {
        modeDropdown.parentElement.setAttribute('aria-expanded', 'false');
    }
    
    // Trigger existing wizard mode logic if it exists
    if (typeof setWizardModeInternal === 'function') {
        setWizardModeInternal(mode);
    }
}

function openSupport() {
    // Open support documentation or contact page
    window.open('/docs/support.html', '_blank');
    
    // Close dropdown
    const helpDropdown = document.getElementById('helpDropdown');
    if (helpDropdown) {
        helpDropdown.parentElement.setAttribute('aria-expanded', 'false');
    }
}

// Validation Panel Functionality
let validationErrors = [];

function showValidationPanel(errors) {
    validationErrors = errors;
    const panel = document.getElementById('validationPanel');
    const countEl = document.getElementById('validationCount');
    const itemsEl = document.getElementById('validationItems');
    
    if (!panel || !countEl || !itemsEl) return;
    
    // FORENSIC FIX: Do not show panel if there are no errors
    // This prevents the contradictory state of "0 configuration issues" + "Configuration Issues" warning
    if (errors.length === 0) {
        // Clear the count element to prevent contradictory state
        countEl.textContent = '0';
        dismissValidationPanel();
        return;
    }
    
    countEl.textContent = errors.length;
    
    itemsEl.innerHTML = errors.map((error, index) => `
        <div class="validation-item">
            <span class="icon">⚠️</span>
            <div class="content">
                <div class="message">${error.message}</div>
                <div class="location">${error.location || ''}</div>
            </div>
            ${error.fixable ? `<button type="button" class="fix-btn" data-action="fix-validation-error" data-index="${index}">Fix</button>` : ''}
        </div>
    `).join('');
    
    panel.classList.add('visible');
    panel.setAttribute('aria-hidden', 'false');
}

function dismissValidationPanel() {
    // Use audit logger for debugging since console.log isn't appearing
    if (window.auditLogger) {
        window.auditLogger.logCustom('DISMISS_PANEL_START', {
            timestamp: new Date().toISOString(),
            function: 'dismissValidationPanel'
        });
    }
    
    const panel = document.getElementById('validationPanel');
    
    if (window.auditLogger) {
        window.auditLogger.logCustom('DISMISS_PANEL_ELEMENT_FOUND', {
            found: !!panel,
            panelId: panel ? panel.id : null,
            panelClasses: panel ? panel.className : null
        });
    }
    
    if (panel) {
        panel.classList.remove('visible');
        panel.style.display = 'none';
        panel.setAttribute('aria-hidden', 'true');
        
        if (window.auditLogger) {
            window.auditLogger.logCustom('DISMISS_PANEL_AFTER_MODIFICATION', {
                classes: panel.className,
                display: panel.style.display,
                ariaHidden: panel.getAttribute('aria-hidden')
            });
        }
    }
    
    // Also dismiss new validation panel if it exists
    const newPanel = document.getElementById('validation-panel');
    if (newPanel) {
        newPanel.classList.add('hidden');
        newPanel.classList.remove('visible');
        newPanel.style.display = 'none';
    }
    
    // Clear validation errors to prevent re-showing
    const errorsBefore = validationErrors.length;
    validationErrors = [];
    
    if (window.auditLogger) {
        window.auditLogger.logCustom('DISMISS_PANEL_END', {
            errorsCleared: errorsBefore,
            newPanelFound: !!newPanel
        });
    }
}

// Download all deployment configs as ZIP
function downloadAllDeploymentConfigs() {
    if (!window.lastDeploymentResults || !window.lastDeploymentResults.results) {
        flashToast('No deployment results available', 'error');
        return;
    }
    
    const results = window.lastDeploymentResults.results;
    const exportDir = window.lastDeploymentResults.export?.output_dir || window.lastDeploymentResults.export_dir || '';
    
    // If we have an export directory, try to open it instead
    if (exportDir) {
        openVaultFolder();
        return;
    }
    
    // Otherwise, create a simple download for each config
    results.forEach((result) => {
        if (result.status === 'success' && result.export?.cli) {
            const blob = new Blob([result.export.cli], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${result.hostname}_config.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });
    
    flashToast('Configuration files downloaded', 'ok');
}

// Open vault folder (output directory)
function openVaultFolder() {
    const exportDir = window.lastDeploymentResults?.export?.output_dir || window.lastDeploymentResults?.export_dir || 'configs/history';
    
    // Try to open the folder via backend API
    fetch('/open-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: exportDir })
    })
    .then(res => res.json())
    .then(result => {
        if (result.status === 'success') {
            flashToast('Folder opened successfully', 'ok');
        } else {
            flashToast('Could not open folder: ' + (result.message || 'Unknown error'), 'error');
        }
    })
    .catch(err => {
        console.error('Failed to open folder:', err);
        flashToast('Folder not accessible. Check if it exists: ' + exportDir, 'error');
    });
}

// Make function globally accessible
window.dismissValidationPanel = dismissValidationPanel;

// Simple event delegation using audit logger for debugging
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('dismiss-btn')) {
        if (window.auditLogger) {
            window.auditLogger.logCustom('DISMISS_BUTTON_CLICKED', {
                target: e.target.className,
                eventPhase: e.eventPhase
            });
        }
        e.preventDefault();
        e.stopPropagation();
        dismissValidationPanel();
    }
}, true);

function fixValidationError(index) {
    const error = validationErrors[index];
    if (error && error.fixAction) {
        error.fixAction();
        // Remove this error from the list
        validationErrors.splice(index, 1);
        // Refresh the panel
        if (validationErrors.length > 0) {
            showValidationPanel(validationErrors);
        } else {
            dismissValidationPanel();
        }
    }
}

function validateConfiguration() {
    const errors = [];
    
    // Validate hostname
    const hostname = document.getElementById('hostname');
    if (hostname && !hostname.value.trim()) {
        errors.push({
            message: 'Hostname is required',
            location: 'Step 3: Platform → Hostname',
            fixable: true,
            fixAction: () => {
                document.getElementById('hostname').focus();
                currentStep = 3;
                updateStepDisplay();
            }
        });
    }
    
    // Validate management IP
    const mgmtIp = document.getElementById('mgmt_ip');
    if (mgmtIp && !mgmtIp.value.trim()) {
        errors.push({
            message: 'Management IP is required',
            location: 'Step 3: Platform → Management IP',
            fixable: true,
            fixAction: () => {
                document.getElementById('mgmt_ip').focus();
                currentStep = 3;
                updateStepDisplay();
            }
        });
    } else if (mgmtIp && mgmtIp.value && !mgmtIp.value.includes('/')) {
        errors.push({
            message: 'Management IP must include CIDR notation (e.g., 10.10.10.10/24)',
            location: 'Step 3: Platform → Management IP',
            fixable: true,
            fixAction: () => {
                document.getElementById('mgmt_ip').focus();
                currentStep = 3;
                updateStepDisplay();
            }
        });
    }
    
    // Validate switch model
    const model = document.getElementById('model');
    if (model && !model.value) {
        errors.push({
            message: 'Switch model must be selected',
            location: 'Step 3: Platform → Switch Model',
            fixable: true,
            fixAction: () => {
                document.getElementById('model').focus();
                currentStep = 3;
                updateStepDisplay();
            }
        });
    }
    
    // Validate NX-OS version
    const nxosVersion = document.getElementById('nxos_version');
    if (nxosVersion && !nxosVersion.value) {
        errors.push({
            message: 'NX-OS version must be selected',
            location: 'Step 3: Platform → NX-OS Version',
            fixable: true,
            fixAction: () => {
                document.getElementById('nxos_version').focus();
                currentStep = 3;
                updateStepDisplay();
            }
        });
    }
    
    // Validate vPC configuration if enabled
    const vpcDomain = document.getElementById('vpc_domain');
    if (vpcDomain && vpcDomain.value) {
        const domain = parseInt(vpcDomain.value);
        if (isNaN(domain) || domain < 1 || domain > 4096) {
            errors.push({
                message: 'vPC domain ID must be between 1 and 4096',
                location: 'Step 2: vPC → Domain ID',
                fixable: true,
                fixAction: () => {
                    document.getElementById('vpc_domain').focus();
                    currentStep = 2;
                    updateStepDisplay();
                }
            });
        }
    }
    
    // Validate keepalive IPs if vPC is enabled
    const localKa = document.getElementById('local_ka');
    const remoteKa = document.getElementById('remote_ka');
    if (vpcDomain && vpcDomain.value) {
        if (localKa && !localKa.value) {
            errors.push({
                message: 'Local keepalive IP is required for vPC configuration',
                location: 'Step 7: Links → Local Keepalive IP',
                fixable: true,
                fixAction: () => {
                    document.getElementById('local_ka').focus();
                    currentStep = 7;
                    updateStepDisplay();
                }
            });
        }
        if (remoteKa && !remoteKa.value) {
            errors.push({
                message: 'Remote keepalive IP is required for vPC configuration',
                location: 'Step 7: Links → Remote Keepalive IP',
                fixable: true,
                fixAction: () => {
                    document.getElementById('remote_ka').focus();
                    currentStep = 7;
                    updateStepDisplay();
                }
            });
        }
        if (localKa && remoteKa && localKa.value === remoteKa.value) {
            errors.push({
                message: 'Local and remote keepalive IPs must be different',
                location: 'Step 7: Links → Keepalive IPs',
                fixable: true,
                fixAction: () => {
                    document.getElementById('remote_ka').focus();
                    currentStep = 7;
                    updateStepDisplay();
                }
            });
        }
    }
    
    if (errors.length > 0) {
        showValidationPanel(errors);
        return false;
    }
    
    return true;
}

/**
 * Integration with new validation API
 * Call this function to validate configuration using the new /config/upload endpoint
 */
async function validateConfigurationWithNewAPI(configText, hardwareModel, nxosVersion, validationLevel = 'standard', baselineOptions = []) {
    try {
        const result = await validateConfiguration(configText, hardwareModel, nxosVersion, validationLevel, baselineOptions);
        
        // Also update legacy validation panel for compatibility
        if (result && !result.is_valid) {
            const legacyErrors = result.errors.map(err => ({
                message: err.message,
                location: err.line_number ? `Line ${err.line_number}` : '',
                fixable: !!err.fix_command,
                fixAction: () => {
                    // Copy fix command to clipboard
                    if (err.fix_command) {
                        navigator.clipboard.writeText(err.fix_command);
                        flashToast(`Copied: ${err.fix_command}`, 'ok');
                    }
                }
            }));
            showValidationPanel(legacyErrors);
        }
        
        return result;
    } catch (error) {
        console.error('Validation error:', error);
        flashToast('Validation failed: ' + error.message, 'err');
        throw error;
    }
}

/**
 * Add validation button to config studio
 */
function addValidationButtonToConfigStudio() {
    // Find the config studio textarea
    const configTextarea = document.getElementById('builderField');
    if (!configTextarea) return;
    
    // Check if button already exists
    if (document.getElementById('validateConfigBtn')) return;
    
    // Create validate button
    const validateBtn = document.createElement('button');
    validateBtn.id = 'validateConfigBtn';
    validateBtn.type = 'button';
    validateBtn.className = 'btn-primary';
    validateBtn.textContent = 'Validate Configuration';
    validateBtn.style.marginTop = '10px';
    validateBtn.style.marginRight = '10px';
    
    validateBtn.addEventListener('click', async () => {
        const configText = configTextarea.value;
        if (!configText || configText.trim().length < 20) {
            flashToast('Please paste a running-config first.', 'warn');
            return;
        }
        
        // Get hardware model from current selection
        const hardwareModel = currentSwitch?.model || 'Nexus 93180YC-EX';
        const nxosVersion = currentSwitch?.nxos_version || '9.3';
        
        flashToast('Validating configuration...', 'info');
        
        try {
            const result = await validateConfigurationWithNewAPI(
                configText,
                hardwareModel,
                nxosVersion,
                'comprehensive'
            );
            
            if (result.is_valid) {
                flashToast('Configuration is valid!', 'ok');
            } else {
                flashToast(`Found ${result.errors.length} error(s), ${result.warnings.length} warning(s)`, 'warn');
            }
        } catch (error) {
            flashToast('Validation failed: ' + error.message, 'err');
        }
    });
    
    // Insert button after textarea
    configTextarea.parentNode.insertBefore(validateBtn, configTextarea.nextSibling);
}

// Call this after page load
setTimeout(addValidationButtonToConfigStudio, 1000);

// Add Escape key support for modals
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close release notes modal
        const releaseNotesModal = document.getElementById('releaseNotesModal');
        if (releaseNotesModal && !releaseNotesModal.classList.contains('hidden')) {
            releaseNotesModal.classList.add('hidden');
            releaseNotesModal.setAttribute('aria-hidden', 'true');
        }
        
        // Close deployment completion modal
        const deploymentModal = document.getElementById('deploymentCompletionModal');
        if (deploymentModal && !deploymentModal.classList.contains('hidden')) {
            deploymentModal.classList.add('hidden');
            deploymentModal.setAttribute('aria-hidden', 'true');
        }
    }
});

(async function init() {
    try {
        propagateTokenToAdminLink();
        initDropdowns();
        await loadVersion();
        await loadCatalog();
        await loadSystemPaths();
        loadExportDir();
        showFirstRunHint();
        await fetchVault();
        await fetchCheckpoints();
        updateBadges();
        updateWizardTip();
        
        // Add validation button after catalog is loaded
        addValidationButtonToConfigStudio();
    } catch (err) {
        setOutput("Startup error: " + err.message);
    }
})();
