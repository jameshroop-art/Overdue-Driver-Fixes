"""
Tests for AI Virtual Kernel Simulator
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai.virtual_kernel_simulator import VirtualKernelSimulator


class MockAIManager:
    """Mock AI manager for testing"""
    
    def is_available(self):
        return True


def test_virtual_kernel_initialization():
    """Test virtual kernel simulator initialization"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    assert vk.kernel_version == "6.1.0-virtual"
    assert len(vk.virtual_devices) == 0
    assert len(vk.loaded_drivers) == 0


def test_create_virtual_device_gpu():
    """Test creating a virtual GPU device"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090',
        'vendor': 'NVIDIA'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    assert device_id in vk.virtual_devices
    assert vk.virtual_devices[device_id]['state'] == 'initialized'
    assert 'graphics_rendering' in vk.virtual_devices[device_id]['capabilities']
    assert 'compute_acceleration' in vk.virtual_devices[device_id]['capabilities']


def test_create_virtual_device_wifi():
    """Test creating a virtual WiFi device"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'WiFi',
        'name': 'Intel AX211',
        'vendor': 'Intel'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    assert device_id in vk.virtual_devices
    assert 'wireless_networking' in vk.virtual_devices[device_id]['capabilities']
    assert 'packet_transmission' in vk.virtual_devices[device_id]['capabilities']


def test_simulate_driver_load_linux():
    """Test simulating Linux driver load"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    driver = {
        'name': 'nvidia-driver-550',
        'version': '550.54.14',
        'target_os': 'linux',
        'source': 'official'
    }
    
    result = vk.simulate_driver_load(device_id, driver)
    
    assert result['success'] == True
    assert result['compatibility_score'] >= 90  # Linux drivers should have high compatibility
    assert len(result['simulation_steps']) > 0
    assert vk.virtual_devices[device_id]['loaded_driver'] == driver['name']
    assert vk.virtual_devices[device_id]['state'] == 'driver_loaded'


def test_simulate_driver_load_windows_converted():
    """Test simulating Windows driver load (converted)"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    driver = {
        'name': 'nvidia-driver-550-converted',
        'version': '550.54.14',
        'target_os': 'windows',
        'source': 'converted'
    }
    
    result = vk.simulate_driver_load(device_id, driver)
    
    # Converted drivers should still load but with warnings
    assert result['compatibility_score'] >= 50
    assert len(result['warnings']) > 0


def test_simulate_driver_operation():
    """Test simulating driver operations"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    driver = {
        'name': 'nvidia-driver-550',
        'version': '550.54.14',
        'target_os': 'linux'
    }
    
    vk.simulate_driver_load(device_id, driver)
    
    # Simulate operations
    result = vk.simulate_driver_operation(device_id, 'stress_test', duration_seconds=1)
    
    assert result['success'] == True
    assert result['operations_performed'] > 0
    assert result['operations_succeeded'] > 0
    assert result['performance_score'] > 90  # Should have high success rate


def test_unload_driver():
    """Test unloading a virtual driver"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    driver = {
        'name': 'nvidia-driver-550',
        'version': '550.54.14',
        'target_os': 'linux'
    }
    
    vk.simulate_driver_load(device_id, driver)
    
    # Unload driver
    result = vk.unload_driver(device_id)
    
    assert result['success'] == True
    assert vk.virtual_devices[device_id]['loaded_driver'] is None
    assert vk.virtual_devices[device_id]['state'] == 'initialized'


def test_simulation_log():
    """Test that simulation log is maintained"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    hardware = {
        'type': 'GPU',
        'name': 'NVIDIA GeForce RTX 3090'
    }
    
    device_id = vk.create_virtual_device(hardware)
    
    log = vk.get_simulation_log()
    
    assert len(log) > 0
    assert any('Created virtual device' in entry for entry in log)


def test_clear_simulation():
    """Test clearing all virtual devices"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    # Create multiple devices
    for i in range(3):
        hardware = {
            'type': 'GPU',
            'name': f'Test GPU {i}'
        }
        vk.create_virtual_device(hardware)
    
    assert len(vk.virtual_devices) == 3
    
    # Clear simulation
    vk.clear_simulation()
    
    assert len(vk.virtual_devices) == 0
    assert len(vk.loaded_drivers) == 0


def test_simulate_driver_without_device():
    """Test that driver load fails without valid device"""
    ai_manager = MockAIManager()
    vk = VirtualKernelSimulator(ai_manager)
    
    driver = {
        'name': 'test-driver',
        'version': '1.0.0',
        'target_os': 'linux'
    }
    
    result = vk.simulate_driver_load('invalid_device_id', driver)
    
    assert result['success'] == False
    assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
