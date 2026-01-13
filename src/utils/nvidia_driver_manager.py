"""
NVIDIA Driver and Feature Management
Comprehensive NVIDIA GPU driver management with all features
"""

from typing import Dict, List, Optional, Tuple
import re

# NVIDIA Driver Series and their features
NVIDIA_DRIVER_SERIES = {
    # Latest Production Branch
    '565': {
        'branch': 'Production',
        'release_date': '2024-11',
        'min_kernel': '4.15',
        'vulkan': '1.3.290',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.6', '12.5', '12.4'],
        'gpus': ['RTX 50 series', 'RTX 40 series', 'RTX 30 series', 'RTX 20 series'],
        'features': [
            'RTX 5090 support',
            'DLSS 3.7',
            'Ray Tracing',
            'NVIDIA Reflex',
            'NVIDIA Broadcast',
            'NVIDIA Studio',
            'Vulkan 1.3',
            'NVENC/NVDEC AV1',
            'Resizable BAR',
            'DisplayPort 2.1',
            'HDMI 2.1 VRR',
            'G-SYNC',
            'Multi-GPU SLI/NVLink'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': True
    },
    
    # Current Production Branch
    '560': {
        'branch': 'Production',
        'release_date': '2024-08',
        'min_kernel': '4.15',
        'vulkan': '1.3.285',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.6', '12.5', '12.4'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series'],
        'features': [
            'RTX 4090 full support',
            'DLSS 3.5',
            'Ray Tracing',
            'NVIDIA Reflex',
            'NVIDIA Broadcast',
            'NVIDIA Studio',
            'Vulkan 1.3',
            'NVENC/NVDEC AV1',
            'Resizable BAR',
            'DisplayPort 2.0',
            'HDMI 2.1 VRR',
            'G-SYNC',
            'Multi-GPU SLI/NVLink'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': True
    },
    
    # Long-Lived Branch
    '550': {
        'branch': 'Long-Lived',
        'release_date': '2024-03',
        'min_kernel': '4.15',
        'vulkan': '1.3.275',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.4', '12.3', '12.2'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series'],
        'features': [
            'DLSS 3.0',
            'Ray Tracing',
            'NVIDIA Reflex',
            'NVIDIA Broadcast',
            'Vulkan 1.3',
            'NVENC/NVDEC',
            'Resizable BAR',
            'G-SYNC',
            'Multi-GPU'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': True
    },
    
    '545': {
        'branch': 'Production',
        'release_date': '2023-11',
        'min_kernel': '4.15',
        'vulkan': '1.3.268',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.3', '12.2', '12.1'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series'],
        'features': [
            'DLSS 3.0',
            'Ray Tracing',
            'NVIDIA Reflex',
            'Vulkan 1.3',
            'NVENC/NVDEC',
            'Resizable BAR',
            'G-SYNC'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': True
    },
    
    '535': {
        'branch': 'Long-Lived',
        'release_date': '2023-06',
        'min_kernel': '4.15',
        'vulkan': '1.3.255',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.2', '12.1', '12.0'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series', 'GTX 10 series'],
        'features': [
            'DLSS 2.0',
            'Ray Tracing',
            'NVIDIA Reflex',
            'Vulkan 1.3',
            'NVENC/NVDEC',
            'G-SYNC'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': True
    },
    
    '530': {
        'branch': 'Production',
        'release_date': '2023-03',
        'min_kernel': '4.15',
        'vulkan': '1.3.240',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.1', '12.0', '11.8'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series', 'GTX 10 series'],
        'features': [
            'DLSS 2.0',
            'Ray Tracing',
            'Vulkan 1.3',
            'NVENC/NVDEC',
            'G-SYNC'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': False
    },
    
    '525': {
        'branch': 'Long-Lived',
        'release_date': '2022-12',
        'min_kernel': '4.15',
        'vulkan': '1.3.235',
        'opengl': '4.6',
        'opencl': '3.0',
        'cuda_support': ['12.0', '11.8', '11.7'],
        'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series', 'GTX 16 series', 'GTX 10 series'],
        'features': [
            'RTX 40 series initial support',
            'DLSS 2.0',
            'Ray Tracing',
            'NVENC/NVDEC',
            'G-SYNC'
        ],
        'xorg_supported': True,
        'wayland_supported': True,
        'gbm_supported': False
    },
}

# NVIDIA GPU Series and recommended drivers
NVIDIA_GPU_RECOMMENDATIONS = {
    'RTX 50 series': {
        'models': ['RTX 5090', 'RTX 5080', 'RTX 5070'],
        'min_driver': '565.25',
        'recommended_driver': '565.57',
        'compute_capability': '10.0',
        'architecture': 'Blackwell',
        'features': ['DLSS 3.7', 'Ray Tracing Gen 5', 'NVENC AV1', 'DisplayPort 2.1']
    },
    'RTX 40 series': {
        'models': ['RTX 4090', 'RTX 4080', 'RTX 4070 Ti', 'RTX 4070', 'RTX 4060 Ti', 'RTX 4060'],
        'min_driver': '525.60',
        'recommended_driver': '560.35',
        'compute_capability': '8.9',
        'architecture': 'Ada Lovelace',
        'features': ['DLSS 3.5', 'Ray Tracing Gen 4', 'NVENC AV1', 'DisplayPort 2.0']
    },
    'RTX 30 series': {
        'models': ['RTX 3090 Ti', 'RTX 3090', 'RTX 3080 Ti', 'RTX 3080', 'RTX 3070 Ti', 'RTX 3070', 'RTX 3060 Ti', 'RTX 3060'],
        'min_driver': '460.00',
        'recommended_driver': '550.54',
        'compute_capability': '8.6',
        'architecture': 'Ampere',
        'features': ['DLSS 3.0', 'Ray Tracing Gen 3', 'NVENC HEVC', 'Resizable BAR']
    },
    'RTX 20 series': {
        'models': ['RTX 2080 Ti', 'RTX 2080 SUPER', 'RTX 2080', 'RTX 2070 SUPER', 'RTX 2070', 'RTX 2060 SUPER', 'RTX 2060'],
        'min_driver': '418.00',
        'recommended_driver': '535.183',
        'compute_capability': '7.5',
        'architecture': 'Turing',
        'features': ['DLSS 2.0', 'Ray Tracing Gen 2', 'NVENC Turing', 'Integer Scaling']
    },
    'GTX 16 series': {
        'models': ['GTX 1660 Ti', 'GTX 1660 SUPER', 'GTX 1660', 'GTX 1650 SUPER', 'GTX 1650'],
        'min_driver': '418.00',
        'recommended_driver': '535.183',
        'compute_capability': '7.5',
        'architecture': 'Turing',
        'features': ['NVENC Turing', 'Integer Scaling', 'Adaptive Shading']
    },
    'GTX 10 series': {
        'models': ['GTX 1080 Ti', 'GTX 1080', 'GTX 1070 Ti', 'GTX 1070', 'GTX 1060', 'GTX 1050 Ti', 'GTX 1050'],
        'min_driver': '375.00',
        'recommended_driver': '535.183',
        'compute_capability': '6.1',
        'architecture': 'Pascal',
        'features': ['NVENC Pascal', 'Simultaneous Multi-Projection', 'VR Ready']
    },
    'Data Center': {
        'models': ['H100', 'H200', 'A100', 'A30', 'A10', 'V100', 'P100'],
        'min_driver': '525.60',
        'recommended_driver': '565.57',
        'compute_capability': '9.0',  # H100/H200
        'architecture': 'Hopper',
        'features': ['Multi-Instance GPU', 'NVLink', 'Tensor Cores', 'HBM Memory']
    },
}

# NVIDIA Features and their availability
NVIDIA_FEATURES = {
    'DLSS': {
        'name': 'Deep Learning Super Sampling',
        'min_driver': '418.81',
        'min_gpu': 'RTX 20 series',
        'description': 'AI-powered upscaling for improved performance',
        'versions': {
            '3.7': {'driver': '565.57', 'gpus': ['RTX 50 series', 'RTX 40 series']},
            '3.5': {'driver': '545.29', 'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series']},
            '3.0': {'driver': '535.98', 'gpus': ['RTX 40 series', 'RTX 30 series', 'RTX 20 series']},
            '2.0': {'driver': '460.89', 'gpus': ['RTX 30 series', 'RTX 20 series']},
        }
    },
    'Ray Tracing': {
        'name': 'Hardware-Accelerated Ray Tracing',
        'min_driver': '418.81',
        'min_gpu': 'RTX 20 series',
        'description': 'Real-time ray tracing with RT cores',
        'generations': {
            'Gen 5': {'gpus': ['RTX 50 series'], 'rt_cores': 'Gen 4'},
            'Gen 4': {'gpus': ['RTX 40 series'], 'rt_cores': 'Gen 3'},
            'Gen 3': {'gpus': ['RTX 30 series'], 'rt_cores': 'Gen 2'},
            'Gen 2': {'gpus': ['RTX 20 series'], 'rt_cores': 'Gen 1'},
        }
    },
    'NVENC': {
        'name': 'NVIDIA Encoder',
        'min_driver': '375.00',
        'min_gpu': 'GTX 10 series',
        'description': 'Hardware-accelerated video encoding',
        'codecs': {
            'AV1': {'driver': '525.60', 'gpus': ['RTX 40 series', 'RTX 50 series']},
            'HEVC': {'driver': '375.00', 'gpus': ['GTX 10 series and newer']},
            'H.264': {'driver': '375.00', 'gpus': ['GTX 10 series and newer']},
        }
    },
    'NVDEC': {
        'name': 'NVIDIA Decoder',
        'min_driver': '375.00',
        'min_gpu': 'GTX 10 series',
        'description': 'Hardware-accelerated video decoding',
        'codecs': ['AV1', 'HEVC', 'H.264', 'VP9', 'VP8']
    },
    'G-SYNC': {
        'name': 'G-SYNC Variable Refresh Rate',
        'min_driver': '340.00',
        'min_gpu': 'GTX 600 series',
        'description': 'Adaptive sync technology for smooth gaming',
        'types': ['G-SYNC', 'G-SYNC Compatible', 'G-SYNC Ultimate']
    },
    'Reflex': {
        'name': 'NVIDIA Reflex',
        'min_driver': '456.38',
        'min_gpu': 'GTX 900 series',
        'description': 'Low latency mode for competitive gaming',
    },
    'Broadcast': {
        'name': 'NVIDIA Broadcast',
        'min_driver': '456.38',
        'min_gpu': 'RTX 20 series',
        'description': 'AI-powered audio and video effects',
        'features': ['Noise Removal', 'Virtual Background', 'Auto Frame', 'Eye Contact']
    },
    'Resizable BAR': {
        'name': 'Resizable BAR / SAM',
        'min_driver': '465.89',
        'min_gpu': 'GTX 10 series',
        'description': 'Full VRAM access for improved performance',
    },
    'Multi-GPU': {
        'name': 'Multi-GPU Support',
        'min_driver': '375.00',
        'min_gpu': 'GTX 10 series',
        'description': 'SLI and NVLink multi-GPU configurations',
        'types': ['SLI', 'NVLink', 'mGPU']
    }
}


class NvidiaDriverManager:
    """Manages NVIDIA drivers and features"""
    
    def __init__(self):
        self.driver_series = NVIDIA_DRIVER_SERIES
        self.gpu_recommendations = NVIDIA_GPU_RECOMMENDATIONS
        self.features = NVIDIA_FEATURES
    
    def get_available_drivers(self) -> List[Dict]:
        """Get all available NVIDIA driver series"""
        drivers = []
        for series, info in self.driver_series.items():
            drivers.append({
                'series': series,
                'branch': info['branch'],
                'release_date': info['release_date'],
                'version': f"{series}.x",
                **info
            })
        
        # Sort by series number (newest first)
        drivers.sort(key=lambda x: int(x['series']), reverse=True)
        return drivers
    
    def get_recommended_driver(self, gpu_model: str) -> Optional[Dict]:
        """Get recommended driver for a GPU model"""
        for series_name, series_info in self.gpu_recommendations.items():
            for model in series_info['models']:
                if model.upper() in gpu_model.upper():
                    # Find driver info
                    recommended_ver = series_info['recommended_driver']
                    driver_series = recommended_ver.split('.')[0]
                    
                    driver_info = self.driver_series.get(driver_series, {})
                    
                    return {
                        'gpu_series': series_name,
                        'recommended_version': recommended_ver,
                        'min_version': series_info['min_driver'],
                        'driver_series': driver_series,
                        'driver_info': driver_info,
                        'gpu_info': series_info
                    }
        
        return None
    
    def get_driver_features(self, driver_version: str) -> List[str]:
        """Get features available in a driver version"""
        driver_series = driver_version.split('.')[0]
        driver_info = self.driver_series.get(driver_series, {})
        
        return driver_info.get('features', [])
    
    def check_feature_support(self, feature_name: str, driver_version: str, gpu_model: str) -> Tuple[bool, str]:
        """Check if a feature is supported
        
        Returns:
            Tuple of (supported, message)
        """
        feature = self.features.get(feature_name)
        if not feature:
            return False, f"Feature '{feature_name}' not found"
        
        # Check driver version
        min_driver = feature.get('min_driver', '0.0')
        if self._compare_versions(driver_version, min_driver) < 0:
            return False, f"Driver {driver_version} is too old. Requires {min_driver} or newer"
        
        # Check GPU support
        min_gpu = feature.get('min_gpu', '')
        if min_gpu and not self._check_gpu_support(gpu_model, min_gpu):
            return False, f"GPU {gpu_model} does not support {feature_name}. Requires {min_gpu} or newer"
        
        return True, f"✓ {feature_name} is supported"
    
    def get_supported_features(self, driver_version: str, gpu_model: str) -> List[Dict]:
        """Get all features supported by driver and GPU combination"""
        supported = []
        
        for feature_name, feature_info in self.features.items():
            is_supported, msg = self.check_feature_support(feature_name, driver_version, gpu_model)
            
            if is_supported:
                supported.append({
                    'name': feature_name,
                    'full_name': feature_info['name'],
                    'description': feature_info.get('description', ''),
                    'message': msg
                })
        
        return supported
    
    def get_cuda_compatible_drivers(self, cuda_version: str) -> List[str]:
        """Get drivers compatible with a CUDA version"""
        compatible = []
        
        for series, info in self.driver_series.items():
            if cuda_version in info.get('cuda_support', []):
                compatible.append(f"{series}.x")
        
        return compatible
    
    def get_driver_info(self, driver_series: str) -> Optional[Dict]:
        """Get detailed information about a driver series"""
        return self.driver_series.get(driver_series)
    
    def is_wayland_supported(self, driver_version: str) -> bool:
        """Check if Wayland is supported"""
        driver_series = driver_version.split('.')[0]
        driver_info = self.driver_series.get(driver_series, {})
        
        return driver_info.get('wayland_supported', False)
    
    def is_gbm_supported(self, driver_version: str) -> bool:
        """Check if GBM (Generic Buffer Management) is supported"""
        driver_series = driver_version.split('.')[0]
        driver_info = self.driver_series.get(driver_series, {})
        
        return driver_info.get('gbm_supported', False)
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings"""
        v1_parts = [int(x) for x in re.findall(r'\d+', version1)]
        v2_parts = [int(x) for x in re.findall(r'\d+', version2)]
        
        # Pad to same length
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        else:
            return 0
    
    def _check_gpu_support(self, gpu_model: str, min_gpu: str) -> bool:
        """Check if GPU meets minimum requirement"""
        # Simplified check - in real implementation would check GPU hierarchy
        gpu_upper = gpu_model.upper()
        
        # Extract series from GPU model
        if 'RTX 50' in gpu_upper or 'RTX 5090' in gpu_upper or 'RTX 5080' in gpu_upper:
            gpu_gen = 50
        elif 'RTX 40' in gpu_upper or 'RTX 4090' in gpu_upper or 'RTX 4080' in gpu_upper:
            gpu_gen = 40
        elif 'RTX 30' in gpu_upper or 'RTX 3090' in gpu_upper or 'RTX 3080' in gpu_upper:
            gpu_gen = 30
        elif 'RTX 20' in gpu_upper or 'RTX 2080' in gpu_upper or 'RTX 2070' in gpu_upper:
            gpu_gen = 20
        elif 'GTX 16' in gpu_upper or 'GTX 1660' in gpu_upper or 'GTX 1650' in gpu_upper:
            gpu_gen = 16
        elif 'GTX 10' in gpu_upper or 'GTX 1080' in gpu_upper or 'GTX 1070' in gpu_upper:
            gpu_gen = 10
        else:
            return True  # Unknown, assume supported
        
        # Extract required series
        if 'RTX 50' in min_gpu:
            min_gen = 50
        elif 'RTX 40' in min_gpu:
            min_gen = 40
        elif 'RTX 30' in min_gpu:
            min_gen = 30
        elif 'RTX 20' in min_gpu:
            min_gen = 20
        elif 'GTX 16' in min_gpu:
            min_gen = 16
        elif 'GTX 10' in min_gpu:
            min_gen = 10
        else:
            return True
        
        return gpu_gen >= min_gen
