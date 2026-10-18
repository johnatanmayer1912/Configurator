/**
 * Validation UI Module - Display configuration validation results
 * 
 * Provides user-friendly validation feedback with:
 * - Severity indicators and color coding
 * - Error/warning/suggestion display
 * - Fix command quick actions
 * - Line number highlighting
 * - Filtering and sorting
 */

class ValidationUI {
    constructor() {
        this.currentValidation = null;
        this.filter = 'all'; // all, errors, warnings, suggestions
        this.sortBy = 'severity'; // severity, line, code
    }

    /**
     * Display validation results in the UI
     */
    displayResults(validationResult) {
        this.currentValidation = validationResult;
        
        // Create or update validation panel
        let panel = document.getElementById('validation-panel');
        if (!panel) {
            panel = this.createValidationPanel();
            document.body.appendChild(panel);
        }
        
        // Update panel content
        this.updatePanelContent(panel, validationResult);
        
        // Show panel
        panel.classList.remove('hidden');
    }

    /**
     * Create validation panel DOM structure
     */
    createValidationPanel() {
        const panel = document.createElement('div');
        panel.id = 'validation-panel';
        panel.className = 'validation-panel hidden';
        
        panel.innerHTML = `
            <div class="validation-header">
                <div class="validation-title">
                    <span class="validation-status-icon"></span>
                    <span class="validation-status-text">Validation Results</span>
                </div>
                <div class="validation-controls">
                    <select id="validation-filter" class="validation-filter">
                        <option value="all">All Issues</option>
                        <option value="errors">Errors Only</option>
                        <option value="warnings">Warnings Only</option>
                        <option value="suggestions">Suggestions Only</option>
                    </select>
                    <select id="validation-sort" class="validation-sort">
                        <option value="severity">Sort by Severity</option>
                        <option value="line">Sort by Line Number</option>
                        <option value="code">Sort by Code</option>
                    </select>
                    <button id="validation-close" class="validation-close" title="Close">×</button>
                </div>
            </div>
            <div class="validation-summary">
                <div class="summary-item">
                    <span class="summary-label">Status:</span>
                    <span class="summary-status"></span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Severity:</span>
                    <span class="summary-severity"></span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Errors:</span>
                    <span class="summary-count error-count">0</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Warnings:</span>
                    <span class="summary-count warning-count">0</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Suggestions:</span>
                    <span class="summary-count suggestion-count">0</span>
                </div>
            </div>
            <div class="validation-content">
                <div class="validation-list" id="validation-list"></div>
            </div>
        `;
        
        // Add event listeners
        panel.querySelector('#validation-close').addEventListener('click', () => {
            this.hide();
        });
        
        panel.querySelector('#validation-filter').addEventListener('change', (e) => {
            this.filter = e.target.value;
            this.updatePanelContent(panel, this.currentValidation);
        });
        
        panel.querySelector('#validation-sort').addEventListener('change', (e) => {
            this.sortBy = e.target.value;
            this.updatePanelContent(panel, this.currentValidation);
        });
        
        return panel;
    }

    /**
     * Update panel content with validation results
     */
    updatePanelContent(panel, result) {
        // Update summary
        const summaryStatus = panel.querySelector('.summary-status');
        const summarySeverity = panel.querySelector('.summary-severity');
        const errorCount = panel.querySelector('.error-count');
        const warningCount = panel.querySelector('.warning-count');
        const suggestionCount = panel.querySelector('.suggestion-count');
        
        summaryStatus.textContent = result.is_valid ? 'Valid' : 'Invalid';
        summaryStatus.className = 'summary-status ' + (result.is_valid ? 'valid' : 'invalid');
        
        summarySeverity.textContent = result.severity;
        summarySeverity.className = 'summary-severity severity-' + result.severity;
        
        errorCount.textContent = result.errors.length;
        warningCount.textContent = result.warnings.length;
        suggestionCount.textContent = result.suggestions.length;
        
        // Update status icon
        const statusIcon = panel.querySelector('.validation-status-icon');
        statusIcon.className = 'validation-status-icon ' + (result.is_valid ? 'icon-valid' : 'icon-invalid');
        
        // Build issue list
        const list = panel.querySelector('#validation-list');
        list.innerHTML = '';
        
        const issues = this.collectIssues(result);
        const filteredIssues = this.filterIssues(issues);
        const sortedIssues = this.sortIssues(filteredIssues);
        
        if (sortedIssues.length === 0) {
            list.innerHTML = '<div class="validation-empty">No issues to display</div>';
            return;
        }
        
        sortedIssues.forEach(issue => {
            const item = this.createIssueItem(issue);
            list.appendChild(item);
        });
    }

    /**
     * Collect all issues from validation result
     */
    collectIssues(result) {
        const issues = [];
        
        result.errors.forEach(error => {
            issues.push({
                type: 'error',
                ...error
            });
        });
        
        result.warnings.forEach(warning => {
            issues.push({
                type: 'warning',
                ...warning
            });
        });
        
        result.suggestions.forEach(suggestion => {
            issues.push({
                type: 'suggestion',
                ...suggestion
            });
        });
        
        return issues;
    }

    /**
     * Filter issues based on current filter
     */
    filterIssues(issues) {
        if (this.filter === 'all') {
            return issues;
        }
        return issues.filter(issue => issue.type === this.filter.slice(0, -1)); // Remove 's' from plural
    }

    /**
     * Sort issues based on current sort order
     */
    sortIssues(issues) {
        const severityOrder = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4 };
        
        return issues.sort((a, b) => {
            if (this.sortBy === 'severity') {
                const severityA = severityOrder[a.severity] || 99;
                const severityB = severityOrder[b.severity] || 99;
                return severityA - severityB;
            } else if (this.sortBy === 'line') {
                const lineA = a.line_number || 0;
                const lineB = b.line_number || 0;
                return lineA - lineB;
            } else if (this.sortBy === 'code') {
                const codeA = (a.error_code || a.warning_code || a.suggestion_code) || '';
                const codeB = (b.error_code || b.warning_code || b.suggestion_code) || '';
                return codeA.localeCompare(codeB);
            }
            return 0;
        });
    }

    /**
     * Create issue item DOM element
     */
    createIssueItem(issue) {
        const item = document.createElement('div');
        item.className = `validation-item issue-${issue.type} severity-${issue.severity}`;
        
        const code = issue.error_code || issue.warning_code || issue.suggestion_code || 'UNKNOWN';
        const message = issue.message || issue.description || '';
        const line = issue.line_number || '?';
        const lineContent = issue.line_content || '';
        const suggestion = issue.suggestion || '';
        const fixCommand = issue.fix_command || '';
        
        item.innerHTML = `
            <div class="issue-header">
                <span class="issue-type-icon icon-${issue.type}"></span>
                <span class="issue-code">${code}</span>
                <span class="issue-severity severity-badge severity-${issue.severity}">${issue.severity}</span>
                <span class="issue-line">Line ${line}</span>
            </div>
            <div class="issue-message">${message}</div>
            ${lineContent ? `<div class="issue-line-content"><code>${this.escapeHtml(lineContent)}</code></div>` : ''}
            ${suggestion ? `<div class="issue-suggestion"><strong>Suggestion:</strong> ${suggestion}</div>` : ''}
            ${fixCommand ? `
                <div class="issue-fix">
                    <strong>Fix Command:</strong>
                    <code class="fix-command">${this.escapeHtml(fixCommand)}</code>
                    <button class="copy-fix-btn" data-command="${this.escapeHtml(fixCommand)}">Copy</button>
                </div>
            ` : ''}
        `;
        
        // Add copy button functionality
        const copyBtn = item.querySelector('.copy-fix-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyToClipboard(fixCommand);
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            });
        }
        
        return item;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            console.error('Failed to copy:', err);
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    /**
     * Hide validation panel
     */
    hide() {
        const panel = document.getElementById('validation-panel');
        if (panel) {
            panel.classList.add('hidden');
            panel.classList.remove('visible');
        }
        
        // Also dismiss legacy validation panel if it exists
        const legacyPanel = document.getElementById('validationPanel');
        if (legacyPanel) {
            legacyPanel.classList.remove('visible');
            legacyPanel.setAttribute('aria-hidden', 'true');
        }
    }

    /**
     * Clear validation results
     */
    clear() {
        this.currentValidation = null;
        this.hide();
    }
}

// Global instance
const validationUI = new ValidationUI();

/**
 * Validate configuration via API
 */
async function validateConfiguration(configText, hardwareModel, nxosVersion, validationLevel = 'standard', baselineOptions = []) {
    try {
        const response = await fetch('/config/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config_text: configText,
                hardware_model: hardwareModel,
                nxos_version: nxosVersion,
                validation_level: validationLevel,
                baseline_options: baselineOptions
            })
        });
        
        if (!response.ok) {
            throw new Error(`Validation failed: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Display results in UI
        validationUI.displayResults(result);
        
        return result;
    } catch (error) {
        console.error('Validation error:', error);
        throw error;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ValidationUI, validationUI, validateConfiguration };
}
