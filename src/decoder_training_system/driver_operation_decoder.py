"""
Driver Operation Decoder and Translator
Decodes hardware information and translates it to driver operations
"""

import re
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path


class DriverOperationDecoder:
    """Decodes and translates hardware information to driver operations"""
    
    # PCI device class codes to driver operation types
    PCI_CLASS_OPERATIONS = {
        '0300': {  # VGA compatible controller
            'type': 'GPU',
            'operations': ['memory_allocation', 'rendering', 'display_output', 'compute'],
            'common_drivers': ['nvidia', 'nouveau', 'amdgpu', 'radeon', 'i915', 'intel']
        },
        '0200': {  # Ethernet controller
            'type': 'Network',
            'operations': ['packet_tx', 'packet_rx', 'link_state', 'dma_transfer'],
            'common_drivers': ['e1000', 'igb', 'r8169', 'tg3', 'bnx2']
        },
        '0280': {  # Network controller (WiFi)
            'type': 'WiFi',
            'operations': ['scan', 'connect', 'authenticate', 'packet_tx', 'packet_rx'],
            'common_drivers': ['iwlwifi', 'ath10k', 'rtw88', 'mt76', 'brcmfmac']
        },
        '0403': {  # Audio device
            'type': 'Audio',
            'operations': ['playback', 'capture', 'mixer', 'dsp'],
            'common_drivers': ['snd_hda_intel', 'snd_usb_audio', 'snd_soc']
        },
        '0c03': {  # USB controller
            'type': 'USB',
            'operations': ['device_enumerate', 'transfer', 'power_management'],
            'common_drivers': ['xhci_hcd', 'ehci_hcd', 'ohci_hcd', 'uhci_hcd']
        },
        '0106': {  # SATA controller
            'type': 'Storage',
            'operations': ['read', 'write', 'command_queue', 'power_management'],
            'common_drivers': ['ahci', 'ata_piix', 'sata_nv']
        },
    }
    
    # Vendor ID to manufacturer mapping
    VENDOR_MAPPING = {
        '10de': 'NVIDIA',
        '1002': 'AMD',
        '8086': 'Intel',
        '14e4': 'Broadcom',
        '168c': 'Atheros',
        '10ec': 'Realtek',
        '1022': 'AMD',
        '1b21': 'ASMedia',
        '197b': 'JMicron',
    }
    
    def __init__(self):
        """Initialize the decoder"""
        self.device_cache = {}
        
    def decode_pci_device(self, pci_address: str) -> Dict[str, Any]:
        """Decode PCI device information and translate to operations
        
        Args:
            pci_address: PCI address like '0000:01:00.0'
            
        Returns:
            Dict with device info and supported operations
        """
        result = {
            'address': pci_address,
            'vendor': 'Unknown',
            'vendor_id': None,
            'device': 'Unknown',
            'device_id': None,
            'class': 'Unknown',
            'class_code': None,
            'subsystem': 'Unknown',
            'driver': None,
            'operations': [],
            'recommended_drivers': [],
            'capabilities': []
        }
        
        try:
            # Get device details using lspci
            cmd = ['lspci', '-v', '-n', '-s', pci_address]
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            
            # Parse vendor and device IDs
            for line in output.split('\n'):
                if pci_address in line:
                    # Format: "0000:01:00.0 0300: 10de:1c03 (rev a1)"
                    match = re.search(r'([0-9a-f]{4}): ([0-9a-f]{4}):([0-9a-f]{4})', line)
                    if match:
                        result['class_code'] = match.group(1)
                        result['vendor_id'] = match.group(2)
                        result['device_id'] = match.group(3)
                        
                        # Translate vendor ID
                        result['vendor'] = self.VENDOR_MAPPING.get(
                            result['vendor_id'], 
                            f"Unknown ({result['vendor_id']})"
                        )
                        
                elif 'Kernel driver in use:' in line:
                    result['driver'] = line.split(':')[1].strip()
                    
                elif 'Subsystem:' in line:
                    result['subsystem'] = line.split(':', 1)[1].strip()
                    
                elif 'Capabilities:' in line:
                    cap = line.split(':', 1)[1].strip()
                    result['capabilities'].append(cap)
            
            # Get human-readable device info
            cmd_readable = ['lspci', '-v', '-s', pci_address]
            output_readable = subprocess.check_output(cmd_readable, text=True, stderr=subprocess.DEVNULL)
            
            for line in output_readable.split('\n'):
                if pci_address in line:
                    # Extract device description
                    parts = line.split(': ', 1)
                    if len(parts) > 1:
                        result['device'] = parts[1].strip()
                        result['class'] = parts[1].split(' ', 1)[0] if ' ' in parts[1] else 'Unknown'
            
            # Translate class code to operations
            if result['class_code']:
                class_info = self.PCI_CLASS_OPERATIONS.get(result['class_code'])
                if class_info:
                    result['operations'] = class_info['operations']
                    result['recommended_drivers'] = class_info['common_drivers']
                    result['device_type'] = class_info['type']
            
        except subprocess.CalledProcessError as e:
            result['error'] = f"Failed to query device: {e}"
        except Exception as e:
            result['error'] = f"Decode error: {e}"
        
        return result
    
    def decode_usb_device(self, bus: str, device: str) -> Dict[str, Any]:
        """Decode USB device information
        
        Args:
            bus: USB bus number
            device: USB device number
            
        Returns:
            Dict with device info and operations
        """
        result = {
            'bus': bus,
            'device': device,
            'vendor': 'Unknown',
            'vendor_id': None,
            'product': 'Unknown',
            'product_id': None,
            'class': 'Unknown',
            'driver': None,
            'operations': ['enumerate', 'transfer', 'power_management'],
            'interface_class': []
        }
        
        try:
            # Use lsusb to get device info
            cmd = ['lsusb', '-s', f'{bus}:{device}', '-v']
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            
            for line in output.split('\n'):
                if 'idVendor' in line:
                    match = re.search(r'0x([0-9a-f]{4})', line)
                    if match:
                        result['vendor_id'] = match.group(1)
                        # Extract vendor name
                        if len(line.split()) > 2:
                            result['vendor'] = ' '.join(line.split()[2:])
                            
                elif 'idProduct' in line:
                    match = re.search(r'0x([0-9a-f]{4})', line)
                    if match:
                        result['product_id'] = match.group(1)
                        # Extract product name
                        if len(line.split()) > 2:
                            result['product'] = ' '.join(line.split()[2:])
                            
                elif 'bInterfaceClass' in line:
                    interface_class = line.split()[1]
                    result['interface_class'].append(interface_class)
                    
        except subprocess.CalledProcessError:
            result['error'] = "Failed to query USB device"
        except Exception as e:
            result['error'] = f"Decode error: {e}"
        
        return result
    
    def translate_device_id_to_operations(self, vendor_id: str, device_id: str) -> List[str]:
        """Translate vendor:device ID pair to driver operations
        
        Args:
            vendor_id: PCI vendor ID (4 hex digits)
            device_id: PCI device ID (4 hex digits)
            
        Returns:
            List of supported operations
        """
        operations = []
        
        # NVIDIA devices
        if vendor_id == '10de':
            operations = [
                'gpu_memory_alloc',
                'gpu_memory_free',
                'gpu_compute_execute',
                'gpu_render_frame',
                'display_mode_set',
                'gpu_clock_control',
                'gpu_power_management',
                'gpu_temperature_monitor'
            ]
        # AMD devices
        elif vendor_id == '1002':
            operations = [
                'gpu_memory_alloc',
                'gpu_compute_execute',
                'display_output',
                'gpu_power_state',
                'gpu_performance_level',
                'gpu_fan_control'
            ]
        # Intel devices
        elif vendor_id == '8086':
            # Check if it's GPU or network
            if device_id.startswith(('0x19', '0x3e', '0x5a', '0x59')):
                # Intel GPU
                operations = [
                    'gpu_render',
                    'display_output',
                    'video_decode',
                    'video_encode',
                    'gpu_power_management'
                ]
            else:
                # Likely network or other
                operations = [
                    'device_init',
                    'data_transfer',
                    'interrupt_handling',
                    'power_management'
                ]
        # Realtek network devices
        elif vendor_id == '10ec':
            operations = [
                'network_init',
                'packet_transmit',
                'packet_receive',
                'link_state_change',
                'interrupt_handling'
            ]
        # Generic operations
        else:
            operations = [
                'device_probe',
                'device_init',
                'device_read',
                'device_write',
                'device_ioctl',
                'device_remove'
            ]
        
        return operations
    
    def decode_driver_binary(self, driver_path: str) -> Dict[str, Any]:
        """Decode driver binary metadata
        
        Args:
            driver_path: Path to driver file (.ko for kernel module)
            
        Returns:
            Dict with driver metadata and operations
        """
        result = {
            'path': driver_path,
            'name': Path(driver_path).stem,
            'type': 'unknown',
            'operations': [],
            'dependencies': [],
            'parameters': [],
            'supported_devices': [],
            'metadata': {}
        }
        
        if not Path(driver_path).exists():
            result['error'] = "Driver file not found"
            return result
        
        try:
            # Check if it's a kernel module
            if driver_path.endswith('.ko'):
                result['type'] = 'kernel_module'
                
                # Use modinfo to get module information
                cmd = ['modinfo', driver_path]
                output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
                
                for line in output.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'depends':
                            result['dependencies'] = [d.strip() for d in value.split(',') if d.strip()]
                        elif key == 'alias':
                            result['supported_devices'].append(value)
                        elif key == 'parm':
                            result['parameters'].append(value)
                        else:
                            result['metadata'][key] = value
                
                # Infer operations from module name
                module_name = result['name'].lower()
                if 'net' in module_name or 'wifi' in module_name or 'eth' in module_name:
                    result['operations'] = ['network_init', 'packet_tx', 'packet_rx', 'link_state']
                elif 'gpu' in module_name or 'drm' in module_name or 'video' in module_name:
                    result['operations'] = ['gpu_init', 'render', 'display', 'memory_alloc']
                elif 'usb' in module_name:
                    result['operations'] = ['usb_probe', 'usb_transfer', 'usb_disconnect']
                elif 'snd' in module_name or 'audio' in module_name:
                    result['operations'] = ['audio_open', 'audio_playback', 'audio_capture']
                else:
                    result['operations'] = ['driver_init', 'driver_ops', 'driver_exit']
                    
        except subprocess.CalledProcessError:
            result['error'] = "Failed to read driver information"
        except Exception as e:
            result['error'] = f"Decode error: {e}"
        
        return result
    
    def translate_hardware_to_driver_commands(self, hardware: Dict[str, Any]) -> List[Dict[str, str]]:
        """Translate hardware information to driver command operations
        
        Args:
            hardware: Hardware dictionary with type, vendor, id, etc.
            
        Returns:
            List of driver command dictionaries
        """
        commands = []
        hw_type = hardware.get('type', '').lower()
        driver = hardware.get('driver', '')
        
        if hw_type == 'gpu':
            commands = [
                {'operation': 'check_status', 'command': f'cat /sys/class/drm/card*/status'},
                {'operation': 'get_memory', 'command': f'nvidia-smi --query-gpu=memory.used --format=csv' if 'nvidia' in driver else 'cat /sys/class/drm/card*/mem_info_vram_used'},
                {'operation': 'get_temperature', 'command': f'nvidia-smi --query-gpu=temperature.gpu --format=csv' if 'nvidia' in driver else 'cat /sys/class/drm/card*/hwmon/hwmon*/temp1_input'},
                {'operation': 'set_power_profile', 'command': f'nvidia-smi -pm 1' if 'nvidia' in driver else 'echo auto > /sys/class/drm/card*/power_profile'},
                {'operation': 'list_processes', 'command': f'nvidia-smi pmon' if 'nvidia' in driver else 'lsof | grep /dev/dri'},
            ]
        elif hw_type == 'network' or hw_type == 'wifi':
            iface = hardware.get('interface', 'eth0')
            commands = [
                {'operation': 'check_link', 'command': f'ethtool {iface} | grep Link'},
                {'operation': 'get_stats', 'command': f'ethtool -S {iface}'},
                {'operation': 'get_driver_info', 'command': f'ethtool -i {iface}'},
                {'operation': 'show_interface', 'command': f'ip addr show {iface}'},
                {'operation': 'get_rx_tx', 'command': f'cat /sys/class/net/{iface}/statistics/{{rx,tx}}_bytes'},
            ]
        elif hw_type == 'storage':
            device = hardware.get('device', 'sda')
            commands = [
                {'operation': 'check_smart', 'command': f'smartctl -H /dev/{device}'},
                {'operation': 'get_info', 'command': f'smartctl -i /dev/{device}'},
                {'operation': 'list_partitions', 'command': f'lsblk /dev/{device}'},
                {'operation': 'check_io_stats', 'command': f'iostat -x /dev/{device}'},
            ]
        elif hw_type == 'audio':
            commands = [
                {'operation': 'list_cards', 'command': 'cat /proc/asound/cards'},
                {'operation': 'check_devices', 'command': 'aplay -l'},
                {'operation': 'get_volume', 'command': 'amixer get Master'},
                {'operation': 'list_controls', 'command': 'amixer controls'},
            ]
        else:
            # Generic device commands
            device_name = hardware.get('name', 'device')
            commands = [
                {'operation': 'check_loaded', 'command': f'lsmod | grep {driver}' if driver else 'lsmod'},
                {'operation': 'get_info', 'command': f'modinfo {driver}' if driver else 'uname -r'},
                {'operation': 'check_dmesg', 'command': f'dmesg | grep -i {device_name.split()[0]}'},
            ]
        
        return commands
    
    def scan_all_devices(self) -> List[Dict[str, Any]]:
        """Scan all PCI devices and decode them
        
        Returns:
            List of decoded device dictionaries
        """
        devices = []
        
        try:
            # Get all PCI devices
            cmd = ['lspci', '-D']
            output = subprocess.check_output(cmd, text=True)
            
            for line in output.split('\n'):
                if line.strip():
                    # Extract PCI address (first field)
                    pci_address = line.split()[0]
                    device_info = self.decode_pci_device(pci_address)
                    devices.append(device_info)
                    
        except subprocess.CalledProcessError as e:
            print(f"Failed to scan devices: {e}")
        except Exception as e:
            print(f"Scan error: {e}")
        
        return devices
    
    def get_operation_details(self, operation: str) -> Dict[str, Any]:
        """Get detailed information about a driver operation
        
        Args:
            operation: Operation name (e.g., 'gpu_memory_alloc')
            
        Returns:
            Dict with operation details
        """
        operation_db = {
            'gpu_memory_alloc': {
                'description': 'Allocate GPU memory for compute or graphics',
                'syscalls': ['ioctl'],
                'kernel_functions': ['drm_gem_object_init', 'ttm_bo_init'],
                'risk_level': 'medium',
                'required_permissions': ['DRM_MASTER']
            },
            'packet_transmit': {
                'description': 'Transmit network packet',
                'syscalls': ['sendto', 'write'],
                'kernel_functions': ['dev_queue_xmit', 'netdev_start_xmit'],
                'risk_level': 'low',
                'required_permissions': ['CAP_NET_RAW']
            },
            'driver_init': {
                'description': 'Initialize device driver',
                'syscalls': ['init_module'],
                'kernel_functions': ['module_init', 'pci_register_driver'],
                'risk_level': 'high',
                'required_permissions': ['CAP_SYS_MODULE']
            },
            'device_ioctl': {
                'description': 'Device I/O control operation',
                'syscalls': ['ioctl'],
                'kernel_functions': ['unlocked_ioctl', 'compat_ioctl'],
                'risk_level': 'medium',
                'required_permissions': ['device_specific']
            }
        }
        
        return operation_db.get(
            operation, 
            {
                'description': f'Generic operation: {operation}',
                'syscalls': ['unknown'],
                'kernel_functions': ['unknown'],
                'risk_level': 'unknown',
                'required_permissions': ['unknown']
            }
        )
