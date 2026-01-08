# Motherboard Detection & Linux Compatibility

## Overview

The driver-mgt application now includes comprehensive motherboard detection that provides:
- **Motherboard Make and Model** identification
- **BIOS Version** and date information
- **Chipset** detection
- **Linux Compatibility** verification with manufacturer support links

## Features

### Automatic Detection

When you run driver-mgt, it automatically detects:

1. **Motherboard Information:**
   - Manufacturer/Vendor (e.g., ASUS, MSI, Gigabyte, ASRock)
   - Model name
   - Board version

2. **BIOS Details:**
   - BIOS vendor
   - BIOS version (firmware version currently installed)
   - BIOS date (when the BIOS was released)

3. **Chipset Information:**
   - Chipset model (e.g., X570, B550, Z690)
   - Chipset vendor (Intel, AMD)

4. **Linux Compatibility:**
   - Support level (Good, Moderate, Unknown)
   - Direct links to manufacturer support pages
   - Direct links to driver download pages
   - Notes about Linux compatibility

## Supported Manufacturers

The application has built-in Linux compatibility information for:

### ✅ ASUS
- **Support Level:** Good
- **Notes:** ASUS provides Linux drivers for most motherboards
- **Links:** Support site and download center included

### ✅ MSI
- **Support Level:** Good  
- **Notes:** MSI motherboards generally work well with Linux. Some RGB/fan control may need third-party tools
- **Links:** Support and download pages included

### ✅ Gigabyte
- **Support Level:** Good
- **Notes:** Gigabyte motherboards have good Linux compatibility. Check for chipset driver support
- **Links:** Support and motherboard-specific download pages included

### ✅ ASRock
- **Support Level:** Good
- **Notes:** ASRock motherboards work well with Linux. Most features supported out-of-box
- **Links:** Support and download pages included

### ⚠️ EVGA
- **Support Level:** Moderate
- **Notes:** EVGA motherboards generally compatible. Some utilities Windows-only
- **Links:** Support and download pages included

### ⚠️ Biostar
- **Support Level:** Moderate
- **Notes:** Basic Linux support. Most hardware works but limited manufacturer utilities
- **Links:** Support and download pages included

## How to Use

### GUI Mode

1. **Launch driver-mgt:**
   ```bash
   ./driver-mgt
   ```

2. **Navigate to Motherboard Tab:**
   - After scanning, a "Motherboard" tab will appear if detected
   - Click on it to view detailed information

3. **View Details:**
   - Device Information section shows:
     - Type, Name, Vendor, Model
     - BIOS Version, BIOS Date
     - Chipset information
     - Linux Support level
   
4. **Access Manufacturer Support:**
   - Click "Manufacturer Support" button to visit the manufacturer's website
   - Click "Download Drivers" button to access driver download page

### CLI Mode

Check motherboard info with the status command:

```bash
./driver-mgt status
```

This will show detected hardware including motherboard details.

## Example Output

```
Motherboard Found:
  Vendor: ASUS
  Model: ROG STRIX X570-E GAMING
  Board Version: Rev 1.xx

BIOS Information:
  BIOS Vendor: American Megatrends Inc.
  BIOS Version: 4602
  BIOS Date: 11/18/2023

Chipset Information:
  Chipset: X570
  Chipset Vendor: AMD

Linux Compatibility:
  Status: supported
  Support Level: Good
  Manufacturer: ASUS
  Support URL: https://www.asus.com/support/
  Drivers URL: https://www.asus.com/support/download-center/
  Notes: ASUS provides Linux drivers for most motherboards. Check support site for specific model.
```

## Technical Details

### Detection Methods

1. **DMI/SMBIOS Information:**
   - Read from `/sys/class/dmi/id/`
   - Includes board_vendor, board_name, bios_version, bios_date

2. **Chipset Detection:**
   - Uses `lspci` to identify host bridge/chipset
   - Parses vendor and model information

3. **Compatibility Database:**
   - Built-in database of known manufacturer support
   - Provides direct links to support resources

### Files Modified

- `src/core/hardware_detector.py`:
  - Enhanced `_detect_motherboard()` with BIOS and chipset detection
  - Added `_detect_chipset()` for chipset identification
  - Added `_check_linux_compatibility()` for manufacturer support info

- `src/gui/device_tab.py`:
  - Enhanced device info display for motherboards
  - Added compatibility widget with manufacturer links
  - Added buttons to open manufacturer support pages

## Verifying BIOS Updates

### Why Check BIOS Version?

- **Stability:** Newer BIOS versions often fix bugs and improve stability
- **Hardware Support:** Updates may enable better Linux compatibility
- **Performance:** BIOS updates can improve memory and CPU performance
- **Security:** Updates patch security vulnerabilities

### How to Check for Updates

1. **Note Your Current BIOS:**
   - Check the BIOS Version shown in driver-mgt
   - Example: "4602" dated "11/18/2023"

2. **Visit Manufacturer Website:**
   - Click "Manufacturer Support" in the motherboard tab
   - Or manually visit the manufacturer's website

3. **Find Your Model:**
   - Search for your exact motherboard model
   - Navigate to Support → Downloads → BIOS

4. **Compare Versions:**
   - Check if newer BIOS versions are available
   - Read the changelog for Linux-relevant improvements

5. **Download and Install:**
   - Follow manufacturer's instructions for BIOS updates
   - **IMPORTANT:** Always follow proper BIOS update procedures
   - Never interrupt a BIOS update

## Linux-Specific Considerations

### What to Check

1. **Chipset Drivers:**
   - Most AMD/Intel chipset drivers are in the Linux kernel
   - Check manufacturer site for additional Linux drivers

2. **Audio Drivers:**
   - Most Realtek audio works with `snd_hda_intel` kernel module
   - Some high-end boards may need additional configuration

3. **Network Drivers:**
   - Intel NICs: Usually excellent support
   - Realtek NICs: Good support, occasionally need firmware
   - 2.5G/10G NICs: Check kernel support

4. **RGB/Fan Control:**
   - May require third-party tools like:
     - OpenRGB (RGB lighting)
     - liquidctl (AIO coolers)
     - fancontrol/lm-sensors (fan control)

### Common Issues

**Issue:** RGB lighting doesn't work
- **Solution:** Install OpenRGB or manufacturer-specific tools

**Issue:** Some USB ports not working
- **Solution:** Update BIOS, check kernel version, enable XHCI in BIOS

**Issue:** Network adapter not detected
- **Solution:** Check for kernel modules, may need firmware package

## Resources

- **Arch Wiki Hardware:** https://wiki.archlinux.org/title/Category:Motherboards
- **Linux Hardware Database:** https://linux-hardware.org/
- **Ubuntu Hardware Certification:** https://ubuntu.com/certified

## Troubleshooting

### No Motherboard Detected

If no motherboard is detected:
1. Ensure you're not in a VM or container
2. Check `/sys/class/dmi/id/` exists and has board_vendor file
3. Run with elevated permissions if needed

### Incorrect Information

If information seems wrong:
1. Check DMI files: `cat /sys/class/dmi/id/board_name`
2. Verify with: `sudo dmidecode -t baseboard`
3. May indicate generic/OEM board with limited DMI data

### Missing Compatibility Info

If "Unknown" manufacturer:
1. This is normal for custom/OEM builds
2. Check chipset vendor for driver support
3. Most Linux support is chipset-based, not board-specific
