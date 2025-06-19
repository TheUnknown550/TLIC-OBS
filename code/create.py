import os
import json
import shutil
import subprocess
import hashlib
import uuid
import winreg
import tkinter as tk
from tkinter import messagebox, ttk
import time


# Configuration
USERS_FILE = "obs_users.json"
CONFIG_BASE = os.path.abspath("obs_configs")

class OBSUserManager:
    def __init__(self):
        self.obs_path = self.detect_obs_path()
        self.users = self.load_users()
        self.setup_directories()

    def detect_obs_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\OBS Studio") as key:
                install_path = winreg.QueryValueEx(key, "")[0]
                obs_path = os.path.join(install_path, "bin", "64bit", "obs64.exe")
                if os.path.exists(obs_path):
                    return obs_path
        except:
            pass

        default_path = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
        if os.path.exists(default_path):
            return default_path

        messagebox.showerror("Error", "OBS Studio not found. Please install OBS first.")
        raise FileNotFoundError("OBS executable not found")

    def setup_directories(self):
        os.makedirs(CONFIG_BASE, exist_ok=True)

    def load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=2)

    def hash_password(self, password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def check_password(self, hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

    def create_user(self, username, password):
        if username in self.users:
            return False, "Username already exists"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        self.users[username] = self.hash_password(password)
        self.save_users()

        self.force_kill_obs()
        self.create_obs_config(username)
        return True, f"User '{username}' created successfully"

    def create_obs_config(self, username):
        user_config_path = os.path.join(CONFIG_BASE, username)
        template_path = os.path.abspath("obs_clean_template")

        if os.path.exists(user_config_path):
            shutil.rmtree(user_config_path)

        if os.path.exists(template_path):
            shutil.copytree(template_path, user_config_path)

            default_profile = os.path.join(user_config_path, "basic", "profiles", "default_profile")
            user_profile = os.path.join(user_config_path, "basic", "profiles", username)
            if os.path.exists(default_profile):
                os.rename(default_profile, user_profile)

            default_scene = os.path.join(user_config_path, "basic", "scenes", "default_scene.json")
            user_scene = os.path.join(user_config_path, "basic", "scenes", f"{username}.json")
            if os.path.exists(default_scene):
                os.rename(default_scene, user_scene)

            with open(os.path.join(user_config_path, "global.ini"), "w") as f:
                f.write("[Basic]\n")
                f.write(f"Profile={username}\n")
                f.write(f"SceneCollection={username}\n")
                f.write(f"SceneCollectionFile={username}.json\n")

            with open(os.path.join(user_profile, "basic.ini"), "w") as f:
                f.write(f"[General]\nName={username}\n")
                f.write("VideoAdapter=0\n")
                f.write("BaseWidth=1920\nBaseHeight=1080\nOutputWidth=1280\nOutputHeight=720\n")

            profiles_ini = os.path.join(user_config_path, "basic", "profiles", "profiles.ini")
            with open(profiles_ini, "w") as f:
                f.write("[General]\n")
                f.write(f"Name={username}\n")
                f.write(f"ProfileDir={username}\n")

        self.verify_configuration(username)

    def verify_configuration(self, username):
        user_config_path = os.path.join(CONFIG_BASE, username)
        required_files = [
            os.path.join(user_config_path, "global.ini"),
            os.path.join(user_config_path, "basic", "profiles", username, "basic.ini"),
            os.path.join(user_config_path, "basic", "scenes", f"{username}.json"),
            os.path.join(user_config_path, "basic", "profiles", "profiles.ini")
        ]
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Configuration file missing: {file}")

    def force_kill_obs(self):
        subprocess.call(["taskkill", "/F", "/IM", "obs64.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def launch_obs(self, username):
        self.force_kill_obs()

        user_config_path = os.path.join(CONFIG_BASE, username)
        appdata_config_path = os.path.join(os.getenv("APPDATA"), "obs-studio")

        if not os.path.exists(user_config_path):
            self.create_obs_config(username)

        # Robustly remove existing config folder if it exists
        if os.path.exists(appdata_config_path):
            try:
                shutil.rmtree(appdata_config_path)
            except Exception as e:
                # Sometimes files can be locked, retry a few times
                for _ in range(5):
                    time.sleep(0.5)
                    try:
                        shutil.rmtree(appdata_config_path)
                        break
                    except Exception:
                        pass
                else:
                    messagebox.showerror("Error", f"Failed to delete existing OBS config folder:\n{e}")
                    return False

        try:
            # Python 3.8+: dirs_exist_ok=True allows copying into existing folders
            shutil.copytree(user_config_path, appdata_config_path)
        except FileExistsError:
            # As a fallback, try with dirs_exist_ok=True if Python version supports it
            try:
                shutil.copytree(user_config_path, appdata_config_path, dirs_exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy OBS config:\n{e}")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy OBS config:\n{e}")
            return False

        # Clean up some files if they exist
        for f in ["global.ini.bak", "global.json", "global.json.bak"]:
            try:
                os.remove(os.path.join(appdata_config_path, f))
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Warning: Could not remove {f}: {e}")

        # Remove unwanted folders quietly
        for folder in ["logs", "crashes", "plugin_config"]:
            shutil.rmtree(os.path.join(appdata_config_path, folder), ignore_errors=True)

        # Create config directory and write basic.ini
        config_dir = os.path.join(appdata_config_path, "config")
        os.makedirs(config_dir, exist_ok=True)
        try:
            with open(os.path.join(config_dir, "basic.ini"), "w") as f:
                f.write(f"[General]\nProfileDir={username}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write basic.ini:\n{e}")
            return False

        # Check if OBS locale file exists
        expected_locale = os.path.join(os.path.dirname(self.obs_path), "..", "..", "data", "obs-studio", "locale", "en-US.ini")
        if not os.path.exists(os.path.abspath(expected_locale)):
            messagebox.showerror("Error", f"Missing OBS locale file: {expected_locale}")
            return False

        return True


class OBSLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OBS User Login")
        self.user_manager = OBSUserManager()

        self.root.geometry("500x420")
        self.root.configure(bg="#2c3e50")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='white', font=('Segoe UI', 11))
        self.style.configure('TButton', font=('Segoe UI', 11), padding=6)
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#ecf0f1', background='#2c3e50')

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="🎥 OBS User Login", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=(0, 10))

        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=(0, 20))

        login_btn = ttk.Button(main_frame, text="Login", command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=(0, 15))

        create_btn = ttk.Button(main_frame, text="Create New Account", command=self.show_create_account)
        create_btn.grid(row=4, column=0, columnspan=2)

        for child in main_frame.winfo_children():
            child.grid_configure(padx=10, sticky=tk.EW)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return

        if username not in self.user_manager.users:
            messagebox.showerror("Error", "Username not found")
            return

        if not self.user_manager.check_password(self.user_manager.users[username], password):
            messagebox.showerror("Error", "Incorrect password")
            return

        with open("current_user.txt", "w") as f:
            f.write(username)

        if self.user_manager.launch_obs(username):
            self.root.destroy()


        time.sleep(1)  # Wait a moment to ensure OBS is ready
        ## Launch OBS after successful login
        obs_exe = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
        obs_cwd = r"C:\Program Files\obs-studio\bin\64bit"  # Main OBS folder
        try:
            subprocess.Popen([obs_exe, "--disable-shutdown-check"], cwd=obs_cwd)
            print("OBS launched successfully.")
        except FileNotFoundError:
            print("OBS executable not found. Please check the path.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def show_create_account(self):
        create_window = tk.Toplevel(self.root)
        create_window.title("Create New Account")
        create_window.geometry("400x300")
        create_window.configure(bg="#2c3e50")

        main_frame = ttk.Frame(create_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="🆕 Create New Account", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(main_frame, text="New Username:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        new_user_entry = ttk.Entry(main_frame, width=30)
        new_user_entry.grid(row=1, column=1, pady=(0, 10))

        ttk.Label(main_frame, text="New Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        new_pass_entry = ttk.Entry(main_frame, width=30, show="*")
        new_pass_entry.grid(row=2, column=1, pady=(0, 20))

        create_btn = ttk.Button(
            main_frame,
            text="Create Account",
            command=lambda: self.handle_create_account(
                new_user_entry.get().strip(),
                new_pass_entry.get(),
                create_window
            )
        )
        create_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        for child in main_frame.winfo_children():
            child.grid_configure(padx=10, sticky=tk.EW)

    def handle_create_account(self, username, password, window):
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return

        success, message = self.user_manager.create_user(username, password)
        if success:
            messagebox.showinfo("Success", message)
            window.destroy()
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = OBSLoginApp(root)
    root.mainloop()
