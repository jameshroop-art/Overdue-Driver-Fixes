"""
Basic tests for driver-mgt
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_manager():
    """Test ConfigManager"""
    from core.config import ConfigManager
    
    config = ConfigManager()
    assert config is not None
    assert config.config is not None
    assert config.ai_config is not None
    
    # Test getting values
    log_level = config.get('general.log_level', 'INFO')
    assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    
    # Test AI config
    model = config.get_ai('monitoring.model', 'starcoder:3b')
    assert model == 'starcoder:3b'
    
    print("✓ ConfigManager tests passed")

def test_hardware_detector():
    """Test HardwareDetector"""
    from core.config import ConfigManager
    from core.hardware_detector import HardwareDetector
    
    config = ConfigManager()
    detector = HardwareDetector(config)
    
    assert detector is not None
    
    # Try to detect hardware (may not find anything in test environment)
    hardware = detector.detect_all()
    assert isinstance(hardware, list)
    
    print(f"✓ HardwareDetector tests passed (found {len(hardware)} devices)")

def test_driver_manager():
    """Test DriverManager"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    manager = DriverManager(config)
    
    assert manager is not None
    
    # Test finding drivers for fake NVIDIA GPU
    fake_gpu = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test GPU'
    }
    
    drivers = manager.find_drivers(fake_gpu)
    assert isinstance(drivers, list)
    assert len(drivers) > 0
    
    print(f"✓ DriverManager tests passed (found {len(drivers)} drivers)")

def test_risk_assessor():
    """Test RiskAssessor"""
    from core.config import ConfigManager
    from core.risk_assessor import RiskAssessor
    
    config = ConfigManager()
    assessor = RiskAssessor(config)
    
    assert assessor is not None
    
    # Test risk assessment for fake hardware
    fake_hardware = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'Test GPU',
        'driver': 'nvidia'
    }
    
    risk = assessor.assess_hardware(fake_hardware)
    assert 'risk_percentage' in risk
    assert 'risk_level' in risk
    assert risk['risk_percentage'] >= 0
    assert risk['risk_percentage'] <= 100
    
    print(f"✓ RiskAssessor tests passed (risk: {risk['risk_percentage']}%)")

def test_ollama_manager():
    """Test OllamaManager"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    
    assert ollama is not None
    
    # Test getting status (may not be running)
    status = ollama.get_status()
    assert 'status' in status
    assert status['status'] in ['running', 'not_running', 'error']
    
    print(f"✓ OllamaManager tests passed (status: {status['status']})")

def run_all_tests():
    """Run all tests"""
    print("Running driver-mgt tests...\n")
    
    tests = [
        test_config_manager,
        test_hardware_detector,
        test_driver_manager,
        test_risk_assessor,
        test_ollama_manager,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\nTests: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
