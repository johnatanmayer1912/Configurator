import os
import zipfile
import shutil
from datetime import datetime

def create_backup():
    # Base directory is one level up from utils/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Read version
    version_file = os.path.join(base_dir, "VERSION")
    with open(version_file, 'r') as f:
        version = f.read().strip()
    
    # Project name
    project_name = os.path.basename(base_dir)
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup file name
    backup_filename = f"backup_{version}_{timestamp}.zip"
    
    # Backups directory
    backups_dir = os.path.join(base_dir, "backups")
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
        
    backup_path = os.path.join(backups_dir, backup_filename)
    
    # Paths to exclude
    exclude_dirs = {'.git', '__pycache__', 'backups', 'logs', 'build', 'dist'}
    
    print(f"Starting backup of {project_name} (v{version})...")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Prune directory search
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if file.endswith('.zip') or file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
                
    print(f"Backup created successfully: {backup_path}")
    return backup_path

if __name__ == "__main__":
    create_backup()
