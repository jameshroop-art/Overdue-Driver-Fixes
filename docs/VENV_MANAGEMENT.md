# Virtual Environment Management

## Overview

driver-mgt automatically manages its own Python virtual environment to ensure consistent dependency management and isolation from system Python packages.

## How It Works

### Automatic Setup

When you run `driver-mgt` for the first time (or if the venv doesn't exist):

1. **Detection**: The application checks if it's running in a virtual environment
2. **Creation**: If not, it creates a new venv in the application directory
3. **Installation**: Installs all requirements from `requirements.txt` into the venv
4. **Restart**: Automatically restarts the application using the venv Python interpreter

This happens transparently - you don't need to manually activate anything.

### During Installation

When using `install.sh`, the virtual environment is created and configured automatically:

```bash
sudo bash install.sh
```

The installer:
- Creates a venv at `/opt/driver-mgt/venv/`
- Installs all requirements into the venv
- The driver-mgt script automatically uses this venv when run

## Usage

### Normal Operation

```bash
# The application automatically uses its venv
driver-mgt status

# No need to activate venv manually - it's automatic
driver-mgt
```

### Development Mode

If you need to skip venv setup (for development):

```bash
# Skip automatic venv setup
driver-mgt --no-venv status
```

### Manual Venv Management

If you want to manually manage the venv:

```bash
# Create venv manually
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt

# Run with --no-venv to skip auto-setup
./driver-mgt --no-venv
```

## Location

The virtual environment is created in:
- **Development**: `<app-dir>/venv/`
- **Installed**: `/opt/driver-mgt/venv/`

## Benefits

### Isolation
- Dependencies don't conflict with system packages
- Each version of driver-mgt can have its own dependency versions
- No risk of breaking other Python applications

### Consistency
- All users run with the same package versions
- Reproducible environments across systems
- Easier troubleshooting

### Clean System
- Doesn't pollute system Python installation
- Easy to remove (just delete the venv directory)
- No sudo needed for package installation (after initial setup)

## Troubleshooting

### Venv Creation Fails

```bash
# Ensure python3-venv is installed
sudo apt-get install python3-venv  # Debian/Ubuntu
sudo dnf install python3-venv      # Fedora
sudo pacman -S python              # Arch (includes venv)

# Try manual creation
cd /opt/driver-mgt  # or your app directory
python3 -m venv venv
```

### Requirements Installation Fails

```bash
# Check venv pip
./venv/bin/pip --version

# Upgrade pip
./venv/bin/pip install --upgrade pip

# Reinstall requirements
./venv/bin/pip install -r requirements.txt
```

### Wrong Python Version

The venv uses the Python version that created it. To use a different version:

```bash
# Remove old venv
rm -rf venv

# Create with specific Python version
python3.11 -m venv venv

# driver-mgt will use this venv automatically
```

### Check Venv Status

```python
# Run this to see venv info
python3 src/utils/venv_manager.py
```

Output shows:
- venv_path: Location of the venv
- venv_exists: Whether venv is created
- venv_active: Whether currently running in venv
- python_path: Current Python interpreter
- python_version: Python version in use

### Reset Venv

To completely reset the virtual environment:

```bash
# Remove venv
rm -rf /opt/driver-mgt/venv  # or your venv location

# Run driver-mgt - it will recreate automatically
driver-mgt
```

## Technical Details

### Implementation

The venv management is implemented in `src/utils/venv_manager.py`:

- **get_venv_path()**: Finds the application root and returns venv path
- **venv_exists()**: Checks if venv is properly configured
- **is_venv_active()**: Detects if running in a venv
- **create_venv()**: Creates a new virtual environment
- **install_requirements()**: Installs packages from requirements.txt
- **restart_in_venv()**: Restarts the application in venv context using `os.execv()`
- **ensure_venv()**: Main function that orchestrates the setup

### Execution Flow

```
driver-mgt starts
    ↓
Check: In venv?
    ↓ No
Check: venv exists?
    ↓ No
Create venv
    ↓
Install requirements
    ↓
Restart with venv Python (os.execv)
    ↓
driver-mgt starts (in venv)
    ↓ Yes (in venv)
Continue normal execution
```

### Security Considerations

- Uses Python's built-in `venv` module (not virtualenv)
- No external dependencies for venv creation
- Requirements installed only from local `requirements.txt`
- No automatic network access during venv creation
- User controls what's in requirements.txt

## Integration with Other Tools

### systemd Services

When running as a service, ensure the service file points to the correct path:

```ini
[Service]
ExecStart=/opt/driver-mgt/driver-mgt
# The script will automatically use its venv
```

### Desktop Entries

The desktop entry automatically uses the venv:

```desktop
[Desktop Entry]
Exec=/usr/local/bin/driver-mgt
# No activation needed - handled automatically
```

### Cron Jobs

For scheduled tasks:

```cron
# driver-mgt automatically uses its venv
0 * * * * /opt/driver-mgt/driver-mgt scan --no-keep-open
```

## Configuration

No configuration is needed - venv management is automatic. However, you can:

### Skip Venv (Development)

```bash
driver-mgt --no-venv <command>
```

### Use Different Requirements

Edit `requirements.txt` and remove/recreate the venv:

```bash
rm -rf venv
driver-mgt  # Will recreate with new requirements
```

## FAQs

**Q: Do I need to activate the venv before running driver-mgt?**
A: No, it's automatic. Just run `driver-mgt` directly.

**Q: Can I use my own venv?**
A: Yes, activate your venv first, then run with `--no-venv` flag.

**Q: What if I want system-wide Python packages?**
A: Use `--no-venv` flag, but this is not recommended.

**Q: Does venv work on Windows?**
A: Yes, the venv_manager supports both Unix and Windows paths.

**Q: How much disk space does venv use?**
A: Typically 100-200MB depending on dependencies (mostly PyQt6).

**Q: Can I share venv between multiple driver-mgt versions?**
A: Not recommended. Each installation should have its own venv.

**Q: What happens if requirements.txt changes?**
A: Remove the venv directory and run again to reinstall with new requirements.
