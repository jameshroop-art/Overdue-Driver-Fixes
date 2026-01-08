# driver-mgt - Advanced Linux Driver & Hardware Management System

**Overdue Driver Adjustment Project**

driver-mgt is a comprehensive driver and hardware management system designed to bridge the gap between Windows-level hardware control and Linux environments. Specifically built to fully utilize NVIDIA RTX graphics cards, ASUS motherboard chipsets, WiFi drivers, and advanced cooling systems on Linux.

## 🎯 Project Goals

- **Full Hardware Potential**: Enable complete functionality of NVIDIA RTX GPUs (Ray Tracing, DLSS, CUDA)
- **ASUS Hardware Support**: Complete chipset and WiFi driver stability
- **Advanced Cooling Control**: Precise pump, fan, and temperature management for watercooled systems
- **Unified Interface**: Single GUI application to control all hardware aspects
- **Low System Impact**: Efficient background operation with minimal resource usage

## ✨ Features

### Driver Management
- 🔍 **Hardware Detection & Identification**
  - Automatic detection of manufacturer make and model
  - Positive identification of installed hardware components
  - Current driver and chipset enumeration
  - Real-time hardware inventory

- 🎮 **NVIDIA RTX Driver Control**
  - Official NVIDIA repository integration
  - Automatic driver detection and switching
  - CUDA toolkit management
  - Performance profile optimization
  - Power management controls
  - Stability and reliability ratings per driver version

- 📡 **ASUS WiFi & Chipset Drivers**
  - Official ASUS repository support
  - MediaTek, Realtek, Intel driver support
  - Firmware management
  - Feature enablement (WiFi 6E, proper speeds)
  - Stability improvements
  - Driver compatibility scoring

- 🔧 **AMD Hardware Support**
  - Official AMD repository integration
  - GPU and chipset driver management
  - AMDGPU and ROCm support
  - Stability and reliability ratings

- 📊 **Multi-Source Driver Discovery**
  - Official manufacturer repositories (NVIDIA, ASUS, AMD, Intel)
  - Distribution-specific package sources
  - Community-maintained drivers with user reviews
  - Stability and reliability ratings for all options
  - Fallback to known Linux sources when official drivers unavailable

### Cooling System Control
- 🌡️ **Advanced Temperature Monitoring**
  - Real-time CPU and GPU temperature graphs
  - Historical data tracking
  - Alert thresholds

- 💨 **Fan & Pump Control**
  - 10-point custom curve editor
  - Individual fan control
  - AIO pump speed management
  - Case fan optimization
  - RPM monitoring

- 🤖 **Auto Mode**
  - Safe parameter enforcement
  - Workload-based adjustments
  - Thermal protection
  - Hybrid cooling strategies

### GUI Features
- 📊 **Dynamic Tabbed Interface**
  - Hardware-specific tabs for each detected component
  - Driver Management with stability ratings
  - NVIDIA Control Center
  - WiFi Control
  - Cooling Control
  - Performance Monitor
  - System Information
  - Per-device driver options and ratings

- 📈 **Real-time Graphs**
  - Temperature tracking
  - Fan speed visualization
  - Performance metrics
  - Power consumption

- ⚡ **Manual & Auto Modes**
  - Full manual control for enthusiasts
  - Intelligent auto mode for stability
  - Quick profile switching

- 🛡️ **Automated Installation Management**
  - GUI-managed driver installs and setup
  - Automatic fallback on installation failure
  - Pre-installation compatibility checks
  - Post-installation verification tests
  - Automatic rollback to previous driver on boot failure

### AI-Assisted Driver Management
- 🤖 **Integrated Ollama LLM (starcoder:3b)**
  - Automatic Ollama installation and configuration if not present
  - Local localhost deployment for privacy
  - AI-guided installation process for user's specific Linux distribution
  - Real-time error detection and automatic correction
  - Installation monitoring and troubleshooting
  - Post-install verification testing

- 🔄 **Intelligent Error Recovery**
  - Automatic detection of driver failures after restart
  - Revert to previous working driver on failure
  - AI-powered error analysis and correction attempts
  - Automated testing after corrections
  - Alternative driver suggestions when correction fails

- 📝 **Automated Issue Reporting**
  - Documentation of installation errors
  - Automatic generation of manufacturer bug reports
  - Includes driver ID, error details, and suggested remediation
  - Excludes attempted remediation details for clean reporting
  - Maintains error log for troubleshooting

- 🔎 **Alternative Driver Discovery**
  - Search for compatible alternative drivers
  - User review aggregation and ratings
  - Community feedback integration
  - Compatibility scoring based on similar hardware configurations

- ⚙️ **Resource Management**
  - Automatic Ollama server shutdown after operations
  - Exclusive use of starcoder:3b model for consistency
  - Minimal resource footprint during idle
  - On-demand AI activation

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# Run the installer
sudo bash install.sh

# Launch driver-mgt
driver-mgt
```

The installer will:
- Install all required dependencies
- Set up Ollama with starcoder:3b model
- Configure localhost AI services
- Set up system services
- Create desktop shortcut
- Configure permissions
- Initialize hardware detection
- Scan for official manufacturer repositories

## 📋 Requirements

### System Requirements
- Linux kernel 5.10 or newer
- Python 3.9+
- Root/sudo access for hardware control
- X11 or Wayland display server

### Supported Hardware
- **GPUs**: NVIDIA RTX 20, 30, 40 series; AMD Radeon RX 5000, 6000, 7000 series
- **Motherboards**: ASUS (ROG, TUF, Prime series), MSI, Gigabyte, ASRock
- **WiFi**: MediaTek, Realtek, Intel, Broadcom adapters
- **Cooling**: Most AIO liquid coolers, PWM fans
- **Chipsets**: Intel, AMD, and ARM-based chipsets

### Dependencies
- PyQt6 (GUI framework)
- nvidia-smi (NVIDIA control)
- lm-sensors (temperature monitoring)
- liquidctl (AIO control)
- i2c-tools (hardware communication)
- Ollama (AI-assisted driver management)
- starcoder:3b model (automatic installation)
- curl/wget (repository access)

## 🎨 GUI Overview

### Main Window Tabs

**Dynamic Hardware-Specific Tabs** - Automatically generated based on detected hardware:

1. **Driver Management Dashboard**
   - Comprehensive hardware inventory
   - Detected components with manufacturer/model
   - Current driver versions and status
   - Available updates from official sources
   - Stability and reliability ratings
   - Quick action buttons for all devices

2. **Per-Device Tabs** (Auto-generated for each detected component)
   - Device-specific information and status
   - Available driver options with ratings:
     * Official manufacturer drivers
     * Distribution-provided drivers
     * Community drivers with user reviews
   - Stability score and reliability metrics
   - Installation status and history
   - One-click install/update/rollback
   - AI-assisted troubleshooting

3. **NVIDIA Control** (if NVIDIA GPU detected)
   - GPU information and specifications
   - Available driver versions from official repo
   - Clock speeds and voltages
   - Power limits
   - Fan curves
   - CUDA settings
   - Driver stability ratings

4. **AMD Control** (if AMD GPU detected)
   - GPU information and specifications
   - AMDGPU driver options
   - ROCm stack management
   - Performance tuning
   - Driver compatibility scores

5. **WiFi Control** (for each WiFi adapter)
   - Adapter model and chipset
   - Driver options and ratings
   - Connection management
   - Driver optimization
   - Feature toggles
   - Signal monitoring

6. **Cooling Control**
   - Temperature graphs (CPU/GPU)
   - Fan curve editor (10-point)
   - Pump speed control
   - RPM monitoring
   - Auto/Manual mode toggle

7. **Performance Monitor**
   - Real-time system metrics
   - Resource usage
   - Workload detection
   - Historical data
   - Driver performance impact

8. **System Info**
   - Complete hardware detection results
   - Driver versions and sources
   - Firmware information
   - System configuration
   - AI assistant status

## 🛠️ Configuration

driver-mgt stores configuration in:
```
~/.config/driver-mgt/
├── config.json          # Main configuration
├── profiles/            # Cooling profiles
├── curves/              # Fan/pump curves
└── logs/                # Application logs
```

### Creating Custom Cooling Profiles

1. Open driver-mgt
2. Navigate to "Cooling Control" tab
3. Click "Create Profile"
4. Set 10 temperature points with corresponding fan/pump speeds
5. Enable "Auto Mode" or use manual override

### Example Curve Configuration
```
Temperature (°C) | Fan Speed (%)
30               | 20
40               | 25
50               | 35
60               | 50
70               | 65
75               | 75
80               | 85
85               | 95
90               | 100
95               | 100
```

## 🤖 AI-Assisted Driver Management Workflow

### Overview
driver-mgt integrates Ollama with the starcoder:3b model to provide intelligent, automated driver management with error recovery and reporting capabilities.

### Automatic Setup Process
1. **Ollama Installation**: If not detected, driver-mgt automatically installs Ollama
2. **Model Configuration**: Downloads and configures starcoder:3b model
3. **Localhost Setup**: Configures Ollama to run on localhost for privacy
4. **Integration**: Connects AI assistant to driver management pipeline

### Driver Installation Workflow

**Step 1: Hardware Detection**
- Scans system for all hardware components
- Identifies manufacturer, make, and model
- Detects currently installed drivers and chipsets
- Creates hardware inventory

**Step 2: Repository Discovery**
- Checks official manufacturer repositories (NVIDIA, ASUS, AMD, Intel)
- Queries distribution-specific package sources
- Searches community driver repositories
- Compiles list with stability ratings and user reviews

**Step 3: Driver Options Presentation**
- GUI displays all available drivers per device
- Shows stability/reliability ratings
- Includes user reviews and compatibility scores
- Highlights recommended options

**Step 4: AI-Guided Installation**
When installing a driver:
1. AI analyzes user's specific Linux distribution
2. Pre-installation compatibility check
3. Monitors installation process in real-time
4. Detects and auto-corrects errors during install
5. Runs post-installation verification tests
6. Validates driver functionality

**Step 5: Post-Install Testing**
- GPU: Rendering tests, compute verification
- WiFi: Connection stability, throughput tests
- Chipset: Device enumeration, functionality checks
- Creates baseline for future comparisons

**Step 6: Error Recovery (if needed)**
If installation fails or system won't boot:
1. **Automatic Detection**: Detects driver failure on boot
2. **Auto-Revert**: Reverts to previous working driver
3. **AI Analysis**: Analyzes error logs and failure mode
4. **Correction Attempt**: If possible, AI attempts automatic fix
5. **Re-test**: Runs verification tests after correction
6. **Alternative Search**: If correction fails, finds alternative drivers

**Step 7: Automated Reporting**
For unresolvable issues:
- Generates clean error report (excludes attempted fixes)
- Includes driver ID, hardware specs, and error details
- Suggests remediation approach
- Saves report to `~/.config/driver-mgt/reports/`
- Optionally submits to manufacturer

**Step 8: Resource Cleanup**
- Ollama server shuts down after operations complete
- Minimal resource usage during idle
- AI reactivates on-demand for next operation

### Privacy & Security
- All AI processing is local (localhost only)
- No data transmitted to external services
- Only starcoder:3b model used for consistency
- Error reports reviewed before external submission
- Full audit trail of AI operations

## 🔧 Advanced Usage

### AI-Assisted Driver Installation

driver-mgt uses Ollama with the starcoder:3b model for intelligent driver management:

```bash
# Manual AI-assisted driver install
driver-mgt install --device <device-id> --ai-assist

# Install with specific driver from official repo
driver-mgt install --device <device-id> --source official --ai-assist

# Test driver installation
driver-mgt test --device <device-id>

# Rollback to previous driver
driver-mgt rollback --device <device-id>

# Check Ollama status
driver-mgt ai-status

# View AI installation logs
driver-mgt logs --ai
```

The AI assistant will:
1. Analyze your specific Linux distribution
2. Verify driver compatibility
3. Guide the installation process
4. Run post-install verification tests
5. Automatically correct any errors
6. Revert on failure and suggest alternatives

### Running as System Service

driver-mgt can run as a background service for automatic hardware management:

```bash
sudo systemctl enable driver-mgt
sudo systemctl start driver-mgt
```

### Command Line Interface

```bash
# Check system status and detected hardware
driver-mgt status

# Scan for available drivers
driver-mgt scan --all

# List drivers for specific device
driver-mgt list-drivers --device <device-id>

# Apply cooling profile
driver-mgt cooling --profile silent

# Update drivers with AI assistance
driver-mgt driver --update nvidia --ai-assist

# Monitor temperatures
driver-mgt monitor --temp

# Generate bug report for manufacturer
driver-mgt report --device <device-id> --error <error-id>
```

## 🐛 Troubleshooting

### NVIDIA Driver Issues
```bash
# Check driver status
nvidia-smi

# Reload driver-mgt NVIDIA module
sudo driver-mgt driver --reload nvidia

# AI-assisted troubleshooting
sudo driver-mgt diagnose --device nvidia --ai-assist

# View available NVIDIA driver versions
driver-mgt list-drivers --device nvidia --source official
```

### Driver Installation Failed
```bash
# View AI installation logs
driver-mgt logs --ai --device <device-id>

# Attempt AI-assisted recovery
sudo driver-mgt fix --device <device-id> --ai-assist

# Rollback to previous working driver
sudo driver-mgt rollback --device <device-id>

# Search for alternative drivers
driver-mgt search-alternatives --device <device-id>
```

### System Won't Boot After Driver Update
The AI assistant automatically detects boot failures and reverts to the previous driver:
- System will automatically boot with previous driver
- Error logs saved to: `~/.config/driver-mgt/logs/boot-failure.log`
- Manufacturer report generated in: `~/.config/driver-mgt/reports/`
- Check suggested alternatives: `driver-mgt alternatives --device <device-id>`

### Cooling Control Not Working
```bash
# Check sensor detection
sensors

# Verify liquidctl devices
sudo liquidctl list

# Check permissions
sudo usermod -a -G i2c $USER
```

### GUI Won't Launch
```bash
# Check dependencies
driver-mgt --check-deps

# Run in debug mode
driver-mgt --debug

# Check logs
cat ~/.config/driver-mgt/logs/driver-mgt.log

# Verify Ollama status
driver-mgt ai-status
```

### Ollama/AI Assistant Issues
```bash
# Reinstall Ollama and starcoder:3b
driver-mgt setup-ai

# Check Ollama is running
systemctl status ollama

# Manually test Ollama
ollama run starcoder:3b "test"

# View AI logs
cat ~/.config/driver-mgt/logs/ai-assistant.log
```

## 🤝 Contributing

Contributions are welcome! This project addresses overdue commitments made to Linux users regarding driver support and hardware control.

### Areas for Contribution
- Additional hardware support (more AMD GPUs, Intel GPUs, other motherboards)
- Driver compatibility improvements
- AI model fine-tuning for better error detection
- GUI enhancements
- Documentation
- Testing on various distributions
- User review and rating system
- Manufacturer repository integration

### Development with AI Features
When working with the AI-assisted features:
- Only starcoder:3b model is used for consistency
- Ollama runs on localhost for privacy
- AI logs are separate from main application logs
- Error reporting excludes attempted remediations
- All AI operations are auditable

## 📜 License

This project is licensed under the GPL-3.0 License - see LICENSE file for details.

## ⚖️ Legal & Ethics

driver-mgt uses only:
- Publicly available drivers released by manufacturers
- Open-source kernel modules
- Official APIs and interfaces
- No reverse engineering of proprietary drivers
- No EULA violations
- Local AI processing (no data sent to external services)
- Privacy-respecting hardware detection

All driver management is performed on officially released Linux drivers. AI assistance runs locally and does not transmit any data externally.

## 🙏 Acknowledgments

- NVIDIA for releasing open-source kernel modules
- AMD for open-source driver support
- Linux kernel developers
- lm-sensors project
- liquidctl project
- Ollama project and starcoder team
- The Linux community

## 📞 Support

- **Issues**: https://github.com/jameshroop-art/driver-mgt/issues
- **Discussions**: https://github.com/jameshroop-art/driver-mgt/discussions
- **Wiki**: https://github.com/jameshroop-art/driver-mgt/wiki

---

**Note**: This project addresses the gap between hardware capabilities and Linux driver implementations. We work exclusively with legally available drivers and public APIs.
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2026-01-08 03:51:59
Current User's Login: jameshroop-art
