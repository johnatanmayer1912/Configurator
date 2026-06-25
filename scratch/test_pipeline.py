import os
import shutil
from models.vlan_model import VLAN
from models.interface_model import Interface
from models.device_model import Device
from pipelines.build_pipeline import ConfigurationPipeline

def test_pipeline():
    # Setup test directory
    test_dist = "test_dist"
    if os.path.exists(test_dist):
        shutil.rmtree(test_dist)
    os.makedirs(test_dist)
    
    pipeline = ConfigurationPipeline(output_dir=test_dist)
    
    # Setup Device
    device = Device(
        hostname="PIPELINE-TEST",
        mgmt_ip="10.1.1.1",
        mgmt_gw="10.1.1.254",
        model="Generic",
        vlans=[VLAN(10, "Data")],
        interfaces=[
            Interface("Ethernet1/1", shutdown=True),
            Interface("Ethernet1/2", shutdown=False)
        ]
    )
    
    msg = pipeline.execute(device)
    print(msg)
    
    # Check if files exist
    files = os.listdir(test_dist)
    config_file = [f for f in files if "config.txt" in f and "PIPELINE-TEST" in f]
    diff_file = [f for f in files if "diff.txt" in f and "PIPELINE-TEST" in f]
    risk_file = [f for f in files if "risk.txt" in f and "PIPELINE-TEST" in f]
    
    assert len(config_file) == 1
    assert len(diff_file) == 1
    assert len(risk_file) == 1
    
    # Read risk report (UTF-8)
    with open(os.path.join(test_dist, risk_file[0]), "r", encoding="utf-8") as f:
        risk_content = f.read()
        # Verify without printing problematic characters to console
        assert "shutdown" in risk_content.lower()
        assert "Matches risk pattern: 'shutdown'" in risk_content
        
    print("\nPipeline Verification Successful!")

if __name__ == "__main__":
    test_pipeline()
