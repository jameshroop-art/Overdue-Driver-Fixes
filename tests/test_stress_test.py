"""
Test for driver stress testing functionality
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_stress_test_initialization():
    """Test DriverStressTest initialization"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {
        'name': 'Test GPU',
        'type': 'GPU',
        'vendor': 'NVIDIA'
    }
    
    stress_tester = DriverStressTest(test_hardware)
    
    assert stress_tester is not None
    assert stress_tester.hardware == test_hardware
    assert not stress_tester.is_running
    assert stress_tester.test_results['overall_status'] == 'not_started'
    
    print("✓ DriverStressTest initialization test passed")

def test_stress_test_config():
    """Test stress test configuration levels"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {'name': 'Test', 'type': 'GPU'}
    stress_tester = DriverStressTest(test_hardware)
    
    # Test all stress levels
    levels = ['light', 'medium', 'heavy', 'extreme']
    
    for level in levels:
        config = stress_tester._get_test_config(level)
        
        assert 'description' in config
        assert 'iterations' in config
        assert 'concurrency' in config
        assert config['iterations'] > 0
        
        print(f"  - {level.upper()}: {config['iterations']} iterations, "
              f"{config['concurrency']} concurrent, {config['delay_ms']}ms delay")
    
    # Heavy config should have more iterations than medium
    heavy = stress_tester._get_test_config('heavy')
    medium = stress_tester._get_test_config('medium')
    assert heavy['iterations'] > medium['iterations']
    
    print("✓ Stress test configuration test passed")

def test_15_minute_heavy_simulation():
    """Test 15-minute heavy load simulation (abbreviated for testing)"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {
        'name': 'NVIDIA GeForce RTX 3080',
        'type': 'GPU',
        'vendor': 'NVIDIA'
    }
    
    stress_tester = DriverStressTest(test_hardware)
    
    # Run abbreviated test (3 seconds instead of 15 minutes for testing)
    test_completed = False
    test_results = None
    
    def on_complete(results):
        nonlocal test_completed, test_results
        test_completed = True
        test_results = results
    
    # Start stress test with heavy load
    success = stress_tester.start_stress_test(
        duration_seconds=3,  # Abbreviated for testing
        stress_level='heavy',
        on_progress=None,
        on_complete=on_complete
    )
    
    assert success, "Stress test should start successfully"
    assert stress_tester.is_running, "Stress test should be running"
    
    # Wait for completion (with timeout)
    timeout = 5
    start = time.time()
    while not test_completed and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert test_completed, "Stress test should complete"
    assert test_results is not None, "Should have test results"
    assert test_results['overall_status'] == 'completed'
    assert test_results['stress_level'] == 'heavy'
    assert len(test_results['tests_performed']) > 0, "Should have performed tests"
    
    print(f"✓ 15-minute heavy load simulation test passed")
    print(f"  - Tests performed: {len(test_results['tests_performed'])}")
    print(f"  - Duration: {test_results['duration_seconds']:.2f}s")

def test_stress_test_results():
    """Test stress test results and reporting"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {
        'name': 'Test WiFi',
        'type': 'WiFi',
        'vendor': 'Intel'
    }
    
    stress_tester = DriverStressTest(test_hardware)
    
    # Run quick test
    test_completed = False
    
    def on_complete(results):
        nonlocal test_completed
        test_completed = True
    
    stress_tester.start_stress_test(
        duration_seconds=2,
        stress_level='medium',
        on_complete=on_complete
    )
    
    # Wait for completion
    timeout = 4
    start = time.time()
    while not test_completed and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    # Get results
    results = stress_tester.get_results()
    
    assert 'summary' in results
    assert 'total_tests' in results['summary']
    assert 'passed_tests' in results['summary']
    assert 'failed_tests' in results['summary']
    assert 'success_rate' in results['summary']
    
    # Generate report
    report = stress_tester.generate_report()
    
    assert 'Driver Stress Test Report' in report
    assert 'WiFi' in report or 'Test WiFi' in report
    assert 'medium' in report.lower()
    
    print("✓ Stress test results and reporting test passed")

def test_no_hardware_impact():
    """Verify stress test is simulated and doesn't impact hardware"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {
        'name': 'Test Device',
        'type': 'GPU',
        'vendor': 'Test'
    }
    
    stress_tester = DriverStressTest(test_hardware)
    
    # The _execute_test method should only sleep briefly and use random
    # This verifies it's simulated
    start = time.time()
    result = stress_tester._execute_test('Test', {'description': 'Heavy'})
    elapsed = time.time() - start
    
    # Should complete very quickly (< 10ms) since it's simulated
    assert elapsed < 0.01, f"Test took {elapsed}s - should be < 0.01s for simulation"
    assert isinstance(result, bool), "Should return boolean"
    
    print("✓ No hardware impact verification test passed")
    print(f"  - Test execution time: {elapsed*1000:.2f}ms (simulated)")

def test_stress_test_stop():
    """Test stopping stress test mid-execution"""
    from utils.driver_stress_test import DriverStressTest
    
    test_hardware = {'name': 'Test', 'type': 'CPU'}
    stress_tester = DriverStressTest(test_hardware)
    
    # Start test
    stress_tester.start_stress_test(
        duration_seconds=10,
        stress_level='light'
    )
    
    assert stress_tester.is_running
    
    # Stop after brief delay
    time.sleep(0.5)
    success = stress_tester.stop_stress_test()
    
    assert success, "Should successfully stop test"
    assert not stress_tester.is_running, "Should not be running after stop"
    assert stress_tester.test_results['overall_status'] == 'stopped'
    
    print("✓ Stress test stop functionality test passed")

def run_all_tests():
    """Run all stress test tests"""
    print("Running driver stress test tests...\n")
    
    tests = [
        test_stress_test_initialization,
        test_stress_test_config,
        test_15_minute_heavy_simulation,
        test_stress_test_results,
        test_no_hardware_impact,
        test_stress_test_stop,
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
