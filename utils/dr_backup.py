import os
import zipfile
import datetime

def create_dr_backup():
    # 1. Discover Version
    version = "1.0.0"
    if os.path.exists("VERSION"):
        with open("VERSION", "r") as f:
            version = f.read().strip()
            
    # 2. Setup Metadata
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_FULL_{version}_{timestamp}.zip"
    backup_path = os.path.join("backups", backup_name)
    
    if not os.path.exists("backups"):
        os.makedirs("backups")

    # 3. Define include/exclude
    # We include all source, models, templates, docs, and build utils
    # We exclude large runtime artifacts like dist/, build/, and test_dist/
    exclude_dirs = {"dist", "build", "backups", ".git", "__pycache__", "test_dist"}
    
    print(f"Initializing Disaster Recovery Backup: {backup_name}")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Filtering directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Exclude specific files if needed
                if file.endswith(('.pyc', '.pyo')):
                    continue
                    
                file_path = os.path.join(root, file)
                # Store with relative path
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)
                
    print(f"SUCCESS: DR Backup completed at {backup_path}")
    return backup_path

if __name__ == "__main__":
    create_dr_backup()
