"""
Test connectivity and Ollama error handling fixes
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_connectivity_timeout_handling():
    """Test that connectivity checks handle timeouts properly"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test with PPA URL (should skip HTTP check)
    ppa_url = 'ppa:graphics-drivers/ppa'
    result = manager.check_source_connectivity(ppa_url)
    assert result == True, "PPA URLs should always return True (checked by package manager)"
    
    # Test with HTTP URL (should handle timeouts gracefully)
    http_url = 'https://developer.download.nvidia.com/compute/cuda/repos/'
    result = manager.check_source_connectivity(http_url)
    # Should return True even on timeout/error to allow installation attempt
    assert isinstance(result, bool), "Should return a boolean"
    
    print("✓ Connectivity timeout handling tests passed")

def test_ollama_404_handling():
    """Test that Ollama 404 errors are handled gracefully"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    
    # Test status check
    status = ollama.get_status()
    assert 'status' in status
    assert status['status'] in ['running', 'not_running', 'error']
    
    # If Ollama is not running, test error messages
    if status['status'] != 'running':
        result = ollama.analyze_text("test prompt")
        assert result['success'] == False
        assert 'error' in result
        assert 'Ollama not available' in result['error']
        print(f"✓ Ollama properly reports: {result['error']}")
    else:
        # If running but model not installed, should get helpful error
        result = ollama.analyze_text("test prompt")
        if not result['success'] and 'HTTP 404' in result.get('error', ''):
            # Check if we're providing helpful error message
            assert 'Model' in result['error'] or 'not found' in result['error']
            print(f"✓ Ollama provides helpful 404 error: {result['error']}")
        else:
            print(f"✓ Ollama is functional with model installed")
    
    print("✓ Ollama 404 handling tests passed")

def test_driver_source_connectivity():
    """Test driver source connectivity with improved error handling"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    # Test NVIDIA driver sources
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test GPU'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    assert len(drivers) > 0, "Should find NVIDIA drivers"
    
    # Verify that drivers have source connectivity status
    for driver in drivers:
        assert 'source_connected' in driver
        # Even if connection fails, should still have driver info
        assert 'name' in driver
        assert 'description' in driver
    
    print(f"✓ Driver source connectivity tests passed ({len(drivers)} drivers found)")

def run_all_tests():
    """Run all connectivity and error handling tests"""
    print("Running connectivity and Ollama error handling tests...\n")
    
    tests = [
        test_connectivity_timeout_handling,
        test_ollama_404_handling,
        test_driver_source_connectivity,
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
