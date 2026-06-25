from models.vlan_model import VLAN
from models.interface_model import Interface
from models.device_model import Device, VPCConfig
from core.engine import ConfigEngine

def test_templates():
    engine = ConfigEngine()
    
    # Setup Device with everything
    device = Device(
        hostname="TEMPLATE-TEST-01",
        mgmt_ip="10.1.1.1/24",
        mgmt_gw="10.1.1.254",
        model="Nexus 93180YC-EX",
        vlans=[VLAN(100, "Production"), VLAN(200, "vMotion")],
        interfaces=[
            Interface("Ethernet1/1", "access", 100, "App-Server-01", shutdown=False),
            Interface("Ethernet1/2", "trunk", description="Uplink-Core", shutdown=False)
        ],
        vpc=VPCConfig(
            domain_id=10,
            keepalive_vrf="management",
            peer_link_id=1,
            role="primary",
            local_keepalive_ip="1.1.1.1",
            remote_keepalive_ip="1.1.1.2"
        ),
        admin_user="network_admin",
        admin_password="SuperSecretPassword"
    )
    
    config = engine.build_config(device)
    print("--- JINJA2 RENDERED CONFIG START ---")
    print(config)
    print("--- JINJA2 RENDERED CONFIG END ---")
    
    # Assertions
    assert "hostname TEMPLATE-TEST-01" in config
    assert "vlan 100" in config
    assert "vpc domain 10" in config
    assert "interface Ethernet1/1" in config
    assert "switchport mode access" in config
    assert "switchport mode trunk" in config
    print("\nVerification successful!")

if __name__ == "__main__":
    test_templates()
