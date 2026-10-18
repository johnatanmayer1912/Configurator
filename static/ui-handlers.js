// UX-008 FIX: External UI event handlers (moved from inline HTML)

// Validation panel dismiss handler
document.addEventListener('DOMContentLoaded', function() {
    const dismissBtn = document.getElementById('dismissValidationBtn');
    if (dismissBtn) {
        dismissBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const panel = document.getElementById('validationPanel');
            if (panel) {
                panel.classList.remove('visible');
                panel.style.display = 'none';
                panel.setAttribute('aria-hidden', 'true');
            }
            const newPanel = document.getElementById('validation-panel');
            if (newPanel) {
                newPanel.classList.add('hidden');
                newPanel.classList.remove('visible');
                newPanel.style.display = 'none';
            }
        });
    }
    
    // UX-008 FIX: Event delegation for common inline handlers
    document.body.addEventListener('click', function(e) {
        // Handle dropdown menu items
        if (e.target.matches('[data-action="set-wizard-mode"]')) {
            const mode = e.target.dataset.mode;
            if (typeof setWizardMode === 'function') {
                setWizardMode(mode);
            }
            // Ensure multi-switch mode is not affected by wizard mode change
            // Close dropdown
            const modeDropdown = document.getElementById('modeDropdown');
            if (modeDropdown) {
                modeDropdown.parentElement.setAttribute('aria-expanded', 'false');
            }
            return;
        }
        
        // Handle toggle actions
        if (e.target.matches('[data-action="toggle-multi-switch"]')) {
            if (typeof toggleMultiSwitchMode === 'function') {
                toggleMultiSwitchMode();
            }
        }
        
        if (e.target.matches('[data-action="toggle-training"]')) {
            if (typeof toggleTrainingMode === 'function') {
                toggleTrainingMode();
            }
        }
        
        // Handle configuration actions
        if (e.target.matches('[data-action="restart-config"]')) {
            if (typeof restartConfiguration === 'function') {
                restartConfiguration();
            }
        }
        
        if (e.target.matches('[data-action="open-config-builder"]')) {
            if (typeof openConfigBuilder === 'function') {
                openConfigBuilder();
            }
        }
        
        if (e.target.matches('[data-action="show-release-notes"]')) {
            if (typeof showReleaseNotesModal === 'function') {
                showReleaseNotesModal();
            }
        }
        
        // Handle help actions
        if (e.target.matches('[data-action="open-help"]')) {
            if (typeof openHelp === 'function') {
                openHelp();
            }
        }
        
        if (e.target.matches('[data-action="open-support"]')) {
            if (typeof openSupport === 'function') {
                openSupport();
            }
        }
        
        // Handle system actions
        if (e.target.matches('[data-action="shutdown-system"]')) {
            if (typeof shutdownSystem === 'function') {
                shutdownSystem();
            }
        }
        
        // Handle wizard actions
        if (e.target.matches('[data-action="dismiss-first-run"]')) {
            if (typeof dismissFirstRunHint === 'function') {
                dismissFirstRunHint();
            }
        }
        
        if (e.target.matches('[data-action="toggle-configure-detail"]')) {
            if (typeof toggleConfigurePathDetail === 'function') {
                toggleConfigurePathDetail();
            }
        }
        
        if (e.target.matches('[data-action="hide-template-gallery"]')) {
            if (typeof hideTemplateGallery === 'function') {
                hideTemplateGallery();
            }
        }
        
        // Handle editor actions
        if (e.target.matches('[data-action="validate-topology"]')) {
            if (typeof validateTopology === 'function') {
                validateTopology();
            }
        }
        
        if (e.target.matches('[data-action="reset-to-template"]')) {
            if (typeof resetToTemplate === 'function') {
                resetToTemplate();
            }
        }
        
        if (e.target.matches('[data-action="save-custom-template"]')) {
            if (typeof saveAsCustomTemplate === 'function') {
                saveAsCustomTemplate();
            }
        }
        
        if (e.target.matches('[data-action="generate-config"]')) {
            if (typeof generateDeploymentConfigs === 'function') {
                generateDeploymentConfigs();
            } else if (typeof generateConfig === 'function') {
                generateConfig();
            }
        }
        
        // Handle topology actions
        if (e.target.matches('[data-action="add-switch"]')) {
            if (typeof addSwitch === 'function') {
                addSwitch();
            }
        }
        
        if (e.target.matches('[data-action="add-vpc-domain"]')) {
            if (typeof addVPCDomain === 'function') {
                addVPCDomain();
            }
        }
        
        // Handle tab switching
        if (e.target.matches('[data-tab]')) {
            const tabName = e.target.dataset.tab;
            if (typeof switchTab === 'function') {
                switchTab(tabName);
            }
        }
        
        // Handle interface template buttons
        if (e.target.matches('[data-action="apply-interface-template"]')) {
            const templateType = e.target.dataset.template;
            if (typeof applyInterfaceTemplate === 'function') {
                applyInterfaceTemplate(templateType);
            }
        }
        
        // Handle bulk VLAN add
        if (e.target.matches('[data-action="bulk-add-vlans"]')) {
            if (typeof bulkAddVLANs === 'function') {
                bulkAddVLANs();
            }
        }
        
        // Handle uplink add
        if (e.target.matches('[data-action="add-uplink"]')) {
            if (typeof addUplink === 'function') {
                addUplink();
            }
        }

        // ── Configuration Editor: switch CRUD ──────────────────────────────
        const editSwitchTarget = e.target.closest('[data-action="edit-switch"]');
        if (editSwitchTarget) {
            const idx = editSwitchTarget.dataset.index;
            const switchId = editSwitchTarget.dataset.switchId;
            if (idx !== undefined && typeof editSwitch === 'function') {
                editSwitch(parseInt(idx));
            } else if (switchId !== undefined && typeof editSwitch === 'function') {
                // legacy switch-list panel uses data-switch-id
                const swIdx = deployment.switches.findIndex(s => s.id === switchId || s.hostname === switchId);
                if (swIdx >= 0) editSwitch(swIdx);
            }
        }

        const cloneSwitchTarget = e.target.closest('[data-action="clone-switch"]');
        if (cloneSwitchTarget) {
            const idx = cloneSwitchTarget.dataset.index;
            if (idx !== undefined && typeof cloneSwitch === 'function') {
                cloneSwitch(parseInt(idx));
            }
        }

        const removeSwitchTarget = e.target.closest('[data-action="remove-switch"]');
        if (removeSwitchTarget) {
            const idx = removeSwitchTarget.dataset.index;
            if (idx !== undefined && typeof removeSwitch === 'function') {
                removeSwitch(parseInt(idx));
            }
        }

        // ── Configuration Editor: vPC CRUD ─────────────────────────────────
        const editVpcTarget = e.target.closest('[data-action="edit-vpc"]');
        if (editVpcTarget) {
            const idx = editVpcTarget.dataset.index;
            if (idx !== undefined && typeof editVPC === 'function') {
                editVPC(parseInt(idx));
            }
        }

        const removeVpcTarget = e.target.closest('[data-action="remove-vpc"]');
        if (removeVpcTarget) {
            const idx = removeVpcTarget.dataset.index;
            if (idx !== undefined && typeof removeVPC === 'function') {
                removeVPC(parseInt(idx));
            }
        }

        // ── Configuration Editor: VLAN CRUD ────────────────────────────────
        const editVlanTarget = e.target.closest('[data-action="edit-vlan"]');
        if (editVlanTarget) {
            const idx = editVlanTarget.dataset.index;
            if (idx !== undefined && typeof editVLAN === 'function') {
                editVLAN(parseInt(idx));
            }
        }

        const removeVlanTarget = e.target.closest('[data-action="remove-vlan"]');
        if (removeVlanTarget) {
            const idx = removeVlanTarget.dataset.index;
            if (idx !== undefined && typeof removeVLAN === 'function') {
                removeVLAN(parseInt(idx));
            }
        }

        // ── Configuration Editor: uplink CRUD ──────────────────────────────
        const editUplinkTarget = e.target.closest('[data-action="edit-uplink"]');
        if (editUplinkTarget) {
            const idx = editUplinkTarget.dataset.index;
            const uplinkId = editUplinkTarget.dataset.uplinkId;
            if (idx !== undefined && typeof editUplink === 'function') {
                editUplink(parseInt(idx));
            } else if (uplinkId !== undefined && typeof editUplink === 'function') {
                editUplink(uplinkId);
            }
        }

        const removeUplinkTarget = e.target.closest('[data-action="remove-uplink"]');
        if (removeUplinkTarget) {
            const idx = removeUplinkTarget.dataset.index;
            if (idx !== undefined && typeof removeUplink === 'function') {
                removeUplink(parseInt(idx));
            }
        }
        
        // Handle info button clicks
        if (e.target.matches('[data-action="show-option-info"]')) {
            const option = e.target.dataset.option;
            if (typeof showOptionInfo === 'function') {
                showOptionInfo(option);
            }
        }
        
        // Handle VLAN template buttons
        if (e.target.matches('[data-action="apply-vlan-template"]')) {
            const template = e.target.dataset.template;
            if (typeof applyVlanTemplate === 'function') {
                applyVlanTemplate(template);
            }
        }
        
        // Handle VLAN add
        if (e.target.matches('[data-action="add-vlan"]')) {
            if (typeof addVlanRow === 'function') {
                addVlanRow();
            }
        }
        
        // Handle range expand
        if (e.target.matches('[data-action="expand-range"]')) {
            if (typeof expandRange === 'function') {
                expandRange();
            }
        }
        
        // Handle interface plan add
        if (e.target.matches('[data-action="add-interface-plan"]')) {
            if (typeof addInterfacePlanRow === 'function') {
                addInterfacePlanRow();
            }
        }
        
        // Handle port map range expand
        if (e.target.matches('[data-action="expand-port-map-range"]')) {
            const type = e.target.dataset.type;
            if (typeof expandPortMapRange === 'function') {
                expandPortMapRange(type);
            }
        }
        
        // Handle sync port fields
        if (e.target.matches('[data-action="sync-port-fields"]')) {
            if (typeof syncPortFieldsFromEditor === 'function') {
                syncPortFieldsFromEditor();
            }
        }
        
        // Handle link planner expert toggle
        if (e.target.matches('[data-action="toggle-link-planner-expert"]')) {
            if (typeof toggleLinkPlannerExpert === 'function') {
                toggleLinkPlannerExpert();
            }
        }
        
        // Handle fabric questionnaire start
        if (e.target.matches('[data-action="start-fabric-questionnaire"]')) {
            if (typeof startFabricQuestionnaire === 'function') {
                startFabricQuestionnaire();
            }
        }
        
        // Handle custom link add
        if (e.target.matches('[data-action="add-custom-link"]')) {
            const linkType = e.target.dataset.linkType;
            if (typeof addCustomLinkRow === 'function') {
                addCustomLinkRow(linkType);
            }
        }
        
        // Handle undo restore
        if (e.target.matches('[data-action="restore-undo"]')) {
            if (typeof restoreUndo === 'function') {
                restoreUndo();
            }
        }
        
        // Handle scenario run
        if (e.target.matches('[data-action="run-scenario"]')) {
            const scenario = e.target.dataset.scenario;
            if (typeof runScenario === 'function') {
                runScenario(scenario);
            }
        }
        
        // Handle build request
        if (e.target.matches('[data-action="request-build"]')) {
            if (typeof requestBuild === 'function') {
                requestBuild();
            }
        }
        
        // Handle config compare
        if (e.target.matches('[data-action="compare-config"]')) {
            if (typeof compareConfig === 'function') {
                compareConfig();
            }
        }
        
        // Handle wizard navigation
        if (e.target.matches('[data-action="wizard-nav"]')) {
            const direction = parseInt(e.target.dataset.direction);
            if (typeof wizardNav === 'function') {
                wizardNav(direction);
            }
        }
        
        // Handle safe defaults
        if (e.target.matches('[data-action="apply-safe-defaults"]')) {
            if (typeof applySafeDefaults === 'function') {
                applySafeDefaults();
            }
        }
        
        // Handle copy output
        if (e.target.matches('[data-action="copy-output"]')) {
            if (typeof copyOutput === 'function') {
                copyOutput();
            }
        }
        
        // Handle vault checkpoints toggle
        if (e.target.matches('[data-action="toggle-vault-checkpoints"]')) {
            if (typeof toggleVaultCheckpoints === 'function') {
                toggleVaultCheckpoints();
            }
        }
        
        // Handle open vault folder
        if (e.target.matches('[data-action="open-vault-folder"]')) {
            if (typeof openVaultFolder === 'function') {
                openVaultFolder();
            }
        }
        
        // Handle hardened build confirm
        if (e.target.matches('[data-action="confirm-hardened-build"]')) {
            if (typeof confirmHardenedBuild === 'function') {
                confirmHardenedBuild();
            }
        }
        
        // Handle close hardened secrets modal
        if (e.target.matches('[data-action="close-hardened-secrets-modal"]')) {
            if (typeof closeHardenedSecretsModal === 'function') {
                closeHardenedSecretsModal();
            }
        }
        
        // Handle build success actions
        if (e.target.matches('[data-action="restart-from-build-success"]')) {
            if (typeof restartFromBuildSuccess === 'function') {
                restartFromBuildSuccess();
            }
        }
        
        if (e.target.matches('[data-action="copy-primary-config"]')) {
            if (typeof copyPrimaryConfig === 'function') {
                copyPrimaryConfig();
            }
        }
        
        if (e.target.matches('[data-action="open-last-export-folder"]')) {
            if (typeof openLastExportFolder === 'function') {
                openLastExportFolder();
            }
        }
        
        if (e.target.matches('[data-action="close-build-success"]')) {
            if (typeof closeBuildSuccess === 'function') {
                closeBuildSuccess();
            }
        }
        
        // Handle builder actions
        if (e.target.matches('[data-action="builder-back"]')) {
            if (typeof builderBack === 'function') {
                builderBack();
            }
        }
        
        if (e.target.matches('[data-action="close-config-builder"]')) {
            if (typeof closeConfigBuilder === 'function') {
                closeConfigBuilder();
            }
        }
        
        if (e.target.matches('[data-action="builder-next"]')) {
            if (typeof builderNext === 'function') {
                builderNext();
            }
        }
        
        // Handle PO conflict resolution
        if (e.target.matches('[data-action="resolve-po-conflict"]')) {
            const resolve = e.target.dataset.resolve === 'true';
            if (typeof resolvePoConflict === 'function') {
                resolvePoConflict(resolve);
            }
        }
        
        // Handle modal close actions
        if (e.target.matches('[data-action="close-release-notes-modal"]')) {
            if (typeof closeReleaseNotesModal === 'function') {
                closeReleaseNotesModal();
            }
        }
        
        if (e.target.matches('[data-action="close-help"]')) {
            if (typeof closeHelp === 'function') {
                closeHelp();
            }
        }
        
        if (e.target.matches('[data-action="close-option-info"]')) {
            if (typeof closeOptionInfo === 'function') {
                closeOptionInfo();
            }
        }
        
        const saveSwitchEditTarget = e.target.closest('[data-action="save-switch-edit"]');
        if (saveSwitchEditTarget) {
            if (typeof saveSwitchEdit === 'function') {
                saveSwitchEdit();
            }
        }
        
        const closeEditSwitchModalTarget = e.target.closest('[data-action="close-edit-switch-modal"]');
        if (closeEditSwitchModalTarget) {
            if (typeof closeEditSwitchModal === 'function') {
                closeEditSwitchModal();
            }
        }
        
        const saveVPCEditTarget = e.target.closest('[data-action="save-vpc-edit"]');
        if (saveVPCEditTarget) {
            if (typeof saveVPCEdit === 'function') {
                saveVPCEdit();
            }
        }
        
        const closeEditVPCModalTarget = e.target.closest('[data-action="close-edit-vpc-modal"]');
        if (closeEditVPCModalTarget) {
            if (typeof closeEditVPCModal === 'function') {
                closeEditVPCModal();
            }
        }
        
        const saveNewVPCTarget = e.target.closest('[data-action="save-new-vpc"]');
        if (saveNewVPCTarget) {
            if (typeof saveNewVPC === 'function') {
                saveNewVPC();
            }
        }
        
        const closeAddVPCModalTarget = e.target.closest('[data-action="close-add-vpc-modal"]');
        if (closeAddVPCModalTarget) {
            if (typeof closeAddVPCModal === 'function') {
                closeAddVPCModal();
            }
        }
        
        const saveBulkVLANsTarget = e.target.closest('[data-action="save-bulk-vlans"]');
        if (saveBulkVLANsTarget) {
            if (typeof saveBulkVLANs === 'function') {
                saveBulkVLANs();
            }
        }
        
        const closeBulkAddVLANsModalTarget = e.target.closest('[data-action="close-bulk-add-vlans-modal"]');
        if (closeBulkAddVLANsModalTarget) {
            if (typeof closeBulkAddVLANsModal === 'function') {
                closeBulkAddVLANsModal();
            }
        }
        
        const saveVLANEditTarget = e.target.closest('[data-action="save-vlan-edit"]');
        if (saveVLANEditTarget) {
            if (typeof saveVLANEdit === 'function') {
                saveVLANEdit();
            }
        }
        
        const closeEditVLANModalTarget = e.target.closest('[data-action="close-edit-vlan-modal"]');
        if (closeEditVLANModalTarget) {
            if (typeof closeEditVLANModal === 'function') {
                closeEditVLANModal();
            }
        }
        
        const saveNewUplinkTarget = e.target.closest('[data-action="save-new-uplink"]');
        if (saveNewUplinkTarget) {
            if (typeof saveNewUplink === 'function') {
                saveNewUplink();
            }
        }
        
        const closeAddUplinkModalTarget = e.target.closest('[data-action="close-add-uplink-modal"]');
        if (closeAddUplinkModalTarget) {
            if (typeof closeAddUplinkModal === 'function') {
                closeAddUplinkModal();
            }
        }
        
        const saveUplinkEditTarget = e.target.closest('[data-action="save-uplink-edit"]');
        if (saveUplinkEditTarget) {
            if (typeof saveUplinkEdit === 'function') {
                saveUplinkEdit();
            }
        }
        
        const closeEditUplinkModalTarget = e.target.closest('[data-action="close-edit-uplink-modal"]');
        if (closeEditUplinkModalTarget) {
            if (typeof closeEditUplinkModal === 'function') {
                closeEditUplinkModal();
            }
        }
        
        const confirmAddSwitchTarget = e.target.closest('[data-action="confirm-add-switch"]');
        if (confirmAddSwitchTarget) {
            if (typeof confirmAddSwitch === 'function') {
                confirmAddSwitch();
            }
        }

        // close-modal: dynamically created modal overlays (e.g., Add Switch modal)
        const closeModalTarget = e.target.closest('[data-action="close-modal"]');
        if (closeModalTarget) {
            const modal = closeModalTarget.closest('.modal-overlay');
            if (modal) modal.remove();
        }
        
        // ── Results panel: view-config, view-port-map ──────────────────────
        const viewConfigTarget = e.target.closest('[data-action="view-config"]');
        if (viewConfigTarget) {
            const hostname = viewConfigTarget.dataset.hostname;
            if (hostname && window.lastDeploymentResults) {
                const r = window.lastDeploymentResults.results?.find(x => x.hostname === hostname);
                const cli = r?.export?.cli || r?.export?.config || 'No configuration available';
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.innerHTML = `<div class="modal-content modal-wide">
                    <h2>CLI Config — ${escapeHtml(hostname)}</h2>
                    <pre style="max-height:60vh;overflow:auto;font-size:12px;background:var(--bg-code,#0f172a);padding:1rem;border-radius:6px;">${escapeHtml(cli)}</pre>
                    <div class="btn-row"><button class="btn-outline" data-action="close-modal">Close</button></div>
                </div>`;
                document.body.appendChild(modal);
            }
        }

        const viewPortMapTarget = e.target.closest('[data-action="view-port-map"]');
        if (viewPortMapTarget) {
            const hostname = viewPortMapTarget.dataset.hostname;
            if (hostname && window.lastDeploymentResults) {
                const r = window.lastDeploymentResults.results?.find(x => x.hostname === hostname);
                const portMap = r?.device_config?.port_map;
                const portMapHtml = portMap?.ports?.length
                    ? portMap.ports.slice(0, 100).map(p =>
                        `<tr><td>${escapeHtml(p.name||'')}</td><td>${escapeHtml(p.type||'')}</td><td>${escapeHtml(p.description||'—')}</td></tr>`).join('')
                    : '<tr><td colspan="3">No port map data</td></tr>';
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.innerHTML = `<div class="modal-content modal-wide">
                    <h2>Port Map — ${escapeHtml(hostname)}</h2>
                    <div style="max-height:60vh;overflow:auto;">
                    <table style="width:100%;font-size:12px;border-collapse:collapse;">
                        <thead><tr><th style="text-align:left;padding:4px 8px;">Port</th><th style="text-align:left;padding:4px 8px;">Type</th><th style="text-align:left;padding:4px 8px;">Description</th></tr></thead>
                        <tbody>${portMapHtml}</tbody>
                    </table></div>
                    <div class="btn-row"><button class="btn-outline" data-action="close-modal">Close</button></div>
                </div>`;
                document.body.appendChild(modal);
            }
        }

        const closeDeploymentCompletionModalTarget = e.target.closest('[data-action="close-deployment-completion-modal"]');
        if (closeDeploymentCompletionModalTarget) {
            if (typeof closeDeploymentCompletionModal === 'function') {
                closeDeploymentCompletionModal();
            }
        }

        if (e.target.matches('[data-action="ms-back-to-editor"]')) {
            // Multi-switch: back to editor from results panel
            const resultsPanel = document.getElementById('multiSwitchResultsPanel');
            const fallback = document.getElementById('multiSwitchResultsPanelFallback');
            if (resultsPanel) { resultsPanel.classList.add('hidden'); resultsPanel.innerHTML = ''; }
            if (fallback) fallback.remove();
            const configEditor = document.getElementById('configurationEditor');
            if (configEditor) configEditor.classList.remove('hidden');
            const wizardNav = document.getElementById('wizardNav');
            if (wizardNav) wizardNav.classList.add('hidden');
            const roadmap = document.getElementById('roadmapSummary');
            if (roadmap) roadmap.classList.add('hidden');
        }

        if (e.target.matches('[data-action="edit-vpc"]')) {
            const index = e.target.dataset.index;
            if (typeof editVPC === 'function') {
                editVPC(parseInt(index));
            }
        }

        if (e.target.matches('[data-action="save-vpc-edit"]')) {
            if (typeof saveVPCEdit === 'function') {
                saveVPCEdit();
            }
        }

        if (e.target.matches('[data-action="close-edit-vpc-modal"]')) {
            if (typeof closeEditVPCModal === 'function') {
                closeEditVPCModal();
            }
        }

        if (e.target.matches('[data-action="remove-vpc"]')) {
            const index = e.target.dataset.index;
            if (typeof removeVPC === 'function') {
                removeVPC(parseInt(index));
            }
        }

        if (e.target.matches('[data-action="show-template-comparison"]')) {
            if (typeof showTemplateComparison === 'function') {
                showTemplateComparison();
            }
        }

        if (e.target.matches('[data-action="filter-templates"]')) {
            const filter = e.target.dataset.filter;
            if (typeof filterTemplates === 'function') {
                filterTemplates(filter);
            }
        }

        if (e.target.matches('[data-action="render-template-gallery"]')) {
            if (typeof renderTemplateGallery === 'function') {
                renderTemplateGallery();
            }
        }
        
        const downloadAllDeploymentConfigsTarget = e.target.closest('[data-action="download-all-deployment-configs"]');
        if (downloadAllDeploymentConfigsTarget) {
            if (typeof downloadAllDeploymentConfigs === 'function') {
                downloadAllDeploymentConfigs();
            }
        }
        
        // Handle close deployment results button
        if (e.target.matches('[data-action="close-deployment-results"]')) {
            const resultsPanel = document.getElementById('multiSwitchResultsPanel');
            const fallback = document.getElementById('multiSwitchResultsPanelFallback');
            if (resultsPanel) { 
                resultsPanel.classList.add('hidden'); 
                resultsPanel.innerHTML = ''; 
            }
            if (fallback) fallback.remove();
            const configEditor = document.getElementById('configurationEditor');
            if (configEditor) configEditor.classList.remove('hidden');
            const wizardNav = document.getElementById('wizardNav');
            if (wizardNav) wizardNav.classList.add('hidden');
            const roadmap = document.getElementById('roadmapSummary');
            if (roadmap) roadmap.classList.add('hidden');
        }
    });
    
    // UX-008 FIX: Handle change events for form inputs
    document.body.addEventListener('change', function(e) {
        // Handle toggle keepalive inputs
        if (e.target.matches('[data-action="toggle-keepalive-inputs"]')) {
            if (typeof toggleKeepaliveInputs === 'function') {
                toggleKeepaliveInputs();
            }
        }
        
        // Handle custom port map toggle
        if (e.target.matches('[data-action="custom-port-map-toggle"]')) {
            if (typeof onCustomPortMapToggle === 'function') {
                onCustomPortMapToggle();
            }
        }
        
        // Handle security tier change
        if (e.target.matches('[data-action="security-tier-change"]')) {
            if (typeof onSecurityTierChange === 'function') {
                onSecurityTierChange();
            }
        }
        
        // Handle save export dir
        if (e.target.matches('[data-action="save-export-dir"]')) {
            if (typeof saveExportDir === 'function') {
                saveExportDir();
            }
        }
        
        // Handle fetch vault
        if (e.target.matches('[data-action="fetch-vault"]')) {
            if (typeof fetchVault === 'function') {
                fetchVault();
            }
        }
        
        // Handle input validation
        if (e.target.matches('[data-action="validate-hostname"]')) {
            if (typeof validateHostname === 'function') {
                validateHostname(e.target);
            }
        }
        
        if (e.target.matches('[data-action="validate-ip"]')) {
            if (typeof validateIP === 'function') {
                validateIP(e.target);
            }
        }
        
        if (e.target.matches('[data-action="validate-vpc-domain"]')) {
            if (typeof validateVPCDomain === 'function') {
                validateVPCDomain(e.target);
            }
        }
        
        // filter-templates is handled in the click handler (line 593 is the correct one)
        
        const applyTemplateTarget = e.target.closest('[data-action="apply-template"]');
        if (applyTemplateTarget) {
            const templateId = applyTemplateTarget.dataset.templateId;
            console.log('[UI-HANDLERS] [APPLY_TEMPLATE] Click detected, templateId:', templateId);
            if (typeof applyTemplate === 'function') {
                console.log('[UI-HANDLERS] [APPLY_TEMPLATE] Calling applyTemplate function');
                applyTemplate(templateId);
            } else {
                console.error('[UI-HANDLERS] [APPLY_TEMPLATE] applyTemplate function not found');
            }
        }
        
        // filter-templates and show-template-comparison are handled in the click handler
        
        // Handle link planner actions
        if (e.target.matches('[data-action="expand-link-members"]')) {
            if (typeof expandLinkMembers === 'function') {
                expandLinkMembers(e.target);
            }
        }
        
        if (e.target.matches('[data-action="suggest-members-row"]')) {
            if (typeof suggestMembersForRow === 'function') {
                suggestMembersForRow(e.target);
            }
        }
        
        // Handle topology node selection
        if (e.target.matches('[data-action="select-topology-node"]')) {
            const nodeId = e.target.dataset.nodeId;
            if (typeof window.selectTopologyNode === 'function') {
                window.selectTopologyNode(nodeId);
            }
        }
        
        // Handle fabric questionnaire actions
        if (e.target.matches('[data-action="questionnaire-pick"]')) {
            const key = e.target.dataset.key;
            const value = e.target.dataset.value;
            if (typeof questionnairePick === 'function') {
                questionnairePick(key, parseInt(value));
            }
        }
        
        if (e.target.matches('[data-action="questionnaire-downlink-continue"]')) {
            if (typeof questionnaireNext === 'function') {
                questionnaireAnswers.downlink_name = document.getElementById('qDownName').value;
                questionnaireNext();
            }
        }
        
        if (e.target.matches('[data-action="questionnaire-auto-ports"]')) {
            const auto = e.target.dataset.auto === 'true';
            if (typeof applyQuestionnaireToPlanner === 'function') {
                questionnaireAnswers.auto_ports = auto;
                applyQuestionnaireToPlanner();
            }
        }
        
        if (e.target.matches('[data-action="skip-fabric-questionnaire"]')) {
            if (typeof skipFabricQuestionnaire === 'function') {
                skipFabricQuestionnaire();
            }
        }
        
        if (e.target.matches('[data-action="questionnaire-prev"]')) {
            if (typeof questionnairePrev === 'function') {
                questionnairePrev();
            }
        }
        
        // Handle builder actions
        if (e.target.matches('[data-action="pick-builder-choice"]')) {
            const questionId = e.target.dataset.question;
            const value = e.target.dataset.value;
            if (typeof pickBuilderChoice === 'function') {
                pickBuilderChoice(questionId, value);
            }
        }
        
        // Handle admin PO map actions
        if (e.target.matches('[data-action="save-po-map"]')) {
            if (typeof savePoMap === 'function') {
                savePoMap();
            }
        }
        
        if (e.target.matches('[data-action="load-po-map"]')) {
            if (typeof loadPoMap === 'function') {
                loadPoMap();
            }
        }

        // close-modal and confirm-add-switch are handled in the click handler above

        if (e.target.matches('[data-action="close-modal-by-id"]')) {
            const modalId = e.target.dataset.modalId;
            if (modalId) {
                const modal = document.getElementById(modalId);
                if (modal) modal.remove();
            }
            // Ensure wizard panel stays hidden in multi-switch mode after modal close
            if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode) {
                const wizardPanel = document.getElementById('wizardPanel');
                if (wizardPanel) {
                    wizardPanel.classList.add('hidden');
                }
            }
        }

        if (e.target.matches('[data-action="download-all-configs-close-modal"]')) {
            const modalId = e.target.dataset.modalId;
            if (typeof downloadAllConfigs === 'function') {
                downloadAllConfigs();
            }
            if (modalId) {
                const modal = document.getElementById(modalId);
                if (modal) modal.remove();
            }
            // Ensure wizard panel stays hidden in multi-switch mode after modal close
            if (typeof multiSwitchMode !== 'undefined' && multiSwitchMode) {
                const wizardPanel = document.getElementById('wizardPanel');
                if (wizardPanel) {
                    wizardPanel.classList.add('hidden');
                }
            }
        }

        if (e.target.matches('[data-action="reload-page"]')) {
            location.reload();
        }

        if (e.target.matches('[data-action="dismiss-error"]')) {
            if (typeof ErrorBoundary !== 'undefined' && typeof ErrorBoundary.hide === 'function') {
                ErrorBoundary.hide();
            }
        }

        if (e.target.matches('[data-action="download-all-configs"]')) {
            if (typeof downloadAllConfigs === 'function') {
                downloadAllConfigs();
            }
        }

        if (e.target.matches('[data-action="download-config"]')) {
            const hostname = e.target.dataset.hostname;
            const config = e.target.dataset.config;
            if (typeof downloadConfig === 'function' && hostname && config) {
                downloadConfig(hostname, config);
            } else if (typeof downloadConfig === 'function' && hostname && window.lastDeploymentResults) {
                // Try to get config from deployment results
                const result = window.lastDeploymentResults.results?.find(r => r.hostname === hostname);
                if (result) {
                    const configData = result.export?.cli || result.export?.config || result.export?.raw?.config_preview || "";
                    downloadConfig(hostname, configData);
                }
            }
        }

        if (e.target.matches('[data-action="view-config"]')) {
            const hostname = e.target.dataset.hostname;
            if (hostname && window.lastDeploymentResults) {
                const result = window.lastDeploymentResults.results?.find(r => r.hostname === hostname);
                if (result) {
                    const config = result.export?.cli || result.export?.config || result.export?.raw?.config_preview || "";
                    const safeHostname = escapeHtml(hostname);
                    const modalId = 'config-view-modal';
                    let modal = document.getElementById(modalId);
                    if (!modal) {
                        modal = document.createElement('div');
                        modal.id = modalId;
                        modal.className = 'modal-backdrop';
                        document.body.appendChild(modal);
                    }
                    modal.innerHTML = `
                        <div class="modal-dialog" style="max-width: 800px; max-height: 80vh; overflow-y: auto; padding: 24px; background: var(--bg-card, #1e293b); color: var(--text-main, #f8fafc); border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
                                <h3 style="margin:0; color: #38bdf8;">Configuration: ${safeHostname}</h3>
                                <button data-action="close-modal-by-id" data-modal-id="${modalId}" style="background:none; border:none; color:#94a3b8; font-size:20px; cursor:pointer;">&times;</button>
                            </div>
                            <pre style="background: rgba(0,0,0,0.3); padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 12px; line-height: 1.4; color: #e2e8f0;">${escapeHtml(config)}</pre>
                            <div style="margin-top: 16px; display:flex; justify-content:flex-end;">
                                <button type="button" class="btn-secondary" data-action="close-modal-by-id" data-modal-id="${modalId}" style="padding: 8px 16px; border-radius: 6px; cursor:pointer;">Close</button>
                            </div>
                        </div>
                    `;
                    modal.style.display = 'flex';
                }
            }
        }

        if (e.target.matches('[data-action="view-port-map"]')) {
            const hostname = e.target.dataset.hostname;
            if (hostname && deployment.switches) {
                const sw = deployment.switches.find(s => s.hostname === hostname);
                if (sw && sw.device_config) {
                    const safeHostname = escapeHtml(hostname);
                    const modalId = 'port-map-view-modal';
                    let modal = document.getElementById(modalId);
                    if (!modal) {
                        modal = document.createElement('div');
                        modal.id = modalId;
                        modal.className = 'modal-backdrop';
                        document.body.appendChild(modal);
                    }
                    // Generate port map HTML
                    let portMapHtml = '';
                    try {
                        portMapHtml = renderPortMapForSwitch(hostname, sw.device_config);
                    } catch (error) {
                        portMapHtml = `<div class="error-message">Error generating port map: ${escapeHtml(error.message)}</div>`;
                    }
                    modal.innerHTML = `
                        <div class="modal-dialog" style="max-width: 900px; max-height: 80vh; overflow-y: auto; padding: 24px; background: var(--bg-card, #1e293b); color: var(--text-main, #f8fafc); border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
                                <h3 style="margin:0; color: #38bdf8;">Port Map: ${safeHostname}</h3>
                                <button data-action="close-modal-by-id" data-modal-id="${modalId}" style="background:none; border:none; color:#94a3b8; font-size:20px; cursor:pointer;">&times;</button>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 16px; border-radius: 8px; overflow-x: auto;">${portMapHtml}</div>
                            <div style="margin-top: 16px; display:flex; justify-content:flex-end;">
                                <button type="button" class="btn-secondary" data-action="close-modal-by-id" data-modal-id="${modalId}" style="padding: 8px 16px; border-radius: 6px; cursor:pointer;">Close</button>
                            </div>
                        </div>
                    `;
                    modal.style.display = 'flex';
                }
            }
        }

        if (e.target.matches('[data-action="remove-parent"]')) {
            if (e.target.parentElement) {
                e.target.parentElement.remove();
            }
        }

        if (e.target.matches('[data-action="save-vpc-pair"]')) {
            if (typeof saveVpcPair === 'function') {
                saveVpcPair();
            }
        }

        if (e.target.matches('[data-action="save-uplink"]')) {
            if (typeof saveUplink === 'function') {
                saveUplink();
            }
        }

        if (e.target.matches('[data-action="select-topology-node"]')) {
            const hostname = e.target.dataset.hostname;
            if (typeof selectTopologyNode === 'function' && hostname) {
                selectTopologyNode(hostname);
            }
        }

        if (e.target.matches('[data-action="switch-tab"]')) {
            const tab = e.target.dataset.tab;
            if (typeof switchTab === 'function' && tab) {
                switchTab(tab);
            }
        }

        if (e.target.matches('[data-action="toggle-config-panel"]')) {
            const panel = e.target.dataset.panel;
            if (typeof toggleConfigPanel === 'function' && panel) {
                toggleConfigPanel(panel);
            }
        }

        if (e.target.matches('[data-action="fix-validation-error"]')) {
            const index = e.target.dataset.index;
            if (typeof fixValidationError === 'function' && index !== undefined) {
                fixValidationError(parseInt(index));
            }
        }

        if (e.target.matches('[data-action="log-model-change"]')) {
            console.log('[SWITCH_ADD] [USER_ACTION] User selected model:', e.target.value);
        }

        if (e.target.matches('[data-action="log-role-change"]')) {
            console.log('[SWITCH_ADD] [USER_ACTION] User selected role:', e.target.value);
        }

        if (e.target.matches('[data-action="log-vpc-primary-change"]')) {
            console.log('[VPC_PAIR_ADD] [USER_ACTION] User selected primary switch:', e.target.value);
        }

        if (e.target.matches('[data-action="log-vpc-secondary-change"]')) {
            console.log('[VPC_PAIR_ADD] [USER_ACTION] User selected secondary switch:', e.target.value);
        }

        if (e.target.matches('[data-action="log-vpc-primary-change-edit"]')) {
            console.log('[VPC_PAIR_EDIT] [USER_ACTION] User selected primary switch:', e.target.value);
        }

        if (e.target.matches('[data-action="log-vpc-secondary-change-edit"]')) {
            console.log('[VPC_PAIR_EDIT] [USER_ACTION] User selected secondary switch:', e.target.value);
        }
    });
});
