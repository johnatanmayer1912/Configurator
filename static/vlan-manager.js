/**
 * VLAN Manager - Advanced VLAN Management Interface
 * 
 * Provides network engineers with comprehensive VLAN management capabilities:
 * - VLAN creation and deletion
 * - VLAN range management
 * - VLAN naming and description
 * - VLAN type configuration (access, trunk, private VLAN)
 * - VLAN consistency across switches
 * - Reserved VLAN management
 */

class VLANManager {
    constructor() {
        this.vlans = new Map();
        this.reservedVlans = new Set([1, 1002-1005, 3968-4095]);
        this.vlanRanges = new Map();
    }

    /**
     * Create a new VLAN
     */
    createVLAN(vlanId, name, options = {}) {
        if (this.isReservedVLAN(vlanId)) {
            throw new Error(`VLAN ${vlanId} is reserved and cannot be used`);
        }

        if (this.vlans.has(vlanId)) {
            throw new Error(`VLAN ${vlanId} already exists`);
        }

        const vlan = {
            vlan_id: vlanId,
            name: name || `VLAN_${vlanId}`,
            description: options.description || '',
            type: options.type || 'access', // access, trunk, private-vlan, voice
            state: options.state || 'active',
            mtu: options.mtu || 1500,
            shutdown: options.shutdown !== false,
            private_vlan_type: options.private_vlan_type || null, // primary, isolated, community
            associated_primary: options.associated_primary || null,
            created_at: new Date().toISOString(),
            switches: new Set() // Track which switches use this VLAN
        };

        this.vlans.set(vlanId, vlan);
        return vlan;
    }

    /**
     * Delete a VLAN
     */
    deleteVLAN(vlanId) {
        if (this.isReservedVLAN(vlanId)) {
            throw new Error(`VLAN ${vlanId} is reserved and cannot be deleted`);
        }

        if (!this.vlans.has(vlanId)) {
            throw new Error(`VLAN ${vlanId} does not exist`);
        }

        const vlan = this.vlans.get(vlanId);
        if (vlan.switches.size > 0) {
            throw new Error(`VLAN ${vlanId} is in use on ${vlan.switches.size} switch(es) and cannot be deleted`);
        }

        return this.vlans.delete(vlanId);
    }

    /**
     * Update VLAN configuration
     */
    updateVLAN(vlanId, updates) {
        const vlan = this.vlans.get(vlanId);
        if (!vlan) {
            throw new Error(`VLAN ${vlanId} does not exist`);
        }

        Object.assign(vlan, updates);
        return vlan;
    }

    /**
     * Create VLAN range
     */
    createVLANRange(startId, endId, name, options = {}) {
        if (startId < 1 || endId > 4094 || startId > endId) {
            throw new Error('Invalid VLAN range. Valid range is 1-4094');
        }

        // Check for reserved VLANs in range
        for (let vlanId = startId; vlanId <= endId; vlanId++) {
            if (this.isReservedVLAN(vlanId)) {
                throw new Error(`VLAN range contains reserved VLAN ${vlanId}`);
            }
        }

        const range = {
            start_id: startId,
            end_id: endId,
            name: name || `VLAN_RANGE_${startId}-${endId}`,
            description: options.description || '',
            purpose: options.purpose || 'general',
            created_at: new Date().toISOString()
        };

        this.vlanRanges.set(`${startId}-${endId}`, range);
        return range;
    }

    /**
     * Assign VLAN to switch
     */
    assignVLANToSwitch(vlanId, switchName, portType = 'access') {
        const vlan = this.vlans.get(vlanId);
        if (!vlan) {
            throw new Error(`VLAN ${vlanId} does not exist`);
        }

        vlan.switches.add(switchName);
        vlan.type = portType;
        
        return vlan;
    }

    /**
     * Remove VLAN from switch
     */
    removeVLANFromSwitch(vlanId, switchName) {
        const vlan = this.vlans.get(vlanId);
        if (!vlan) {
            throw new Error(`VLAN ${vlanId} does not exist`);
        }

        vlan.switches.delete(switchName);
        return vlan;
    }

    /**
     * Check if VLAN is reserved
     */
    isReservedVLAN(vlanId) {
        // Check individual reserved VLANs
        if (this.reservedVlans.has(vlanId)) {
            return true;
        }

        // Check reserved ranges
        for (const range of this.reservedVlans) {
            if (typeof range === 'object' && range.start && range.end) {
                if (vlanId >= range.start && vlanId <= range.end) {
                    return true;
                }
            }
        }

        // Default reserved ranges
        if (vlanId === 1) return true; // Default VLAN
        if (vlanId >= 1002 && vlanId <= 1005) return true; // Token Ring/FDDI VLANs
        if (vlanId >= 3968 && vlanId <= 4095) return true; // Reserved for internal use

        return false;
    }

    /**
     * Get VLAN information
     */
    getVLAN(vlanId) {
        return this.vlans.get(vlanId);
    }

    /**
     * List all VLANs
     */
    listVLANs(options = {}) {
        let vlans = Array.from(this.vlans.values());

        if (options.filter) {
            vlans = vlans.filter(vlan => {
                if (options.filter.type && vlan.type !== options.filter.type) return false;
                if (options.filter.state && vlan.state !== options.filter.state) return false;
                return true;
            });
        }

        if (options.sort) {
            vlans.sort((a, b) => {
                if (options.sort === 'id') return a.vlan_id - b.vlan_id;
                if (options.sort === 'name') return a.name.localeCompare(b.name);
                return 0;
            });
        }

        return vlans;
    }

    /**
     * List VLAN ranges
     */
    listVLANRanges() {
        return Array.from(this.vlanRanges.values());
    }

    /**
     * Get VLAN usage statistics
     */
    getVLANStatistics() {
        const totalVLANs = this.vlans.size;
        const activeVLANs = Array.from(this.vlans.values()).filter(v => v.state === 'active').length;
        const inUseVLANs = Array.from(this.vlans.values()).filter(v => v.switches.size > 0).length;
        
        const vlanUsage = {};
        for (const [vlanId, vlan] of this.vlans) {
            vlanUsage[vlanId] = vlan.switches.size;
        }

        return {
            total_vlans: totalVLANs,
            active_vlans: activeVLANs,
            inactive_vlans: totalVLANs - activeVLANs,
            in_use_vlans: inUseVLANs,
            unused_vlans: totalVLANs - inUseVLANs,
            vlan_usage: vlanUsage
        };
    }

    /**
     * Validate VLAN configuration
     */
    validateConfiguration(vlanId) {
        const vlan = this.vlans.get(vlanId);
        if (!vlan) {
            return { valid: false, errors: [`VLAN ${vlanId} does not exist`] };
        }

        const errors = [];
        const warnings = [];

        // Validate VLAN ID range
        if (vlan.vlan_id < 1 || vlan.vlan_id > 4094) {
            errors.push('VLAN ID must be between 1 and 4094');
        }

        // Validate name
        if (!vlan.name || vlan.name.trim().length === 0) {
            warnings.push('VLAN name is empty');
        }

        // Validate MTU
        if (vlan.mtu < 576 || vlan.mtu > 9216) {
            warnings.push('MTU value should be between 576 and 9216');
        }

        // Validate private VLAN configuration
        if (vlan.type === 'private-vlan') {
            if (!vlan.private_vlan_type) {
                errors.push('Private VLAN type must be specified (primary, isolated, or community)');
            }
            if (vlan.private_vlan_type !== 'primary' && !vlan.associated_primary) {
                warnings.push('Secondary private VLANs should be associated with a primary VLAN');
            }
        }

        // Check for VLAN conflicts
        for (const [otherId, otherVLAN] of this.vlans) {
            if (otherId !== vlanId && otherVLAN.name === vlan.name) {
                warnings.push(`VLAN name "${vlan.name}" is also used by VLAN ${otherId}`);
            }
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    }

    /**
     * Generate VLAN configuration for a switch
     */
    generateConfig(vlanIds, switchName) {
        const config = [];
        
        config.push(`! VLAN Configuration for ${switchName}`);
        
        for (const vlanId of vlanIds) {
            const vlan = this.vlans.get(vlanId);
            if (!vlan) {
                warnings.push(`VLAN ${vlanId} not found, skipping`);
                continue;
            }

            config.push(`vlan ${vlanId}`);
            config.push(`  name ${vlan.name}`);
            
            if (vlan.description) {
                config.push(`  description ${vlan.description}`);
            }
            
            if (vlan.state === 'active') {
                config.push(`  state active`);
            } else {
                config.push(`  state suspend`);
            }
            
            if (vlan.shutdown) {
                config.push(`  shutdown`);
            }
            
            if (vlan.mtu !== 1500) {
                config.push(`  mtu ${vlan.mtu}`);
            }
            
            // Private VLAN configuration
            if (vlan.type === 'private-vlan') {
                if (vlan.private_vlan_type === 'primary') {
                    config.push(`  private-vlan primary`);
                } else if (vlan.private_vlan_type === 'isolated') {
                    config.push(`  private-vlan isolated`);
                    if (vlan.associated_primary) {
                        config.push(`  private-vlan association ${vlan.associated_primary}`);
                    }
                } else if (vlan.private_vlan_type === 'community') {
                    config.push(`  private-vlan community`);
                    if (vlan.associated_primary) {
                        config.push(`  private-vlan association ${vlan.associated_primary}`);
                    }
                }
            }
            
            config.push(`  exit`);
        }

        return config.join('\n');
    }

    /**
     * Find available VLANs in a range
     */
    findAvailableVLANs(startId, endId, count = 1) {
        const available = [];
        
        for (let vlanId = startId; vlanId <= endId && available.length < count; vlanId++) {
            if (!this.isReservedVLAN(vlanId) && !this.vlans.has(vlanId)) {
                available.push(vlanId);
            }
        }

        return available;
    }

    /**
     * Import VLAN configuration from text
     */
    importConfig(configText) {
        const lines = configText.split('\n');
        const importedVLANs = [];
        let currentVLAN = null;

        for (const line of lines) {
            const trimmed = line.trim();
            
            if (trimmed.startsWith('vlan ')) {
                const match = trimmed.match(/vlan (\d+)/);
                if (match) {
                    currentVLAN = {
                        vlan_id: parseInt(match[1], 10),
                        name: '',
                        description: '',
                        state: 'active',
                        mtu: 1500,
                        shutdown: false
                    };
                }
            } else if (trimmed.startsWith('name ') && currentVLAN) {
                currentVLAN.name = trimmed.substring(5).trim();
            } else if (trimmed.startsWith('description ') && currentVLAN) {
                currentVLAN.description = trimmed.substring(12).trim();
            } else if (trimmed.startsWith('state ') && currentVLAN) {
                currentVLAN.state = trimmed.substring(6).trim();
            } else if (trimmed.startsWith('mtu ') && currentVLAN) {
                currentVLAN.mtu = parseInt(trimmed.substring(4), 10);
            } else if (trimmed === 'shutdown' && currentVLAN) {
                currentVLAN.shutdown = true;
            } else if (trimmed === 'exit' && currentVLAN) {
                try {
                    const vlan = this.createVLAN(currentVLAN.vlan_id, currentVLAN.name, currentVLAN);
                    importedVLANs.push(vlan);
                } catch (error) {
                    console.error(`Failed to import VLAN ${currentVLAN.vlan_id}:`, error.message);
                }
                currentVLAN = null;
            }
        }

        return importedVLANs;
    }

    /**
     * Export VLAN configuration
     */
    exportConfig(vlanIds) {
        const config = [];
        
        for (const vlanId of vlanIds) {
            const vlan = this.vlans.get(vlanId);
            if (vlan) {
                config.push(`vlan ${vlanId}`);
                config.push(`  name ${vlan.name}`);
                if (vlan.description) config.push(`  description ${vlan.description}`);
                config.push(`  state ${vlan.state}`);
                if (vlan.shutdown) config.push(`  shutdown`);
                if (vlan.mtu !== 1500) config.push(`  mtu ${vlan.mtu}`);
                config.push(`  exit`);
            }
        }

        return config.join('\n');
    }

    /**
     * Get VLAN conflicts across switches
     */
    findVLANConflicts() {
        const conflicts = [];
        
        for (const [vlanId, vlan] of this.vlans) {
            if (vlan.switches.size > 1) {
                // Check for configuration differences across switches
                const switches = Array.from(vlan.switches);
                for (let i = 0; i < switches.length; i++) {
                    for (let j = i + 1; j < switches.length; j++) {
                        conflicts.push({
                            vlan_id: vlanId,
                            switch1: switches[i],
                            switch2: switches[j],
                            type: 'vlan_exists_on_multiple_switches',
                            severity: 'warning'
                        });
                    }
                }
            }
        }

        return conflicts;
    }

    /**
     * Clear all VLANs
     */
    clearAllVLANs() {
        this.vlans.clear();
        this.vlanRanges.clear();
    }
}

// Global instance
const vlanManager = new VLANManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VLANManager, vlanManager };
}
