from fastapi.testclient import TestClient
from web_launcher import app
import os

client = TestClient(app)

def test_web_authority_system():
    print("--- TESTING WEB AUTHORITY SYSTEM FINAL ---")
    
    # 1. UI Accessibility
    ui_res = client.get("/")
    print(f"GET / (UI): {ui_res.status_code}")
    assert ui_res.status_code == 200
    assert "Configuration Authority System" in ui_res.text
    
    # 2. Static Assets
    css_res = client.get("/static/styles.css")
    print(f"GET /static/styles.css: {css_res.status_code}")
    assert css_res.status_code == 200

    # 3. Range Expansion Utility (Phase 1.1)
    range_res = client.get("/util/expand-range?range_str=Eth1/1-3")
    print(f"GET /util/expand-range: {range_res.json()}")
    assert "Eth1/3" in range_res.json()["expanded"]

    # 4. Compliance Auditing (Phase 1.2)
    audit_data = {
        "hostname": "DC-INVALID ROLE!", # Invalid hostname
        "mgmt_ip": "10.1.1.1", # Missing CIDR
        "mgmt_gw": "10.1.1.254",
        "vlans": [{"id": 3968, "name": "Reserved"}], # Reserved VLAN
        "interfaces": [],
        "motd": "Test"
    }
    audit_res = client.post("/validate", json=audit_data)
    findings = audit_res.json()["compliance_findings"]
    print(f"POST /validate (Compliance Findings): {len(findings)} found")
    
    # Verify specific findings
    messages = [f["message"] for f in findings]
    assert any("reserved NX-OS range" in m for m in messages)
    assert any("CIDR notation" in m for m in messages)
    assert any("invalid characters" in m for m in messages)

    print("\nWEB AUTHORITY SYSTEM QA PASS: SUCCESS")

if __name__ == "__main__":
    test_web_authority_system()
