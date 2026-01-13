"""
Test Driver Operation Decoder functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_driver_operation_decoder():
    """Test the driver operation decoder"""
    from utils.driver_operation_decoder import DriverOperationDecoder
    
    print("=" * 70)
    print("DRIVER OPERATION DECODER TESTS")
    print("=" * 70)
    print()
    
    decoder = DriverOperationDecoder()
    
    # Test 1: Translate device IDs to operations
    print("Test 1: Translating NVIDIA GPU device ID to operations")
    print("-" * 70)
    nvidia_ops = decoder.translate_device_id_to_operations('10de', '1c03')
    print(f"NVIDIA Device (10de:1c03) Operations:")
    for op in nvidia_ops:
        print(f"  • {op}")
    print()
    
    # Test 2: Translate AMD GPU device ID
    print("Test 2: Translating AMD GPU device ID to operations")
    print("-" * 70)
    amd_ops = decoder.translate_device_id_to_operations('1002', '687f')
    print(f"AMD Device (1002:687f) Operations:")
    for op in amd_ops:
        print(f"  • {op}")
    print()
    
    # Test 3: Get operation details
    print("Test 3: Getting operation details")
    print("-" * 70)
    op_detail = decoder.get_operation_details('gpu_memory_alloc')
    print(f"Operation: gpu_memory_alloc")
    print(f"  Description: {op_detail['description']}")
    print(f"  Risk Level: {op_detail['risk_level']}")
    print(f"  Syscalls: {', '.join(op_detail['syscalls'])}")
    print(f"  Kernel Functions: {', '.join(op_detail['kernel_functions'])}")
    print()
    
    # Test 4: Translate hardware to driver commands
    print("Test 4: Translating hardware to driver commands")
    print("-" * 70)
    test_hardware = {
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'driver': 'nvidia'
    }
    commands = decoder.translate_hardware_to_driver_commands(test_hardware)
    print(f"GPU Driver Commands:")
    for cmd in commands[:3]:  # Show first 3
        print(f"  • {cmd['operation']}: {cmd['command']}")
    print()
    
    # Test 5: Scan devices (if available)
    print("Test 5: Scanning PCI devices")
    print("-" * 70)
    try:
        devices = decoder.scan_all_devices()
        if devices:
            print(f"Found {len(devices)} PCI devices")
            # Show first 3 devices with operations
            for device in devices[:3]:
                if device.get('operations'):
                    print(f"\n  Device: {device.get('device', 'Unknown')}")
                    print(f"  Vendor: {device.get('vendor', 'Unknown')}")
                    print(f"  Driver: {device.get('driver', 'None')}")
                    print(f"  Operations: {', '.join(device.get('operations', [])[:3])}")
        else:
            print("  No devices found (this is normal in some environments)")
    except Exception as e:
        print(f"  Cannot scan devices: {e}")
        print("  (This is normal in restricted environments)")
    print()
    
    print("=" * 70)
    print("✓ ALL DECODER TESTS COMPLETED")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        test_driver_operation_decoder()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
