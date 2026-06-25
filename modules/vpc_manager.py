def build_vpc_config(c, role, domain, kpa_vrf, pl_id, kpa_local, kpa_remote, vpc_ports=None):
    """
    Appends vPC configuration to the provided config list.
    Note: vpc_ports is optional here; if provided, it will generate interface configs.
    If not provided (because interfaces are already in the device.interfaces list), 
    it will only generate the global domain config.
    """
    c.append("\n! vPC Global Configuration")
    c.append(f"vpc domain {domain}")
    c.append(f"  role priority {10 if role == 'primary' else 20}")
    # Handling IP strip for keepalive destination
    kpa_dest = kpa_remote.split('/')[0] if '/' in kpa_remote else kpa_remote
    kpa_src = kpa_local.split('/')[0] if '/' in kpa_local else kpa_local
    c.append(f"  peer-keepalive destination {kpa_dest} source {kpa_src} vrf {kpa_vrf}")
    c.append("  peer-gateway")
    c.append("  auto-recovery")
    c.append("  ip arp synchronize")

    if vpc_ports:
        # Peer Link PO
        c.append(f"\n! vPC Peer-Link (Ports: {', '.join(vpc_ports.get('peer_link', []))})")
        c.append(f"interface port-channel{pl_id}")
        c.append("  description vPC Peer-Link")
        c.append("  switchport mode trunk")
        c.append("  vpc peer-link")
        c.append("  spanning-tree port type network")
        c.append("  no shutdown")
        
        for p in vpc_ports.get('peer_link', []):
            c.append(f"interface {p}")
            c.append("  description vPC Peer-Link Member")
            c.append("  switchport mode trunk")
            c.append(f"  channel-group {pl_id} mode active")
            c.append("  no shutdown")

        # Keepalive PO (if 100)
        kpa_ports = vpc_ports.get('keepalive', [])
        c.append(f"\n! vPC Keepalive Link (Ports: {', '.join(kpa_ports)})")
        c.append("interface port-channel100")
        c.append("  description vPC Keepalive Link")
        c.append(f"  vrf member {kpa_vrf}")
        c.append(f"  ip address {kpa_local}") 
        c.append("  no shutdown")
        
        for p in kpa_ports:
            c.append(f"interface {p}")
            c.append("  description vPC Keepalive Member")
            c.append("  no switchport")
            c.append("  channel-group 100 mode active")
            c.append("  no shutdown")
