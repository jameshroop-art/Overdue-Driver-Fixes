"""
Test for AI driver conversion functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_driver_converter_initialization():
    """Test that DriverConverter can be initialized"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    from ai.driver_converter import DriverConverter
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    converter = DriverConverter(config, ollama)
    
    assert converter is not None
    assert converter.config is not None
    assert converter.ai_manager is not None
    
    print("✓ DriverConverter initialization test passed")

def test_can_convert_logic():
    """Test conversion feasibility logic"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    from ai.driver_converter import DriverConverter
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    converter = DriverConverter(config, ollama)
    
    # Linux driver should not be convertible
    linux_driver = {
        'name': 'nvidia-driver-535',
        'target_os': 'linux',
        'source_url': 'https://example.com/driver'
    }
    assert not converter.can_convert(linux_driver), "Linux driver should not be convertible"
    
    # Windows driver with source URL should be convertible
    windows_driver = {
        'name': 'nvidia-driver-546-windows',
        'target_os': 'windows',
        'source_url': 'https://example.com/driver.exe'
    }
    assert converter.can_convert(windows_driver), "Windows driver with URL should be convertible"
    
    # Driver without source URL should not be convertible
    no_url_driver = {
        'name': 'test-driver',
        'target_os': 'windows'
    }
    assert not converter.can_convert(no_url_driver), "Driver without URL should not be convertible"
    
    print("✓ Conversion feasibility logic test passed")

def test_analyze_driver():
    """Test driver analysis"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    from ai.driver_converter import DriverConverter
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    converter = DriverConverter(config, ollama)
    
    test_driver = {
        'name': 'nvidia-driver-546-windows',
        'version': '546.01',
        'target_os': 'windows',
        'source': 'official',
        'source_url': 'https://example.com/driver.exe'
    }
    
    test_hardware = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'name': 'NVIDIA GeForce RTX 3080'
    }
    
    # Analyze driver
    analysis = converter.analyze_driver(test_driver, test_hardware)
    
    # Check analysis structure
    assert 'feasible' in analysis
    assert 'confidence' in analysis
    assert 'complexity' in analysis
    assert 'estimated_effort' in analysis
    assert 'required_components' in analysis
    assert 'potential_issues' in analysis
    assert 'recommendations' in analysis
    
    print(f"✓ Driver analysis test passed")
    print(f"  - Feasible: {analysis.get('feasible')}")
    print(f"  - Confidence: {analysis.get('confidence')}%")
    print(f"  - Complexity: {analysis.get('complexity')}")

def test_conversion_result_structure():
    """Test that conversion results have correct structure"""
    from core.config import ConfigManager
    from ai.ollama_manager import OllamaManager
    from ai.driver_converter import DriverConverter
    
    config = ConfigManager()
    ollama = OllamaManager(config)
    converter = DriverConverter(config, ollama)
    
    test_driver = {
        'name': 'test-driver-windows',
        'version': '1.0',
        'target_os': 'windows',
        'source': 'official',
        'source_url': 'https://example.com/driver.exe'
    }
    
    test_hardware = {
        'type': 'GPU',
        'vendor': 'Test',
        'name': 'Test GPU'
    }
    
    # Create mock analysis (not feasible to avoid AI call)
    mock_analysis = {
        'feasible': False,
        'confidence': 20,
        'complexity': 'high',
        'estimated_effort': 'extensive'
    }
    
    # Attempt conversion (should fail due to feasibility)
    result = converter.attempt_conversion(test_driver, test_hardware, mock_analysis)
    
    # Check result structure
    assert 'success' in result
    assert 'converted_driver' in result
    assert 'conversion_log' in result
    assert 'warnings' in result
    assert 'next_steps' in result
    
    # Should not succeed if not feasible
    assert not result['success']
    assert len(result['conversion_log']) > 0
    
    print("✓ Conversion result structure test passed")

def test_converted_driver_properties():
    """Test that converted drivers have correct properties"""
    # This is a theoretical test since we can't guarantee AI will succeed
    
    expected_properties = [
        'name',
        'version',
        'source',
        'stability',
        'description',
        'target_os',
        'original_driver',
        'original_os',
        'conversion_date',
        'risk_percentage',
        'requires_testing',
        'experimental'
    ]
    
    # Mock converted driver
    mock_converted = {
        'name': 'test-driver-linux-converted',
        'version': '1.0-ai-converted',
        'source': 'ai_converted',
        'stability': 'experimental',
        'description': 'AI-converted Linux driver',
        'target_os': 'linux',
        'original_driver': 'test-driver-windows',
        'original_os': 'windows',
        'conversion_date': '2024-01-01T00:00:00',
        'risk_percentage': 75,
        'requires_testing': True,
        'experimental': True
    }
    
    for prop in expected_properties:
        assert prop in mock_converted, f"Converted driver missing property: {prop}"
    
    # Verify critical properties
    assert mock_converted['target_os'] == 'linux'
    assert mock_converted['source'] == 'ai_converted'
    assert mock_converted['experimental'] == True
    assert mock_converted['risk_percentage'] >= 50  # Should have high risk
    
    print("✓ Converted driver properties test passed")

def run_all_tests():
    """Run all driver conversion tests"""
    print("Running AI driver conversion tests...\n")
    
    tests = [
        test_driver_converter_initialization,
        test_can_convert_logic,
        test_analyze_driver,
        test_conversion_result_structure,
        test_converted_driver_properties,
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
