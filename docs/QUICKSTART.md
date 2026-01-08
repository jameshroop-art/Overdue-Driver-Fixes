# Quick Start Guide

## Installation

driver-mgt integrates CLI and GUI components seamlessly. A single installation provides both interfaces.

### Method 1: Using install.sh (Recommended)

```bash
# Clone the repository
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# Run the installer (requires sudo)
sudo bash install.sh

# Launch driver-mgt
driver-mgt
```

### Method 2: Manual Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Make driver-mgt executable
chmod +x driver-mgt

# Run driver-mgt
./driver-mgt
```

## First Run

When you first run driver-mgt, it will:
1. Create configuration directories in `~/.config/driver-mgt/`
2. Copy configuration templates
3. Initialize both GUI and CLI components
4. Scan for hardware (if you use CLI commands)

The installation ensures the GUI and program work together seamlessly, sharing the same configuration and virtual environment.

## Basic Usage

### GUI Mode

Simply run:
```bash
driver-mgt
```

This will open the graphical interface where you can:
- View detected hardware in the Dashboard tab
- Check system information
- Monitor AI assistant status

### CLI Mode

#### Check System Status
```bash
driver-mgt status
```
Shows detected hardware components.

#### Scan for Drivers
```bash
driver-mgt scan --all
```
Scans for available drivers for all detected hardware.

#### Check AI Assistant
```bash
driver-mgt ai-status
```
Checks if Ollama is running and configured.

#### Check Dependencies
```bash
driver-mgt --check-deps
```
Verifies all required Python packages are installed.

## Configuration

Configuration files are located in `~/.config/driver-mgt/`:

- `config.json` - Main application settings
- `ai-config.json` - AI assistant settings
- `logs/` - Application logs
- `corrections/` - AI correction event logs
- `reports/` - Error reports

## Troubleshooting

### PyQt6 Not Found

If you get "No module named 'PyQt6'":
```bash
pip3 install PyQt6
```

### Permission Errors

Some operations require root privileges. Use:
```bash
sudo driver-mgt [command]
```

### Hardware Not Detected

Make sure you have `lspci` installed:
```bash
# Ubuntu/Debian
sudo apt-get install pciutils

# Fedora
sudo dnf install pciutils

# Arch
sudo pacman -S pciutils
```

## Next Steps

1. **Install Ollama** (optional, for AI features):
   - Visit https://ollama.ai
   - Follow installation instructions
   - Run: `ollama pull starcoder:3b`

2. **Explore the GUI**:
   - Check the Dashboard for detected hardware
   - View System Info tab
   - Check AI status

3. **Use CLI Commands**:
   - Try `driver-mgt status`
   - Try `driver-mgt scan --all`
   - Try `driver-mgt ai-status`

## Getting Help

- Check the full README.md for detailed documentation
- Check docs/DEVELOPMENT.md for developer information
- Report issues on GitHub

## Privacy Note

- All AI processing is local (Ollama runs on localhost)
- No data is transmitted externally
- All logs remain on your system
- Only starcoder:3b model is used
