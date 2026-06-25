import subprocess
import time
import httpx
import os

def test_system_shutdown():
    print(">>> Starting System Shutdown Validation Audit")
    
    # 1. Start Server
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(
        ["python", "web_launcher.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    print(">>> Waiting for stabilization (8s)...")
    time.sleep(8)
    
    try:
        # 2. Trigger Shutdown
        print(">>> Sending POST /system/shutdown...")
        res = httpx.post("http://127.0.0.1:9000/system/shutdown")
        print(f">>> Response: {res.status_code} - {res.json()}")
        
        # 3. Wait for process to die
        print(">>> Monitoring process termination (max 10s)...")
        for _ in range(10):
            time.sleep(1)
            if proc.poll() is not None:
                print(f"\n>>> VALIDATION SUCCESS: Process {proc.pid} terminated gracefully.")
                return True
        
        print("\n>>> VALIDATION FAILED: Process is still alive after 10s.")
        return False
        
    except Exception as e:
        print(f"\n>>> VALIDATION ERROR: {e}")
        return False
    finally:
        # Cleanup
        if proc.poll() is None:
            print(">>> Force killing remaining process...")
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], capture_output=True)
            else:
                proc.terminate()

if __name__ == "__main__":
    test_system_shutdown()
