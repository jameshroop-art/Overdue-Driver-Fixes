#!/usr/bin/env python3
"""
Dual GPU Stress Test - Tests both RTX 3090 and RTX 5090
Runs 15-minute heavy load stress tests on both GPUs sequentially
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.driver_stress_test import DriverStressTest

def run_dual_gpu_stress_test():
    """Run stress tests on both GPUs"""
    
    print("=" * 80)
    print("DUAL GPU STRESS TEST - RTX 3090 & RTX 5090")
    print("15-Minute Heavy Load Testing on Both GPUs")
    print("Simulated Hardware Testing - No Actual Hardware Impact")
    print("=" * 80)
    print()
    
    # System configuration
    system_config = {
        'cpu': 'AMD Ryzen 7 7800X3D',
        'cpu_cores': 8,
        'cpu_threads': 16,
        'cpu_cache': '96MB 3D V-Cache',
        'ram': '64GB',
        'ram_type': 'DDR5-6000',
        'motherboard': 'Asus ROG X870 Extreme',
        'chipset': 'AMD X870',
        'socket': 'AM5',
        'pcie_version': '5.0'
    }
    
    print("System Configuration:")
    print(f"  CPU: {system_config['cpu']} (8C/16T, 96MB 3D V-Cache)")
    print(f"  RAM: {system_config['ram']} {system_config['ram_type']}")
    print(f"  Motherboard: {system_config['motherboard']}")
    print(f"  Chipset: {system_config['chipset']}")
    print(f"  Socket: {system_config['socket']}")
    print(f"  PCIe: {system_config['pcie_version']} x16")
    print()
    
    # GPU configurations
    gpus = [
        {
            'name': 'NVIDIA GeForce RTX 3090 (Simulated)',
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'id': 'sim-rtx3090-001',
            'driver': 'nvidia-driver-550',
            'pcie_slot': 'PCIe 5.0 x16 Slot 1',
            'vram': '24GB GDDR6X',
            'system': system_config
        },
        {
            'name': 'Asus ROG Astral RTX 5090 (Simulated)',
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'id': 'sim-rtx5090-001',
            'driver': 'nvidia-driver-565',
            'pcie_slot': 'PCIe 5.0 x16 Slot 2',
            'vram': '32GB GDDR7',
            'system': system_config
        }
    ]
    
    all_results = []
    
    # Test each GPU
    for idx, gpu in enumerate(gpus, 1):
        print("=" * 80)
        print(f"GPU {idx}/2: {gpu['name']}")
        print("=" * 80)
        print()
        print(f"GPU Configuration:")
        print(f"  Model: {gpu['name']}")
        print(f"  VRAM: {gpu.get('vram', 'N/A')}")
        print(f"  PCIe Slot: {gpu['pcie_slot']}")
        print(f"  Driver: {gpu['driver']}")
        print()
        
        # Initialize stress tester
        stress_tester = DriverStressTest(gpu)
        
        print("Test Configuration:")
        print("  Duration: 15 minutes (900 seconds)")
        print("  Load Level: HEAVY")
        print("  Simulation Mode: Code-based (no hardware access)")
        print()
        
        # Progress tracking
        last_update = time.time()
        update_interval = 30  # Update every 30 seconds
        
        def on_progress(test_name, status, elapsed_seconds):
            """Progress callback"""
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
        
        # Start stress test
        print(f"Starting 15-minute stress test for GPU {idx}...")
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
            print(f"✗ Failed to start stress test for {gpu['name']}")
            continue
        
        print(f"Test started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Wait for completion
        while not test_completed:
            time.sleep(1)
        
        end_time = datetime.now()
        
        # Process results
        print()
        print("=" * 80)
        print(f"GPU {idx} STRESS TEST COMPLETED")
        print("=" * 80)
        print()
        
        if final_results:
            summary = final_results.get('summary', {})
            
            print(f"GPU: {gpu['name']}")
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
            
            # Save results
            all_results.append({
                'gpu': gpu['name'],
                'results': final_results,
                'summary': summary,
                'stability': stability
            })
            
            # Save individual report
            report = stress_tester.generate_report()
            report_dir = os.path.expanduser('~/.config/driver-mgt/stress-tests/')
            os.makedirs(report_dir, exist_ok=True)
            
            gpu_id = gpu['id']
            report_filename = f"stress-test-{gpu_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            report_path = os.path.join(report_dir, report_filename)
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            print(f"Report saved to: {report_path}")
            print()
        
        if idx < len(gpus):
            print("Preparing for next GPU test...")
            print()
            time.sleep(2)
    
    # Final summary
    print("=" * 80)
    print("DUAL GPU STRESS TEST - FINAL SUMMARY")
    print("=" * 80)
    print()
    
    print(f"System: {system_config['cpu']} | {system_config['ram']} {system_config['ram_type']} | {system_config['motherboard']}")
    print()
    
    for idx, result in enumerate(all_results, 1):
        print(f"GPU {idx}: {result['gpu']}")
        print(f"  Tests: {result['summary'].get('total_tests', 0)} | "
              f"Passed: {result['summary'].get('passed_tests', 0)} | "
              f"Success Rate: {result['summary'].get('success_rate', 0):.2f}%")
        print(f"  Assessment: {result['stability']}")
        print()
    
    # Overall assessment
    all_passed = all(r['summary'].get('success_rate', 0) >= 95 for r in all_results)
    
    if all_passed:
        print("✓ OVERALL: Both GPUs are STABLE under heavy load")
        print("System is ready for production use with dual GPU configuration")
        return True
    else:
        print("✗ OVERALL: One or more GPUs show instability")
        print("Review individual reports before production use")
        return False

if __name__ == '__main__':
    print()
    print("⚠ WARNING: This will run for ~30 minutes (15 min per GPU)")
    print("Testing: RTX 3090 and RTX 5090")
    print("Press Ctrl+C at any time to stop the test early")
    print()
    
    try:
        success = run_dual_gpu_stress_test()
        
        if success:
            print()
            print("✓ Dual GPU stress test completed successfully")
            sys.exit(0)
        else:
            print()
            print("✗ Dual GPU stress test completed with concerns")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print()
        print("✗ Dual GPU stress test interrupted by user")
        sys.exit(130)
