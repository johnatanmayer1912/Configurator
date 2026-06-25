from models.vlan_model import VLAN
from models.interface_model import Interface
from models.device_model import Device, VPCConfig
from core.engine import ConfigEngine

def test_models():
    engine = ConfigEngine()
    
    # Setup VLANs
    vlans = [VLAN(10, "Data"), VLAN(20, "Voice")]
    
    # Setup Interfaces
    interfaces = [
        Interface("Ethernet1/1", "access", 10, "Desktop Port", shutdown=False),
        Interface("Ethernet1/2", "access", 20, "Phone Port", shutdown=False),
        Interface("Ethernet1/48", "trunk", description="Uplink", shutdown=False)
    ]
    
    # Setup Device
    device = Device(
        hostname="TEST-SW-01",
        mgmt_ip="192.168.1.10/24",
        mgmt_gw="192.168.1.1",
        model="Nexus 93180YC-EX",
        vlans=vlans,
        interfaces=interfaces,
        admin_user="admin",
        admin_password="Password123"
    )
    
    config = engine.build_config(device)
    print("--- GENERATED CONFIG START ---")
    print(config)
    print("--- GENERATED CONFIG END ---")

if __name__ == "__main__":
    test_models()
