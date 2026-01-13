# Quick Start Guide - Updated for v1.0.1

## What's Fixed
- ✅ GUI no longer crashes with AttributeError
- ✅ Device tabs now display correctly
- ✅ Root privileges properly handled
- ✅ Clear privilege status indicator in GUI

## Installation

### Fresh Install
```bash
sudo bash install.sh
```

### Update Existing Installation
If you already have driver-mgt installed and are experiencing the AttributeError crash:
```bash
cd /path/to/Overdue-Driver-Fixes
git pull
sudo bash install.sh
```

## Running the Application

### Method 1: Desktop Launcher (Recommended)
- Click **"driver-mgt"** in your applications menu
- You'll be prompted for your password (pkexec authentication)
- Application launches with full root privileges
- Green indicator shows "🔓 Running with Root Privileges"

### Method 2: Command Line with Root
```bash
sudo driver-mgt
```

### Method 3: Limited Mode (View Only)
```bash
driver-mgt
```
- Orange indicator shows "⚠ Limited Mode (No Root)"
- Can view hardware information
- Cannot perform driver installations or system changes

## GUI Features

### Privilege Indicator
Look for the status in the title bar:
- **🔓 Running with Root Privileges** (green) - Full functionality
- **⚠ Limited Mode (No Root)** (orange) - View only mode

### Tabs Available
1. **Dashboard** - Hardware overview and driver status
2. **AI Settings** - Configure AI backend (Ollama/LLM Studio)
3. **System Info** - Detailed system information
4. **Device Tabs** - One tab per detected hardware device (NEW: Now working!)

### AI Assistant Features
- Real-time driver monitoring
- Risk assessment before driver installation
- Interactive chat for hardware questions
- Error analysis and troubleshooting

## CLI Commands

```bash
# Check system status
sudo driver-mgt status

# Scan for hardware
sudo driver-mgt scan

# Check AI status
driver-mgt ai-status

# Sign in to Ollama (if needed)
driver-mgt ai-signin
```

## Troubleshooting

### GUI Won't Start
```bash
# Check dependencies
driver-mgt --check-deps

# Install missing Qt libraries (Debian/Ubuntu)
sudo apt-get install libxcb-cursor0 libxkbcommon-x11-0 libegl1

# Install missing Qt libraries (Fedora)
sudo dnf install libxcb xcb-util-cursor libxkbcommon-x11 mesa-libEGL
```

### No Device Tabs Appearing
- Make sure you're running with root privileges (see green indicator)
- Run hardware scan: Click "Scan Hardware" button on Dashboard
- Check if hardware is detected: `sudo lspci` or `sudo lshw`

### AI Features Not Working
```bash
# Check if Ollama is running
systemctl status ollama

# Or check LM Studio status
driver-mgt ai-status

# Sign in to Ollama if needed
driver-mgt ai-signin
```

### Permission Issues
- Desktop launcher should automatically request password
- If running from terminal, use `sudo driver-mgt`
- Check that you're in sudoers group: `groups`

## Configuration Files

User configs stored in: `~/.config/driver-mgt/`
- profiles/
- curves/
- logs/
- corrections/
- reports/

System configs: `/etc/driver-mgt/`

## AI Backend Selection

### Using Ollama (Default)
- Installed automatically by `install.sh`
- Runs locally, requires sign-in for some models
- Start: `systemctl start ollama`

### Using LM Studio (Alternative)

**📖 Full Guide**: See [LMSTUDIO_SETUP.md](LMSTUDIO_SETUP.md) for complete installation and configuration instructions.

**Quick Setup**:
```bash
# 1. Download and install LM Studio
wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio.AppImage
chmod +x lm-studio.AppImage

# 2. Launch LM Studio
./lm-studio.AppImage

# 3. In LM Studio application:
#    - Go to "Search" tab and download models (e.g., starcoder, codellama)
#    - Go to "Local Server" tab
#    - Click "Start Server" (will run on localhost:1234)
#    - Select a model from the dropdown to load it

# 4. Launch driver-mgt with LM Studio
driver-mgt-lmstudio
# Or use the desktop launcher: "Driver Manager (LLM Studio)"
```

**💡 Bonus - Share Models with Ollama**:
```bash
# Share models between LM Studio and Ollama (saves disk space!)
bash setup-model-sharing.sh

# Now models from Ollama are accessible in LM Studio
# See: LMSTUDIO_OLLAMA_MODEL_SHARING.md
```

**Features**:
- ✓ Localhost operation (complete privacy)
- ✓ Download additional models from online repositories
- ✓ OpenAI-compatible API
- ✓ Multiple concurrent instances supported
- ✓ GPU acceleration (NVIDIA/AMD)
- ✓ Can share models with Ollama (no duplication)

**Requirements**:
- LM Studio must be running on http://localhost:1234
- At least one model downloaded and loaded
- 8GB+ RAM recommended (16GB+ for larger models)

## Support

### Logs
- Application logs: `~/.config/driver-mgt/logs/`
- System logs: `journalctl -u ollama` (for Ollama issues)

### Common Issues Fixed in This Update
- ❌ **Fixed**: AttributeError 'ollama_manager' crash
- ❌ **Fixed**: Missing device tabs
- ❌ **Fixed**: Privilege handling inconsistencies
- ✅ **Improved**: Clear privilege status indication
- ✅ **Improved**: Desktop launcher with automatic elevation

### Getting Help
1. Check logs in `~/.config/driver-mgt/logs/`
2. Run with debug mode: `sudo driver-mgt --debug`
3. Check BUGFIX_SUMMARY.md for detailed technical information
4. Report issues on GitHub

## Security Notes

- Application requires root for driver management operations
- pkexec provides secure privilege escalation (better than gksudo)
- Password prompt is from system polkit (trusted)
- AI backends can be sandboxed via configuration
- Domain whitelist protects against unauthorized network access

## What's Next

Future updates will include:
- Automatic driver updates
- Advanced cooling profiles
- Motherboard-specific optimizations
- Enhanced AI monitoring capabilities
- Integration with more AI backends

---

**Version**: 1.0.1
**Last Updated**: 2026-01-13
**Branch**: copilot/fix-gui-attribute-error
