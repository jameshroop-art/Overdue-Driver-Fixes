# GUI Usage Guide for driver-mgt

## Overview

The driver-mgt GUI provides a comprehensive interface for managing hardware drivers on Linux systems with AI-assisted features, risk assessment, and automatic fallback capabilities.

## Features

### 1. Dashboard
- Quick overview of all detected hardware
- One-click access to device-specific management
- Scan hardware button for detecting new devices
- Double-click any device to open its dedicated tab

### 2. Device-Specific Tabs

Each detected hardware component gets its own tab with:

#### Device Information
- Complete hardware details (type, name, vendor, ID, model)
- Current driver status and version
- Active/inactive status indicator

#### Current Driver Section
- Current driver name and status
- Test driver functionality
- Rollback to previous driver option
- Visual status indicators (green=active, red=no driver)

#### Risk Assessment
- Real-time risk percentage calculation
- Color-coded risk levels:
  - Green: Very Low (0-10%)
  - Light Green: Low (10-30%)
  - Orange: Medium (30-50%)
  - Red: High (50%+)
- AI remediation capability indicator
- Refresh button for updated assessment

#### Available Drivers
- Tabular view of all compatible drivers
- Filter by source: Official, Distribution, Community
- Columns display:
  - Driver name and version
  - Source (color-coded: green for official)
  - Stability rating (stable/beta)
  - Risk percentage
  - Install button with AI assistance
- Color-coded cells for quick visual assessment

#### AI-Assisted Features
- Real-time AI status indicator
- Available AI features list:
  - Pre-installation risk assessment
  - Real-time installation monitoring
  - Automatic error detection and correction
  - Post-installation verification
  - Proactive failure prevention
- AI analyze current setup button
- Enable/disable AI monitoring toggle

#### Fallback Plan
- Automatic fallback procedures detailed
- Recovery steps if installation fails
- Estimated recovery time
- Previous driver backup status
- Recovery mode indicator

### 3. System Information Tab
- Operating system details
- Hardware specifications
- Python version
- Configuration directory location
- AI assistant status with real-time updates

## Using the GUI

### Starting the Application

```bash
# Launch GUI (default mode)
driver-mgt

# Or explicitly specify GUI mode
driver-mgt --gui
```

### Managing Drivers

1. **Scan for Hardware**
   - Click "Scan Hardware" button on Dashboard
   - Wait for detection to complete
   - New tabs appear for each detected device

2. **View Device Details**
   - Click on any device tab
   - Review current driver status
   - Check risk assessment

3. **Install a Driver**
   - Navigate to device tab
   - Review available drivers table
   - Filter by source if needed
   - Click "Install with AI" on desired driver
   - Confirm installation
   - Monitor progress dialog
   - Wait for AI-assisted installation

4. **Test Current Driver**
   - Go to device tab
   - Click "Test Driver" button
   - Review test results

5. **Rollback Driver**
   - Navigate to device tab
   - Click "Rollback Driver" button
   - Confirm rollback
   - Previous driver will be restored

### AI-Assisted Installation Process

When you click "Install with AI", the system:

1. **Pre-Installation (20%)**
   - Assesses installation risks
   - Checks for known issues
   - Validates compatibility

2. **Installation (50%)**
   - Installs driver with monitoring
   - Detects errors in real-time
   - Applies automatic corrections

3. **Post-Installation (80%)**
   - Tests driver functionality
   - Verifies proper operation
   - Creates backup for rollback

4. **Completion (100%)**
   - Reports success/failure
   - Updates driver status
   - Refreshes risk assessment

### Understanding Risk Assessment

**Risk Percentage**: Likelihood of errors with current configuration
- Based on: Known issues database, hardware compatibility, driver stability
- Updated: Automatically after driver changes
- AI Remediation: Indicates if AI can prevent identified errors

**Color Coding**:
- **Green Background**: Safe (official source, stable)
- **Yellow Background**: Caution (beta, community source)
- **Red Background**: High Risk (>30% error probability)

### Fallback Protection

Every driver installation includes:
- **Automatic Backup**: Previous driver saved
- **Boot Failure Detection**: System detects if new driver fails
- **Automatic Revert**: Rolls back to working driver
- **Error Analysis**: AI analyzes failure cause
- **Alternative Suggestions**: Lists compatible alternatives

## Keyboard Shortcuts

- `Ctrl+R`: Refresh/Rescan hardware
- `Ctrl+Q`: Quit application
- `F5`: Refresh current tab
- `Ctrl+Tab`: Switch between tabs

## Configuration

GUI settings are stored in `~/.config/driver-mgt/config.json`:

```json
{
  "gui": {
    "theme": "dark",
    "start_minimized": false,
    "show_tray_icon": true,
    "auto_scan_on_start": true
  }
}
```

## Troubleshooting

### GUI Won't Launch
```bash
# Check dependencies
driver-mgt --check-deps

# Install missing dependencies
pip3 install PyQt6 psutil requests pyyaml

# Run in debug mode
driver-mgt --debug
```

### Device Not Detected
- Click "Scan Hardware" button
- Ensure hardware is properly connected
- Check system logs: `~/.config/driver-mgt/logs/`
- Run with debug: `driver-mgt --debug`

### AI Features Not Working
- Check AI status in System Info tab
- Verify Ollama is installed: `ollama --version`
- Start Ollama service: `systemctl start ollama`
- Install starcoder model: `ollama pull starcoder:3b`

### Installation Progress Stuck
- Wait for timeout (5 minutes)
- Check terminal for error messages
- Review logs in `~/.config/driver-mgt/logs/`
- Try installation without AI: Use system package manager

## Advanced Features

### Custom Driver Sources

Add custom driver repositories in config:
```json
{
  "drivers": {
    "custom_sources": [
      {
        "name": "Custom Repo",
        "url": "https://example.com/drivers",
        "type": "community"
      }
    ]
  }
}
```

### Monitoring Configuration

Enable continuous AI monitoring:
```bash
# From terminal
driver-mgt monitor --enable --ai-watch

# Or use GUI button in AI Features section
```

### Export Driver Reports

```bash
# Export current driver configuration
driver-mgt export-config --output ~/driver-config.json

# Export AI correction logs
driver-mgt export-corrections --output ~/corrections.txt
```

## Tips

1. **Always Review Risk Assessment** before installing drivers
2. **Use Official Sources** when available for lowest risk
3. **Enable AI Monitoring** for critical hardware (GPU, WiFi)
4. **Keep Backups** - automatic but verify in Fallback Plan section
5. **Test After Installation** using the Test Driver button
6. **Update Regularly** - check for driver updates weekly

## Support

- View logs: `~/.config/driver-mgt/logs/driver-mgt.log`
- AI logs: `~/.config/driver-mgt/logs/ai-assistant.log`
- Corrections: `~/.config/driver-mgt/corrections/`
- Reports: `~/.config/driver-mgt/reports/`

For issues, check the main README.md troubleshooting section.
