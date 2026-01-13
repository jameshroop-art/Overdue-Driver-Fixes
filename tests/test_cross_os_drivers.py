"""
Test for cross-OS driver discovery and download functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import constants
from core.driver_manager import RISK_OFFICIAL_STABLE

# Test fixtures
FAKE_NVIDIA_GPU = {
    'type': 'GPU',
    'vendor': 'NVIDIA',
    'name': 'Test NVIDIA GPU'
}

FAKE_AMD_GPU = {
    'type': 'GPU',
    'vendor': 'AMD',
    'name': 'Test AMD GPU'
}

def test_linux_only_drivers():
    """Test that only Linux drivers are returned by default"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Get drivers without cross-OS
    nvidia_drivers = manager.find_drivers(FAKE_NVIDIA_GPU, include_cross_os=False)
    
    # All drivers should be Linux
    for driver in nvidia_drivers:
        target_os = driver.get('target_os', 'linux').lower()
        assert target_os == 'linux', f"Driver {driver.get('name')} should be Linux-only, got {target_os}"
    
    print(f"✓ Linux-only mode returned {len(nvidia_drivers)} Linux drivers")

def test_cross_os_drivers_nvidia():
    """Test that Windows drivers are included when requested"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Get drivers with cross-OS
    all_drivers = manager.find_drivers(FAKE_NVIDIA_GPU, include_cross_os=True)
    
    # Should have both Linux and Windows drivers
    linux_drivers = [d for d in all_drivers if d.get('target_os', 'linux').lower() == 'linux']
    windows_drivers = [d for d in all_drivers if d.get('target_os', '').lower() == 'windows']
    
    assert len(linux_drivers) > 0, "Should have Linux drivers"
    assert len(windows_drivers) > 0, "Should have Windows drivers when include_cross_os=True"
    
    print(f"✓ Cross-OS mode returned {len(linux_drivers)} Linux and {len(windows_drivers)} Windows drivers")

def test_cross_os_drivers_amd():
    """Test that AMD Windows drivers are included"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Get drivers with cross-OS
    all_drivers = manager.find_drivers(FAKE_AMD_GPU, include_cross_os=True)
    
    # Should have both Linux and Windows drivers
    windows_drivers = [d for d in all_drivers if d.get('target_os', '').lower() == 'windows']
    
    assert len(windows_drivers) > 0, "Should have AMD Windows drivers"
    
    print(f"✓ AMD cross-OS mode returned {len(windows_drivers)} Windows driver(s)")

def test_cross_os_driver_properties():
    """Test that cross-OS drivers have correct properties"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Get drivers with cross-OS
    all_drivers = manager.find_drivers(FAKE_NVIDIA_GPU, include_cross_os=True)
    windows_drivers = [d for d in all_drivers if d.get('target_os', '').lower() == 'windows']
    
    for driver in windows_drivers:
        # Windows drivers should be marked as download-only
        assert driver.get('download_only') == True, f"Windows driver {driver.get('name')} should be download-only"
        
        # Should have compatibility note
        assert 'compatibility_note' in driver, f"Windows driver {driver.get('name')} missing compatibility note"
        
        # Should have source URL
        assert 'source_url' in driver, f"Windows driver {driver.get('name')} missing source URL"
        
        # Should have higher risk percentage
        risk = driver.get('risk_percentage', 0)
        assert risk >= 50, f"Windows driver {driver.get('name')} should have risk >= 50%, got {risk}%"
    
    print("✓ Cross-OS drivers have correct properties (download-only, compatibility notes, higher risk)")

def test_target_os_field():
    """Test that all drivers have target_os field"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test with multiple hardware types
    test_hardware = [
        FAKE_NVIDIA_GPU,
        FAKE_AMD_GPU,
        {'type': 'GPU', 'vendor': 'Intel', 'name': 'Test Intel GPU'},
    ]
    
    for hw in test_hardware:
        # Get drivers with cross-OS
        all_drivers = manager.find_drivers(hw, include_cross_os=True)
        
        for driver in all_drivers:
            assert 'target_os' in driver, f"Driver {driver.get('name')} missing target_os field"
            target_os = driver.get('target_os', '').lower()
            assert target_os in ['linux', 'windows', 'macos'], \
                f"Driver {driver.get('name')} has invalid target_os: {target_os}"
    
    print("✓ All drivers have valid target_os field")

def test_risk_calculation_cross_os():
    """Test that cross-OS drivers get higher risk scores"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Get both Linux and cross-OS drivers
    all_drivers = manager.find_drivers(FAKE_NVIDIA_GPU, include_cross_os=True)
    
    linux_drivers = [d for d in all_drivers if d.get('target_os', 'linux').lower() == 'linux']
    windows_drivers = [d for d in all_drivers if d.get('target_os', '').lower() == 'windows']
    
    # Official stable Linux drivers should have low risk
    linux_official_stable = [d for d in linux_drivers 
                             if d.get('source') == 'official' and d.get('stability') == 'stable']
    
    for driver in linux_official_stable:
        risk = driver.get('risk_percentage', 0)
        assert risk <= RISK_OFFICIAL_STABLE, \
            f"Linux official stable driver should have low risk, got {risk}%"
    
    # Windows drivers should have higher risk
    for driver in windows_drivers:
        risk = driver.get('risk_percentage', 0)
        assert risk >= 50, f"Windows driver should have risk >= 50%, got {risk}%"
    
    print("✓ Risk calculation correctly assigns higher risk to cross-OS drivers")

def run_all_tests():
    """Run all cross-OS driver tests"""
    print("Running cross-OS driver discovery tests...\n")
    
    tests = [
        test_linux_only_drivers,
        test_cross_os_drivers_nvidia,
        test_cross_os_drivers_amd,
        test_cross_os_driver_properties,
        test_target_os_field,
        test_risk_calculation_cross_os,
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
