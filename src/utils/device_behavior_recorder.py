"""
Device Behavior Recorder
Records actual device behaviors, kernel interactions, and hardware processes
for accurate AI simulation
"""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import glob


class DeviceBehaviorRecorder:
    """Records real device and kernel behavior for AI simulation"""
    
    def __init__(self):
        """Initialize device behavior recorder"""
        self.behaviors = {}
        self.kernel_version = self._get_kernel_version()
        self.system_info = self._get_system_info()
        
    def _get_kernel_version(self) -> str:
        """Get current kernel version"""
        try:
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {
            'kernel_version': self.kernel_version,
            'recorded_at': datetime.now().isoformat(),
            'architecture': self._run_command(['uname', '-m']),
            'distribution': self._get_distribution()
        }
        return info
    
    def _get_distribution(self) -> str:
        """Get Linux distribution information"""
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            return line.split('=')[1].strip().strip('"')
        except Exception:
            pass
        return "Unknown Linux"
    
    def _run_command(self, cmd: List[str], timeout: int = 5) -> str:
        """Safely run a command and return output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip()
        except Exception:
            return ""
    
    def record_device_behavior(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Record current behavior of detected device
        
        Args:
            hardware: Hardware information
            
        Returns:
            Recorded device behavior profile
        """
        hw_type = hardware.get('type', '').lower()
        hw_name = hardware.get('name', 'Unknown')
        
        behavior = {
            'hardware': hardware,
            'kernel_version': self.kernel_version,
            'recorded_at': datetime.now().isoformat(),
            'kernel_interactions': {},
            'current_driver': None,
            'device_capabilities': [],
            'io_operations': {},
            'power_states': [],
            'error_states': [],
            'performance_metrics': {}
        }
        
        # Record type-specific behaviors
        if hw_type == 'gpu':
            behavior.update(self._record_gpu_behavior(hardware))
        elif hw_type == 'wifi':
            behavior.update(self._record_wifi_behavior(hardware))
        elif hw_type == 'network':
            behavior.update(self._record_network_behavior(hardware))
        else:
            behavior.update(self._record_generic_behavior(hardware))
        
        # Record kernel module information
        behavior['kernel_modules'] = self._get_loaded_kernel_modules(hw_type)
        
        # Record device node information
        behavior['device_nodes'] = self._get_device_nodes(hw_type)
        
        # Record sysfs information
        behavior['sysfs_attributes'] = self._get_sysfs_info(hardware)
        
        # Store behavior profile
        device_key = f"{hw_type}_{hw_name}".replace(' ', '_')
        self.behaviors[device_key] = behavior
        
        return behavior
    
    def _record_gpu_behavior(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Record GPU-specific behavior"""
        behavior = {
            'current_driver': self._get_gpu_driver(),
            'device_capabilities': self._get_gpu_capabilities(),
            'display_info': self._get_display_info(),
            'memory_info': self._get_gpu_memory_info(),
            'power_profile': self._get_gpu_power_profile(),
            'kernel_interactions': {
                'drm_subsystem': self._check_drm_subsystem(),
                'framebuffer': self._check_framebuffer(),
                'modeset': self._check_modesetting()
            }
        }
        return behavior
    
    def _record_wifi_behavior(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Record WiFi-specific behavior"""
        behavior = {
            'current_driver': self._get_wifi_driver(hardware),
            'device_capabilities': self._get_wifi_capabilities(),
            'interface_state': self._get_wireless_interfaces(),
            'regulatory_domain': self._get_regulatory_domain(),
            'kernel_interactions': {
                'cfg80211': self._check_cfg80211(),
                'mac80211': self._check_mac80211(),
                'nl80211': 'supported'
            }
        }
        return behavior
    
    def _record_network_behavior(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Record Network-specific behavior"""
        behavior = {
            'current_driver': self._get_network_driver(hardware),
            'device_capabilities': self._get_network_capabilities(),
            'interface_state': self._get_network_interfaces(),
            'ethtool_info': self._get_ethtool_info(),
            'kernel_interactions': {
                'netdev': self._check_netdev(),
                'ethtool': 'supported',
                'tc': self._check_tc()
            }
        }
        return behavior
    
    def _record_generic_behavior(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Record generic device behavior"""
        behavior = {
            'current_driver': self._get_generic_driver(hardware),
            'device_capabilities': ['generic_device'],
            'kernel_interactions': {
                'sysfs': 'available',
                'udev': 'active',
                'devfs': self._check_devfs()
            }
        }
        return behavior
    
    def _get_gpu_driver(self) -> Optional[str]:
        """Get currently loaded GPU driver"""
        # Check for NVIDIA driver
        nvidia_check = self._run_command(['lsmod'])
        if 'nvidia' in nvidia_check:
            version = self._run_command(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'])
            if version:
                return f"nvidia-{version}"
        
        # Check for AMD driver
        if 'amdgpu' in nvidia_check:
            return "amdgpu"
        
        # Check for Intel driver
        if 'i915' in nvidia_check:
            return "i915"
        
        return None
    
    def _get_gpu_capabilities(self) -> List[str]:
        """Get GPU capabilities"""
        caps = []
        
        # Check for NVIDIA capabilities
        nvidia_info = self._run_command(['nvidia-smi', '--query-gpu=name,compute_cap', '--format=csv,noheader'])
        if nvidia_info:
            caps.extend(['3d_acceleration', 'compute', 'video_decode', 'video_encode', 'cuda'])
        
        # Check for Vulkan
        if os.path.exists('/usr/bin/vulkaninfo'):
            caps.append('vulkan')
        
        # Check for OpenGL
        glx_info = self._run_command(['glxinfo', '-B'])
        if 'OpenGL' in glx_info:
            caps.append('opengl')
        
        # Check for DRM
        if os.path.exists('/dev/dri'):
            caps.extend(['drm', 'kms'])
        
        return caps
    
    def _get_display_info(self) -> Dict[str, Any]:
        """Get display information"""
        xrandr_output = self._run_command(['xrandr', '--query'])
        
        displays = []
        if xrandr_output:
            for line in xrandr_output.split('\n'):
                if ' connected' in line:
                    displays.append(line.split()[0])
        
        return {
            'connected_displays': displays,
            'display_server': self._get_display_server(),
            'compositor': self._get_compositor()
        }
    
    def _get_display_server(self) -> str:
        """Detect display server type"""
        if os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'
        elif os.environ.get('DISPLAY'):
            return 'x11'
        return 'none'
    
    def _get_compositor(self) -> str:
        """Detect compositor"""
        # Check common compositors
        compositors = ['kwin_wayland', 'gnome-shell', 'mutter', 'compiz']
        ps_output = self._run_command(['ps', 'aux'])
        
        for comp in compositors:
            if comp in ps_output:
                return comp
        
        return 'unknown'
    
    def _get_gpu_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information"""
        nvidia_mem = self._run_command(['nvidia-smi', '--query-gpu=memory.total,memory.used', '--format=csv,noheader'])
        
        if nvidia_mem:
            parts = nvidia_mem.split(',')
            return {
                'total': parts[0].strip() if len(parts) > 0 else 'unknown',
                'used': parts[1].strip() if len(parts) > 1 else 'unknown'
            }
        
        return {'total': 'unknown', 'used': 'unknown'}
    
    def _get_gpu_power_profile(self) -> Dict[str, Any]:
        """Get GPU power profile"""
        nvidia_power = self._run_command(['nvidia-smi', '--query-gpu=power.draw,power.limit', '--format=csv,noheader'])
        
        if nvidia_power:
            parts = nvidia_power.split(',')
            return {
                'current_draw': parts[0].strip() if len(parts) > 0 else 'unknown',
                'power_limit': parts[1].strip() if len(parts) > 1 else 'unknown'
            }
        
        return {'current_draw': 'unknown', 'power_limit': 'unknown'}
    
    def _get_wifi_driver(self, hardware: Dict[str, Any]) -> Optional[str]:
        """Get currently loaded WiFi driver"""
        lsmod = self._run_command(['lsmod'])
        
        # Check common WiFi drivers
        wifi_drivers = ['iwlwifi', 'ath10k', 'ath11k', 'mt7921e', 'rtw88', 'rtw89', 'brcmfmac']
        
        for driver in wifi_drivers:
            if driver in lsmod:
                return driver
        
        return None
    
    def _get_wifi_capabilities(self) -> List[str]:
        """Get WiFi capabilities"""
        iw_output = self._run_command(['iw', 'list'])
        
        caps = []
        if '802.11ac' in iw_output or 'VHT' in iw_output:
            caps.append('wifi5')
        if '802.11ax' in iw_output or 'HE' in iw_output:
            caps.append('wifi6')
        if '6 GHz' in iw_output:
            caps.append('wifi6e')
        if 'WPA3' in iw_output:
            caps.append('wpa3')
        
        return caps
    
    def _get_wireless_interfaces(self) -> List[str]:
        """Get wireless interfaces"""
        iw_dev = self._run_command(['iw', 'dev'])
        
        interfaces = []
        for line in iw_dev.split('\n'):
            if 'Interface' in line:
                parts = line.split()
                if len(parts) >= 2:
                    interfaces.append(parts[1])
        
        return interfaces
    
    def _get_regulatory_domain(self) -> str:
        """Get wireless regulatory domain"""
        iw_reg = self._run_command(['iw', 'reg', 'get'])
        
        if 'country' in iw_reg:
            for line in iw_reg.split('\n'):
                if 'country' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1].rstrip(':')
        
        return 'unknown'
    
    def _get_network_driver(self, hardware: Dict[str, Any]) -> Optional[str]:
        """Get currently loaded network driver"""
        lsmod = self._run_command(['lsmod'])
        
        # Check common network drivers
        net_drivers = ['e1000e', 'igb', 'ixgbe', 'r8169', 'atlantic']
        
        for driver in net_drivers:
            if driver in lsmod:
                return driver
        
        return None
    
    def _get_network_capabilities(self) -> List[str]:
        """Get network capabilities"""
        caps = ['ethernet']
        
        # Check for high-speed capabilities
        ethtool_features = self._run_command(['ethtool', '-k', 'eth0'])
        if 'tcp-segmentation-offload: on' in ethtool_features:
            caps.append('tso')
        if 'rx-checksumming: on' in ethtool_features:
            caps.append('checksum_offload')
        
        return caps
    
    def _get_network_interfaces(self) -> List[str]:
        """Get network interfaces"""
        ip_link = self._run_command(['ip', 'link', 'show'])
        
        interfaces = []
        for line in ip_link.split('\n'):
            if ': ' in line and '<' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    iface = parts[1].strip()
                    if iface not in ['lo']:
                        interfaces.append(iface)
        
        return interfaces
    
    def _get_ethtool_info(self) -> Dict[str, Any]:
        """Get ethtool information"""
        interfaces = self._get_network_interfaces()
        
        if interfaces:
            iface = interfaces[0]
            ethtool_output = self._run_command(['ethtool', iface])
            
            info = {}
            for line in ethtool_output.split('\n'):
                if 'Speed:' in line:
                    info['speed'] = line.split(':')[1].strip()
                elif 'Duplex:' in line:
                    info['duplex'] = line.split(':')[1].strip()
                elif 'Link detected:' in line:
                    info['link'] = line.split(':')[1].strip()
            
            return info
        
        return {}
    
    def _get_generic_driver(self, hardware: Dict[str, Any]) -> Optional[str]:
        """Get generic device driver"""
        # Try to find driver from lspci or lsusb
        vendor = hardware.get('vendor', '')
        device = hardware.get('device', '')
        
        if vendor and device:
            lspci = self._run_command(['lspci', '-k'])
            for line in lspci.split('\n'):
                if vendor in line or device in line:
                    # Look for kernel driver line
                    idx = lspci.split('\n').index(line)
                    for next_line in lspci.split('\n')[idx:idx+5]:
                        if 'Kernel driver in use:' in next_line:
                            return next_line.split(':')[1].strip()
        
        return None
    
    def _get_loaded_kernel_modules(self, hw_type: str) -> List[str]:
        """Get loaded kernel modules relevant to hardware type"""
        lsmod = self._run_command(['lsmod'])
        
        modules = []
        for line in lsmod.split('\n')[1:]:  # Skip header
            parts = line.split()
            if parts:
                module_name = parts[0]
                
                # Filter by hardware type
                if hw_type == 'gpu' and any(x in module_name for x in ['nvidia', 'amdgpu', 'i915', 'drm']):
                    modules.append(module_name)
                elif hw_type == 'wifi' and any(x in module_name for x in ['iwl', 'ath', 'mt', 'rtw', 'brcm', 'cfg80211', 'mac80211']):
                    modules.append(module_name)
                elif hw_type == 'network' and any(x in module_name for x in ['e1000', 'igb', 'r8169', 'atlantic']):
                    modules.append(module_name)
        
        return modules
    
    def _get_device_nodes(self, hw_type: str) -> List[str]:
        """Get device nodes for hardware type"""
        nodes = []
        
        if hw_type == 'gpu':
            if os.path.exists('/dev/dri'):
                nodes.extend(glob.glob('/dev/dri/card*'))
                nodes.extend(glob.glob('/dev/dri/renderD*'))
            if os.path.exists('/dev/nvidia0'):
                nodes.extend(glob.glob('/dev/nvidia*'))
        elif hw_type == 'wifi':
            # Wireless devices are typically network interfaces
            nodes = self._get_wireless_interfaces()
        elif hw_type == 'network':
            nodes = self._get_network_interfaces()
        
        return nodes
    
    def _get_sysfs_info(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Get sysfs attributes for device"""
        info = {}
        
        # Try to find device in sysfs
        hw_type = hardware.get('type', '').lower()
        
        if hw_type == 'gpu':
            # Check /sys/class/drm
            drm_cards = glob.glob('/sys/class/drm/card*')
            if drm_cards:
                card = drm_cards[0]
                info['drm_card'] = card
                
                # Read some attributes
                for attr in ['enabled', 'status', 'dpms']:
                    attr_path = os.path.join(card, attr)
                    if os.path.exists(attr_path):
                        try:
                            with open(attr_path, 'r') as f:
                                info[attr] = f.read().strip()
                        except Exception:
                            pass
        
        return info
    
    def _check_drm_subsystem(self) -> str:
        """Check DRM subsystem status"""
        return 'active' if os.path.exists('/sys/class/drm') else 'inactive'
    
    def _check_framebuffer(self) -> str:
        """Check framebuffer status"""
        return 'active' if os.path.exists('/dev/fb0') else 'inactive'
    
    def _check_modesetting(self) -> str:
        """Check kernel modesetting status"""
        # Check if KMS is active
        if os.path.exists('/sys/class/drm'):
            return 'kms_active'
        return 'legacy'
    
    def _check_cfg80211(self) -> str:
        """Check cfg80211 wireless configuration API"""
        lsmod = self._run_command(['lsmod'])
        return 'active' if 'cfg80211' in lsmod else 'inactive'
    
    def _check_mac80211(self) -> str:
        """Check mac80211 wireless stack"""
        lsmod = self._run_command(['lsmod'])
        return 'active' if 'mac80211' in lsmod else 'inactive'
    
    def _check_netdev(self) -> str:
        """Check network device subsystem"""
        return 'active' if os.path.exists('/sys/class/net') else 'inactive'
    
    def _check_tc(self) -> str:
        """Check traffic control"""
        tc_check = self._run_command(['tc', '-V'])
        return 'active' if tc_check else 'inactive'
    
    def _check_devfs(self) -> str:
        """Check devfs status"""
        return 'active' if os.path.exists('/dev') else 'inactive'
    
    def save_behaviors(self, filepath: str):
        """Save recorded behaviors to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    'system_info': self.system_info,
                    'behaviors': self.behaviors
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to save behaviors: {e}")
    
    def load_behaviors(self, filepath: str) -> bool:
        """Load recorded behaviors from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.system_info = data.get('system_info', {})
                self.behaviors = data.get('behaviors', {})
            return True
        except Exception as e:
            print(f"Failed to load behaviors: {e}")
            return False
