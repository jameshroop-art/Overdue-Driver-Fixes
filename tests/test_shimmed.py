"""
Test shimmed driver installation indicator
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_nvidia_driver_shimmed():
    """Test that NVIDIA drivers have shimmed flag set to False"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test finding drivers for fake NVIDIA GPU
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'GeForce RTX 3090'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    assert isinstance(drivers, list)
    assert len(drivers) > 0
    
    # Find nvidia-driver-535
    nvidia_535 = None
    for driver in drivers:
        if driver['name'] == 'nvidia-driver-535':
            nvidia_535 = driver
            break
    
    assert nvidia_535 is not None, "nvidia-driver-535 not found"
    assert 'shimmed' in nvidia_535, "shimmed flag not present"
    assert not nvidia_535['shimmed'], "nvidia-driver-535 should not be shimmed"
    assert 'glvnd' in nvidia_535, "glvnd flag not present"
    assert not nvidia_535['glvnd'], "nvidia-driver-535 should not use GLVND"
    
    print("✓ NVIDIA driver shimmed flag test passed")
    print(f"  nvidia-driver-535: shimmed={nvidia_535['shimmed']}, glvnd={nvidia_535['glvnd']}")

def test_install_driver_output():
    """Test that install_driver displays shimmed status as No"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    import io
    import contextlib
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test driver data
    driver = {
        'name': 'nvidia-driver-535',
        'version': '535.xx',
        'shimmed': False,
        'glvnd': False
    }
    
    hardware = {
        'name': 'GeForce RTX 3090',
        'type': 'GPU',
        'vendor': 'NVIDIA'
    }
    
    # Capture output
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = manager.install_driver(driver, hardware)
    
    output = f.getvalue()
    
    assert result, "install_driver should return True"
    assert "Would install driver: nvidia-driver-535" in output, "Missing driver name in output"
    assert "GeForce RTX 3090" in output, "Missing hardware name in output"
    assert "Is this installation shimmed?" in output, "Missing shimmed question in output"
    assert "No" in output, "Should show No for shimmed status"
    
    print("✓ install_driver output test passed")
    print(f"  Output: {output.strip()}")

def test_nouveau_not_shimmed():
    """Test that nouveau driver is not shimmed"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test finding drivers for fake NVIDIA GPU
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test GPU'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    
    # Find nouveau
    nouveau = None
    for driver in drivers:
        if driver['name'] == 'nouveau':
            nouveau = driver
            break
    
    assert nouveau is not None, "nouveau not found"
    assert 'shimmed' in nouveau, "shimmed flag not present"
    assert not nouveau['shimmed'], "nouveau should not be shimmed"
    
    print("✓ nouveau not shimmed test passed")
    print(f"  nouveau: shimmed={nouveau['shimmed']}")

def test_amd_drivers_shimmed():
    """Test that AMD drivers are not shimmed"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test finding drivers for fake AMD GPU
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'AMD',
        'name': 'Radeon RX 6800'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    assert isinstance(drivers, list)
    assert len(drivers) > 0
    
    # Check all AMD drivers are not shimmed
    for driver in drivers:
        assert 'shimmed' in driver, f"shimmed flag not present in {driver['name']}"
        assert not driver['shimmed'], f"{driver['name']} should not be shimmed"
    
    print("✓ AMD drivers not shimmed test passed")

def run_all_tests():
    """Run all shimmed tests"""
    print("Running shimmed driver tests...\n")
    
    tests = [
        test_nvidia_driver_shimmed,
        test_install_driver_output,
        test_nouveau_not_shimmed,
        test_amd_drivers_shimmed,
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
