from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_api_endpoints():
    print("--- TESTING API ENDPOINTS ---")
    
    # 1. Version Check
    v_res = client.get("/version")
    print(f"GET /version: {v_res.status_code} - {v_res.json()}")
    assert v_res.status_code == 200
    
    # 2. Validation Check (Pass)
    valid_data = {
        "hostname": "API-TEST-PASS",
        "mgmt_ip": "10.0.0.1/24",
        "mgmt_gw": "10.0.0.254",
        "vlans": [{"id": 10, "name": "Data"}],
        "interfaces": [{"name": "Eth1/1", "mode": "access", "vlan": 10}]
    }
    val_res = client.post("/validate", json=valid_data)
    print(f"POST /validate (Valid): {val_res.status_code} - Status: {val_res.json()['status']}")
    assert val_res.status_code == 200
    assert val_res.json()["status"] == "pass"

    # 3. Validation Check (Fail - Duplicate VLAN)
    invalid_data = {
        "hostname": "API-TEST-FAIL",
        "mgmt_ip": "10.0.0.1/24",
        "mgmt_gw": "10.0.0.254",
        "vlans": [{"id": 10, "name": "A"}, {"id": 10, "name": "B"}],
        "interfaces": []
    }
    fail_res = client.post("/validate", json=invalid_data)
    print(f"POST /validate (Invalid): {fail_res.status_code} - Errors: {fail_res.json()['errors']}")
    assert "Duplicate VLAN IDs" in fail_res.json()["errors"][0]

    # 4. Generation Check
    gen_res = client.post("/generate-config", json=valid_data)
    print(f"POST /generate-config: {gen_res.status_code} - {gen_res.json()['message']}")
    assert gen_res.status_code == 200
    
    print("\nAPI QA Pass: SUCCESS")

if __name__ == "__main__":
    test_api_endpoints()
