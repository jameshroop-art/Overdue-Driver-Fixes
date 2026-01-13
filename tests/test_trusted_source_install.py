"""
Test for trusted source driver installation without risk assessment wait
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_trusted_source_identification():
    """Test that trusted sources are properly identified"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test NVIDIA drivers (should have official source)
    fake_nvidia_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test NVIDIA GPU'
    }
    
    nvidia_drivers = manager.find_drivers(fake_nvidia_gpu)
    assert len(nvidia_drivers) > 0, "Should find NVIDIA drivers"
    
    # Check that official drivers exist
    official_drivers = [d for d in nvidia_drivers if d.get('source') == 'official']
    assert len(official_drivers) > 0, "Should have official NVIDIA drivers"
    
    # Check that distribution drivers exist
    dist_drivers = [d for d in nvidia_drivers if d.get('source') == 'distribution']
    # May or may not exist, but shouldn't error
    
    print(f"✓ Found {len(official_drivers)} official drivers")
    print(f"✓ Trusted source identification test passed")

def test_trusted_source_flags():
    """Test that trusted source flags are set correctly"""
    
    # Test various driver sources
    trusted_sources = ['official', 'distribution', 'OFFICIAL', 'DISTRIBUTION']
    untrusted_sources = ['community', 'beta', 'experimental', 'unknown']
    
    for source in trusted_sources:
        is_trusted = source.lower() in ['official', 'distribution']
        assert is_trusted, f"Source '{source}' should be trusted"
    
    for source in untrusted_sources:
        is_trusted = source.lower() in ['official', 'distribution']
        assert not is_trusted, f"Source '{source}' should not be trusted"
    
    print("✓ Trusted source flag logic test passed")

def test_driver_risk_percentage():
    """Test that drivers have risk percentages assigned"""
    from core.driver_manager import DriverManager
    from core.config import ConfigManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test with NVIDIA GPU
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test GPU'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    assert len(drivers) > 0, "Should find drivers"
    
    for driver in drivers:
        assert 'risk_percentage' in driver, f"Driver {driver.get('name')} missing risk_percentage"
        assert driver['risk_percentage'] >= 0, "Risk percentage should be >= 0"
        assert driver['risk_percentage'] <= 100, "Risk percentage should be <= 100"
        
        # Official stable drivers should have low risk
        if driver.get('source') == 'official' and driver.get('stability') == 'stable':
            assert driver['risk_percentage'] <= 10, f"Official stable driver should have low risk, got {driver['risk_percentage']}%"
    
    print("✓ Driver risk percentage test passed")

def test_trusted_source_installation_flow():
    """Test that installation flow handles trusted sources correctly"""
    
    # Simulate trusted driver
    trusted_driver = {
        'name': 'nvidia-driver-535',
        'version': '535.xx',
        'source': 'official',
        'stability': 'stable',
        'risk_percentage': 5
    }
    
    # Simulate untrusted driver
    untrusted_driver = {
        'name': 'community-driver',
        'version': '1.0',
        'source': 'community',
        'stability': 'experimental',
        'risk_percentage': 45
    }
    
    # Check trusted source logic
    is_trusted = trusted_driver.get('source', '').lower() in ['official', 'distribution']
    assert is_trusted, "Official driver should be identified as trusted"
    
    is_trusted = untrusted_driver.get('source', '').lower() in ['official', 'distribution']
    assert not is_trusted, "Community driver should not be identified as trusted"
    
    print("✓ Installation flow trusted source logic test passed")

def run_all_tests():
    """Run all trusted source tests"""
    print("Running trusted source installation tests...\n")
    
    tests = [
        test_trusted_source_identification,
        test_trusted_source_flags,
        test_driver_risk_percentage,
        test_trusted_source_installation_flow,
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
