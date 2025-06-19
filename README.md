# OBS User Manager

## Overview

**OBS User Manager** is a Windows application that allows multiple users to manage their own OBS Studio configurations on a shared computer. Each user can create an account, log in, and have their own personalized OBS settings, scenes, and profiles. The application ensures that each user's OBS environment is isolated and secure.

## Features

- **User Accounts:** Create and manage individual user accounts with secure password hashing.
- **OBS Configuration Isolation:** Each user gets a separate OBS configuration, including scenes and profiles.
- **Easy Login:** Simple graphical interface for logging in and switching users.
- **Safe Config Management:** Automatically saves and restores user-specific OBS settings.
- **No OBS Launch:** The app prepares the environment but does not launch OBS automatically.

## How to Use

1. **Download and Extract:** Download the exported `.exe` file and place it in a folder of your choice.
2. **Run the Application:** Double-click the `.exe` file to start the OBS User Manager.
3. **Create an Account:** Click "Create New Account" and enter a username (min. 3 characters) and password (min. 6 characters).
4. **Login:** Enter your credentials and click "Login".
5. **Start OBS:** After login, open OBS Studio manually. Your personalized configuration will be loaded.
6. **Switch Users:** Close OBS, then log in as a different user through the OBS User Manager.

## Requirements

- **Windows 10/11**
- **OBS Studio installed** (default path: `C:\Program Files\obs-studio`)
- The `.exe` must be run with permissions to read/write to the OBS configuration directories.

## Notes

- The application does **not** launch OBS automatically; it prepares the configuration for the logged-in user.
- User data is stored in `obs_users.json` and configuration folders under `obs_configs`.
- To save your OBS settings, always close OBS before switching users.

## Troubleshooting

- **OBS Not Found:** Ensure OBS Studio is installed in the default location.
- **Permissions:** Run the application as an administrator if you encounter permission errors.
- **Missing Files:** If you see errors about missing configuration files, contact your administrator.

## License

This project is for educational and internal use only.
