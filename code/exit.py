import os
import shutil
import subprocess
import time

CONFIG_BASE = os.path.abspath("obs_configs")

def get_current_user():
    if not os.path.exists("current_user.txt"):
        raise FileNotFoundError("No current user file found.")
    with open("current_user.txt", "r") as f:
        return f.read().strip()

def force_kill_obs():
    try:
        subprocess.call(["taskkill", "/F", "/IM", "obs64.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def save_current_config():
    username = get_current_user()
    user_config_path = os.path.join(CONFIG_BASE, username)
    appdata_config_path = os.path.join(os.getenv("APPDATA"), "obs-studio")

    if not os.path.exists(appdata_config_path):
        print("OBS config directory not found.")
        return

    # Ensure OBS is closed
    force_kill_obs()

    # Give some time for process to terminate fully
    time.sleep(1)

    # Save current config
    if os.path.exists(user_config_path):
        shutil.rmtree(user_config_path)
    shutil.copytree(appdata_config_path, user_config_path)
    print(f"✅ Configuration for '{username}' saved.")

    # Now wipe out appdata OBS config to inject empty config
    try:
        shutil.rmtree(appdata_config_path)
        print(f"✅ Cleared OBS config directory at {appdata_config_path}")
    except Exception as e:
        print(f"Failed to clear OBS config: {e}")
        return

    # Recreate minimal empty config folder structure if needed
    os.makedirs(appdata_config_path, exist_ok=True)
    # You can create minimal config files here if needed, for now just empty folder

    print("✅ Injected empty OBS config (empty folder).")

if __name__ == "__main__":
    save_current_config()
