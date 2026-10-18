/**
 * Port Visualizer - Port Mapping Visualization
 * 
 * Provides network engineers with comprehensive port mapping visualization:
 * - Physical port layout visualization
 * - Port status and configuration display
 * - Port channel membership visualization
 * - VLAN assignment visualization
 * - Port utilization statistics
 * - Interactive port selection and configuration
 */

class PortVisualizer {
    constructor() {
        this.ports = new Map();
        this.portChannels = new Map();
        this.hardwareProfile = null;
        this.selectedPorts = new Set();
    }

    /**
     * Set hardware profile for port mapping
     */
    setHardwareProfile(profile) {
        this.hardwareProfile = profile;
        this.initializePortsFromProfile(profile);
    }

    /**
     * Initialize ports from hardware profile
     */
    initializePortsFromProfile(profile) {
        this.ports.clear();
        
        if (!profile || !profile.port_groups) {
            return;
        }

        for (const group of profile.port_groups) {
            for (const port of group.ports) {
                this.ports.set(port, {
                    port_id: port,
                    group: group.name,
                    speed: group.speed || '10G',
                    type: group.type || 'ethernet',
                    status: 'available',
                    description: '',
                    mode: 'access',
                    vlan: null,
                    port_channel: null,
                    vpc_peer_link: false,
                    vpc_keepalive: false,
                    uplink: false,
                    configured: false
                });
            }
        }
    }

    /**
     * Configure a port
     */
    configurePort(portId, config) {
        const port = this.ports.get(portId);
        if (!port) {
            throw new Error(`Port ${portId} not found`);
        }

        Object.assign(port, config);
        port.configured = true;
        
        return port;
    }

    /**
     * Create port channel
     */
    createPortChannel(channelId, ports, options = {}) {
        // Validate ports exist
        for (const portId of ports) {
            if (!this.ports.has(portId)) {
                throw new Error(`Port ${portId} not found`);
            }
        }

        // Check if ports are already in other channels
        for (const portId of ports) {
            const port = this.ports.get(portId);
            if (port.port_channel && port.port_channel !== channelId) {
                throw new Error(`Port ${portId} is already in port-channel ${port.port_channel}`);
            }
        }

        const portChannel = {
            channel_id: channelId,
            ports: ports,
            mode: options.mode || 'active', // active, passive, on
            description: options.description || `Port-Channel ${channelId}`,
            speed: options.speed || '10G',
            vlan: options.vlan || null,
            trunk_vlans: options.trunk_vlans || [],
            vpc: options.vpc || false,
            created_at: new Date().toISOString()
        };

        this.portChannels.set(channelId, portChannel);

        // Update port configurations
        for (const portId of ports) {
            const port = this.ports.get(portId);
            port.port_channel = channelId;
            port.mode = 'trunk';
            port.configured = true;
        }

        return portChannel;
    }

    /**
     * Delete port channel
     */
    deletePortChannel(channelId) {
        const portChannel = this.portChannels.get(channelId);
        if (!portChannel) {
            throw new Error(`Port-channel ${channelId} not found`);
        }

        // Reset port configurations
        for (const portId of portChannel.ports) {
            const port = this.ports.get(portId);
            if (port) {
                port.port_channel = null;
                port.mode = 'access';
                port.configured = false;
            }
        }

        return this.portChannels.delete(channelId);
    }

    /**
     * Assign VLAN to port
     */
    assignVLANToPort(portId, vlanId, mode = 'access') {
        const port = this.ports.get(portId);
        if (!port) {
            throw new Error(`Port ${portId} not found`);
        }

        port.vlan = vlanId;
        port.mode = mode;
        port.configured = true;
        
        return port;
    }

    /**
     * Set port as vPC peer-link
     */
    setVPCPeerLink(portId, domainId) {
        const port = this.ports.get(portId);
        if (!port) {
            throw new Error(`Port ${portId} not found`);
        }

        port.vpc_peer_link = true;
        port.vpc_domain = domainId;
        port.mode = 'trunk';
        port.configured = true;
        
        return port;
    }

    /**
     * Set port as vPC keepalive
     */
    setVPCKeepalive(portId) {
        const port = this.ports.get(portId);
        if (!port) {
            throw new Error(`Port ${portId} not found`);
        }

        port.vpc_keepalive = true;
        port.mode = 'access';
        port.configured = true;
        
        return port;
    }

    /**
     * Set port as uplink
     */
    setUplink(portId, targetSwitch, targetPorts) {
        const port = this.ports.get(portId);
        if (!port) {
            throw new Error(`Port ${portId} not found`);
        }

        port.uplink = true;
        port.target_switch = targetSwitch;
        port.target_ports = targetPorts;
        port.mode = 'trunk';
        port.configured = true;
        
        return port;
    }

    /**
     * Get port information
     */
    getPort(portId) {
        return this.ports.get(portId);
    }

    /**
     * List all ports
     */
    listPorts(options = {}) {
        let ports = Array.from(this.ports.values());

        if (options.filter) {
            ports = ports.filter(port => {
                if (options.filter.status && port.status !== options.filter.status) return false;
                if (options.filter.mode && port.mode !== options.filter.mode) return false;
                if (options.filter.group && port.group !== options.filter.group) return false;
                if (options.filter.configured !== undefined && port.configured !== options.filter.configured) return false;
                return true;
            });
        }

        if (options.sort) {
            ports.sort((a, b) => {
                if (options.sort === 'id') return a.port_id.localeCompare(b.port_id);
                if (options.sort === 'group') return a.group.localeCompare(b.group);
                if (options.sort === 'status') return a.status.localeCompare(b.status);
                return 0;
            });
        }

        return ports;
    }

    /**
     * List port channels
     */
    listPortChannels() {
        return Array.from(this.portChannels.values());
    }

    /**
     * Get port utilization statistics
     */
    getPortStatistics() {
        const totalPorts = this.ports.size;
        const configuredPorts = Array.from(this.ports.values()).filter(p => p.configured).length;
        const availablePorts = totalPorts - configuredPorts;
        
        const portChannels = this.portChannels.size;
        const vpcPeerLinks = Array.from(this.ports.values()).filter(p => p.vpc_peer_link).length;
        const vpcKeepalives = Array.from(this.ports.values()).filter(p => p.vpc_keepalive).length;
        const uplinks = Array.from(this.ports.values()).filter(p => p.uplink).length;

        // Group statistics
        const groupStats = {};
        for (const port of this.ports.values()) {
            if (!groupStats[port.group]) {
                groupStats[port.group] = { total: 0, configured: 0, available: 0 };
            }
            groupStats[port.group].total++;
            if (port.configured) {
                groupStats[port.group].configured++;
            } else {
                groupStats[port.group].available++;
            }
        }

        return {
            total_ports: totalPorts,
            configured_ports: configuredPorts,
            available_ports: availablePorts,
            utilization_percent: totalPorts > 0 ? ((configuredPorts / totalPorts) * 100).toFixed(2) : 0,
            port_channels: portChannels,
            vpc_peer_links: vpcPeerLinks,
            vpc_keepalives: vpcKeepalives,
            uplinks: uplinks,
            group_statistics: groupStats
        };
    }

    /**
     * Generate visualization data for port layout
     */
    generateVisualizationData() {
        const groups = {};
        
        for (const port of this.ports.values()) {
            if (!groups[port.group]) {
                groups[port.group] = {
                    name: port.group,
                    ports: []
                };
            }
            groups[port.group].ports.push(port);
        }

        return {
            hardware_profile: this.hardwareProfile?.name || 'Unknown',
            groups: groups,
            port_channels: Array.from(this.portChannels.values()),
            statistics: this.getPortStatistics()
        };
    }

    /**
     * Generate port configuration commands
     */
    generateConfig(portIds) {
        const config = [];
        
        for (const portId of portIds) {
            const port = this.ports.get(portId);
            if (!port) {
                continue;
            }

            config.push(`! Port Configuration: ${portId}`);
            config.push(`interface ${portId}`);
            
            if (port.description) {
                config.push(`  description ${port.description}`);
            }
            
            if (port.mode === 'access') {
                config.push(`  switchport mode access`);
                if (port.vlan) {
                    config.push(`  switchport access vlan ${port.vlan}`);
                }
            } else if (port.mode === 'trunk') {
                config.push(`  switchport mode trunk`);
                if (port.vlan) {
                    config.push(`  switchport trunk native vlan ${port.vlan}`);
                }
            }
            
            if (port.port_channel) {
                const channel = this.portChannels.get(port.port_channel);
                if (channel) {
                    config.push(`  channel-group ${port.port_channel} mode ${channel.mode}`);
                }
            }
            
            if (port.vpc_peer_link) {
                config.push(`  vpc peer-link`);
            }
            
            if (!port.configured) {
                config.push(`  shutdown`);
            } else {
                config.push(`  no shutdown`);
            }
            
            config.push(`  exit`);
        }

        return config.join('\n');
    }

    /**
     * Generate port-channel configuration
     */
    generatePortChannelConfig(channelId) {
        const channel = this.portChannels.get(channelId);
        if (!channel) {
            throw new Error(`Port-channel ${channelId} not found`);
        }

        const config = [];
        
        config.push(`! Port-Channel Configuration: ${channelId}`);
        config.push(`interface port-channel${channelId}`);
        config.push(`  description ${channel.description}`);
        config.push(`  switchport mode trunk`);
        
        if (channel.vlan) {
            config.push(`  switchport trunk native vlan ${channel.vlan}`);
        }
        
        if (channel.trunk_vlans.length > 0) {
            config.push(`  switchport trunk allowed vlan ${channel.trunk_vlans.join(',')}`);
        }
        
        if (channel.vpc) {
            config.push(`  vpc peer-link`);
        }
        
        config.push(`  no shutdown`);
        config.push(`  exit`);

        return config.join('\n');
    }

    /**
     * Find available ports in a group
     */
    findAvailablePorts(group, count = 1, speed = null) {
        const available = [];
        
        for (const [portId, port] of this.ports) {
            if (port.group === group && !port.configured) {
                if (speed && port.speed !== speed) continue;
                available.push(portId);
                if (available.length >= count) break;
            }
        }

        return available;
    }

    /**
     * Validate port configuration
     */
    validateConfiguration(portId) {
        const port = this.ports.get(portId);
        if (!port) {
            return { valid: false, errors: [`Port ${portId} not found`] };
        }

        const errors = [];
        const warnings = [];

        // Validate vPC peer-link configuration
        if (port.vpc_peer_link && port.mode !== 'trunk') {
            errors.push('vPC peer-link ports must be configured in trunk mode');
        }

        // Validate vPC keepalive configuration
        if (port.vpc_keepalive && port.mode !== 'access') {
            warnings.push('vPC keepalive ports should typically be in access mode');
        }

        // Validate port channel membership
        if (port.port_channel) {
            const channel = this.portChannels.get(port.port_channel);
            if (!channel) {
                errors.push(`Port is assigned to non-existent port-channel ${port.port_channel}`);
            }
        }

        // Validate VLAN assignment
        if (port.vlan && port.mode === 'trunk') {
            warnings.push('VLAN assignment on trunk port may not work as expected');
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    }

    /**
     * Select port for operations
     */
    selectPort(portId) {
        if (!this.ports.has(portId)) {
            throw new Error(`Port ${portId} not found`);
        }
        this.selectedPorts.add(portId);
    }

    /**
     * Deselect port
     */
    deselectPort(portId) {
        return this.selectedPorts.delete(portId);
    }

    /**
     * Clear all selected ports
     */
    clearSelectedPorts() {
        this.selectedPorts.clear();
    }

    /**
     * Get selected ports
     */
    getSelectedPorts() {
        return Array.from(this.selectedPorts).map(portId => this.ports.get(portId));
    }

    /**
     * Import port configuration from text
     */
    importConfig(configText) {
        const lines = configText.split('\n');
        const importedPorts = [];
        let currentPort = null;

        for (const line of lines) {
            const trimmed = line.trim();
            
            if (trimmed.startsWith('interface ') && !trimmed.includes('port-channel')) {
                const match = trimmed.match(/interface (\S+)/);
                if (match) {
                    currentPort = {
                        port_id: match[1],
                        description: '',
                        mode: 'access',
                        vlan: null,
                        port_channel: null,
                        configured: true
                    };
                }
            } else if (trimmed.startsWith('description ') && currentPort) {
                currentPort.description = trimmed.substring(12).trim();
            } else if (trimmed.includes('switchport mode access') && currentPort) {
                currentPort.mode = 'access';
            } else if (trimmed.includes('switchport mode trunk') && currentPort) {
                currentPort.mode = 'trunk';
            } else if (trimmed.includes('switchport access vlan') && currentPort) {
                const match = trimmed.match(/switchport access vlan (\d+)/);
                if (match) {
                    currentPort.vlan = parseInt(match[1], 10);
                }
            } else if (trimmed.includes('channel-group') && currentPort) {
                const match = trimmed.match(/channel-group (\d+)/);
                if (match) {
                    currentPort.port_channel = parseInt(match[1], 10);
                }
            } else if (trimmed === 'exit' && currentPort) {
                try {
                    const port = this.configurePort(currentPort.port_id, currentPort);
                    importedPorts.push(port);
                } catch (error) {
                    console.error(`Failed to import port ${currentPort.port_id}:`, error.message);
                }
                currentPort = null;
            }
        }

        return importedPorts;
    }

    /**
     * Clear all port configurations
     */
    clearAllConfigurations() {
        for (const port of this.ports.values()) {
            port.configured = false;
            port.mode = 'access';
            port.vlan = null;
            port.port_channel = null;
            port.vpc_peer_link = false;
            port.vpc_keepalive = false;
            port.uplink = false;
            port.description = '';
        }
        this.portChannels.clear();
        this.selectedPorts.clear();
    }
}

// Global instance
const portVisualizer = new PortVisualizer();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PortVisualizer, portVisualizer };
}
