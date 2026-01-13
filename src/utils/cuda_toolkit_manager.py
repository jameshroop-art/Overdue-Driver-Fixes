"""
CUDA Toolkit Management Module
Manages CUDA Toolkit versions and driver compatibility
"""

from typing import Dict, List, Optional, Tuple
import re

# CUDA Toolkit version to minimum driver version mapping
# Source: NVIDIA CUDA Toolkit Release Notes
CUDA_DRIVER_COMPATIBILITY = {
    # CUDA 12.x series
    '12.6': {
        'min_driver_linux': '560.28.03',
        'min_driver_windows': '560.76',
        'release_date': '2024-08',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'H100 support'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.5': {
        'min_driver_linux': '555.42.02',
        'min_driver_windows': '555.85',
        'release_date': '2024-05',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'H100 support'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.4': {
        'min_driver_linux': '550.54.14',
        'min_driver_windows': '551.61',
        'release_date': '2024-03',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'RTX 40 series'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.3': {
        'min_driver_linux': '545.23.06',
        'min_driver_windows': '545.84',
        'release_date': '2023-11',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'RTX 40 series'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.2': {
        'min_driver_linux': '535.54.03',
        'min_driver_windows': '536.25',
        'release_date': '2023-07',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'H100 support'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.1': {
        'min_driver_linux': '530.30.02',
        'min_driver_windows': '531.14',
        'release_date': '2023-03',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'RTX 40 series'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    '12.0': {
        'min_driver_linux': '525.60.13',
        'min_driver_windows': '527.41',
        'release_date': '2022-12',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'H100 initial'],
        'architectures': ['Hopper', 'Ada', 'Ampere', 'Turing', 'Volta'],
        'compute_capability': ['9.0', '8.9', '8.7', '8.6', '8.0', '7.5', '7.0']
    },
    
    # CUDA 11.x series
    '11.8': {
        'min_driver_linux': '520.61.05',
        'min_driver_windows': '522.06',
        'release_date': '2022-11',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU', 'RTX 30 series'],
        'architectures': ['Ampere', 'Turing', 'Volta', 'Pascal'],
        'compute_capability': ['8.9', '8.7', '8.6', '8.0', '7.5', '7.0', '6.1', '6.0']
    },
    '11.7': {
        'min_driver_linux': '515.43.04',
        'min_driver_windows': '516.01',
        'release_date': '2022-05',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU'],
        'architectures': ['Ampere', 'Turing', 'Volta', 'Pascal'],
        'compute_capability': ['8.6', '8.0', '7.5', '7.0', '6.1', '6.0']
    },
    '11.6': {
        'min_driver_linux': '510.39.01',
        'min_driver_windows': '511.23',
        'release_date': '2022-01',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU'],
        'architectures': ['Ampere', 'Turing', 'Volta', 'Pascal'],
        'compute_capability': ['8.6', '8.0', '7.5', '7.0', '6.1', '6.0']
    },
    '11.5': {
        'min_driver_linux': '495.29.05',
        'min_driver_windows': '496.04',
        'release_date': '2021-10',
        'features': ['Dynamic parallelism', 'Unified memory', 'Multi-GPU'],
        'architectures': ['Ampere', 'Turing', 'Volta', 'Pascal'],
        'compute_capability': ['8.6', '8.0', '7.5', '7.0', '6.1', '6.0']
    },
    
    # CUDA 10.x series (legacy support)
    '10.2': {
        'min_driver_linux': '440.33',
        'min_driver_windows': '441.22',
        'release_date': '2019-11',
        'features': ['Dynamic parallelism', 'Unified memory'],
        'architectures': ['Turing', 'Volta', 'Pascal', 'Maxwell'],
        'compute_capability': ['7.5', '7.0', '6.1', '6.0', '5.3', '5.2']
    },
}

# GPU Architecture to Compute Capability mapping
GPU_ARCHITECTURES = {
    'Hopper': ['9.0'],  # H100, H200
    'Ada': ['8.9'],  # RTX 40 series (RTX 4090, 4080, 4070, etc.)
    'Ampere': ['8.6', '8.7', '8.0'],  # RTX 30 series, A100, A30
    'Turing': ['7.5'],  # RTX 20 series, GTX 16 series
    'Volta': ['7.0'],  # V100, Titan V
    'Pascal': ['6.1', '6.0'],  # GTX 10 series, P100
    'Maxwell': ['5.3', '5.2'],  # GTX 900/700 series
}

# Common GPU models and their compute capability
GPU_COMPUTE_CAPABILITY = {
    # RTX 50 series (Blackwell - future)
    'RTX 5090': '10.0',
    'RTX 5080': '10.0',
    
    # RTX 40 series (Ada Lovelace)
    'RTX 4090': '8.9',
    'RTX 4080': '8.9',
    'RTX 4070': '8.9',
    'RTX 4060': '8.9',
    
    # RTX 30 series (Ampere)
    'RTX 3090': '8.6',
    'RTX 3080': '8.6',
    'RTX 3070': '8.6',
    'RTX 3060': '8.6',
    
    # RTX 20 series (Turing)
    'RTX 2080': '7.5',
    'RTX 2070': '7.5',
    'RTX 2060': '7.5',
    
    # GTX 16 series (Turing)
    'GTX 1660': '7.5',
    'GTX 1650': '7.5',
    
    # GTX 10 series (Pascal)
    'GTX 1080': '6.1',
    'GTX 1070': '6.1',
    'GTX 1060': '6.1',
    
    # Data Center GPUs
    'H100': '9.0',
    'H200': '9.0',
    'A100': '8.0',
    'A30': '8.0',
    'V100': '7.0',
    'P100': '6.0',
}


class CudaToolkitManager:
    """Manages CUDA Toolkit versions and compatibility"""
    
    def __init__(self):
        self.cuda_versions = CUDA_DRIVER_COMPATIBILITY
        self.gpu_capabilities = GPU_COMPUTE_CAPABILITY
    
    def get_compatible_cuda_versions(self, driver_version: str, os_type: str = 'linux') -> List[Dict]:
        """Get all CUDA versions compatible with a driver version
        
        Args:
            driver_version: Driver version string (e.g., '550.54.14')
            os_type: 'linux' or 'windows'
            
        Returns:
            List of compatible CUDA versions with details
        """
        compatible_versions = []
        driver_field = f'min_driver_{os_type}'
        
        for cuda_ver, info in self.cuda_versions.items():
            min_driver = info.get(driver_field, '0')
            
            if self._compare_versions(driver_version, min_driver) >= 0:
                compatible_versions.append({
                    'cuda_version': cuda_ver,
                    'min_driver_required': min_driver,
                    'release_date': info['release_date'],
                    'features': info['features'],
                    'architectures': info['architectures'],
                    'compute_capability': info['compute_capability']
                })
        
        # Sort by version (newest first)
        compatible_versions.sort(key=lambda x: self._version_to_tuple(x['cuda_version']), reverse=True)
        
        return compatible_versions
    
    def get_required_driver_version(self, cuda_version: str, os_type: str = 'linux') -> Optional[str]:
        """Get minimum required driver version for a CUDA version
        
        Args:
            cuda_version: CUDA version (e.g., '12.4')
            os_type: 'linux' or 'windows'
            
        Returns:
            Minimum driver version string or None
        """
        cuda_info = self.cuda_versions.get(cuda_version)
        if not cuda_info:
            return None
        
        driver_field = f'min_driver_{os_type}'
        return cuda_info.get(driver_field)
    
    def is_cuda_compatible(self, cuda_version: str, driver_version: str, os_type: str = 'linux') -> Tuple[bool, str]:
        """Check if CUDA version is compatible with driver version
        
        Args:
            cuda_version: CUDA version (e.g., '12.4')
            driver_version: Driver version (e.g., '550.54.14')
            os_type: 'linux' or 'windows'
            
        Returns:
            Tuple of (is_compatible, message)
        """
        required_driver = self.get_required_driver_version(cuda_version, os_type)
        
        if required_driver is None:
            return False, f"CUDA {cuda_version} not found in compatibility database"
        
        if self._compare_versions(driver_version, required_driver) >= 0:
            return True, f"✓ Driver {driver_version} is compatible with CUDA {cuda_version}"
        else:
            return False, f"✗ Driver {driver_version} is too old. CUDA {cuda_version} requires {required_driver} or newer"
    
    def get_gpu_compute_capability(self, gpu_model: str) -> Optional[str]:
        """Get compute capability for a GPU model
        
        Args:
            gpu_model: GPU model name (e.g., 'RTX 3090')
            
        Returns:
            Compute capability string or None
        """
        # Try exact match first
        for model, capability in self.gpu_capabilities.items():
            if model.upper() in gpu_model.upper():
                return capability
        
        return None
    
    def get_cuda_for_gpu(self, gpu_model: str, driver_version: str, os_type: str = 'linux') -> List[Dict]:
        """Get recommended CUDA versions for a specific GPU and driver
        
        Args:
            gpu_model: GPU model name
            driver_version: Current driver version
            os_type: 'linux' or 'windows'
            
        Returns:
            List of recommended CUDA versions
        """
        compute_capability = self.get_gpu_compute_capability(gpu_model)
        compatible_cuda = self.get_compatible_cuda_versions(driver_version, os_type)
        
        recommendations = []
        for cuda in compatible_cuda:
            # Check if GPU's compute capability is supported
            if compute_capability and compute_capability in cuda['compute_capability']:
                cuda['recommended'] = True
                cuda['gpu_supported'] = True
            else:
                cuda['recommended'] = False
                cuda['gpu_supported'] = compute_capability in cuda['compute_capability'] if compute_capability else False
            
            recommendations.append(cuda)
        
        return recommendations
    
    def get_latest_cuda_for_driver(self, driver_version: str, os_type: str = 'linux') -> Optional[Dict]:
        """Get the latest CUDA version compatible with driver
        
        Args:
            driver_version: Driver version
            os_type: 'linux' or 'windows'
            
        Returns:
            Latest compatible CUDA info or None
        """
        compatible = self.get_compatible_cuda_versions(driver_version, os_type)
        return compatible[0] if compatible else None
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings
        
        Returns:
            1 if version1 > version2
            0 if version1 == version2
            -1 if version1 < version2
        """
        v1_parts = self._version_to_tuple(version1)
        v2_parts = self._version_to_tuple(version2)
        
        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        else:
            return 0
    
    def _version_to_tuple(self, version: str) -> tuple:
        """Convert version string to tuple for comparison"""
        # Extract numeric parts only
        parts = re.findall(r'\d+', version)
        return tuple(int(p) for p in parts)
    
    def get_all_cuda_versions(self) -> List[str]:
        """Get list of all available CUDA versions"""
        versions = list(self.cuda_versions.keys())
        versions.sort(key=lambda x: self._version_to_tuple(x), reverse=True)
        return versions
    
    def get_cuda_info(self, cuda_version: str) -> Optional[Dict]:
        """Get detailed information about a CUDA version"""
        return self.cuda_versions.get(cuda_version)
