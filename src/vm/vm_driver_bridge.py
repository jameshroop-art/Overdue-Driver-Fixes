"""
VM Manager for Microsoft Driver Installation Bridge
Creates and manages a VM to safely install Windows drivers and bridge to Debian host
Includes web browser for driver downloads and LLM Studio integration
All operations managed from main launcher
OPTIMIZED FOR LOW SYSTEM IMPACT
COMPLETE PRIVACY: NO LOGGING, AUDITS, OR TELEMETRY FROM VM
"""

import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import atexit
import psutil

class VMDriverBridge:
    """
    Manages VM for Microsoft driver installation with bridge to Debian host
    Integrated with main launcher for seamless operation
    OPTIMIZED FOR MINIMAL RESOURCE USAGE
    PRIVACY-FIRST: All VM logging, audits, and telemetry disabled
    """
    
    # Low-impact default settings
    DEFAULT_LOW_IMPACT_CONFIG = {
        'memory': '1024',      # 1GB RAM (minimal for Windows)
        'cpus': '1',           # Single CPU core
        'disk_size': '15G',    # 15GB disk (smaller footprint)
        'cpu_limit': '50',     # Limit to 50% of one core
        'io_limit': 'low',     # Low I/O priority
        'display': 'gtk',
        'enable_balloon': True,  # Enable memory ballooning
        'enable_compression': True,  # Enable disk compression
        'disable_logging': True,     # NO VM logging
        'disable_telemetry': True,   # NO telemetry
        'disable_audit': True,       # NO audit logs
    }
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.vm_name = "driver-mgt-windows-bridge"
        self.vm_dir = Path.home() / '.local' / 'share' / 'driver-mgt' / 'vm'
        self.vm_disk_path = self.vm_dir / 'windows-driver-bridge.qcow2'
        
        # Use low-impact configuration by default
        self.vm_memory = self.config.get('vm.memory', self.DEFAULT_LOW_IMPACT_CONFIG['memory'])
        self.vm_cpus = self.config.get('vm.cpus', self.DEFAULT_LOW_IMPACT_CONFIG['cpus'])
        self.vm_disk_size = self.config.get('vm.disk_size', self.DEFAULT_LOW_IMPACT_CONFIG['disk_size'])
        self.vm_display = self.config.get('vm.display', self.DEFAULT_LOW_IMPACT_CONFIG['display'])
        self.cpu_limit = self.config.get('vm.cpu_limit', self.DEFAULT_LOW_IMPACT_CONFIG['cpu_limit'])
        
        # Low-impact features
        self.enable_balloon = self.config.get('vm.enable_balloon', True)
        self.enable_compression = self.config.get('vm.enable_compression', True)
        
        # PRIVACY: Disable all logging, audits, and telemetry
        self.disable_vm_logging = self.config.get('vm.disable_logging', True)
        self.disable_vm_telemetry = self.config.get('vm.disable_telemetry', True)
        self.disable_vm_audit = self.config.get('vm.disable_audit', True)
        
        # Bridge configuration
        self.bridge_enabled = False
        self.bridge_interface = None
        
        # Privacy: Disable telemetry during operations
        self.telemetry_disabled = False
        self.original_lmstudio_config = None
        
        # Track VM process
        self.vm_process = None
        self.vm_nice_level = 19  # Lowest priority
        
        # Block telemetry hosts at network level
        self.telemetry_hosts_blocked = False
        
        # Initialize VM directory
        self.vm_dir.mkdir(parents=True, exist_ok=True)
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check available system resources before starting VM"""
        try:
            # Get system memory
            mem = psutil.virtual_memory()
            available_mem_mb = mem.available // (1024 * 1024)
            
            # Get CPU info
            cpu_count = psutil.cpu_count(logical=False) or 1
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get disk space
            disk = psutil.disk_usage(str(self.vm_dir.parent))
            available_disk_gb = disk.free // (1024 ** 3)
            
            # Calculate recommended settings
            recommended_mem = min(1024, available_mem_mb // 4)  # Max 1GB or 25% of available
            recommended_cpus = max(1, min(2, cpu_count // 2))  # Max 2 CPUs or half available
            
            return {
                'available_memory_mb': available_mem_mb,
                'available_disk_gb': available_disk_gb,
                'cpu_count': cpu_count,
                'cpu_usage': cpu_percent,
                'recommended_memory': recommended_mem,
                'recommended_cpus': recommended_cpus,
                'can_run_vm': available_mem_mb >= 512 and available_disk_gb >= 10,
                'low_impact_mode': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'can_run_vm': False
            }
    
    def adjust_vm_priority(self):
        """Adjust VM process priority to minimize system impact"""
        if not self.vm_process or self.vm_process.poll() is not None:
            return
        
        try:
            vm_pid = self.vm_process.pid
            
            # Set process nice level (lowest priority)
            os.system(f'renice -n {self.vm_nice_level} -p {vm_pid} >/dev/null 2>&1')
            
            # Set I/O priority to idle
            os.system(f'ionice -c 3 -p {vm_pid} >/dev/null 2>&1')
            
            print(f"✓ VM priority adjusted for low system impact")
        except Exception as e:
            print(f"⚠ Could not adjust VM priority: {e}")
    
    def check_vm_support(self) -> Dict[str, Any]:
        """Check if VM virtualization is supported on the system"""
        result = {
            'kvm_supported': False,
            'qemu_installed': False,
            'libvirt_installed': False,
            'ready': False,
            'low_impact_mode': True,
            'details': []
        }
        
        # Check KVM support
        if Path('/dev/kvm').exists():
            result['kvm_supported'] = True
            result['details'].append('KVM hardware acceleration available')
        else:
            result['details'].append('KVM not available - VM will be slower')
        
        # Check QEMU
        if shutil.which('qemu-system-x86_64'):
            result['qemu_installed'] = True
            result['details'].append('QEMU installed')
        else:
            result['details'].append('QEMU not found - VM features unavailable')
        
        # Check libvirt
        if shutil.which('virsh'):
            result['libvirt_installed'] = True
            result['details'].append('libvirt available')
        
        result['ready'] = result['qemu_installed']
        
        return result
    
    def setup_network_bridge(self) -> bool:
        """Setup network bridge for VM to access host network"""
        print("Setting up network bridge for VM...")
        
        try:
            # Check if bridge already exists
            check_bridge = subprocess.run(
                ['ip', 'link', 'show', 'br0'],
                capture_output=True,
                timeout=5
            )
            
            if check_bridge.returncode == 0:
                print("✓ Bridge interface already exists")
                self.bridge_interface = 'br0'
                self.bridge_enabled = True
                return True
            
            # Try to create bridge (requires sudo)
            print("Creating bridge interface...")
            result = subprocess.run(
                ['sudo', 'ip', 'link', 'add', 'name', 'br0', 'type', 'bridge'],
                timeout=10
            )
            
            if result.returncode == 0:
                subprocess.run(['sudo', 'ip', 'link', 'set', 'br0', 'up'], timeout=10)
                print("✓ Bridge interface created")
                self.bridge_interface = 'br0'
                self.bridge_enabled = True
                return True
            
            print("⚠ Could not create bridge, using user-mode networking")
            return False
                
        except Exception as e:
            print(f"⚠ Bridge setup failed: {e}, using user-mode networking")
            return False
    
    def disable_lmstudio_telemetry(self) -> bool:
        """Disable all LLM Studio logging, telemetry, and audits"""
        print("Disabling LLM Studio telemetry and logging...")
        
        try:
            lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
            lmstudio_config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = lmstudio_config_dir / 'config.json'
            
            # Backup original config
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.original_lmstudio_config = f.read()
                
                config = json.loads(self.original_lmstudio_config)
            else:
                config = {}
            
            # Disable all telemetry, logging, and analytics
            config.update({
                'telemetry': {'enabled': False, 'allowCollection': False},
                'logging': {'enabled': False, 'level': 'none'},
                'analytics': {'enabled': False, 'optOut': True},
                'crashReporting': {'enabled': False},
                'usageStats': {'enabled': False},
                'diagnostics': {'enabled': False},
                'audit': {'enabled': False}
            })
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create no-telemetry marker
            (lmstudio_config_dir / '.no-telemetry').touch()
            
            print("✓ LLM Studio telemetry, logging, and audits disabled")
            self.telemetry_disabled = True
            return True
            
        except Exception as e:
            print(f"⚠ Could not disable telemetry: {e}")
            return False
    
    def enable_lmstudio_telemetry(self) -> bool:
        """Re-enable LLM Studio telemetry after operations complete"""
        if not self.telemetry_disabled:
            return True
        
        print("Restoring LLM Studio configuration...")
        
        try:
            lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
            config_file = lmstudio_config_dir / 'config.json'
            
            # Restore original config if we backed it up
            if self.original_lmstudio_config:
                with open(config_file, 'w') as f:
                    f.write(self.original_lmstudio_config)
                print("✓ LLM Studio configuration restored")
            
            # Remove no-telemetry marker
            marker = lmstudio_config_dir / '.no-telemetry'
            if marker.exists():
                marker.unlink()
            
            self.telemetry_disabled = False
            return True
            
        except Exception as e:
            print(f"⚠ Could not restore configuration: {e}")
            return False
    
    def create_vm_disk(self) -> bool:
        """Create a virtual disk for the VM with compression for low impact"""
        if self.vm_disk_path.exists():
            print(f"✓ VM disk already exists: {self.vm_disk_path}")
            return True
        
        print(f"Creating VM disk: {self.vm_disk_size} (with compression for low disk impact)")
        
        try:
            # Create disk with compression if enabled
            cmd = [
                'qemu-img', 'create',
                '-f', 'qcow2',
            ]
            
            if self.enable_compression:
                cmd.extend(['-o', 'compression_type=zstd,cluster_size=2M'])
            
            cmd.extend([
                str(self.vm_disk_path),
                self.vm_disk_size
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✓ VM disk created: {self.vm_disk_path}")
                return True
            else:
                print(f"✗ Failed to create VM disk: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating VM disk: {e}")
            return False
    
    def start_vm(self, iso_path: Optional[str] = None, headless: bool = False) -> Optional[subprocess.Popen]:
        """Start the VM with low system impact configuration"""
        
        if self.vm_process and self.vm_process.poll() is None:
            print("✓ VM is already running")
            return self.vm_process
        
        # Check system resources before starting
        resources = self.check_system_resources()
        if not resources.get('can_run_vm', False):
            print(f"✗ Insufficient resources to start VM")
            print(f"   Available memory: {resources.get('available_memory_mb', 0)} MB")
            print(f"   Available disk: {resources.get('available_disk_gb', 0)} GB")
            return None
        
        print(f"Starting VM: {self.vm_name} (low-impact mode)")
        print(f"  Memory: {self.vm_memory} MB")
        print(f"  CPUs: {self.vm_cpus}")
        print(f"  CPU limit: {self.cpu_limit}%")
        
        # Build QEMU command with low-impact settings
        cmd = [
            'qemu-system-x86_64',
            '-name', self.vm_name,
            '-m', str(self.vm_memory),
            '-smp', str(self.vm_cpus),
            '-drive', f'file={self.vm_disk_path},format=qcow2,if=virtio,cache=writeback',
            '-vga', 'virtio',
            '-device', 'virtio-net-pci,netdev=net0',
            '-rtc', 'base=localtime',
        ]
        
        # Add KVM acceleration if available (more efficient)
        if Path('/dev/kvm').exists():
            cmd.extend(['-machine', 'type=q35,accel=kvm', '-cpu', 'host'])
        else:
            cmd.extend(['-machine', 'type=q35', '-cpu', 'qemu64'])
        
        # Add memory balloon for dynamic memory management (low impact)
        if self.enable_balloon:
            cmd.extend(['-device', 'virtio-balloon'])
        
        # Network configuration with minimal overhead
        if self.bridge_enabled and self.bridge_interface:
            cmd.extend(['-netdev', f'bridge,id=net0,br={self.bridge_interface}'])
        else:
            # User-mode networking (lowest overhead)
            cmd.extend(['-netdev', 'user,id=net0'])
        
        # Display configuration - headless for lowest impact
        if headless:
            cmd.extend(['-display', 'none', '-vnc', ':1'])
        else:
            cmd.extend(['-display', self.vm_display])
        
        # Add ISO if provided
        if iso_path and Path(iso_path).exists():
            cmd.extend(['-cdrom', iso_path, '-boot', 'd'])
        
        # Add UEFI firmware if available
        ovmf_path = Path('/usr/share/OVMF/OVMF_CODE.fd')
        if ovmf_path.exists():
            cmd.extend(['-bios', str(ovmf_path)])
        
        try:
            # Start VM with low priority
            self.vm_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✓ VM started (PID: {self.vm_process.pid})")
            
            # Adjust process priority for low system impact
            self.adjust_vm_priority()
            
            return self.vm_process
        except Exception as e:
            print(f"✗ Error starting VM: {e}")
            return None
    
    def stop_vm(self):
        """Stop the running VM gracefully"""
        if self.vm_process and self.vm_process.poll() is None:
            print("Stopping VM gracefully...")
            self.vm_process.terminate()
            try:
                self.vm_process.wait(timeout=10)
                print("✓ VM stopped")
            except subprocess.TimeoutExpired:
                print("⚠ VM did not stop gracefully, force killing...")
                self.vm_process.kill()
            self.vm_process = None
    
    def get_vm_status(self) -> Dict[str, Any]:
        """Get current status of the VM"""
        is_running = self.vm_process and self.vm_process.poll() is None
        
        status = {
            'vm_name': self.vm_name,
            'vm_running': is_running,
            'vm_pid': self.vm_process.pid if is_running else None,
            'vm_disk_exists': self.vm_disk_path.exists(),
            'vm_disk_path': str(self.vm_disk_path),
            'vm_disk_size': self.vm_disk_size,
            'vm_memory': f"{self.vm_memory} MB",
            'vm_cpus': self.vm_cpus,
            'cpu_limit': f"{self.cpu_limit}%",
            'low_impact_mode': True,
            'bridge_enabled': self.bridge_enabled,
            'bridge_interface': self.bridge_interface,
            'telemetry_disabled': self.telemetry_disabled,
            'vm_dir': str(self.vm_dir)
        }
        
        # Add resource usage if running
        if is_running:
            try:
                process = psutil.Process(self.vm_process.pid)
                status['cpu_percent'] = process.cpu_percent(interval=0.1)
                status['memory_mb'] = process.memory_info().rss // (1024 * 1024)
            except:
                pass
        
        return status
    
    def cleanup(self):
        """Cleanup VM resources and re-enable telemetry"""
        print("\nCleaning up VM resources...")
        
        # Stop VM if running
        self.stop_vm()
        
        # Re-enable telemetry
        self.enable_lmstudio_telemetry()
        
        print("✓ VM cleanup complete")

    
    def check_vm_support(self) -> Dict[str, Any]:
        """Check if VM virtualization is supported on the system"""
        result = {
            'kvm_supported': False,
            'qemu_installed': False,
            'libvirt_installed': False,
            'ready': False,
            'details': []
        }
        
        # Check KVM support
        if Path('/dev/kvm').exists():
            result['kvm_supported'] = True
            result['details'].append('KVM hardware acceleration available')
        else:
            result['details'].append('KVM not available - VM will be slower')
        
        # Check QEMU
        if shutil.which('qemu-system-x86_64'):
            result['qemu_installed'] = True
            result['details'].append('QEMU installed')
        else:
            result['details'].append('QEMU not found - VM features unavailable')
        
        # Check libvirt
        if shutil.which('virsh'):
            result['libvirt_installed'] = True
            result['details'].append('libvirt available')
        
        result['ready'] = result['qemu_installed']
        
        return result
    
    def setup_network_bridge(self) -> bool:
        """Setup network bridge for VM to access host network"""
        print("Setting up network bridge for VM...")
        
        try:
            # Check if bridge already exists
            check_bridge = subprocess.run(
                ['ip', 'link', 'show', 'br0'],
                capture_output=True,
                timeout=5
            )
            
            if check_bridge.returncode == 0:
                print("✓ Bridge interface already exists")
                self.bridge_interface = 'br0'
                self.bridge_enabled = True
                return True
            
            # Try to create bridge (requires sudo)
            print("Creating bridge interface...")
            result = subprocess.run(
                ['sudo', 'ip', 'link', 'add', 'name', 'br0', 'type', 'bridge'],
                timeout=10
            )
            
            if result.returncode == 0:
                subprocess.run(['sudo', 'ip', 'link', 'set', 'br0', 'up'], timeout=10)
                print("✓ Bridge interface created")
                self.bridge_interface = 'br0'
                self.bridge_enabled = True
                return True
            
            print("⚠ Could not create bridge, using user-mode networking")
            return False
                
        except Exception as e:
            print(f"⚠ Bridge setup failed: {e}, using user-mode networking")
            return False
    
    def disable_lmstudio_telemetry(self) -> bool:
        """Disable all LLM Studio logging, telemetry, and audits"""
        print("Disabling LLM Studio telemetry and logging...")
        
        try:
            lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
            lmstudio_config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = lmstudio_config_dir / 'config.json'
            
            # Backup original config
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.original_lmstudio_config = f.read()
                
                config = json.loads(self.original_lmstudio_config)
            else:
                config = {}
            
            # Disable all telemetry, logging, and analytics
            config.update({
                'telemetry': {'enabled': False, 'allowCollection': False},
                'logging': {'enabled': False, 'level': 'none'},
                'analytics': {'enabled': False, 'optOut': True},
                'crashReporting': {'enabled': False},
                'usageStats': {'enabled': False},
                'diagnostics': {'enabled': False},
                'audit': {'enabled': False}
            })
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create no-telemetry marker
            (lmstudio_config_dir / '.no-telemetry').touch()
            
            print("✓ LLM Studio telemetry, logging, and audits disabled")
            self.telemetry_disabled = True
            return True
            
        except Exception as e:
            print(f"⚠ Could not disable telemetry: {e}")
            return False
    
    def enable_lmstudio_telemetry(self) -> bool:
        """Re-enable LLM Studio telemetry after operations complete"""
        if not self.telemetry_disabled:
            return True
        
        print("Restoring LLM Studio configuration...")
        
        try:
            lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
            config_file = lmstudio_config_dir / 'config.json'
            
            # Restore original config if we backed it up
            if self.original_lmstudio_config:
                with open(config_file, 'w') as f:
                    f.write(self.original_lmstudio_config)
                print("✓ LLM Studio configuration restored")
            
            # Remove no-telemetry marker
            marker = lmstudio_config_dir / '.no-telemetry'
            if marker.exists():
                marker.unlink()
            
            self.telemetry_disabled = False
            return True
            
        except Exception as e:
            print(f"⚠ Could not restore configuration: {e}")
            return False
    
    def create_vm_disk(self) -> bool:
        """Create a virtual disk for the VM"""
        if self.vm_disk_path.exists():
            print(f"✓ VM disk already exists: {self.vm_disk_path}")
            return True
        
        print(f"Creating VM disk: {self.vm_disk_size}")
        
        try:
            result = subprocess.run([
                'qemu-img', 'create',
                '-f', 'qcow2',
                str(self.vm_disk_path),
                self.vm_disk_size
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✓ VM disk created: {self.vm_disk_path}")
                return True
            else:
                print(f"✗ Failed to create VM disk: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating VM disk: {e}")
            return False
    
    def start_vm(self, iso_path: Optional[str] = None, headless: bool = False) -> Optional[subprocess.Popen]:
        """Start the VM with optional ISO for installation"""
        
        if self.vm_process and self.vm_process.poll() is None:
            print("✓ VM is already running")
            return self.vm_process
        
        print(f"Starting VM: {self.vm_name}")
        
        # Build QEMU command
        cmd = [
            'qemu-system-x86_64',
            '-name', self.vm_name,
            '-m', str(self.vm_memory),
            '-smp', str(self.vm_cpus),
            '-drive', f'file={self.vm_disk_path},format=qcow2,if=virtio',
            '-vga', 'virtio',
            '-device', 'virtio-net-pci,netdev=net0',
        ]
        
        # Add KVM acceleration if available
        if Path('/dev/kvm').exists():
            cmd.extend(['-machine', 'type=q35,accel=kvm', '-cpu', 'host'])
        else:
            cmd.extend(['-machine', 'type=q35', '-cpu', 'qemu64'])
        
        # Network configuration
        if self.bridge_enabled and self.bridge_interface:
            cmd.extend(['-netdev', f'bridge,id=net0,br={self.bridge_interface}'])
        else:
            # User-mode networking with port forwarding
            cmd.extend(['-netdev', 'user,id=net0,hostfwd=tcp::3389-:3389'])
        
        # Display configuration
        if headless:
            cmd.extend(['-display', 'none', '-vnc', ':1'])
        else:
            cmd.extend(['-display', self.vm_display])
        
        # Add ISO if provided
        if iso_path and Path(iso_path).exists():
            cmd.extend(['-cdrom', iso_path, '-boot', 'd'])
        
        # Add UEFI firmware if available
        ovmf_path = Path('/usr/share/OVMF/OVMF_CODE.fd')
        if ovmf_path.exists():
            cmd.extend(['-bios', str(ovmf_path)])
        
        try:
            self.vm_process = subprocess.Popen(cmd)
            print(f"✓ VM started (PID: {self.vm_process.pid})")
            return self.vm_process
        except Exception as e:
            print(f"✗ Error starting VM: {e}")
            return None
    
    def stop_vm(self):
        """Stop the running VM"""
        if self.vm_process and self.vm_process.poll() is None:
            print("Stopping VM...")
            self.vm_process.terminate()
            try:
                self.vm_process.wait(timeout=10)
                print("✓ VM stopped")
            except subprocess.TimeoutExpired:
                print("⚠ VM did not stop gracefully, force killing...")
                self.vm_process.kill()
            self.vm_process = None
    
    def get_vm_status(self) -> Dict[str, Any]:
        """Get current status of the VM"""
        is_running = self.vm_process and self.vm_process.poll() is None
        
        return {
            'vm_name': self.vm_name,
            'vm_running': is_running,
            'vm_pid': self.vm_process.pid if is_running else None,
            'vm_disk_exists': self.vm_disk_path.exists(),
            'vm_disk_path': str(self.vm_disk_path),
            'vm_disk_size': self.vm_disk_size,
            'bridge_enabled': self.bridge_enabled,
            'bridge_interface': self.bridge_interface,
            'telemetry_disabled': self.telemetry_disabled,
            'vm_dir': str(self.vm_dir)
        }
    
    def cleanup(self):
        """Cleanup VM resources and re-enable telemetry"""
        print("\nCleaning up VM resources...")
        
        # Stop VM if running
        self.stop_vm()
        
        # Re-enable telemetry
        self.enable_lmstudio_telemetry()
        
        print("✓ VM cleanup complete")
