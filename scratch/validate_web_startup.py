import subprocess
import time
import httpx
import os
import signal

def validate_startup():
    print(">>> Starting Startup Validation Audit (Port 9000)")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    
    proc = subprocess.Popen(
        ["python", "web_launcher.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    print(">>> Waiting for engine stabilization (10s)...")
    time.sleep(10)
    
    try:
        # Probe Root Endpoint on 9000
        res = httpx.get("http://127.0.0.1:9000/", timeout=10.0)
        print(f">>> Root Probe: Status {res.status_code}")
        
        # Probe Static Assets on 9000
        static_res = httpx.get("http://127.0.0.1:9000/static/styles.css", timeout=10.0)
        print(f">>> Static Asset Probe: Status {static_res.status_code}")
        
        if res.status_code == 200 and static_res.status_code == 200:
            print("\n>>> VALIDATION SUCCESS: Web Engine is operational.")
        else:
            print("\n>>> VALIDATION FAILED: Unexpected status codes.")
            
    except Exception as e:
        print(f"\n>>> VALIDATION CRITICAL FAILURE: {e}")
    finally:
        print(">>> Terminating validation process...")
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], capture_output=True)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    validate_startup()
