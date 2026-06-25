import httpx
import json

def verify_professional_build():
    print(">>> VERIFYING PROFESSIONAL ENGINEERING LOGIC (1.7.0)")
    
    payload = {
        "hostname": "DC-LEAF-01A",
        "mgmt_ip": "10.1.1.2/24",
        "mgmt_gw": "10.1.1.254",
        "model": "N93180YC-EX",
        "vlans": [{"id": 10, "name": "APP_PROD"}],
        "svis": [{
            "vlan_id": 10,
            "ip_address": "10.10.10.2/24",
            "hsrp": {"group": 10, "vip": "10.10.10.1"}
        }],
        "vpc": {
            "domain_id": 100,
            "role": "primary",
            "keepalive_vrf": "management",
            "local_keepalive_ip": "10.1.1.2",
            "remote_keepalive_ip": "10.1.1.3",
            "peer_link_id": 4096,
            "peer_link_interfaces": ["Eth1/49", "Eth1/50"]
        },
        "interfaces": [
            {"name": "Eth1/1", "mode": "access", "vlan": 10, "vpc_id": 10}
        ]
    }

    from api.main import map_to_core, DeviceInput
    from core.renderer import ConfigRenderer
    
    device_input = DeviceInput(**payload)
    device = map_to_core(device_input)
    
    renderer = ConfigRenderer()
    config = renderer.render_device_config(device)
    
    print("\n[VPC ARCHITECTURE CHECK]")
    assert "vpc domain 100" in config
    assert "role priority 10" in config
    assert "peer-link" in config.lower()
    print("PASS: vPC Domain and Role established.")

    print("\n[INTERFACE BINDING CHECK]")
    assert "interface Eth1/49" in config
    assert "channel-group 4096 mode active" in config
    assert "vpc 10" in config
    print("PASS: Physical Peer-Link and vPC member IDs verified.")

    print("\n[L3 SERVICE CHECK]")
    assert "interface Vlan10" in config
    assert "ip address 10.10.10.2/24" in config
    assert "hsrp 10" in config
    print("PASS: SVI and HSRP v2 verification successful.")

if __name__ == "__main__":
    verify_professional_build()
