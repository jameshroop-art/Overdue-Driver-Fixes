"""
Hardware Detection Module
Detects and identifies hardware components
Enforces domain whitelist for web searches
"""

import subprocess
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.terminal import run_with_output
from utils.security import DomainValidator
import requests

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
        
        # Initialize domain validator for security
        self.domain_validator = DomainValidator(config_manager)
    
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
        """Detect motherboard/chipset with BIOS information and update checking"""
        boards = []
        
        try:
            # Try to read DMI information
            dmi_path = Path('/sys/class/dmi/id')
            if dmi_path.exists():
                board_vendor = self._read_dmi_file(dmi_path / 'board_vendor')
                board_name = self._read_dmi_file(dmi_path / 'board_name')
                board_version = self._read_dmi_file(dmi_path / 'board_version')
                
                # Read BIOS information
                bios_vendor = self._read_dmi_file(dmi_path / 'bios_vendor')
                bios_version = self._read_dmi_file(dmi_path / 'bios_version')
                bios_date = self._read_dmi_file(dmi_path / 'bios_date')
                
                if board_vendor and board_name:
                    # Detect chipset from lspci
                    chipset_info = self._detect_chipset()
                    
                    # Check Linux compatibility and search for repos
                    compat_info = self._check_linux_compatibility(board_vendor, board_name)
                    
                    board_info = {
                        'type': 'Motherboard',
                        'name': f"{board_vendor} {board_name}",
                        'vendor': board_vendor,
                        'model': board_name,
                        'board_version': board_version,
                        'bios_vendor': bios_vendor,
                        'bios_version': bios_version,
                        'bios_date': bios_date,
                        'chipset': chipset_info.get('name', 'Unknown') if chipset_info else 'Unknown',
                        'chipset_vendor': chipset_info.get('vendor', 'Unknown') if chipset_info else 'Unknown',
                        'driver': None,
                        'linux_compatible': compat_info
                    }
                    
                    # Check for BIOS updates if we have version info
                    if bios_version:
                        bios_update_info = self.check_bios_updates(board_vendor, board_name, bios_version)
                        board_info['bios_update_info'] = bios_update_info
                    
                    boards.append(board_info)
        
        except Exception as e:
            print(f"Error detecting motherboard: {e}")
        
        return boards
    
    def _detect_chipset(self) -> Dict[str, Any]:
        """Detect motherboard chipset from lspci"""
        try:
            show_output = self.config.get('cli.show_subprocess_output', False)
            result = run_with_output(
                ['lspci'],
                show_output=show_output,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Look for host bridge, ISA bridge, or LPC bridge
                    if any(keyword in line.lower() for keyword in ['host bridge', 'isa bridge', 'lpc']):
                        # Extract chipset info
                        vendor = None
                        name = line
                        
                        if 'Intel' in line:
                            vendor = 'Intel'
                            # Extract chipset model - try multiple patterns
                            # Pattern 1: Standard chipset naming (e.g., "Z690", "H610")
                            match = re.search(r'\b([ZBHQX]\d{3,4}[A-Z]*)\b', line)
                            if not match:
                                # Pattern 2: Full description with Chipset/Series
                                match = re.search(r'Intel.*?(\d{3,4}\s*[A-Z]*\s*(?:Chipset|Series))', line)
                            if match:
                                name = match.group(1)
                        elif 'AMD' in line:
                            vendor = 'AMD'
                            # Extract chipset model with broader pattern
                            # Covers: X570, B550, A520, X670E, TRX40, WRX80, etc.
                            match = re.search(r'\b([ABXTW][R]?[X]?\d{3,4}[A-Z]*)\b', line)
                            if match:
                                name = match.group(1)
                        
                        if vendor:
                            return {'vendor': vendor, 'name': name}
        except Exception as e:
            print(f"Error detecting chipset: {e}")
        
        return None
    
    def _check_linux_compatibility(self, vendor: str, model: str) -> Dict[str, Any]:
        """Check Linux compatibility for motherboard manufacturer
        
        Returns dict with compatibility info and manufacturer support URL
        """
        if not vendor or not model:
            return {
                'status': 'unknown', 
                'support_url': None, 
                'drivers_url': None,
                'notes': 'Insufficient information'
            }
        
        vendor_lower = vendor.lower()
        
        # Manufacturer Linux support information
        manufacturer_info = {
            'asus': {
                'name': 'ASUS',
                'linux_support': 'Good',
                'support_url': 'https://www.asus.com/support/',
                'drivers_url': 'https://www.asus.com/support/download-center/',
                'notes': 'ASUS provides Linux drivers for most motherboards. Check support site for specific model.'
            },
            'msi': {
                'name': 'MSI',
                'linux_support': 'Good',
                'support_url': 'https://www.msi.com/support',
                'drivers_url': 'https://www.msi.com/support/download',
                'notes': 'MSI motherboards generally work well with Linux. Some RGB/fan control may need third-party tools.'
            },
            'gigabyte': {
                'name': 'Gigabyte',
                'linux_support': 'Good',
                'support_url': 'https://www.gigabyte.com/Support',
                'drivers_url': 'https://www.gigabyte.com/Support/Motherboard',
                'notes': 'Gigabyte motherboards have good Linux compatibility. Check for chipset driver support.'
            },
            'asrock': {
                'name': 'ASRock',
                'linux_support': 'Good',
                'support_url': 'https://www.asrock.com/support/',
                'drivers_url': 'https://www.asrock.com/support/download.asp',
                'notes': 'ASRock motherboards work well with Linux. Most features supported out-of-box.'
            },
            'evga': {
                'name': 'EVGA',
                'linux_support': 'Moderate',
                'support_url': 'https://www.evga.com/support/',
                'drivers_url': 'https://www.evga.com/support/download/',
                'notes': 'EVGA motherboards generally compatible. Some utilities Windows-only.'
            },
            'biostar': {
                'name': 'Biostar',
                'linux_support': 'Moderate',
                'support_url': 'https://www.biostar.com.tw/app/en/support/',
                'drivers_url': 'https://www.biostar.com.tw/app/en/support/download.php',
                'notes': 'Basic Linux support. Most hardware works but limited manufacturer utilities.'
            }
        }
        
        # Try to match vendor
        for key, info in manufacturer_info.items():
            if key in vendor_lower or info['name'].lower() in vendor_lower:
                return {
                    'status': 'supported',
                    'manufacturer': info['name'],
                    'linux_support': info['linux_support'],
                    'support_url': info['support_url'],
                    'drivers_url': info['drivers_url'],
                    'notes': info['notes'],
                    'model': model
                }
        
        # Unknown manufacturer - try to find repos
        compat_info = {
            'status': 'unknown',
            'manufacturer': vendor,
            'linux_support': 'Unknown',
            'support_url': None,
            'drivers_url': None,
            'notes': f'Linux compatibility for {vendor} motherboards not verified. Check manufacturer website.',
            'model': model
        }
        
        # Search for repos if manufacturer not in database
        repos = self._search_manufacturer_repos(vendor, model)
        hf_repos = self._search_huggingface_repos(vendor, model)
        
        # Combine both GitHub and HuggingFace results
        all_repos = repos + hf_repos
        
        if all_repos:
            compat_info['repos'] = all_repos
            compat_info['notes'] = f'Found {len(all_repos)} community/manufacturer repos for Linux support (GitHub: {len(repos)}, HuggingFace: {len(hf_repos)}).'
        
        return compat_info
    
    def _search_manufacturer_repos(self, vendor: str, model: str) -> List[Dict[str, Any]]:
        """Search for manufacturer and community repos on GitHub
        
        Searches for:
        1. Official manufacturer repos
        2. User repos with driver/BIOS updates
        3. Linux compatibility tools
        
        Returns list of repos with Linux-compatible updates
        
        Note: Only searches GitHub which is whitelisted for driver searches
        """
        repos = []
        
        if not vendor:
            return repos
        
        try:
            # Search terms for manufacturer repos
            search_terms = [
                f"{vendor} linux driver",
                f"{vendor} linux bios",
                f"{vendor} motherboard linux",
                f"{vendor} chipset linux"
            ]
            
            for search_term in search_terms:
                try:
                    # Validate search query (must be driver/chipset related)
                    is_allowed, reason = self.domain_validator.validate_github_search(search_term)
                    if not is_allowed:
                        print(f"⚠ GitHub search blocked: {reason}")
                        continue
                    
                    # Use GitHub API to search repos
                    url = "https://api.github.com/search/repositories"
                    
                    # Validate URL against whitelist
                    url_allowed, url_reason = self.domain_validator.is_url_allowed(url)
                    if not url_allowed:
                        print(f"⚠ GitHub API access blocked: {url_reason}")
                        break
                    
                    params = {
                        'q': search_term,
                        'sort': 'stars',
                        'order': 'desc',
                        'per_page': 5
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    # Handle rate limiting and errors
                    if response.status_code == 403:
                        print(f"⚠ GitHub API rate limit reached")
                        break
                    elif response.status_code != 200:
                        print(f"⚠ GitHub API returned status {response.status_code}")
                        continue
                    
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        # Check if repo seems relevant
                        repo_name = item.get('name', '').lower()
                        repo_desc = (item.get('description') or '').lower()
                        repo_full_name = item.get('full_name', '')
                        repo_owner = repo_full_name.split('/')[0].lower() if '/' in repo_full_name else ''
                        
                        # Check for relevance
                        is_relevant = (
                            vendor.lower() in repo_name or
                            vendor.lower() in repo_desc or
                            'driver' in repo_name or
                            'bios' in repo_name or
                            'linux' in repo_name or
                            'motherboard' in repo_name
                        )
                        
                        # Better official repo detection
                        # Only mark as official if:
                        # 1. Owner exactly matches vendor name, OR
                        # 2. Owner is a known official account
                        official_accounts = {
                            'asus': ['asus', 'asus-linux'],
                            'msi': ['msi', 'msi-gaming'],
                            'gigabyte': ['gigabyte', 'gigabyte-technology'],
                            'asrock': ['asrock'],
                        }
                        
                        is_official = False
                        vendor_key = vendor.lower()
                        if vendor_key in official_accounts:
                            is_official = repo_owner in official_accounts[vendor_key]
                        else:
                            is_official = repo_owner == vendor_key
                        
                        if is_relevant and item.get('html_url'):
                            repo_info = {
                                'name': item.get('name'),
                                'full_name': repo_full_name,
                                'url': item.get('html_url'),
                                'description': item.get('description', 'No description'),
                                'stars': item.get('stargazers_count', 0),
                                'official': is_official
                            }
                            
                            # Avoid duplicates
                            if not any(r['url'] == repo_info['url'] for r in repos):
                                repos.append(repo_info)
                    
                    # Limit to top 10 repos total
                    if len(repos) >= 10:
                        break
                
                except requests.exceptions.Timeout:
                    print(f"⚠ GitHub API timeout for search: {search_term}")
                    continue
                except requests.exceptions.ConnectionError:
                    print(f"⚠ Cannot connect to GitHub API")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"⚠ GitHub API error: {e}")
                    continue
                except Exception as e:
                    # Continue with other search terms on error
                    print(f"⚠ Error parsing GitHub response: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching repos: {e}")
        
        # Sort repos: official first, then by stars
        repos.sort(key=lambda x: (not x['official'], -x['stars']))
        return repos[:10]  # Return top 10
    
    def _search_huggingface_repos(self, vendor: str, model: str) -> List[Dict[str, Any]]:
        """Search for manufacturer repos on HuggingFace
        
        Searches HuggingFace for:
        1. Driver-related models/datasets
        2. Hardware compatibility tools
        3. Linux firmware collections
        
        Returns list of repos with potential Linux-compatible drivers
        
        Note: Only searches HuggingFace which is whitelisted for driver searches
        """
        repos = []
        
        if not vendor:
            return repos
        
        try:
            # Search terms for HuggingFace
            search_terms = [
                f"{vendor} linux driver",
                f"{vendor} firmware linux",
                f"{vendor} hardware linux"
            ]
            
            for search_term in search_terms:
                try:
                    # Validate search query (must be driver/hardware related)
                    is_allowed, reason = self.domain_validator.validate_huggingface_search(search_term)
                    if not is_allowed:
                        print(f"⚠ HuggingFace search blocked: {reason}")
                        continue
                    
                    # HuggingFace API endpoint for model search
                    url = "https://huggingface.co/api/models"
                    
                    # Validate URL against whitelist
                    url_allowed, url_reason = self.domain_validator.is_url_allowed(url)
                    if not url_allowed:
                        print(f"⚠ HuggingFace API access blocked: {url_reason}")
                        break
                    
                    params = {
                        'search': search_term,
                        'limit': 5
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    # Handle errors
                    if response.status_code == 429:
                        print(f"⚠ HuggingFace API rate limit reached")
                        break
                    elif response.status_code != 200:
                        print(f"⚠ HuggingFace API returned status {response.status_code}")
                        continue
                    
                    items = response.json()
                    
                    for item in items:
                        if isinstance(item, dict):
                            # Extract repo info
                            repo_id = item.get('modelId', '')
                            repo_name = repo_id.split('/')[-1] if '/' in repo_id else repo_id
                            
                            # Check for relevance (driver/firmware related)
                            is_relevant = any(keyword in repo_name.lower() or 
                                            keyword in item.get('tags', [])
                                            for keyword in ['driver', 'firmware', 'hardware', 'linux'])
                            
                            if is_relevant and repo_id:
                                repo_info = {
                                    'name': repo_name,
                                    'full_name': repo_id,
                                    'url': f"https://huggingface.co/{repo_id}",
                                    'description': item.get('description', 'No description'),
                                    'downloads': item.get('downloads', 0),
                                    'source': 'huggingface'
                                }
                                
                                # Avoid duplicates
                                if not any(r['url'] == repo_info['url'] for r in repos):
                                    repos.append(repo_info)
                        
                        # Limit to top 5 from HuggingFace
                        if len(repos) >= 5:
                            break
                    
                    if len(repos) >= 5:
                        break
                
                except requests.exceptions.Timeout:
                    print(f"⚠ HuggingFace API timeout for search: {search_term}")
                    continue
                except requests.exceptions.ConnectionError:
                    print(f"⚠ Cannot connect to HuggingFace API")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"⚠ HuggingFace API error: {e}")
                    continue
                except Exception as e:
                    print(f"⚠ Error parsing HuggingFace response: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching HuggingFace repos: {e}")
        
        # Sort by downloads
        repos.sort(key=lambda x: -x.get('downloads', 0))
        return repos[:5]  # Return top 5
    
    def check_bios_updates(self, vendor: str, model: str, current_version: str) -> Dict[str, Any]:
        """Check for BIOS updates from manufacturer
        
        Args:
            vendor: Motherboard vendor
            model: Motherboard model
            current_version: Current BIOS version
            
        Returns:
            Dict with update availability and download info
        """
        result = {
            'update_available': False,
            'current_version': current_version,
            'latest_version': None,
            'download_url': None,
            'notes': 'Unable to check for updates automatically. Please visit manufacturer website.'
        }
        
        # Get compatibility info which includes manufacturer URLs
        compat = self._check_linux_compatibility(vendor, model)
        
        if compat.get('drivers_url'):
            result['check_url'] = compat['drivers_url']
            result['notes'] = f"Visit {compat['manufacturer']} support site to check for BIOS updates: {compat['drivers_url']}"
        
        # Check repos for BIOS updates
        repos = self._search_manufacturer_repos(vendor, model)
        
        # Also check HuggingFace for firmware/driver repos
        hf_repos = self._search_huggingface_repos(vendor, model)
        
        # Combine results
        all_repos = repos + hf_repos
        
        if all_repos:
            bios_repos = [r for r in all_repos if 'bios' in r['name'].lower() or 'firmware' in r['name'].lower()]
            if bios_repos:
                result['community_repos'] = bios_repos
                result['notes'] += f"\n\nFound {len(bios_repos)} community repos with potential BIOS/firmware updates."
        
        return result
    
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
