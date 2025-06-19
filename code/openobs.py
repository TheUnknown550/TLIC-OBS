import subprocess

obs_exe = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
obs_cwd = r"C:\Program Files\obs-studio\bin\64bit"  # Main OBS folder

try:
    subprocess.Popen(obs_exe, cwd=obs_cwd)
    print("OBS launched successfully.")
except FileNotFoundError:
    print("OBS executable not found. Please check the path.")
except Exception as e:
    print(f"An error occurred: {e}")
