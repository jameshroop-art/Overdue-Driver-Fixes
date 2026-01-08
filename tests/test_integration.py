#!/usr/bin/env python3
"""
Integration test to verify GUI and program components work together
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from core.config import ConfigManager
        print("  ✓ ConfigManager")
    except ImportError as e:
        print(f"  ✗ ConfigManager: {e}")
        return False
    
    try:
        from core.hardware_detector import HardwareDetector
        print("  ✓ HardwareDetector")
    except ImportError as e:
        print(f"  ✗ HardwareDetector: {e}")
        return False
    
    try:
        from core.driver_manager import DriverManager
        print("  ✓ DriverManager")
    except ImportError as e:
        print(f"  ✗ DriverManager: {e}")
        return False
    
    try:
        from core.risk_assessor import RiskAssessor
        print("  ✓ RiskAssessor")
    except ImportError as e:
        print(f"  ✗ RiskAssessor: {e}")
        return False
    
    try:
        from ai.ollama_manager import OllamaManager
        print("  ✓ OllamaManager")
    except ImportError as e:
        print(f"  ✗ OllamaManager: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        print("  ✓ Logger")
    except ImportError as e:
        print(f"  ✗ Logger: {e}")
        return False
    
    try:
        from utils.venv_manager import get_venv_info
        print("  ✓ VenvManager")
    except ImportError as e:
        print(f"  ✗ VenvManager: {e}")
        return False
    
    # GUI imports (may not be available if PyQt6 not installed)
    try:
        import PyQt6
        from gui.main_window import MainWindow
        from gui.device_tab import DeviceTab
        print("  ✓ GUI modules (PyQt6 available)")
    except ImportError as e:
        print(f"  ⚠ GUI modules unavailable (PyQt6 not installed)")
        # Not a failure - GUI optional for CLI mode
    
    return True


def test_component_integration():
    """Test that components can be initialized and work together"""
    print("\nTesting component integration...")
    
    from core.config import ConfigManager
    from core.hardware_detector import HardwareDetector
    from core.driver_manager import DriverManager
    from ai.ollama_manager import OllamaManager
    from core.risk_assessor import RiskAssessor
    
    try:
        # Initialize config
        config = ConfigManager()
        print("  ✓ ConfigManager initialized")
        
        # Initialize hardware detector
        detector = HardwareDetector(config)
        print("  ✓ HardwareDetector initialized")
        
        # Initialize driver manager
        driver_mgr = DriverManager(config)
        print("  ✓ DriverManager initialized")
        
        # Initialize Ollama manager
        ollama = OllamaManager(config)
        print("  ✓ OllamaManager initialized")
        
        # Initialize risk assessor
        risk_assessor = RiskAssessor(config, ollama)
        print("  ✓ RiskAssessor initialized")
        
        # Test integration: detect hardware -> find drivers -> assess risk
        print("\n  Testing workflow integration:")
        hardware = detector.detect_all()
        print(f"    ✓ Detected {len(hardware)} hardware components")
        
        if hardware:
            sample_hw = hardware[0]
            drivers = driver_mgr.find_drivers(sample_hw)
            print(f"    ✓ Found {len(drivers)} drivers for {sample_hw['type']}")
            
            risk = risk_assessor.assess_hardware(sample_hw)
            print(f"    ✓ Risk assessed: {risk['risk_percentage']}%")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_initialization():
    """Test that GUI can be initialized (if PyQt6 available)"""
    print("\nTesting GUI initialization...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        from core.config import ConfigManager
        
        # Create application (without showing window)
        app = QApplication([])
        
        # Initialize config
        config = ConfigManager()
        
        # Create main window (don't show)
        window = MainWindow(config)
        print("  ✓ MainWindow created successfully")
        
        # Check that expected components exist
        assert hasattr(window, 'tabs'), "MainWindow missing tabs"
        assert hasattr(window, 'hardware_table'), "MainWindow missing hardware_table"
        assert hasattr(window, 'statusBar'), "MainWindow missing statusBar"
        print("  ✓ MainWindow has expected components")
        
        # Clean up
        app.quit()
        
        return True
        
    except ImportError:
        print("  ⚠ PyQt6 not available, skipping GUI test")
        return True  # Not a failure
    except Exception as e:
        print(f"  ✗ GUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_installation_structure():
    """Test that installation directories and files are properly set up"""
    print("\nTesting installation structure...")
    
    from core.config import ConfigManager
    
    config = ConfigManager()
    
    # Check config directories
    config_dir = config.get_config_dir()
    if not config_dir.exists():
        print(f"  ✗ Config directory not found: {config_dir}")
        return False
    print(f"  ✓ Config directory exists: {config_dir}")
    
    # Check subdirectories
    subdirs = ['profiles', 'curves', 'logs', 'corrections', 'reports']
    for subdir in subdirs:
        subdir_path = config_dir / subdir
        if not subdir_path.exists():
            print(f"  ✗ Subdirectory missing: {subdir}")
            return False
        print(f"  ✓ Subdirectory exists: {subdir}")
    
    # Check config files are created
    if not (config_dir / 'config.json').exists():
        print("  ⚠ config.json not yet created (will be created on first use)")
    else:
        print("  ✓ config.json exists")
    
    if not (config_dir / 'ai-config.json').exists():
        print("  ⚠ ai-config.json not yet created (will be created on first use)")
    else:
        print("  ✓ ai-config.json exists")
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("Driver-mgt Integration Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Component Integration", test_component_integration),
        ("GUI Initialization", test_gui_initialization),
        ("Installation Structure", test_installation_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Test: {test_name}")
        print('=' * 60)
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} PASSED")
            else:
                failed += 1
                print(f"\n✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
