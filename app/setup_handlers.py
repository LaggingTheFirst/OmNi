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
        print("Config not found in AppData. Attempting to create...")
        
        # 1. Try to find bundled config
        source_config = None
        
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            # we added ('config.py', '.') so it should be in sys._MEIPASS
            base_dir = sys._MEIPASS
            source_config = os.path.join(base_dir, 'config.py')
            print(f"Running frozen. Looking for config at: {source_config}")
        else:
            # Running from source (dev)
            # This file is in app/setup_handlers.py, config is in root (parent of app)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            source_config = os.path.join(base_dir, 'config.py')
            print(f"Running from source. Looking for config at: {source_config}")

        # 2. Copy if source exists
        if source_config and os.path.exists(source_config):
            try:
                shutil.copy2(source_config, config_path)
                print(f"Copied config from {source_config} to {config_path}")
            except Exception as e:
                print(f"Failed to copy config: {e}")
        else:
            # 3. Fallback: Write default config string
            print("Source config not found. Writing default config.")
            default_config = """import os

basedir = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = 'dev-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'omni.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'mp4', 'mp3', 'mkv', 'iso', 'exe', 'msi'}
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin'
    HOST = '0.0.0.0'
    PORT = 5000

    @staticmethod
    def init_app(app):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        instance_path = os.path.join(Config.basedir, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
"""
            try:
                with open(config_path, 'w') as f:
                    f.write(default_config)
                print(f"Created default config at {config_path}")
            except Exception as e:
                print(f"Failed to write default config: {e}")
            
    return base_path