"""
Test for driver backup and timer safety features
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_backup_manager_initialization():
    """Test DriverBackupManager initialization"""
    from utils.driver_backup import DriverBackupManager
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        assert backup_manager is not None
        assert backup_manager.backup_dir.exists()
        
        print("✓ DriverBackupManager initialization test passed")

def test_create_backup():
    """Test creating driver backup"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': 'Test GPU',
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'id': 'test-001',
            'driver': 'nvidia-driver-535'
        }
        
        test_driver = {
            'name': 'nvidia-driver-535',
            'version': '535.xx',
            'source': 'official',
            'stability': 'stable'
        }
        
        # Create backup
        backup_path = backup_manager.create_backup(test_hardware, test_driver)
        
        # Verify backup file exists
        assert os.path.exists(backup_path), f"Backup file should exist: {backup_path}"
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert 'backup_date' in backup_data
        assert 'hardware' in backup_data
        assert 'driver' in backup_data
        assert backup_data['hardware']['name'] == 'Test GPU'
        assert backup_data['driver']['name'] == 'nvidia-driver-535'
        
        print(f"✓ Create backup test passed")
        print(f"  - Backup file: {os.path.basename(backup_path)}")
        print(f"  - Hardware: {backup_data['hardware']['name']}")
        print(f"  - Driver: {backup_data['driver']['name']}")

def test_get_latest_backup():
    """Test retrieving latest backup"""
    from utils.driver_backup import DriverBackupManager
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': 'Test GPU',
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'id': 'test-001'
        }
        
        # Create multiple backups
        backup_manager.create_backup(test_hardware, {'name': 'driver-v1', 'version': '1.0'})
        time.sleep(0.1)
        backup_manager.create_backup(test_hardware, {'name': 'driver-v2', 'version': '2.0'})
        time.sleep(0.1)
        backup_manager.create_backup(test_hardware, {'name': 'driver-v3', 'version': '3.0'})
        
        # Get latest backup
        latest = backup_manager.get_latest_backup(test_hardware)
        
        assert latest is not None
        assert latest['driver']['name'] == 'driver-v3', "Should return most recent backup"
        
        print("✓ Get latest backup test passed")
        print(f"  - Latest driver: {latest['driver']['name']}")

def test_test_timer_initialization():
    """Test DriverTestTimer initialization"""
    from utils.driver_test_timer import DriverTestTimer
    
    timer = DriverTestTimer(test_duration_minutes=5)
    
    assert timer is not None
    assert timer.test_duration_minutes == 5
    assert timer.test_duration_seconds == 300
    assert not timer.is_test_active()
    
    print("✓ DriverTestTimer initialization test passed")

def test_timer_remaining_time():
    """Test timer remaining time calculation"""
    from utils.driver_test_timer import DriverTestTimer
    
    timer = DriverTestTimer(test_duration_minutes=5)
    
    # Initially no active test
    minutes, seconds = timer.get_remaining_time()
    assert minutes == 0 and seconds == 0, "Should return (0, 0) when no test active"
    
    print("✓ Timer remaining time test passed")

def test_backup_file_naming():
    """Test that backup files include driver name and timestamp"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': 'NVIDIA GeForce RTX 3080',
            'type': 'GPU',
            'vendor': 'NVIDIA'
        }
        
        test_driver = {
            'name': 'nvidia-driver-545',
            'version': '545.29'
        }
        
        backup_path = backup_manager.create_backup(test_hardware, test_driver)
        filename = os.path.basename(backup_path)
        
        # Check filename contains hardware and driver name
        assert 'NVIDIA' in filename or 'GeForce' in filename or 'RTX' in filename
        assert 'nvidia-driver' in filename or 'nvidia' in filename
        assert filename.endswith('.json')
        
        # Check that timestamp is in filename (YYYYMMDD_HHMMSS format)
        assert any(char.isdigit() for char in filename), "Filename should contain timestamp"
        
        print(f"✓ Backup file naming test passed")
        print(f"  - Filename: {filename}")

def test_restore_driver_method():
    """Test that driver_manager has restore_driver method"""
    from core.config import ConfigManager
    from core.driver_manager import DriverManager
    
    config = ConfigManager()
    driver_manager = DriverManager(config)
    
    # Check method exists
    assert hasattr(driver_manager, 'restore_driver'), "DriverManager should have restore_driver method"
    
    # Test restore with dummy data
    test_driver = {
        'name': 'test-driver',
        'version': '1.0'
    }
    
    test_hardware = {
        'name': 'Test Device',
        'type': 'GPU'
    }
    
    # Should not crash
    result = driver_manager.restore_driver(test_driver, test_hardware)
    assert isinstance(result, bool), "restore_driver should return boolean"
    
    print("✓ Restore driver method test passed")

def run_all_tests():
    """Run all backup and timer tests"""
    print("Running driver backup and timer safety tests...\n")
    
    tests = [
        test_backup_manager_initialization,
        test_create_backup,
        test_get_latest_backup,
        test_test_timer_initialization,
        test_timer_remaining_time,
        test_backup_file_naming,
        test_restore_driver_method,
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
