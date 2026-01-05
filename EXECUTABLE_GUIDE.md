# OmNi Standalone Build & Distribution Guide

> [!IMPORTANT]
> **Standalone builds are OS-specific.** An `.exe` file created on Windows will **only** run on Windows. To distribute OmNi on Linux or macOS, you must build the binary on a machine running that specific operating system.

## Quick Start (Windows)

### Building the Windows Executable (.exe)

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Build the executable:**
   ```powershell
   .\build_exe.ps1
   ```

   The executable will be created at: `dist\OmNi.exe`

### Configuration

- **Config Location:** `%APPDATA%\OmNi\config.py` (Windows)
  - *Note: On Linux/macOS, the path would be `~/.config/omni/config.py` but you must build a native binary first.*

- **First Run:** The config file is automatically created in the user's appdata directory on first run.
- **Customization:** Users can edit the config file directly for custom settings.

### Customizing the Executable

#### Adding an Icon
Edit `omni.spec` and add your icon path:
```python
exe = EXE(
    ...
    icon='path/to/your/icon.ico',
)
```

#### Changing the Name
Change `name='OmNi'` in `omni.spec` to your desired executable name.

#### Hidden Imports
If you add new dependencies, update the `hiddenimports` list in `omni.spec`.

### Distribution

1. Users can simply run: `OmNi.exe`
2. The app will automatically:
   - Create config directory in `%APPDATA%\OmNi\`
   - Copy the bundled config template if no config exists
   - Use the user's config for customization

### Environment Variables

Users can still set these environment variables for sensitive data:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Custom database URL
- `ADMIN_USERNAME` - Admin username
- `ADMIN_PASSWORD` - Admin password

### Directory Structure After Build

```
OmNi/
├── dist/
│   └── OmNi.exe          # Your executable
├── build/                # Build artifacts
├── config.py             # Config template (bundled)
├── main_exe.py           # Entry point
├── omni.spec             # PyInstaller spec
├── build_exe.ps1         # Build script
└── app/                  # Your Flask app (bundled)
```

### Troubleshooting

**Issue:** Antivirus blocking the executable
- Solution: This is common with PyInstaller. Test with a signed certificate or add exclusion.

**Issue:** Config file not found
- Solution: Check that `%APPDATA%\OmNi\config.py` exists. It's created on first run.

**Issue:** Database or uploads folder not found
- Solution: Update paths in config.py to use absolute paths or relative to `%APPDATA%\OmNi\`.

### Advanced Configuration

For production use, consider:
1. Setting environment variables for sensitive config (SECRET_KEY, admin credentials)
2. Using a separate database server instead of SQLite
3. Configuring uploads folder to a network location
