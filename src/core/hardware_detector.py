"""
Hardware Detection Module
Detects and identifies hardware components
"""

import subprocess
import re
from typing import List, Dict, Any
from pathlib import Path

class HardwareDetector:
    """Detects hardware components in the system"""
    
    # Vendor detection mapping
    VENDOR_PATTERNS = {
        'NVIDIA': ['NVIDIA', 'nvidia'],
        'AMD': ['AMD', 'ATI', 'Radeon'],
        'Intel': ['Intel'],
        'Realtek': ['Realtek', 'RTL'],
        'MediaTek': ['MediaTek', 'MT'],
        'Broadcom': ['Broadcom'],
    }
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.detected_hardware = []
    
    def detect_all(self) -> List[Dict[str, Any]]:
        """Detect all hardware components"""
        hardware = []
        
        # Detect GPUs
        hardware.extend(self._detect_gpus())
        
        # Detect WiFi adapters
        hardware.extend(self._detect_wifi())
        
        # Detect motherboard/chipset
        hardware.extend(self._detect_motherboard())
        
        # Detect cooling devices
        hardware.extend(self._detect_cooling())
        
        self.detected_hardware = hardware
        return hardware
    
    def _detect_gpus(self) -> List[Dict[str, Any]]:
        """Detect GPU hardware"""
        gpus = []
        
        try:
            # Use lspci to detect GPUs
            result = subprocess.run(
                ['lspci', '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'VGA compatible controller' in line or '3D controller' in line:
                        # Extract GPU info
                        gpu_info = self._parse_gpu_info(line, lines[i:i+10])
                        if gpu_info:
                            gpus.append(gpu_info)
        
        except Exception as e:
            print(f"Error detecting GPUs: {e}")
        
        return gpus
    
    def _parse_gpu_info(self, main_line: str, context_lines: List[str]) -> Dict[str, Any]:
        """Parse GPU information from lspci output"""
        info = {
            'type': 'GPU',
            'name': 'Unknown GPU',
            'vendor': 'Unknown',
            'driver': None,
            'id': None
        }
        
        # Detect vendor using patterns
        vendor = self._detect_vendor(main_line)
        if vendor:
            info['vendor'] = vendor
            
            # Extract model name based on vendor
            if vendor == 'NVIDIA':
                match = re.search(r'NVIDIA.*?(\[.*?\])', main_line)
                if match:
                    info['name'] = match.group(1).strip('[]')
                else:
                    info['name'] = 'NVIDIA GPU'
            
            elif vendor == 'AMD':
                match = re.search(r'(Radeon.*?)(\[|$)', main_line)
                if match:
                    info['name'] = match.group(1).strip()
                else:
                    info['name'] = 'AMD GPU'
            
            elif vendor == 'Intel':
                match = re.search(r'Intel.*?Graphics.*?(\[.*?\])', main_line)
                if match:
                    info['name'] = match.group(1).strip('[]')
                else:
                    info['name'] = 'Intel GPU'
        
        # Extract PCI ID
        match = re.search(r'^([0-9a-f:\.]+)', main_line)
        if match:
            info['id'] = match.group(1)
        
        # Look for driver in context
        for line in context_lines:
            if 'Kernel driver in use:' in line:
                driver_match = re.search(r'Kernel driver in use:\s+(\S+)', line)
                if driver_match:
                    info['driver'] = driver_match.group(1)
                    break
        
        return info
    
    def _detect_wifi(self) -> List[Dict[str, Any]]:
        """Detect WiFi adapters"""
        wifi_adapters = []
        
        try:
            result = subprocess.run(
                ['lspci', '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Network controller' in line or 'Wireless' in line:
                        wifi_info = self._parse_wifi_info(line, lines[i:i+10])
                        if wifi_info:
                            wifi_adapters.append(wifi_info)
        
        except Exception as e:
            print(f"Error detecting WiFi adapters: {e}")
        
        return wifi_adapters
    
    def _parse_wifi_info(self, main_line: str, context_lines: List[str]) -> Dict[str, Any]:
        """Parse WiFi adapter information"""
        info = {
            'type': 'WiFi',
            'name': 'Unknown WiFi Adapter',
            'vendor': 'Unknown',
            'driver': None,
            'id': None
        }
        
        # Detect vendor using patterns
        vendor = self._detect_vendor(main_line)
        if vendor:
            info['vendor'] = vendor
            
            # Set name based on vendor
            if vendor == 'Intel':
                match = re.search(r'Intel.*?(Wi-Fi.*?)(\[|$)', main_line)
                if match:
                    info['name'] = match.group(1).strip()
                else:
                    info['name'] = 'Intel WiFi Adapter'
            else:
                info['name'] = f'{vendor} WiFi Adapter'
        
        # Extract PCI ID
        match = re.search(r'^([0-9a-f:\.]+)', main_line)
        if match:
            info['id'] = match.group(1)
        
        # Look for driver
        for line in context_lines:
            if 'Kernel driver in use:' in line:
                driver_match = re.search(r'Kernel driver in use:\s+(\S+)', line)
                if driver_match:
                    info['driver'] = driver_match.group(1)
                    break
        
        return info
    
    def _detect_motherboard(self) -> List[Dict[str, Any]]:
        """Detect motherboard/chipset"""
        boards = []
        
        try:
            # Try to read DMI information
            dmi_path = Path('/sys/class/dmi/id')
            if dmi_path.exists():
                board_vendor = self._read_dmi_file(dmi_path / 'board_vendor')
                board_name = self._read_dmi_file(dmi_path / 'board_name')
                
                if board_vendor and board_name:
                    boards.append({
                        'type': 'Motherboard',
                        'name': f"{board_vendor} {board_name}",
                        'vendor': board_vendor,
                        'model': board_name,
                        'driver': None
                    })
        
        except Exception as e:
            print(f"Error detecting motherboard: {e}")
        
        return boards
    
    def _read_dmi_file(self, path: Path) -> str:
        """Read DMI file content"""
        try:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read().strip()
        except:
            pass
        return None
    
    def _detect_cooling(self) -> List[Dict[str, Any]]:
        """Detect cooling devices"""
        # This would require lm-sensors and liquidctl
        # For now, return empty list as these tools may not be installed
        return []
    
    def get_hardware_by_type(self, hw_type: str) -> List[Dict[str, Any]]:
        """Get hardware by type"""
        return [hw for hw in self.detected_hardware if hw['type'] == hw_type]
    
    def get_hardware_by_vendor(self, vendor: str) -> List[Dict[str, Any]]:
        """Get hardware by vendor"""
        return [hw for hw in self.detected_hardware if hw.get('vendor') == vendor]
    
    def _detect_vendor(self, text: str) -> str:
        """Detect vendor from text using pattern mapping"""
        for vendor, patterns in self.VENDOR_PATTERNS.items():
            if any(pattern in text for pattern in patterns):
                return vendor
        return 'Unknown'
