# GUI Architecture and Component Guide

## Window Structure

```
┌──────────────────────────────────────────────────────────────┐
│  driver-mgt - Advanced Linux Driver Management              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Dashboard │ System Info │ GPU │ WiFi │ CPU │ ...      │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │                    [TAB CONTENT]                        │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Status: Ready                                              │
└──────────────────────────────────────────────────────────────┘
```

## Dashboard Tab

```
┌─────────────────────────────────────────────────────────────┐
│ Driver Management Dashboard        [Scan Hardware]          │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Type │ Name          │ Vendor │ Driver    │ Status     │ │
│ ├──────┼───────────────┼────────┼───────────┼────────────┤ │
│ │ GPU  │ NVIDIA RTX... │ NVIDIA │ nvidia    │ Active     │ │
│ │ WiFi │ Intel AX200   │ Intel  │ iwlwifi   │ Active     │ │
│ │ CPU  │ AMD Ryzen...  │ AMD    │ None      │ No Driver  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Update Driver] [Rollback Driver] [Test Driver]             │
└─────────────────────────────────────────────────────────────┘
```

## Device Tab (Example: GPU Tab)

```
┌─────────────────────────────────────────────────────────────┐
│ Device Information                                           │
├─────────────────────────────────────────────────────────────┤
│ Type:      GPU                                              │
│ Name:      NVIDIA RTX 3080                                  │
│ Vendor:    NVIDIA                                           │
│ Device ID: 00:08.0                                          │
│ Model:     RTX 3080                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Current Driver                                               │
├─────────────────────────────────────────────────────────────┤
│ Driver: nvidia-driver-535                                   │
│ Status: Active ●                                            │
│                                                              │
│ [Test Driver] [Rollback Driver]                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Risk Assessment                                              │
├─────────────────────────────────────────────────────────────┤
│ Risk Level: Low (12%)                                       │
│ ████████████░░░░░░░░░░░░░░░░░░░░  12%                      │
│ AI Remediation: Yes (Can prevent all known errors)         │
│                                                              │
│ [Refresh Risk Assessment]                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Available Drivers          Filter: [All ▼]                  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │Driver    │Ver  │Source │Stab  │Risk │Actions           │ │
│ ├──────────┼─────┼───────┼──────┼─────┼──────────────────┤ │
│ │nvidia-535│535xx│Official│Stable│5%  │[Install with AI]│ │
│ │nvidia-545│545xx│Official│Beta  │20% │[Install with AI]│ │
│ │nouveau   │latest│Community│Stable│10%│[Install with AI]│ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ AI-Assisted Features                                         │
├─────────────────────────────────────────────────────────────┤
│ AI Status: Online (starcoder:3b) ●                         │
│                                                              │
│ Available AI Features:                                      │
│   ✓ Pre-installation risk assessment                       │
│   ✓ Real-time installation monitoring                      │
│   ✓ Automatic error detection and correction               │
│   ✓ Post-installation verification                         │
│   ✓ Proactive failure prevention                           │
│                                                              │
│ [AI Analyze Current Setup] [Enable AI Monitoring]          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Fallback Plan                                                │
├─────────────────────────────────────────────────────────────┤
│ Automatic fallback procedures if driver installation fails: │
│                                                              │
│ 1. Automatic detection of driver failure on boot           │
│ 2. Revert to previous working driver automatically         │
│ 3. AI analysis of error logs and failure mode              │
│ 4. Attempt automatic correction if possible                │
│ 5. Search for alternative compatible drivers               │
│ 6. Generate detailed error report for manufacturer         │
│ 7. Suggest manual recovery steps if needed                 │
│                                                              │
│ Previous Driver Backup: Available                           │
│ Recovery Mode: Enabled                                      │
│ Estimated Recovery Time: 2-5 minutes                        │
└─────────────────────────────────────────────────────────────┘
```

## Installation Progress Dialog

```
┌───────────────────────────────────┐
│  Driver Installation              │
├───────────────────────────────────┤
│                                   │
│  Installing nvidia-driver-545...  │
│                                   │
│  ████████████████░░░░░░░░░  60%  │
│                                   │
│  Current step: Testing driver...  │
│                                   │
│            [Cancel]               │
└───────────────────────────────────┘
```

## Color Scheme (Dark Theme)

### Backgrounds
- Main Window: `#2b2b2b`
- Widgets: `#3b3b3b`
- Selected Tab: `#4b4b4b`
- Buttons: `#4b4b4b`

### Text
- Primary Text: `#ffffff` (white)
- Secondary Text: `#cccccc` (light gray)

### Status Colors
- Success/Active: `#50c878` (green)
- Warning: `#ffa500` (orange)
- Error/Inactive: `#ff6b6b` (red)
- Info: `#4b9bff` (blue)

### Risk Level Colors
- Very Low (0-10%): Green background `#326432`
- Low (10-30%): Light green background `#646432`
- Medium (30-50%): Orange background `#646432`
- High (50%+): Red background `#643232`

## Component Interaction Flow

```
User Action          →  Component          →  Backend
─────────────────────────────────────────────────────────
Scan Hardware       →  MainWindow         →  HardwareDetector
                    ↓
                    Creates DeviceTabs
                    ↓
Double-click Device →  Switch to DeviceTab

Click Install       →  DeviceTab          →  DriverInstallWorker
                    ↓                      ↓
                    Progress Dialog    →  DriverManager
                    ↓                      ↓
                    Updates UI         ←  OllamaManager (AI)

Test Driver         →  DeviceTab          →  DriverManager
                    ↓
                    Shows Results

Rollback            →  DeviceTab          →  DriverManager
                    ↓
                    Confirms & Updates

AI Analyze          →  DeviceTab          →  OllamaManager
                    ↓
                    Shows Analysis

Enable Monitoring   →  DeviceTab          →  OllamaManager
                    ↓
                    Updates Status
```

## Thread Safety

### Main Thread
- UI updates
- User interactions
- Widget creation

### Worker Threads
- Driver installation (`DriverInstallWorker`)
- Hardware scanning (optional)
- AI analysis (optional)

### Signals/Slots
```python
# Worker Thread Signals
progress(int, str)   # Update progress: (percentage, message)
finished(bool, str)  # Installation complete: (success, message)

# Connected to Main Thread
update_install_progress(value, message)  # Update dialog
install_finished(success, message)       # Show result
```

## Data Flow

```
Configuration (config.json)
        ↓
ConfigManager
        ↓
    ┌───┴───┐
    ↓       ↓
MainWindow  Managers
    ↓           ↓
DeviceTabs      ↓
    ↓           ↓
Hardware ← HardwareDetector
    ↓
Drivers  ← DriverManager ← OllamaManager (AI)
```

## Error Handling

### Levels
1. **User-Facing**: QMessageBox dialogs
2. **Logging**: Written to `~/.config/driver-mgt/logs/`
3. **Status Bar**: Brief status messages
4. **Console**: Debug output (when `--debug` flag)

### Example
```python
try:
    # Operation
    driver_manager.install_driver(driver, hardware)
except Exception as e:
    # Log error
    logger.error(f"Installation failed: {e}")
    # Show user
    QMessageBox.critical(self, "Error", f"Installation failed: {e}")
    # Update status
    self.statusBar.showMessage("Installation failed")
```

## Performance Considerations

### Lazy Loading
- Device tabs created only when hardware is scanned
- Driver lists loaded on-demand
- AI analysis triggered by user action

### Caching
- Hardware detection results cached
- Driver list cached until refresh
- AI status checked periodically, not continuously

### Resource Management
- Worker threads properly terminated
- Connections cleaned up when tabs removed
- Progress dialogs deleted after use

## Accessibility

### Features
- Keyboard navigation support
- Tab order configured logically
- Status indicators use color + text
- Tooltips on important buttons
- Clear error messages

### Future Enhancements
- Screen reader support
- High contrast themes
- Font size adjustment
- Keyboard shortcuts documented
