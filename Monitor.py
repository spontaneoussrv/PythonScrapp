import psutil
import time
import os
import subprocess

def get_running_python_scripts():
    """Returns a dictionary of running Python scripts with PID as key."""
    running_scripts = {}
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
        if proc.info['name'] and "python" in proc.info['name'].lower():
            cmdline = proc.info['cmdline']
            cwd = proc.info.get('cwd', '')  # Get working directory
            if cmdline and len(cmdline) > 1 and cwd:  # Ensure there's a script name & cwd
                script_path = cmdline[1]  # Full path of script
                script_name = os.path.basename(script_path)  # Extract filename
                running_scripts[proc.info['pid']] = (script_name, script_path, cwd)
    return running_scripts

def get_latest_folder_and_count(directory):
    """Finds the latest modified folder in the directory and counts its subfolders."""
    if not os.path.exists(directory):
        return None, 0  # Directory doesn't exist

    folders = [f for f in os.scandir(directory) if f.is_dir()]
    if not folders:
        return None, 0  # No folders found

    latest_folder = max(folders, key=lambda f: f.stat().st_mtime, default=None)
    if not latest_folder:
        return None, 0  # No valid latest folder

    latest_folder_path = latest_folder.path
    subfolders = [f for f in os.scandir(latest_folder_path) if f.is_dir()]
    return os.path.basename(latest_folder_path), len(subfolders)

# ANSI escape codes for colored output
green_text = "\033[92m"
red_text = "\033[91m"
reset_color = "\033[0m"

# Initial list of running scripts
running_scripts = get_running_python_scripts()
print("Monitoring running Python scripts...")

while True:
    time.sleep(5)  # Check every 5 seconds
    current_scripts = get_running_python_scripts()

    for pid in list(running_scripts.keys()):
        if pid not in current_scripts:
            script_name, script_path, script_cwd = running_scripts[pid]
            print(f"{red_text}[STOPPED] ❌ {script_name} (PID: {pid}){reset_color}")
            
            latest_folder, subfolder_count = get_latest_folder_and_count(script_cwd)
            if latest_folder:
                print(f"📁 Latest folder: {latest_folder}")
                print(f"📂 Result Start Must be: {subfolder_count - 1}")
            else:
                print("📁 No folders found in the script directory.")

            print(f"🔄 Restarting {script_name}...")
            try:
                new_cmd = f'start cmd /k "cd /d \"{script_cwd}\" && python \"{script_path}\""'
                subprocess.Popen(new_cmd, shell=True, cwd=script_cwd)
                print(f"{green_text}[RESTARTED] ✅ {script_name} in new CMD window{reset_color}")
            except Exception as e:
                print(f"[ERROR] ⚠️ Failed to restart {script_name}: {e}")

            del running_scripts[pid]

    for pid, (script_name, script_path, script_cwd) in current_scripts.items():
        if pid not in running_scripts:
            print(f"{green_text}[STARTED] ✅ {script_name} (PID: {pid}){reset_color}")
            running_scripts[pid] = (script_name, script_path, script_cwd)
