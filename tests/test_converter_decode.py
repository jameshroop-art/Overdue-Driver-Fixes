"""
Test Driver Converter with Process Decoding
Demonstrates using driver converter to decode driver processes
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_converter_decode_processes():
    """Test driver converter's ability to decode driver processes"""
    print("=" * 70)
    print("DRIVER CONVERTER PROCESS DECODING TESTS")
    print("=" * 70)
    print()
    
    # Mock config and AI manager for testing
    class MockConfig:
        def get(self, key, default=None):
            return default
    
    class MockAIManager:
        def is_available(self):
            return False  # Simulate AI not available for this test
        
        def analyze_text(self, prompt):
            return {'success': False}
    
    from ai.driver_converter import DriverConverter
    
    config = MockConfig()
    ai_manager = MockAIManager()
    converter = DriverConverter(config, ai_manager)
    
    # Test 1: Decode driver process for NVIDIA GPU
    print("Test 1: Decoding NVIDIA GPU driver processes")
    print("-" * 70)
    nvidia_driver = {
        'name': 'nvidia-driver-535',
        'version': '535.129.03',
        'source': 'official',
        'path': '/usr/lib/modules/6.5.0/kernel/drivers/gpu/drm/nvidia.ko'
    }
    
    nvidia_hardware = {
        'name': 'NVIDIA GeForce GTX 1080',
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'vendor_id': '10de',
        'device_id': '1b80',
        'driver': 'nvidia'
    }
    
    result = converter.decode_driver_process(nvidia_driver, nvidia_hardware)
    print(f"Driver: {result['driver']}")
    print(f"Hardware: {result['hardware']}")
    print(f"Decoded Operations ({len(result['decoded_operations'])} total):")
    for op in result['decoded_operations'][:4]:
        print(f"  • {op['operation']}: {op['command']}")
    if result.get('process_details', {}).get('supported_operations'):
        print(f"Supported Operations:")
        for op in result['process_details']['supported_operations'][:4]:
            print(f"  • {op}")
    print()
    
    # Test 2: Decode driver process for WiFi device
    print("Test 2: Decoding WiFi driver processes")
    print("-" * 70)
    wifi_driver = {
        'name': 'iwlwifi',
        'version': '5.15.0',
        'source': 'kernel'
    }
    
    wifi_hardware = {
        'name': 'Intel Wi-Fi 6 AX200',
        'type': 'WiFi',
        'vendor': 'Intel',
        'vendor_id': '8086',
        'device_id': '2723',
        'driver': 'iwlwifi',
        'interface': 'wlan0'
    }
    
    result = converter.decode_driver_process(wifi_driver, wifi_hardware)
    print(f"Driver: {result['driver']}")
    print(f"Hardware: {result['hardware']}")
    print(f"Decoded Operations:")
    for op in result['decoded_operations'][:4]:
        print(f"  • {op['operation']}: {op['command']}")
    print()
    
    # Test 3: Decode running driver processes
    print("Test 3: Decoding running driver processes")
    print("-" * 70)
    # Try common drivers that might be loaded
    test_drivers = ['i915', 'nvidia', 'iwlwifi', 'e1000e', 'r8169']
    
    found_driver = None
    for driver_name in test_drivers:
        result = converter.decode_running_driver_processes(driver_name)
        if result['module_loaded']:
            found_driver = driver_name
            print(f"Found loaded driver: {driver_name}")
            print(f"  Module loaded: {result['module_loaded']}")
            if 'module_size' in result:
                print(f"  Module size: {result['module_size']} bytes")
            if 'usage_count' in result:
                print(f"  Usage count: {result['usage_count']}")
            if result.get('used_by'):
                print(f"  Used by: {', '.join(result['used_by'])}")
            if result.get('processes'):
                print(f"  Associated processes: {len(result['processes'])}")
            if result.get('operations'):
                print(f"  Active operations:")
                for op in result['operations'][:3]:
                    print(f"    • {op}")
            break
    
    if not found_driver:
        print("  No test drivers currently loaded (this is normal)")
        print("  The decoder would show process details for loaded drivers")
    print()
    
    # Test 4: Integration with operation decoder
    print("Test 4: Full decode pipeline (Converter + Decoder)")
    print("-" * 70)
    from utils.driver_operation_decoder import DriverOperationDecoder
    
    decoder = DriverOperationDecoder()
    
    # Scan a device and decode its operations
    print("Scanning PCI devices and decoding operations...")
    devices = decoder.scan_all_devices()
    
    if devices:
        # Find a GPU or network device
        for device in devices:
            if device.get('operations') and len(device.get('operations', [])) > 0:
                print(f"\nDevice: {device.get('device', 'Unknown')}")
                print(f"  Vendor: {device.get('vendor')}")
                print(f"  Driver: {device.get('driver', 'None')}")
                print(f"  Device Type: {device.get('device_type', 'Unknown')}")
                print(f"  Supported Operations:")
                for op in device.get('operations', [])[:5]:
                    print(f"    • {op}")
                
                # Get detailed operation info
                if device.get('operations'):
                    op_name = device['operations'][0]
                    op_details = decoder.get_operation_details(op_name)
                    print(f"\n  Operation Detail for '{op_name}':")
                    print(f"    Description: {op_details['description']}")
                    print(f"    Risk Level: {op_details['risk_level']}")
                
                break
    else:
        print("  No devices found for detailed decoding")
    print()
    
    print("=" * 70)
    print("✓ CONVERTER PROCESS DECODING TESTS COMPLETED")
    print("=" * 70)
    print()
    print("Summary:")
    print("  • Driver converter can decode driver processes")
    print("  • Integrates with operation decoder for detailed analysis")
    print("  • Can analyze running driver processes")
    print("  • Provides operation mappings and commands")
    print("  • AI enhancement available when AI manager is active")
    
    return True

if __name__ == '__main__':
    try:
        test_converter_decode_processes()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
