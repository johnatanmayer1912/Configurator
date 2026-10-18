/**
 * vPC Configurator - Advanced vPC Configuration Tools
 * 
 * Provides network engineers with comprehensive vPC configuration capabilities:
 * - vPC domain management
 * - Peer-link configuration
 * - Keepalive link setup
 * - Consistency parameter validation
 * - vPC topology visualization
 */

class VPCConfigurator {
    constructor() {
        this.vpcDomains = new Map();
        this.currentDomain = null;
    }

    /**
     * Create a new vPC domain
     */
    createDomain(domainId, primarySwitch, secondarySwitch, options = {}) {
        const domain = {
            domain_id: domainId,
            primary_switch: primarySwitch,
            secondary_switch: secondarySwitch,
            peer_link_ports: options.peer_link_ports || 'E1/35-36',
            keepalive_ports: options.keepalive_ports || 'E1/37',
            keepalive_ip_primary: options.keepalive_ip_primary || '192.168.1.1/30',
            keepalive_ip_secondary: options.keepalive_ip_secondary || '192.168.1.2/30',
            role_priority: options.role_priority || { primary: 100, secondary: 200 },
            auto_recovery: options.auto_recovery !== false,
            delay_restore: options.delay_restore || 30,
            peer_gateway: options.peer_gateway !== false,
            ip_hash: options.ip_hash || 'src-dst',
            consistency_check: options.consistency_check !== false,
            created_at: new Date().toISOString()
        };

        this.vpcDomains.set(domainId, domain);
        this.currentDomain = domainId;
        
        return domain;
    }

    /**
     * Generate vPC configuration for a switch
     */
    generateConfig(domainId, switchRole) {
        const domain = this.vpcDomains.get(domainId);
        if (!domain) {
            throw new Error(`vPC domain ${domainId} not found`);
        }

        const isPrimary = switchRole === 'primary';
        const switchName = isPrimary ? domain.primary_switch : domain.secondary_switch;
        const priority = isPrimary ? domain.role_priority.primary : domain.role_priority.secondary;
        const keepaliveIP = isPrimary ? domain.keepalive_ip_primary : domain.keepalive_ip_secondary;

        let config = [];
        
        // vPC domain configuration
        config.push(`! vPC Domain ${domain.domain_id}`);
        config.push(`vpc domain ${domain.domain_id}`);
        config.push(`  role priority ${priority}`);
        
        if (isPrimary) {
            config.push(`  peer-keepalive destination ${domain.keepalive_ip_secondary} source ${domain.keepalive_ip_primary} vrf management`);
        } else {
            config.push(`  peer-keepalive destination ${domain.keepalive_ip_primary} source ${domain.keepalive_ip_secondary} vrf management`);
        }
        
        config.push(`  delay restore ${domain.delay_restore}`);
        
        if (domain.auto_recovery) {
            config.push(`  auto-recovery`);
        }
        
        // Peer-link configuration
        config.push(`! vPC Peer-Link`);
        config.push(`interface port-channel${domain.domain_id}`);
        config.push(`  description vPC Peer-Link`);
        config.push(`  switchport mode trunk`);
        config.push(`  switchport trunk allowed vlan 1-3967,4048-4093`);
        config.push(`  spanning-tree port type network`);
        config.push(`  vpc peer-link`);
        
        // Configure member ports
        const portRange = domain.peer_link_ports;
        config.push(`interface ${portRange}`);
        config.push(`  description vPC Peer-Link Member`);
        config.push(`  switchport mode trunk`);
        config.push(`  channel-group ${domain.domain_id} mode active`);
        
        // vPC consistency parameters
        if (domain.consistency_check) {
            config.push(`! vPC Consistency Parameters`);
            config.push(`vpc domain ${domain.domain_id}`);
            config.push(`  peer-gateway`);
            config.push(`  ip arp synchronize`);
        }
        
        // Keepalive interface
        config.push(`! vPC Keepalive`);
        config.push(`interface ${domain.keepalive_ports}`);
        config.push(`  description vPC Keepalive`);
        config.push(`  no shutdown`);
        
        return config.join('\n');
    }

    /**
     * Validate vPC configuration
     */
    validateConfiguration(domainId) {
        const domain = this.vpcDomains.get(domainId);
        if (!domain) {
            return { valid: false, errors: [`vPC domain ${domainId} not found`] };
        }

        const errors = [];
        const warnings = [];

        // Validate domain ID range
        if (domain.domain_id < 1 || domain.domain_id > 4096) {
            errors.push('vPC domain ID must be between 1 and 4096');
        }

        // Validate priority values
        if (domain.role_priority.primary < 1 || domain.role_priority.primary > 65535) {
            errors.push('Primary switch role priority must be between 1 and 65535');
        }
        if (domain.role_priority.secondary < 1 || domain.role_priority.secondary > 65535) {
            errors.push('Secondary switch role priority must be between 1 and 65535');
        }

        // Validate priority difference
        if (domain.role_priority.primary === domain.role_priority.secondary) {
            errors.push('Primary and secondary switch priorities must');
        }

        // Validate IP addresses
        if (!this.isValidIP(domain.keepalive_ip_primary)) {
            errors.push('Invalid primary keepalive IP address');
        }
        if (!this.isValidIP(domain.keepalive_ip_secondary)) {
            errors.push('Invalid secondary keepalive IP address');
        }

        // Validate port format
        if (!this.isValidPortFormat(domain.peer_link_ports)) {
            warnings.push('Peer-link port format may be invalid (expected format: E1/35-36)');
        }

        // Validate delay restore
        if (domain.delay_restore < 0 || domain.delay_restore > 3600) {
            warnings.push('Delay restore value should be between 0 and 3600 seconds');
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    }

    /**
     * Validate IP address format
     */
    isValidIP(ip) {
        const ipPattern = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/;
        if (!ipPattern.test(ip)) return false;
        
        const parts = ip.split('/');
        const addr = parts[0];
        const octets = addr.split('.');
        
        for (const octet of octets) {
            const num = parseInt(octet, 10);
            if (num < 0 || num > 255) return false;
        }
        
        return true;
    }

    /**
     * Validate port format
     */
    isValidPortFormat(port) {
        // Accept formats like: E1/1, E1/1-2, E1/1-2,E1/3-4
        const portPattern = /^[Ee]\d+\/\d+(-\d+)?(,[Ee]\d+\/\d+(-\d+)?)*$/;
        return portPattern.test(port);
    }

    /**
     * Get vPC domain summary
     */
    getDomainSummary(domainId) {
        const domain = this.vpcDomains.get(domainId);
        if (!domain) {
            return null;
        }

        return {
            domain_id: domain.domain_id,
            primary_switch: domain.primary_switch,
            secondary_switch: domain.secondary_switch,
            peer_link_ports: domain.peer_link_ports,
            keepalive_config: {
                ports: domain.keepalive_ports,
                primary_ip: domain.keepalive_ip_primary,
                secondary_ip: domain.keepalive_ip_secondary
            },
            role_priorities: domain.role_priority,
            features: {
                auto_recovery: domain.auto_recovery,
                peer_gateway: domain.peer_gateway,
                consistency_check: domain.consistency_check
            },
            created_at: domain.created_at
        };
    }

    /**
     * List all vPC domains
     */
    listDomains() {
        return Array.from(this.vpcDomains.values()).map(domain => ({
            domain_id: domain.domain_id,
            primary_switch: domain.primary_switch,
            secondary_switch: domain.secondary_switch,
            peer_link_ports: domain.peer_link_ports,
            created_at: domain.created_at
        }));
    }

    /**
     * Delete vPC domain
     */
    deleteDomain(domainId) {
        return this.vpcDomains.delete(domainId);
    }

    /**
     * Update vPC domain configuration
     */
    updateDomain(domainId, updates) {
        const domain = this.vpcDomains.get(domainId);
        if (!domain) {
            throw new Error(`vPC domain ${domainId} not found`);
        }

        Object.assign(domain, updates);
        return domain;
    }

    /**
     * Generate vPC topology visualization data
     */
    generateTopologyData(domainId) {
        const domain = this.vpcDomains.get(domainId);
        if (!domain) {
            return null;
        }

        return {
            nodes: [
                {
                    id: domain.primary_switch,
                    label: domain.primary_switch,
                    type: 'switch',
                    role: 'primary',
                    priority: domain.role_priority.primary
                },
                {
                    id: domain.secondary_switch,
                    label: domain.secondary_switch,
                    type: 'switch',
                    role: 'secondary',
                    priority: domain.role_priority.secondary
                }
            ],
            edges: [
                {
                    source: domain.primary_switch,
                    target: domain.secondary_switch,
                    type: 'peer-link',
                    ports: domain.peer_link_ports,
                    label: 'Peer-Link'
                },
                {
                    source: domain.primary_switch,
                    target: domain.secondary_switch,
                    type: 'keepalive',
                    ports: domain.keepalive_ports,
                    label: 'Keepalive'
                }
            ]
        };
    }

    /**
     * Export vPC configuration to file
     */
    exportConfig(domainId, switchRole) {
        const config = this.generateConfig(domainId, switchRole);
        const blob = new Blob([config], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `vpc-domain-${domainId}-${switchRole}.cfg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Import vPC configuration from text
     */
    importConfig(configText) {
        const lines = configText.split('\n');
        const domain = {};
        
        // Parse vPC domain configuration
        for (const line of lines) {
            const trimmed = line.trim();
            
            if (trimmed.startsWith('vpc domain')) {
                const match = trimmed.match(/vpc domain (\d+)/);
                if (match) {
                    domain.domain_id = parseInt(match[1], 10);
                }
            } else if (trimmed.includes('role priority')) {
                const match = trimmed.match(/role priority (\d+)/);
                if (match) {
                    domain.role_priority = domain.role_priority || {};
                    domain.role_priority.primary = parseInt(match[1], 10);
                }
            } else if (trimmed.includes('peer-keepalive')) {
                const match = trimmed.match(/destination ([\d.\/]+) source ([\d.\/]+)/);
                if (match) {
                    domain.keepalive_ip_primary = match[2];
                    domain.keepalive_ip_secondary = match[1];
                }
            }
        }

        if (domain.domain_id) {
            this.createDomain(
                domain.domain_id,
                'SWITCH-PRIMARY',
                'SWITCH-SECONDARY',
                domain
            );
            return domain;
        }

        throw new Error('Could not parse vPC domain configuration');
    }
}

// Global instance
const vpcConfigurator = new VPCConfigurator();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VPCConfigurator, vpcConfigurator };
}
