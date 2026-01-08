"""
Test motherboard detection including BIOS and chipset information
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_motherboard_detection():
    """Test enhanced motherboard detection with BIOS and chipset"""
    from core.config import ConfigManager
    from core.hardware_detector import HardwareDetector
    
    config = ConfigManager()
    detector = HardwareDetector(config)
    
    # Detect all hardware
    hardware = detector.detect_all()
    
    # Find motherboard
    motherboards = [hw for hw in hardware if hw.get('type') == 'Motherboard']
    
    print("\n=== Motherboard Detection Test ===")
    
    if motherboards:
        for mb in motherboards:
            print(f"\nMotherboard Found:")
            print(f"  Vendor: {mb.get('vendor', 'Unknown')}")
            print(f"  Model: {mb.get('model', 'Unknown')}")
            print(f"  Board Version: {mb.get('board_version', 'N/A')}")
            print(f"\nBIOS Information:")
            print(f"  BIOS Vendor: {mb.get('bios_vendor', 'Unknown')}")
            print(f"  BIOS Version: {mb.get('bios_version', 'Unknown')}")
            print(f"  BIOS Date: {mb.get('bios_date', 'Unknown')}")
            print(f"\nChipset Information:")
            print(f"  Chipset: {mb.get('chipset', 'Unknown')}")
            print(f"  Chipset Vendor: {mb.get('chipset_vendor', 'Unknown')}")
            
            # Check Linux compatibility info
            compat = mb.get('linux_compatible', {})
            print(f"\nLinux Compatibility:")
            print(f"  Status: {compat.get('status', 'unknown')}")
            print(f"  Support Level: {compat.get('linux_support', 'Unknown')}")
            print(f"  Manufacturer: {compat.get('manufacturer', 'Unknown')}")
            
            if compat.get('support_url'):
                print(f"  Support URL: {compat.get('support_url')}")
            if compat.get('drivers_url'):
                print(f"  Drivers URL: {compat.get('drivers_url')}")
            if compat.get('notes'):
                print(f"  Notes: {compat.get('notes')}")
            
            # Verify required fields are present
            assert 'vendor' in mb, "Motherboard should have vendor"
            assert 'model' in mb, "Motherboard should have model"
            assert 'bios_version' in mb, "Motherboard should have BIOS version"
            assert 'bios_date' in mb, "Motherboard should have BIOS date"
            assert 'chipset' in mb, "Motherboard should have chipset info"
            assert 'linux_compatible' in mb, "Motherboard should have compatibility info"
            
        print("\n✓ Motherboard detection tests passed")
        return True
    else:
        print("\n⚠ No motherboard detected (this may be normal in VM/container)")
        print("✓ Test passed (no errors occurred)")
        return True

def test_linux_compatibility_check():
    """Test Linux compatibility checking for known manufacturers"""
    from core.config import ConfigManager
    from core.hardware_detector import HardwareDetector
    
    config = ConfigManager()
    detector = HardwareDetector(config)
    
    print("\n=== Linux Compatibility Check Test ===")
    
    # Test known manufacturers
    test_cases = [
        ('ASUS', 'ROG STRIX X570-E GAMING'),
        ('MSI', 'B550 TOMAHAWK'),
        ('Gigabyte', 'X670E AORUS MASTER'),
        ('ASRock', 'B650M-HDV/M.2'),
        ('Unknown Vendor', 'Test Board')
    ]
    
    for vendor, model in test_cases:
        compat = detector._check_linux_compatibility(vendor, model)
        print(f"\n{vendor} {model}:")
        print(f"  Status: {compat.get('status')}")
        print(f"  Support: {compat.get('linux_support')}")
        
        assert 'status' in compat, "Compatibility info should have status"
        assert 'linux_support' in compat, "Compatibility info should have support level"
        
        # Known vendors should have support URLs
        if vendor.upper() in ['ASUS', 'MSI', 'GIGABYTE', 'ASROCK']:
            assert compat.get('support_url'), f"{vendor} should have support URL"
            assert compat.get('drivers_url'), f"{vendor} should have drivers URL"
    
    print("\n✓ Linux compatibility check tests passed")

def run_all_tests():
    """Run all motherboard-related tests"""
    print("Running motherboard detection tests...\n")
    
    tests = [
        test_motherboard_detection,
        test_linux_compatibility_check,
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
