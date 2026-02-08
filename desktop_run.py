import os
import sys
import threading
import time
import webbrowser
import webview
import ctypes
from app import create_app

def hide_console():
    """Hide the console window on Windows."""
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd != 0:
            user32.ShowWindow(hWnd, 0) # 0 = SW_HIDE

def run_flask(app):
    """Run the Flask server."""
    app.run(host='127.0.0.1', port=5000, threaded=True, use_reloader=False)


class Api:
    """Python API exposed to JavaScript for native operations."""
    
    def download_file(self, url):
        """Open download URL in system browser."""
        webbrowser.open(url)
        return True
    
    def open_uploads_folder(self):
        """Open the uploads folder in File Explorer."""
        import subprocess
        # Use the same AppData path that Flask uses
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        uploads_path = os.path.join(appdata, 'OmNi', 'uploads')
        if os.path.exists(uploads_path):
            subprocess.Popen(f'explorer "{uploads_path}"')
            return True
        return False


if __name__ == '__main__':
    # Hide console on windows for "App" feel
    hide_console()

    # Initialize Flask app
    flask_app = create_app()
    
    # Start Flask in a background thread
    t = threading.Thread(target=run_flask, args=(flask_app,))
    t.daemon = True
    t.start()

    # Wait for the server to spin up
    print("Starting OmNi Desktop...")
    time.sleep(2)

    # Launch PyWebView
    # PyWebView on Windows prefers PNG over ICO
    icon_path = os.path.abspath(os.path.join('app', 'static', 'icon-512.png'))
    
    # Create API instance for JS bridge
    api = Api()
    
    window = webview.create_window(
        'OmNi Desktop', 
        'http://127.0.0.1:5000',
        width=1200, 
        height=800,
        min_size=(800, 600),
        background_color='#050508',
        js_api=api  # Expose Python API to JavaScript
    )

    # Start with icon (PyWebView 6.x API)
    webview.start(icon=icon_path if os.path.exists(icon_path) else None)


