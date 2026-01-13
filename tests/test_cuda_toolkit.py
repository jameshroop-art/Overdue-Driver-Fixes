"""
Test suite for CUDA Toolkit management and compatibility
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.cuda_toolkit_manager import CudaToolkitManager

def test_cuda_manager_initialization():
    """Test CUDA manager initializes correctly"""
    manager = CudaToolkitManager()
    
    assert manager is not None
    assert len(manager.cuda_versions) > 0
    assert len(manager.gpu_capabilities) > 0
    
    print("✓ CUDA manager initialization test passed")

def test_driver_compatibility():
    """Test driver version compatibility checking"""
    manager = CudaToolkitManager()
    
    # Test with driver 550.54.14 (should support CUDA 12.4)
    compatible = manager.get_compatible_cuda_versions('550.54.14', 'linux')
    
    assert len(compatible) > 0
    assert any(c['cuda_version'] == '12.4' for c in compatible)
    
    print("✓ Driver compatibility test passed")
    print(f"  - Found {len(compatible)} compatible CUDA versions for driver 550.54.14")

def test_cuda_compatibility_check():
    """Test CUDA version compatibility with driver"""
    manager = CudaToolkitManager()
    
    # CUDA 12.4 requires driver 550.54.14 or newer
    is_compat, msg = manager.is_cuda_compatible('12.4', '550.54.14', 'linux')
    assert is_compat is True
    
    # Driver too old
    is_compat, msg = manager.is_cuda_compatible('12.4', '525.60.13', 'linux')
    assert is_compat is False
    
    print("✓ CUDA compatibility check test passed")

def test_gpu_compute_capability():
    """Test GPU compute capability detection"""
    manager = CudaToolkitManager()
    
    # Test known GPUs
    rtx3090_cap = manager.get_gpu_compute_capability('RTX 3090')
    assert rtx3090_cap == '8.6'
    
    rtx4090_cap = manager.get_gpu_compute_capability('RTX 4090')
    assert rtx4090_cap == '8.9'
    
    h100_cap = manager.get_gpu_compute_capability('H100')
    assert h100_cap == '9.0'
    
    print("✓ GPU compute capability test passed")
    print(f"  - RTX 3090: {rtx3090_cap}")
    print(f"  - RTX 4090: {rtx4090_cap}")
    print(f"  - H100: {h100_cap}")

def test_cuda_for_gpu():
    """Test getting CUDA recommendations for specific GPU"""
    manager = CudaToolkitManager()
    
    # Get CUDA versions for RTX 3090 with driver 550.54.14
    recommendations = manager.get_cuda_for_gpu('RTX 3090', '550.54.14', 'linux')
    
    assert len(recommendations) > 0
    
    # Should have recommended versions
    recommended = [r for r in recommendations if r.get('recommended', False)]
    assert len(recommended) > 0
    
    print("✓ CUDA for GPU test passed")
    print(f"  - Found {len(recommendations)} compatible CUDA versions")
    print(f"  - {len(recommended)} recommended for RTX 3090")

def test_latest_cuda():
    """Test getting latest compatible CUDA version"""
    manager = CudaToolkitManager()
    
    latest = manager.get_latest_cuda_for_driver('560.28.03', 'linux')
    
    assert latest is not None
    assert 'cuda_version' in latest
    
    print("✓ Latest CUDA test passed")
    print(f"  - Latest CUDA for driver 560.28.03: {latest['cuda_version']}")

def test_cuda_versions_list():
    """Test getting all CUDA versions"""
    manager = CudaToolkitManager()
    
    versions = manager.get_all_cuda_versions()
    
    assert len(versions) > 0
    assert '12.6' in versions or '12.5' in versions or '12.4' in versions
    
    print("✓ CUDA versions list test passed")
    print(f"  - Total CUDA versions available: {len(versions)}")
    print(f"  - Latest version: {versions[0]}")

def test_cuda_info():
    """Test getting detailed CUDA information"""
    manager = CudaToolkitManager()
    
    info = manager.get_cuda_info('12.4')
    
    assert info is not None
    assert 'min_driver_linux' in info
    assert 'release_date' in info
    assert 'features' in info
    assert 'architectures' in info
    
    print("✓ CUDA info test passed")
    print(f"  - CUDA 12.4 min driver: {info['min_driver_linux']}")
    print(f"  - Release date: {info['release_date']}")
    print(f"  - Architectures: {', '.join(info['architectures'])}")

def test_version_comparison():
    """Test version comparison logic"""
    manager = CudaToolkitManager()
    
    # Test version comparisons
    assert manager._compare_versions('550.54.14', '545.23.06') > 0
    assert manager._compare_versions('525.60.13', '550.54.14') < 0
    assert manager._compare_versions('550.54.14', '550.54.14') == 0
    
    print("✓ Version comparison test passed")

def test_windows_compatibility():
    """Test Windows driver compatibility"""
    manager = CudaToolkitManager()
    
    # Test Windows driver compatibility
    compatible = manager.get_compatible_cuda_versions('551.61', 'windows')
    
    assert len(compatible) > 0
    
    print("✓ Windows compatibility test passed")
    print(f"  - Found {len(compatible)} compatible CUDA versions for Windows driver")

def test_rtx_5090_support():
    """Test RTX 5090 support"""
    manager = CudaToolkitManager()
    
    # RTX 5090 should have compute capability
    cap = manager.get_gpu_compute_capability('RTX 5090')
    
    assert cap is not None
    print(f"✓ RTX 5090 support test passed")
    print(f"  - RTX 5090 compute capability: {cap}")

def run_all_tests():
    """Run all CUDA toolkit tests"""
    print("Running CUDA Toolkit Manager tests...\n")
    
    tests = [
        test_cuda_manager_initialization,
        test_driver_compatibility,
        test_cuda_compatibility_check,
        test_gpu_compute_capability,
        test_cuda_for_gpu,
        test_latest_cuda,
        test_cuda_versions_list,
        test_cuda_info,
        test_version_comparison,
        test_windows_compatibility,
        test_rtx_5090_support,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\nTests: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
