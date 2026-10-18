/**
 * Configuration Comparator - Configuration Comparison Tools
 * 
 * Provides network engineers with comprehensive configuration comparison capabilities:
 * - Side-by-side configuration comparison
 * - Line-by-line diff visualization
 * - Configuration change detection
 * - Configuration rollback support
 * - Configuration versioning
 * - Configuration merge capabilities
 */

class ConfigComparator {
    constructor() {
        this.configurations = new Map();
        this.comparisons = new Map();
    }

    /**
     * Store a configuration with metadata
     */
    storeConfiguration(configId, configText, metadata = {}) {
        const config = {
            config_id: configId,
            config_text: configText,
            metadata: {
                switch_name: metadata.switch_name || 'unknown',
                hardware_model: metadata.hardware_model || 'unknown',
                nxos_version: metadata.nxos_version || 'unknown',
                timestamp: metadata.timestamp || new Date().toISOString(),
                description: metadata.description || '',
                author: metadata.author || 'unknown'
            },
            lines: configText.split('\n'),
            hash: this.generateHash(configText),
            created_at: new Date().toISOString()
        };

        this.configurations.set(configId, config);
        return config;
    }

    /**
     * Generate hash for configuration
     */
    generateHash(text) {
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            const char = text.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString(16);
    }

    /**
     * Compare two configurations
     */
    compareConfigs(configId1, configId2, options = {}) {
        const config1 = this.configurations.get(configId1);
        const config2 = this.configurations.get(configId2);

        if (!config1) {
            throw new Error(`Configuration ${configId1} not found`);
        }
        if (!config2) {
            throw new Error(`Configuration ${configId2} not found`);
        }

        const comparison = {
            comparison_id: `${configId1}_vs_${configId2}`,
            config1_id: configId1,
            config2_id: configId2,
            config1_metadata: config1.metadata,
            config2_metadata: config2.metadata,
            identical: config1.hash === config2.hash,
            changes: [],
            additions: [],
            deletions: [],
            modifications: [],
            statistics: {},
            created_at: new Date().toISOString()
        };

        if (!comparison.identical) {
            const diff = this.computeDiff(config1.lines, config2.lines, options);
            comparison.changes = diff.changes;
            comparison.additions = diff.additions;
            comparison.deletions = diff.deletions;
            comparison.modifications = diff.modifications;
            comparison.statistics = this.computeStatistics(diff);
        }

        this.comparisons.set(comparison.comparison_id, comparison);
        return comparison;
    }

    /**
     * Compute line-by-line diff between configurations
     */
    computeDiff(lines1, lines2, options = {}) {
        const ignoreWhitespace = options.ignoreWhitespace !== false;
        const ignoreComments = options.ignoreComments || false;
        const caseSensitive = options.caseSensitive !== false;

        const processedLines1 = this.preprocessLines(lines1, ignoreWhitespace, ignoreComments, caseSensitive);
        const processedLines2 = this.preprocessLines(lines2, ignoreWhitespace, ignoreComments, caseSensitive);

        const lcs = this.computeLCS(processedLines1, processedLines2);
        
        const changes = [];
        const additions = [];
        const deletions = [];
        const modifications = [];

        let i = 0, j = 0;
        while (i < processedLines1.length || j < processedLines2.length) {
            if (i < processedLines1.length && j < processedLines2.length && 
                processedLines1[i] === processedLines2[j]) {
                // Lines match
                i++;
                j++;
            } else {
                // Lines differ
                if (i < processedLines1.length && j < processedLines2.length) {
                    // Modification
                    modifications.push({
                        line_number_1: i + 1,
                        line_number_2: j + 1,
                        old_line: lines1[i],
                        new_line: lines2[j]
                    });
                    i++;
                    j++;
                } else if (i < processedLines1.length) {
                    // Deletion
                    deletions.push({
                        line_number: i + 1,
                        line: lines1[i]
                    });
                    i++;
                } else if (j < processedLines2.length) {
                    // Addition
                    additions.push({
                        line_number: j + 1,
                        line: lines2[j]
                    });
                    j++;
                }
            }
        }

        return { changes, additions, deletions, modifications };
    }

    /**
     * Preprocess lines for comparison
     */
    preprocessLines(lines, ignoreWhitespace, ignoreComments, caseSensitive) {
        return lines.map(line => {
            let processed = line;
            
            if (ignoreWhitespace) {
                processed = processed.trim();
            }
            
            if (ignoreComments && processed.startsWith('!')) {
                processed = '';
            }
            
            if (!caseSensitive) {
                processed = processed.toLowerCase();
            }
            
            return processed;
        });
    }

    /**
     * Compute Longest Common Subsequence
     */
    computeLCS(arr1, arr2) {
        const m = arr1.length;
        const n = arr2.length;
        const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                if (arr1[i - 1] === arr2[j - 1]) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        // Reconstruct LCS
        const lcs = [];
        let i = m, j = n;
        while (i > 0 && j > 0) {
            if (arr1[i - 1] === arr2[j - 1]) {
                lcs.unshift(arr1[i - 1]);
                i--;
                j--;
            } else if (dp[i - 1][j] > dp[i][j - 1]) {
                i--;
            } else {
                j--;
            }
        }

        return lcs;
    }

    /**
     * Compute statistics from diff
     */
    computeStatistics(diff) {
        return {
            total_changes: diff.changes.length,
            total_additions: diff.additions.length,
            total_deletions: diff.deletions.length,
            total_modifications: diff.modifications.length,
            change_percentage: this.calculateChangePercentage(diff)
        };
    }

    /**
     * Calculate percentage of lines changed
     */
    calculateChangePercentage(diff) {
        const totalChanges = diff.additions.length + diff.deletions.length + diff.modifications.length;
        const totalLines = diff.additions.length + diff.deletions.length + diff.modifications.length + 
                          (diff.changes.length - diff.modifications.length);
        
        if (totalLines === 0) return 0;
        return ((totalChanges / totalLines) * 100).toFixed(2);
    }

    /**
     * Generate unified diff format
     */
    generateUnifiedDiff(configId1, configId2) {
        const comparison = this.compareConfigs(configId1, configId2);
        const config1 = this.configurations.get(configId1);
        const config2 = this.configurations.get(configId2);

        let diff = '';
        diff += `--- ${config1.metadata.switch_name} (${config1.metadata.timestamp})\n`;
        diff += `+++ ${config2.metadata.switch_name} (${config2.metadata.timestamp})\n`;
        diff += `@@ Configuration Comparison @@\n`;

        for (const deletion of comparison.deletions) {
            diff += `- ${deletion.line}\n`;
        }

        for (const addition of comparison.additions) {
            diff += `+ ${addition.line}\n`;
        }

        for (const modification of comparison.modifications) {
            diff += `- ${modification.old_line}\n`;
            diff += `+ ${modification.new_line}\n`;
        }

        return diff;
    }

    /**
     * Generate side-by-side comparison view
     */
    generateSideBySideView(configId1, configId2) {
        const comparison = this.compareConfigs(configId1, configId2);
        const config1 = this.configurations.get(configId1);
        const config2 = this.configurations.get(configId2);

        const view = {
            left_panel: {
                title: `${config1.metadata.switch_name} (${config1.metadata.timestamp})`,
                lines: config1.lines,
                changes: comparison.deletions.map(d => d.line_number)
            },
            right_panel: {
                title: `${config2.metadata.switch_name} (${config2.metadata.timestamp})`,
                lines: config2.lines,
                changes: comparison.additions.map(a => a.line_number)
            },
            modifications: comparison.modifications
        };

        return view;
    }

    /**
     * Find configuration differences by keyword
     */
    findDifferencesByKeyword(configId1, configId2, keyword) {
        const comparison = this.compareConfigs(configId1, configId2);
        const keywordLower = keyword.toLowerCase();

        const relevantChanges = comparison.changes.filter(change => {
            if (change.old_line && change.old_line.toLowerCase().includes(keywordLower)) return true;
            if (change.new_line && change.new_line.toLowerCase().includes(keywordLower)) return true;
            return false;
        });

        return {
            keyword: keyword,
            total_matches: relevantChanges.length,
            matches: relevantChanges
        };
    }

    /**
     * Generate rollback configuration
     */
    generateRollbackConfig(configId1, configId2) {
        const comparison = this.compareConfigs(configId1, configId2);
        
        // Generate commands to revert from config2 to config1
        const rollbackCommands = [];
        
        for (const addition of comparison.additions) {
            // Find the interface or section this line belongs to
            const section = this.findSection(configId2, addition.line_number);
            if (section) {
                rollbackCommands.push(`configure terminal`);
                rollbackCommands.push(section);
                rollbackCommands.push(`  no ${addition.line.trim()}`);
                rollbackCommands.push(`  exit`);
            }
        }

        for (const modification of comparison.modifications) {
            const section = this.findSection(configId2, modification.line_number_2);
            if (section) {
                rollbackCommands.push(`configure terminal`);
                rollbackCommands.push(section);
                rollbackCommands.push(`  no ${modification.new_line.trim()}`);
                rollbackCommands.push(`  ${modification.old_line.trim()}`);
                rollbackCommands.push(`  exit`);
            }
        }

        return rollbackCommands.join('\n');
    }

    /**
     * Find configuration section for a line
     */
    findSection(configId, lineNumber) {
        const config = this.configurations.get(configId);
        if (!config) return null;

        const lines = config.lines;
        let section = null;

        // Search backwards from the line to find the section header
        for (let i = lineNumber - 1; i >= 0; i--) {
            const line = lines[i].trim();
            if (line.startsWith('interface ') || line.startsWith('vlan ') || 
                line.startsWith('vpc domain ') || line.startsWith('router ')) {
                section = line;
                break;
            }
        }

        return section;
    }

    /**
     * Merge two configurations
     */
    mergeConfigs(configId1, configId2, options = {}) {
        const config1 = this.configurations.get(configId1);
        const config2 = this.configurations.get(configId2);

        if (!config1 || !config2) {
            throw new Error('One or both configurations not found');
        }

        const comparison = this.compareConfigs(configId1, configId2);
        
        let mergedConfig = config1.config_text;
        const mergeStrategy = options.strategy || 'prefer_new'; // prefer_new, prefer_old, manual

        if (mergeStrategy === 'prefer_new') {
            // Apply all additions and modifications from config2
            for (const addition of comparison.additions) {
                mergedConfig += `\n${addition.line}`;
            }
            for (const modification of comparison.modifications) {
                mergedConfig = mergedConfig.replace(modification.old_line, modification.new_line);
            }
        } else if (mergeStrategy === 'prefer_old') {
            // Keep original config, ignore changes from config2
            // No changes needed
        }

        const mergedConfigId = `merged_${configId1}_${configId2}_${Date.now()}`;
        return this.storeConfiguration(mergedConfigId, mergedConfig, {
            switch_name: 'merged_config',
            description: `Merged configuration from ${configId1} and ${configId2}`,
            author: 'config_comparator'
        });
    }

    /**
     * Get configuration history
     */
    getConfigurationHistory(configId) {
        const config = this.configurations.get(configId);
        if (!config) {
            throw new Error(`Configuration ${configId} not found`);
        }

        const relatedComparisons = [];
        for (const [compId, comparison] of this.comparisons) {
            if (comparison.config1_id === configId || comparison.config2_id === configId) {
                relatedComparisons.push(comparison);
            }
        }

        return {
            config: config,
            related_comparisons: relatedComparisons.sort((a, b) => 
                new Date(b.created_at) - new Date(a.created_at)
            )
        };
    }

    /**
     * Export comparison report
     */
    exportComparisonReport(configId1, configId2) {
        const comparison = this.compareConfigs(configId1, configId2);
        
        const report = {
            comparison_id: comparison.comparison_id,
            generated_at: new Date().toISOString(),
            config1: comparison.config1_metadata,
            config2: comparison.config2_metadata,
            summary: {
                identical: comparison.identical,
                statistics: comparison.statistics
            },
            detailed_changes: {
                additions: comparison.additions,
                deletions: comparison.deletions,
                modifications: comparison.modifications
            },
            unified_diff: this.generateUnifiedDiff(configId1, configId2)
        };

        return JSON.stringify(report, null, 2);
    }

    /**
     * Validate configuration consistency
     */
    validateConsistency(configId) {
        const config = this.configurations.get(configId);
        if (!config) {
            throw new Error(`Configuration ${configId} not found`);
        }

        const issues = [];
        const warnings = [];

        // Check for duplicate interface configurations
        const interfaces = new Map();
        for (let i = 0; i < config.lines.length; i++) {
            const line = config.lines[i].trim();
            if (line.startsWith('interface ')) {
                const interfaceName = line.substring(10).trim();
                if (interfaces.has(interfaceName)) {
                    issues.push({
                        type: 'duplicate_interface',
                        line_number: i + 1,
                        message: `Duplicate interface configuration: ${interfaceName}`,
                        severity: 'error'
                    });
                } else {
                    interfaces.set(interfaceName, []);
                }
                interfaces.get(interfaceName).push(i + 1);
            }
        }

        // Check for VLAN consistency
        const vlans = new Set();
        for (let i = 0; i < config.lines.length; i++) {
            const line = config.lines[i].trim();
            if (line.startsWith('vlan ')) {
                const match = line.match(/vlan (\d+)/);
                if (match) {
                    const vlanId = parseInt(match[1], 10);
                    if (vlanId < 1 || vlanId > 4094) {
                        warnings.push({
                            type: 'invalid_vlan',
                            line_number: i + 1,
                            message: `VLAN ${vlanId} is outside valid range (1-4094)`,
                            severity: 'warning'
                        });
                    }
                }
            }
        }

        return {
            valid: issues.length === 0,
            issues: issues,
            warnings: warnings
        };
    }

    /**
     * Delete configuration
     */
    deleteConfiguration(configId) {
        // Also delete related comparisons
        for (const [compId, comparison] of this.comparisons) {
            if (comparison.config1_id === configId || comparison.config2_id === configId) {
                this.comparisons.delete(compId);
            }
        }
        
        return this.configurations.delete(configId);
    }

    /**
     * List all configurations
     */
    listConfigurations() {
        return Array.from(this.configurations.values()).map(config => ({
            config_id: config.config_id,
            metadata: config.metadata,
            hash: config.hash,
            created_at: config.created_at
        }));
    }

    /**
     * Clear all configurations
     */
    clearAllConfigurations() {
        this.configurations.clear();
        this.comparisons.clear();
    }
}

// Global instance
const configComparator = new ConfigComparator();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ConfigComparator, configComparator };
}
