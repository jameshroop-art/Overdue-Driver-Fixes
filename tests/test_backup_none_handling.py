"""
Test for NoneType error handling in driver backup system
Tests the fix for: 'NoneType' object has no attribute 'replace'
"""

import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_backup_with_none_hardware_name():
    """Test that create_backup handles None hardware name"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        # Hardware with None name (this is the bug scenario)
        test_hardware = {
            'name': None,  # This causes 'NoneType' object has no attribute 'replace'
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'id': 'test-001'
        }
        
        test_driver = {
            'name': 'test-driver',
            'version': '1.0',
            'source': 'official'
        }
        
        # This should NOT raise AttributeError
        try:
            backup_path = backup_manager.create_backup(test_hardware, test_driver)
            assert os.path.exists(backup_path), "Backup file should be created"
            print("✓ create_backup handles None hardware name")
        except AttributeError as e:
            print(f"✗ create_backup failed with None hardware name: {e}")
            raise

def test_backup_with_none_driver_name():
    """Test that create_backup handles None driver name"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': 'Test GPU',
            'type': 'GPU',
            'vendor': 'NVIDIA'
        }
        
        # Driver with None name
        test_driver = {
            'name': None,  # This could also cause the error
            'version': '1.0'
        }
        
        # This should NOT raise AttributeError
        try:
            backup_path = backup_manager.create_backup(test_hardware, test_driver)
            assert os.path.exists(backup_path), "Backup file should be created"
            print("✓ create_backup handles None driver name")
        except AttributeError as e:
            print(f"✗ create_backup failed with None driver name: {e}")
            raise

def test_get_latest_backup_with_none_hardware_name():
    """Test that get_latest_backup handles None hardware name"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': None,  # This causes the error
            'type': 'GPU'
        }
        
        # This should NOT raise AttributeError
        try:
            latest = backup_manager.get_latest_backup(test_hardware)
            # It's OK if there's no backup (returns None)
            print("✓ get_latest_backup handles None hardware name")
        except AttributeError as e:
            print(f"✗ get_latest_backup failed with None hardware name: {e}")
            raise

def test_list_backups_with_none_hardware_name():
    """Test that list_backups handles None hardware name"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': None,  # This causes the error
            'type': 'GPU'
        }
        
        # This should NOT raise AttributeError
        try:
            backups = backup_manager.list_backups(test_hardware)
            assert isinstance(backups, list), "Should return a list"
            print("✓ list_backups handles None hardware name")
        except AttributeError as e:
            print(f"✗ list_backups failed with None hardware name: {e}")
            raise

def test_backup_with_missing_hardware_name():
    """Test that create_backup handles missing hardware name key"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        # Hardware with missing name key
        test_hardware = {
            'type': 'GPU',
            'vendor': 'NVIDIA'
        }
        
        test_driver = {
            'name': 'test-driver',
            'version': '1.0'
        }
        
        # This should work with default 'unknown'
        try:
            backup_path = backup_manager.create_backup(test_hardware, test_driver)
            assert os.path.exists(backup_path), "Backup file should be created"
            assert 'unknown' in os.path.basename(backup_path), "Should use 'unknown' as hardware name"
            print("✓ create_backup handles missing hardware name key")
        except Exception as e:
            print(f"✗ create_backup failed with missing hardware name: {e}")
            raise

def test_backup_none_driver_with_none_current_driver():
    """Test backup when current_driver is None (as returned by get_current_driver)"""
    from utils.driver_backup import DriverBackupManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_manager = DriverBackupManager(backup_dir=tmpdir)
        
        test_hardware = {
            'name': 'Test GPU',
            'type': 'GPU',
            'driver': 'test-driver'  # This is used as fallback
        }
        
        # current_driver is None (this is what get_current_driver returns sometimes)
        current_driver = None
        
        # This should work - create_backup handles None driver
        try:
            backup_path = backup_manager.create_backup(test_hardware, current_driver)
            assert os.path.exists(backup_path), "Backup file should be created"
            print("✓ create_backup handles None current_driver")
        except Exception as e:
            print(f"✗ create_backup failed with None current_driver: {e}")
            raise

def run_all_tests():
    """Run all None-handling tests"""
    print("Running NoneType error handling tests for driver backup...\n")
    
    tests = [
        test_backup_with_none_hardware_name,
        test_backup_with_none_driver_name,
        test_get_latest_backup_with_none_hardware_name,
        test_list_backups_with_none_hardware_name,
        test_backup_with_missing_hardware_name,
        test_backup_none_driver_with_none_current_driver,
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
