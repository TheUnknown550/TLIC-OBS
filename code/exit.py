import os
import shutil
import subprocess

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

    force_kill_obs()

    if os.path.exists(user_config_path):
        shutil.rmtree(user_config_path)
    shutil.copytree(appdata_config_path, user_config_path)

    print(f"✅ Configuration for '{username}' saved.")

if __name__ == "__main__":
    save_current_config()
