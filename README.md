# OmNi File Sharer 

> **Current Status**: 🚀 **Beta v1.0.0**

OmNi is a self-hosted, local network file-sharing application designed for speed, privacy, and ease of use. Built with Python (Flask) and a modern glassmorphism UI, it allows you to share files securely across devices on your LAN.

![OmNi Dashboard](screenshots/dashboard.png)
## Features

- **📂 Smart Organization**: Create folders, navigate breadcrumbs, and organize your files.
![Smart Organization Demo](screenshots/newfoldertest.mp4)
- **🚀 Drag & Drop**: Upload files easily by dragging them anywhere on the dashboard.
- **👁️ Live Previews**: Preview images, videos, audio, and PDFs directly in the browser.
- **🔍 Instant Search**: Filter files by name or type instantly.
- **🔒 Privacy Control**: Mark files and **Folders** as **Public** (visible to everyone) or **Private** (only you).
- **🖥️ Smart Organization**: Automatically sorts large file collections into logical folders (Movies, Images, Documents, Music, Archives).
- **🔒 End-to-End Encryption (E2EE)**: Encrypt files in your browser before upload. Only you hold the password.
- **👤 User Profiles**: Customize your identity with a bio, display name, and avatar.
- **🌏 Unicode Support**: Full support for multi-language filenames (Korean, Chinese, Emoji, etc.).
- **📱 PWA & Mobile-Ready**: Install as an app on your phone. Connect instantly by scanning a QR code.
- **📂 Smart Dashboard**: Grid view with file previews, size details, and quick actions.
- **🛡️ Global Admin**: Admins have full visibility over all folders and files to manage the server effectively.
- **👥 User Sharing**: Share private files with specific users securely.

- **🛡️ Admin Dashboard**: Manage users, view activity logs, and moderate content.
![OmNi Dashboard](screenshots/admin.png)

- **📱 Fully Mobile Responsive**: A stacked, touch-friendly interface that works perfectly on phones and tablets.
  - adaptive grids
  - touch-optimized controls
  - smart layouts for small screens
- **📲 PWA Support**: Install OmNi as a native-like app on your home screen for quick access.
- **🔗 QR Connection**: Instantly connect mobile devices by scanning a QR code—no manual IP entry required.

## Technology Stack

- **Backend**: Python 3, Flask, SQLAlchemy (SQLite)
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), Vanilla JavaScript
- **Auth**: Flask-Login, Bcrypt

### Design Philosophy
> "I chose languages that even a 4th grader should be able to work with."

This project works with **standard, readable technologies** (Python, HTML, CSS) to ensure it is **easy to understand and modify**.
- **Security Check**: While basic security is implemented, you are encouraged to audit the code and add more layers (like SSL/TLS) yourself.
- **Future**: More advanced security features may be implemented in future updates, but the codebase is yours to improve!

## Installation

### Prerequisites
- Python 3.8+
- Git

### Setup

> [!WARNING]
> **Security Configuration**: Before running in production or on a shared network, you **MUST** review `config.py`.
> - Change `SECRET_KEY` to a random secure string.
> - Change `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
> - Review `ALLOWED_EXTENSIONS` for your security needs.

1. **Clone the repository**
   ```bash
   git clone https://codeberg.org/lagging/omni.git
   cd omni
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: If `requirements.txt` is missing, install: `flask flask-sqlalchemy flask-login flask-bcrypt`)*

4. **Initialize the Database**
   The database is created automatically on the first run.
   
   *Important*: If you modify the database models, you may need to delete `instance/omni.db` to reset it.

5. **Run the Application**
   ```bash
   python run.py
   ```

6. **Access the App**
   Open your browser and go to:
   - Local: `http://127.0.0.1:5000`
   - Network: `http://<YOUR_LOCAL_IP>:5000` (e.g., `192.168.1.15:5000`)

## Building a Standalone Windows Executable (.exe)

> [!NOTE]
> This step is **completely optional**. Running OmNi directly with `python run.py` works perfectly fine on all platforms (Windows, Linux, Mac). The executable option is provided for convenience for **Windows users** who don't have Python installed.
>
> **Linux/macOS Users**: Please run the application using the standard Python setup instructions above. Standalone binaries for these platforms must be built on their respective systems using PyInstaller.
>
> **Remember:** Only the host machine needs to run OmNi — other users simply connect through their browser via the network!

You can build OmNi as a standalone Windows `.exe` file for easy distribution — no Python installation required for end users! **Even when packaged, the config file remains fully editable** so you can still customize settings.

### 🐳 Docker (Easy!)
1. Install Docker Desktop.
2. Run:
   ```bash
   docker-compose up -d
   ```
   OmNi will be available at `http://localhost:5000`.

### 🌍 Remote Access
Want to access OmNi from outside your home network?
👉 [Read the Remote Access Guide](REMOTE_ACCESS.md)

## 🤝 Contributing

### Quick Build

```powershell
# Install dependencies (includes PyInstaller)
pip install -r requirements.txt

# Build the executable
.\build_exe.ps1
```

The executable will be created at `dist\OmNi.exe`.

### Configuration for Executable

- Config is stored at `%APPDATA%\OmNi\config.py` (Windows) or `~/.config/omni/config.py` (Linux/Mac)
- Config file is auto-created on first run
- Users can customize settings by editing the config file directly

> See [EXECUTABLE_GUIDE.md](EXECUTABLE_GUIDE.md) for detailed build instructions, customization options, and troubleshooting.

## Usage

- **Default Admin Login**:
  - Username: `admin`
  - Password: `admin`
  - *Please change these credentials in `config.py` or create a new admin account immediately.*

## License

MIT License. Feel free to modify and host it for your own needs.
