"""
Test AI Training Data Collection for Driver Operations
Demonstrates collecting driver data for AI model training
"""

import sys
import os
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_training_data_collection():
    """Test collecting training data for AI models"""
    print("=" * 70)
    print("AI TRAINING DATA COLLECTION TESTS")
    print("=" * 70)
    print()
    
    from utils.driver_training_data import DriverTrainingDataCollector
    from utils.driver_operation_decoder import DriverOperationDecoder
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = DriverTrainingDataCollector(data_dir=tmpdir)
        decoder = DriverOperationDecoder()
        
        # Test 1: Collect operation samples
        print("Test 1: Collecting driver operation samples")
        print("-" * 70)
        
        nvidia_operation = {
            'driver_name': 'nvidia',
            'hardware_type': 'GPU',
            'hardware_vendor': 'NVIDIA',
            'operation_type': 'memory_allocation',
            'operation_name': 'gpu_memory_alloc',
            'operation_command': 'nvidia-smi --query-gpu=memory.used',
            'success': True,
            'execution_time_ms': 15.3,
            'metadata': {
                'memory_size': '8GB',
                'allocation_type': 'video_memory'
            }
        }
        
        sample_id = collector.collect_operation_sample(nvidia_operation)
        print(f"✓ Collected operation sample (ID: {sample_id})")
        
        wifi_operation = {
            'driver_name': 'iwlwifi',
            'hardware_type': 'WiFi',
            'hardware_vendor': 'Intel',
            'operation_type': 'network_scan',
            'operation_name': 'wifi_scan',
            'operation_command': 'iw dev wlan0 scan',
            'success': True,
            'execution_time_ms': 142.7
        }
        
        sample_id2 = collector.collect_operation_sample(wifi_operation)
        print(f"✓ Collected operation sample (ID: {sample_id2})")
        print()
        
        # Test 2: Collect device samples
        print("Test 2: Collecting device samples")
        print("-" * 70)
        
        nvidia_device = {
            'name': 'NVIDIA GeForce GTX 1080',
            'type': 'GPU',
            'vendor': 'NVIDIA',
            'vendor_id': '10de',
            'device_id': '1b80',
            'driver': 'nvidia',
            'driver_version': '535.129',
            'operations': ['gpu_memory_alloc', 'gpu_render', 'display_output'],
            'capabilities': ['OpenGL 4.6', 'Vulkan 1.3', 'CUDA 8.0']
        }
        
        device_id = collector.collect_device_sample(nvidia_device)
        print(f"✓ Collected device sample (ID: {device_id})")
        
        intel_wifi = {
            'name': 'Intel Wi-Fi 6 AX200',
            'type': 'WiFi',
            'vendor': 'Intel',
            'vendor_id': '8086',
            'device_id': '2723',
            'driver': 'iwlwifi',
            'driver_version': '5.15.0',
            'operations': ['scan', 'connect', 'authenticate'],
            'capabilities': ['802.11ax', 'WPA3', 'Bluetooth 5.2']
        }
        
        device_id2 = collector.collect_device_sample(intel_wifi)
        print(f"✓ Collected device sample (ID: {device_id2})")
        print()
        
        # Test 3: Collect conversion samples
        print("Test 3: Collecting driver conversion samples")
        print("-" * 70)
        
        conversion_sample = {
            'source_driver': 'nvidia-driver-windows',
            'source_os': 'windows',
            'target_os': 'linux',
            'hardware_type': 'GPU',
            'feasible': True,
            'confidence': 0.75,
            'complexity': 'high',
            'ai_analysis': 'Conversion feasible but requires significant adaptation',
            'success': False
        }
        
        conv_id = collector.collect_conversion_sample(conversion_sample)
        print(f"✓ Collected conversion sample (ID: {conv_id})")
        print()
        
        # Test 4: Collect process samples
        print("Test 4: Collecting driver process samples")
        print("-" * 70)
        
        process_sample = {
            'driver_name': 'nvidia',
            'pid': 12345,
            'process_name': 'nvidia-persistenced',
            'cpu_usage': 0.5,
            'memory_usage': 45.2,
            'context': {
                'operation': 'persistence_daemon',
                'state': 'running'
            }
        }
        
        proc_id = collector.collect_process_sample(process_sample)
        print(f"✓ Collected process sample (ID: {proc_id})")
        print()
        
        # Test 5: Create comprehensive dataset from system
        print("Test 5: Creating training dataset from system scan")
        print("-" * 70)
        
        dataset_summary = collector.create_training_dataset(decoder=decoder)
        print(f"Dataset Creation Summary:")
        print(f"  Timestamp: {dataset_summary['timestamp']}")
        print(f"  Session ID: {dataset_summary['session_id'][:12]}...")
        print(f"  Devices Scanned: {dataset_summary['devices_scanned']}")
        print(f"  Operations Collected: {dataset_summary['operations_collected']}")
        print(f"  Total Samples: {dataset_summary['samples_created']}")
        print()
        
        # Test 6: Get statistics
        print("Test 6: Training data statistics")
        print("-" * 70)
        
        stats = collector.get_statistics()
        print(f"Training Data Statistics:")
        print(f"  Session ID: {stats['session_id'][:12]}...")
        print(f"  Total Samples Collected: {stats['samples_collected']}")
        print(f"  Driver Operations: {stats['tables']['driver_operations']}")
        print(f"  Devices: {stats['tables']['devices']}")
        print(f"  Conversions: {stats['tables']['driver_conversions']}")
        print(f"  Processes: {stats['tables']['driver_processes']}")
        print(f"  Unique Drivers: {stats['unique_drivers']}")
        print(f"  Unique Hardware Types: {stats['unique_hardware_types']}")
        print(f"  Operation Success Rate: {stats['operation_success_rate']:.2%}")
        print()
        
        # Test 7: Export to JSON
        print("Test 7: Exporting training data to JSON")
        print("-" * 70)
        
        json_file = collector.export_to_json(table='all')
        print(f"✓ Exported to JSON: {os.path.basename(json_file)}")
        
        # Verify JSON content
        with open(json_file, 'r') as f:
            data = json.load(f)
            print(f"  Metadata: {data['metadata']['total_samples']} total samples")
            print(f"  Tables exported: {', '.join([k for k in data.keys() if k != 'metadata'])}")
        print()
        
        # Test 8: Export to CSV
        print("Test 8: Exporting training data to CSV")
        print("-" * 70)
        
        csv_files = collector.export_to_csv(table='all')
        print(f"✓ Exported {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"  • {os.path.basename(csv_file)}")
        print()
        
        # Test 9: Export to ML format
        print("Test 9: Exporting ML-ready training data")
        print("-" * 70)
        
        ml_labeled = collector.export_to_ml_format(format_type='labeled')
        print(f"✓ Exported labeled dataset: {os.path.basename(ml_labeled)}")
        
        # Show sample
        with open(ml_labeled, 'r') as f:
            first_line = f.readline()
            if first_line:
                sample = json.loads(first_line)
                print(f"  Sample input: {sample['input']}")
                print(f"  Sample output: {sample['output']}")
        
        ml_features = collector.export_to_ml_format(format_type='features')
        print(f"✓ Exported feature dataset: {os.path.basename(ml_features)}")
        print()
    
    print("=" * 70)
    print("✓ ALL TRAINING DATA COLLECTION TESTS COMPLETED")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✓ Driver operations collected for AI training")
    print("  ✓ Device information captured")
    print("  ✓ Conversion attempts recorded")
    print("  ✓ Process information logged")
    print("  ✓ Data exported in multiple formats (JSON, CSV, JSONL)")
    print("  ✓ ML-ready labeled datasets created")
    print("  ✓ Ready for supervised and unsupervised learning")
    print()
    print("Use Cases:")
    print("  • Train models to predict driver operations")
    print("  • Learn hardware-to-driver mappings")
    print("  • Predict conversion feasibility")
    print("  • Classify device types and capabilities")
    print("  • Optimize driver operation sequences")
    
    return True

if __name__ == '__main__':
    try:
        test_training_data_collection()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
