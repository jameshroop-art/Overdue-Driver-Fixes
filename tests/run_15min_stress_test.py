#!/usr/bin/env python3
"""
15-Minute Heavy Load Driver Stress Test Demonstration
Simulates extended period stress testing on hardware without actual hardware impact
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.driver_stress_test import DriverStressTest

def run_15_minute_stress_test(hardware_name='NVIDIA GeForce RTX 3090', hardware_id='sim-gpu-001', motherboard='Asus ROG X870 Extreme', cpu='AMD Ryzen 7 7800X3D', ram='64GB'):
    """Run full 15-minute heavy load stress test simulation
    
    Args:
        hardware_name: Name of the GPU to simulate
        hardware_id: Hardware identifier
        motherboard: Motherboard model
        cpu: CPU model
        ram: RAM capacity
    """
    
    print("=" * 80)
    print("15-MINUTE HEAVY LOAD DRIVER STRESS TEST")
    print("Simulated Hardware Testing - No Actual Hardware Impact")
    print("=" * 80)
    print()
    
    # Create simulated hardware device
    simulated_hardware = {
        'name': f'{hardware_name} (Simulated)',
        'type': 'GPU',
        'vendor': 'NVIDIA',
        'id': hardware_id,
        'driver': 'nvidia-driver-550',
        'motherboard': motherboard,
        'pcie_slot': 'PCIe 5.0 x16',
        'system': {
            'cpu': cpu,
            'cpu_cores': 8,
            'cpu_threads': 16,
            'cpu_cache': '96MB 3D V-Cache',
            'ram': ram,
            'ram_type': 'DDR5',
            'ram_speed': '6000MHz',
            'mb_model': motherboard,
            'chipset': 'AMD X870',
            'socket': 'AM5',
            'pcie_version': '5.0',
            'memory_type': 'DDR5'
        }
    }
    
    print(f"System Configuration:")
    print(f"  CPU: {cpu} (8C/16T, 96MB 3D V-Cache)")
    print(f"  RAM: {ram} DDR5-6000")
    print(f"  Motherboard: {motherboard}")
    print(f"  Chipset: AMD X870")
    print(f"  Socket: AM5")
    print(f"  PCIe: 5.0 x16")
    print()
    print(f"GPU Configuration:")
    print(f"  Hardware: {simulated_hardware['name']}")
    print(f"  Type: {simulated_hardware['type']}")
    print(f"  Vendor: {simulated_hardware['vendor']}")
    print(f"  Driver: {simulated_hardware['driver']}")
    print()
    
    # Initialize stress tester
    stress_tester = DriverStressTest(simulated_hardware)
    
    print("Test Configuration:")
    print("  Duration: 15 minutes (900 seconds)")
    print("  Load Level: HEAVY")
    print("  Simulation Mode: Code-based (no hardware access)")
    print()
    
    # Progress tracking
    last_update = time.time()
    update_interval = 30  # Update every 30 seconds
    
    def on_progress(test_name, status, elapsed_seconds):
        """Progress callback - show updates every 30 seconds"""
        nonlocal last_update
        current_time = time.time()
        
        if current_time - last_update >= update_interval:
            results = stress_tester.get_results()
            summary = results.get('summary', {})
            
            elapsed_min = int(elapsed_seconds // 60)
            elapsed_sec = int(elapsed_seconds % 60)
            remaining_sec = 900 - elapsed_seconds
            remaining_min = int(remaining_sec // 60)
            remaining_sec_display = int(remaining_sec % 60)
            
            print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] "
                  f"Tests: {summary.get('total_tests', 0)} | "
                  f"Passed: {summary.get('passed_tests', 0)} | "
                  f"Failed: {summary.get('failed_tests', 0)} | "
                  f"Success: {summary.get('success_rate', 0):.1f}% | "
                  f"Remaining: {remaining_min:02d}:{remaining_sec_display:02d}")
            
            last_update = current_time
    
    test_completed = False
    final_results = None
    
    def on_complete(results):
        """Completion callback"""
        nonlocal test_completed, final_results
        test_completed = True
        final_results = results
    
    # Start the 15-minute stress test
    print("Starting 15-minute stress test...")
    print("Progress updates every 30 seconds:")
    print()
    
    start_time = datetime.now()
    success = stress_tester.start_stress_test(
        duration_seconds=900,  # 15 minutes
        stress_level='heavy',
        on_progress=on_progress,
        on_complete=on_complete
    )
    
    if not success:
        print("✗ Failed to start stress test")
        return False
    
    # Wait for completion with status updates
    print(f"Test started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Monitor test execution
    while not test_completed:
        time.sleep(1)
    
    end_time = datetime.now()
    
    # Test completed - show results
    print()
    print("=" * 80)
    print("STRESS TEST COMPLETED")
    print("=" * 80)
    print()
    
    if final_results:
        summary = final_results.get('summary', {})
        
        print(f"Completion Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Duration: {final_results.get('duration_seconds', 0):.1f} seconds")
        print()
        
        print("Test Results:")
        print(f"  Total Tests Performed: {summary.get('total_tests', 0)}")
        print(f"  Passed: {summary.get('passed_tests', 0)}")
        print(f"  Failed: {summary.get('failed_tests', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.2f}%")
        print()
        
        # Determine stability
        success_rate = summary.get('success_rate', 0)
        if success_rate >= 99:
            stability = "EXCELLENT - Driver is highly stable under heavy load"
        elif success_rate >= 97:
            stability = "GOOD - Driver is stable under heavy load"
        elif success_rate >= 95:
            stability = "ACCEPTABLE - Driver shows good stability"
        elif success_rate >= 90:
            stability = "MARGINAL - Driver may have issues under stress"
        else:
            stability = "POOR - Driver shows instability under load"
        
        print(f"Overall Assessment: {stability}")
        print()
        
        # Show full report
        print("=" * 80)
        print("DETAILED REPORT")
        print("=" * 80)
        report = stress_tester.generate_report()
        print(report)
        
        # Save report to file
        report_dir = os.path.expanduser('~/.config/driver-mgt/stress-tests/')
        os.makedirs(report_dir, exist_ok=True)
        
        report_filename = f"stress-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        report_path = os.path.join(report_dir, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"Report saved to: {report_path}")
        print()
        
        return success_rate >= 95
    
    return False

if __name__ == '__main__':
    print()
    
    # Check command line arguments for hardware selection
    import argparse
    parser = argparse.ArgumentParser(description='15-Minute GPU Stress Test')
    parser.add_argument('--gpu', type=str, default='NVIDIA GeForce RTX 3090',
                        help='GPU model to simulate (default: NVIDIA GeForce RTX 3090)')
    parser.add_argument('--id', type=str, default='sim-gpu-001',
                        help='Hardware ID (default: sim-gpu-001)')
    parser.add_argument('--motherboard', type=str, default='Asus ROG X870 Extreme',
                        help='Motherboard model (default: Asus ROG X870 Extreme)')
    parser.add_argument('--cpu', type=str, default='AMD Ryzen 7 7800X3D',
                        help='CPU model (default: AMD Ryzen 7 7800X3D)')
    parser.add_argument('--ram', type=str, default='64GB',
                        help='RAM capacity (default: 64GB)')
    args = parser.parse_args()
    
    print(f"Test Configuration:")
    print(f"  CPU: {args.cpu}")
    print(f"  RAM: {args.ram} DDR5")
    print(f"  GPU: {args.gpu}")
    print(f"  Motherboard: {args.motherboard}")
    print()
    print("⚠ WARNING: This will run for 15 minutes")
    print("Press Ctrl+C at any time to stop the test early")
    print()
    
    try:
        success = run_15_minute_stress_test(
            hardware_name=args.gpu, 
            hardware_id=args.id,
            motherboard=args.motherboard,
            cpu=args.cpu,
            ram=args.ram
        )
        
        if success:
            print("✓ Stress test completed successfully - Driver is stable")
            sys.exit(0)
        else:
            print("✗ Stress test completed with concerns - Review results")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print()
        print("✗ Stress test interrupted by user")
        sys.exit(130)
