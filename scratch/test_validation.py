from models.vlan_model import VLAN
from models.interface_model import Interface
from models.device_model import Device
from core.engine import ConfigEngine
from core.validator import ValidationError

def test_validation():
    engine = ConfigEngine()
    
    # 1. Test Duplicate VLANs
    device_dup_vlan = Device(
        hostname="VALIDATOR-TEST-01",
        mgmt_ip="10.1.1.1",
        mgmt_gw="10.1.1.254",
        model="Generic",
        vlans=[VLAN(10, "Data"), VLAN(10, "Duplicate")],
        interfaces=[]
    )
    
    try:
        engine.build_config(device_dup_vlan)
        print("FAIL: Duplicate VLAN should have raised ValidationError")
    except ValidationError as e:
        print(f"PASS: Caught expected error: {e.report['errors']}")

    # 2. Test Invalid IP
    device_bad_ip = Device(
        hostname="VALIDATOR-TEST-02",
        mgmt_ip="999.999.999.999",
        mgmt_gw="10.1.1.254",
        model="Generic",
        vlans=[],
        interfaces=[]
    )
    
    try:
        engine.build_config(device_bad_ip)
        print("FAIL: Invalid IP should have raised ValidationError")
    except ValidationError as e:
        print(f"PASS: Caught expected error: {e.report['errors']}")

    # 3. Test Duplicate Interfaces
    device_dup_intf = Device(
        hostname="VALIDATOR-TEST-03",
        mgmt_ip="10.1.1.1",
        mgmt_gw="10.1.1.254",
        model="Generic",
        vlans=[],
        interfaces=[
            Interface("Ethernet1/1"),
            Interface("Ethernet1/1")
        ]
    )
    
    try:
        engine.build_config(device_dup_intf)
        print("FAIL: Duplicate Interface should have raised ValidationError")
    except ValidationError as e:
        print(f"PASS: Caught expected error: {e.report['errors']}")

    # 4. Test Valid config
    device_valid = Device(
        hostname="VALID-SW-01",
        mgmt_ip="10.1.1.1/24",
        mgmt_gw="10.1.1.254",
        model="Generic",
        vlans=[VLAN(10, "Data")],
        interfaces=[Interface("Ethernet1/1")]
    )
    
    try:
        engine.build_config(device_valid)
        print("PASS: Valid configuration passed validation")
    except ValidationError as e:
        print(f"FAIL: Valid configuration raised ValidationError: {e.report['errors']}")

if __name__ == "__main__":
    test_validation()
