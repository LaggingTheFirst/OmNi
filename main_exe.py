"""
Entry point for OmNi executable.
Handles config file setup and ensures it's available in the user's appdata directory.
"""
import sys
import multiprocessing
# Import the consolidated setup logic
# Since main_exe is in the root, and we move setup_handlers.py to app/, we need to import it from app.
# However, app package might assume config exists for its __init__.py. 
# So we import ensure_app_structure without triggering app.__init__ if possible, 
# OR we rely on the fact that we can import submodules.
from app.setup_handlers import ensure_app_structure

def main():
    # 1. Setup AppData environment (Config & Folders)
    # This must happen before importing app (which uses config)
    try:
        config_dir = ensure_app_structure()
        
        # 2. Add config dir to path so 'import config' works and finds the one in AppData
        # (if we want to prioritize user config)
        sys.path.insert(0, config_dir)
        print(f"Added {config_dir} to sys.path")
        
    except Exception as e:
        print(f"Critical error during setup: {e}")
        # In a real GUI app we might want to show a message box here, 
        # but for console exe print is fine.
    
    # 3. Import and create app
    # Only import create_app AFTER setup is done
    try:
        from app import create_app
        app = create_app()
        
        print(f"Starting OmNi...")
        # Bind to 0.0.0.0 as requested for file sharing
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == '__main__':
    # PyInstaller multiprocessing fix for Windows
    multiprocessing.freeze_support()
    main()
