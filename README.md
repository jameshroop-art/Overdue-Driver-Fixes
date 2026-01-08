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
- 🎮 **NVIDIA RTX Driver Control**
  - Automatic driver detection and switching
  - CUDA toolkit management
  - Performance profile optimization
  - Power management controls

- 📡 **ASUS WiFi & Chipset Drivers**
  - MediaTek, Realtek, Intel driver support
  - Firmware management
  - Feature enablement (WiFi 6E, proper speeds)
  - Stability improvements

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
- 📊 **Tabbed Interface**
  - Driver Management
  - NVIDIA Control Center
  - WiFi Control
  - Cooling Control
  - Performance Monitor
  - System Information

- 📈 **Real-time Graphs**
  - Temperature tracking
  - Fan speed visualization
  - Performance metrics
  - Power consumption

- ⚡ **Manual & Auto Modes**
  - Full manual control for enthusiasts
  - Intelligent auto mode for stability
  - Quick profile switching

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
- Set up system services
- Create desktop shortcut
- Configure permissions
- Initialize hardware detection

## 📋 Requirements

### System Requirements
- Linux kernel 5.10 or newer
- Python 3.9+
- Root/sudo access for hardware control
- X11 or Wayland display server

### Supported Hardware
- **GPUs**: NVIDIA RTX 20, 30, 40 series
- **Motherboards**: ASUS (ROG, TUF, Prime series)
- **WiFi**: MediaTek, Realtek, Intel adapters
- **Cooling**: Most AIO liquid coolers, PWM fans

### Dependencies
- PyQt6 (GUI framework)
- nvidia-smi (NVIDIA control)
- lm-sensors (temperature monitoring)
- liquidctl (AIO control)
- i2c-tools (hardware communication)

## 🎨 GUI Overview

### Main Window Tabs

1. **Driver Management**
   - View installed drivers
   - Install/update drivers
   - Switch between driver versions
   - Manage kernel modules

2. **NVIDIA Control**
   - GPU information
   - Clock speeds and voltages
   - Power limits
   - Fan curves
   - CUDA settings

3. **WiFi Control**
   - Connection management
   - Driver optimization
   - Feature toggles
   - Signal monitoring

4. **Cooling Control**
   - Temperature graphs (CPU/GPU)
   - Fan curve editor (10-point)
   - Pump speed control
   - RPM monitoring
   - Auto/Manual mode toggle

5. **Performance Monitor**
   - Real-time system metrics
   - Resource usage
   - Workload detection
   - Historical data

6. **System Info**
   - Hardware detection results
   - Driver versions
   - Firmware information
   - System configuration

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

## 🔧 Advanced Usage

### Running as System Service

driver-mgt can run as a background service for automatic hardware management:

```bash
sudo systemctl enable driver-mgt
sudo systemctl start driver-mgt
```

### Command Line Interface

```bash
# Check system status
driver-mgt status

# Apply cooling profile
driver-mgt cooling --profile silent

# Update drivers
driver-mgt driver --update nvidia

# Monitor temperatures
driver-mgt monitor --temp
```

## 🐛 Troubleshooting

### NVIDIA Driver Issues
```bash
# Check driver status
nvidia-smi

# Reload driver-mgt NVIDIA module
sudo driver-mgt driver --reload nvidia
```

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
```

## 🤝 Contributing

Contributions are welcome! This project addresses overdue commitments made to Linux users regarding driver support and hardware control.

### Areas for Contribution
- Additional hardware support (AMD GPUs, other motherboards)
- Driver compatibility improvements
- GUI enhancements
- Documentation
- Testing on various distributions

## 📜 License

This project is licensed under the GPL-3.0 License - see LICENSE file for details.

## ⚖️ Legal & Ethics

driver-mgt uses only:
- Publicly available drivers released by manufacturers
- Open-source kernel modules
- Official APIs and interfaces
- No reverse engineering of proprietary drivers
- No EULA violations

All driver management is performed on officially released Linux drivers.

## 🙏 Acknowledgments

- NVIDIA for releasing open-source kernel modules
- Linux kernel developers
- lm-sensors project
- liquidctl project
- The Linux community

## 📞 Support

- **Issues**: https://github.com/jameshroop-art/driver-mgt/issues
- **Discussions**: https://github.com/jameshroop-art/driver-mgt/discussions
- **Wiki**: https://github.com/jameshroop-art/driver-mgt/wiki

---

**Note**: This project addresses the gap between hardware capabilities and Linux driver implementations. We work exclusively with legally available drivers and public APIs.
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2026-01-08 03:51:59
Current User's Login: jameshroop-art
