"""
Hardware Detection Module
Detects and identifies hardware components
"""

import subprocess
import re
from typing import List, Dict, Any
from pathlib import Path
from utils.terminal import run_with_output

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
        
        # Detect CPUs
        hardware.extend(self._detect_cpus())
        
        # Detect GPUs
        hardware.extend(self._detect_gpus())
        
        # Detect WiFi adapters
        hardware.extend(self._detect_wifi())
        
        # Detect motherboard/chipset
        hardware.extend(self._detect_motherboard())
        
        # Detect RAM
        hardware.extend(self._detect_ram())
        
        # Detect cooling devices
        hardware.extend(self._detect_cooling())
        
        self.detected_hardware = hardware
        return hardware
    
    def _detect_gpus(self) -> List[Dict[str, Any]]:
        """Detect GPU hardware"""
        gpus = []
        
        try:
            # Use lspci to detect GPUs
            # Note: capture_output=True to parse results programmatically
            # Use verbose mode for CLI to show output
            show_output = self.config.get('cli.show_subprocess_output', False)
            result = run_with_output(
                ['lspci', '-v'],
                show_output=show_output,
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
            show_output = self.config.get('cli.show_subprocess_output', False)
            result = run_with_output(
                ['lspci', '-v'],
                show_output=show_output,
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
    
    def _detect_cpus(self) -> List[Dict[str, Any]]:
        """Detect CPU hardware"""
        cpus = []
        
        try:
            # Read CPU info from /proc/cpuinfo
            cpu_info = {}
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.strip():
                        key, _, value = line.partition(':')
                        key = key.strip()
                        value = value.strip()
                        if key == 'model name' and 'model name' not in cpu_info:
                            cpu_info['model name'] = value
                        elif key == 'vendor_id' and 'vendor_id' not in cpu_info:
                            cpu_info['vendor_id'] = value
                        elif key == 'cpu MHz' and 'cpu MHz' not in cpu_info:
                            cpu_info['cpu MHz'] = value
                        elif key == 'cache size' and 'cache size' not in cpu_info:
                            cpu_info['cache size'] = value
                        elif key == 'flags' and 'flags' not in cpu_info:
                            cpu_info['flags'] = value
            
            if cpu_info:
                model_name = cpu_info.get('model name', 'Unknown CPU')
                vendor = 'Unknown'
                
                # Detect vendor
                vendor_id = cpu_info.get('vendor_id', '').lower()
                if 'amd' in vendor_id or 'authenticamd' in vendor_id:
                    vendor = 'AMD'
                elif 'intel' in vendor_id or 'genuineintel' in vendor_id:
                    vendor = 'Intel'
                
                # Check for AMD X3D (3D V-Cache) models
                has_3d_vcache = False
                x3d_model = None
                if vendor == 'AMD':
                    # Check if it's an X3D model (e.g., 7800X3D, 5800X3D, 7950X3D)
                    x3d_match = re.search(r'(\d{4}X3D)', model_name, re.IGNORECASE)
                    if x3d_match:
                        has_3d_vcache = True
                        x3d_model = x3d_match.group(1)
                
                cpu_data = {
                    'type': 'CPU',
                    'name': model_name,
                    'vendor': vendor,
                    'driver': None,
                    'frequency': cpu_info.get('cpu MHz', 'Unknown'),
                    'cache_size': cpu_info.get('cache size', 'Unknown'),
                    'has_3d_vcache': has_3d_vcache
                }
                
                if x3d_model:
                    cpu_data['x3d_model'] = x3d_model
                
                cpus.append(cpu_data)
        
        except Exception as e:
            print(f"Error detecting CPU: {e}")
        
        return cpus
    
    def _detect_ram(self) -> List[Dict[str, Any]]:
        """Detect RAM hardware"""
        ram_info = []
        
        try:
            # Read memory info from /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        meminfo[key.strip()] = value.strip()
            
            # Get total memory in GB
            total_kb = int(meminfo.get('MemTotal', '0').split()[0])
            total_gb = total_kb / (1024 * 1024)
            
            # Try to get more detailed RAM info from dmidecode if available
            ram_details = self._get_ram_details()
            
            ram_data = {
                'type': 'RAM',
                'name': f"System Memory ({total_gb:.1f} GB)",
                'vendor': 'Unknown',
                'driver': None,
                'total_gb': round(total_gb, 1),
                'total_kb': total_kb
            }
            
            # Add detailed info if available
            if ram_details:
                ram_data.update(ram_details)
            
            ram_info.append(ram_data)
        
        except Exception as e:
            print(f"Error detecting RAM: {e}")
        
        return ram_info
    
    def _get_ram_details(self) -> Dict[str, Any]:
        """Get detailed RAM information using dmidecode"""
        details = {}
        
        try:
            # Try to run dmidecode to get RAM details
            show_output = self.config.get('cli.show_subprocess_output', False)
            result = run_with_output(
                ['dmidecode', '-t', 'memory'],
                show_output=show_output,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse RAM speed
                speed_match = re.search(r'Speed:\s*(\d+)\s*MT/s', output)
                if speed_match:
                    details['speed_mhz'] = int(speed_match.group(1))
                
                # Parse RAM type
                type_match = re.search(r'Type:\s*(DDR\d+)', output)
                if type_match:
                    details['ram_type'] = type_match.group(1)
                
                # Parse manufacturer
                mfr_match = re.search(r'Manufacturer:\s*(.+)', output)
                if mfr_match:
                    mfr = mfr_match.group(1).strip()
                    if mfr and mfr != 'NO DIMM':
                        details['manufacturer'] = mfr
        
        except Exception as e:
            # dmidecode may not be available or require root
            pass
        
        return details
    
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
