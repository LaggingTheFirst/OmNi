import os
import sys
import shutil

def get_app_data_path():
    """Get the application data path for the current platform."""
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'OmNi')
    else:
        return os.path.join(os.path.expanduser('~'), '.omni')

def ensure_app_structure():
    """
    Ensures that the AppData directory structure exists.
    Creates:
    - Root folder (OmNi)
    - Uploads folder
    - Default config.py if missing (copies from bundle or writes default)
    """
    base_path = get_app_data_path()
    uploads_path = os.path.join(base_path, 'uploads')
    config_path = os.path.join(base_path, 'config.py')
    
    # Create directories
    try:
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(uploads_path, exist_ok=True)
        print(f"Directory structure ensured at: {base_path}")
    except Exception as e:
        print(f"Error creating directories: {e}")

    # Handle Config File
    if not os.path.exists(config_path):
        print("Config not found in AppData. Creating default flat config.")
        
        # We need a FLAT config (key=value) for from_pyfile to work correctly within Flask.
        # The source config.py uses specific python classes which doesn't mix well when 
        # mixing config.from_object and config.from_pyfile.
        
        default_config = """import os

# AppData Config for OmNi
# You can edit this file to change settings. Restart the app for changes to take effect.

# SECURITY: Change this to a random string for production security!
SECRET_KEY = 'dev-key-change-in-prod-if-exposed'

# Network Settings
HOST = '0.0.0.0'
PORT = 5000

# Admin Credentials (Initial setup only)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Setup Status
SETUP_COMPLETE = False

# Database & Uploads (Best left alone to ensure persistence)
# Paths are automatically handled by the app to point to this folder.
"""
        try:
            with open(config_path, 'w') as f:
                f.write(default_config)
            print(f"Created default config at {config_path}")
        except Exception as e:
            print(f"Failed to write default config: {e}")
            
    return base_path