"""
Integration module for Decoder and Training System
Maps decoder/training processes to existing driver management programs
"""

import sys
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from decoder_training_system import DriverOperationDecoder, DriverTrainingDataCollector
from core.driver_manager import DriverManager
from ai.driver_converter import DriverConverter


class DecoderTrainingIntegration:
    """Integrates decoder and training system with existing driver management"""
    
    def __init__(self, config_manager, ai_manager=None):
        """Initialize integration
        
        Args:
            config_manager: ConfigManager instance
            ai_manager: AIManager instance (optional)
        """
        self.config = config_manager
        self.ai_manager = ai_manager
        
        # Initialize components
        self.decoder = DriverOperationDecoder()
        self.collector = DriverTrainingDataCollector()
        self.driver_manager = DriverManager(config_manager)
        
        if ai_manager:
            self.converter = DriverConverter(config_manager, ai_manager)
        else:
            self.converter = None
    
    def decode_hardware(self, hardware_dict):
        """Decode hardware information to operations
        
        Args:
            hardware_dict: Hardware information from driver_manager
            
        Returns:
            Dict with decoded operations and commands
        """
        result = {
            'hardware': hardware_dict,
            'operations': [],
            'commands': [],
            'decoded_info': {}
        }
        
        # Get vendor and device IDs if available
        vendor_id = hardware_dict.get('vendor_id')
        device_id = hardware_dict.get('device_id')
        
        if vendor_id and device_id:
            # Decode using IDs
            operations = self.decoder.translate_device_id_to_operations(vendor_id, device_id)
            result['operations'] = operations
        
        # Get executable commands
        commands = self.decoder.translate_hardware_to_driver_commands(hardware_dict)
        result['commands'] = commands
        
        # Get PCI device info if address available
        pci_address = hardware_dict.get('pci_address')
        if pci_address:
            decoded = self.decoder.decode_pci_device(pci_address)
            result['decoded_info'] = decoded
        
        return result
    
    def decode_and_collect(self, hardware_dict, driver_dict=None):
        """Decode hardware and collect training data
        
        Args:
            hardware_dict: Hardware information
            driver_dict: Driver information (optional)
            
        Returns:
            Dict with decode results and sample ID
        """
        # Decode hardware
        decode_result = self.decode_hardware(hardware_dict)
        
        # Collect device sample
        device_sample = {
            'name': hardware_dict.get('name'),
            'type': hardware_dict.get('type'),
            'vendor': hardware_dict.get('vendor'),
            'vendor_id': hardware_dict.get('vendor_id'),
            'device_id': hardware_dict.get('device_id'),
            'driver': hardware_dict.get('driver'),
            'driver_version': driver_dict.get('version') if driver_dict else None,
            'operations': decode_result['operations'],
            'capabilities': hardware_dict.get('capabilities', [])
        }
        
        sample_id = self.collector.collect_device_sample(device_sample)
        
        # Collect operation samples
        for cmd in decode_result['commands']:
            operation_sample = {
                'driver_name': hardware_dict.get('driver'),
                'hardware_type': hardware_dict.get('type'),
                'hardware_vendor': hardware_dict.get('vendor'),
                'operation_type': 'driver_command',
                'operation_name': cmd['operation'],
                'operation_command': cmd['command'],
                'success': True,
                'metadata': {
                    'device_name': hardware_dict.get('name'),
                    'vendor_id': hardware_dict.get('vendor_id'),
                    'device_id': hardware_dict.get('device_id')
                }
            }
            self.collector.collect_operation_sample(operation_sample)
        
        return {
            'decode_result': decode_result,
            'sample_id': sample_id,
            'samples_collected': len(decode_result['commands']) + 1
        }
    
    def process_driver_conversion(self, driver_info, hardware_info):
        """Process driver conversion with decoder integration
        
        Args:
            driver_info: Driver information dict
            hardware_info: Hardware information dict
            
        Returns:
            Conversion result with decoded processes
        """
        if not self.converter:
            return {'error': 'AI converter not available'}
        
        # Use converter to decode driver process
        decode_result = self.converter.decode_driver_process(driver_info, hardware_info)
        
        # Collect conversion sample if it's a cross-OS conversion
        if driver_info.get('target_os') and driver_info['target_os'].lower() != 'linux':
            conversion_sample = {
                'source_driver': driver_info.get('name'),
                'source_os': driver_info.get('target_os'),
                'target_os': 'linux',
                'hardware_type': hardware_info.get('type'),
                'feasible': decode_result.get('ai_insights') is not None,
                'confidence': 0.5,
                'complexity': 'medium',
                'ai_analysis': str(decode_result.get('ai_insights', '')),
                'success': False
            }
            self.collector.collect_conversion_sample(conversion_sample)
        
        return decode_result
    
    def scan_and_collect_all(self):
        """Scan all system devices and collect training data
        
        Returns:
            Summary of collection
        """
        return self.collector.create_training_dataset(decoder=self.decoder, converter=self.converter)
    
    def export_training_data(self, output_dir=None, formats=['json', 'csv', 'ml']):
        """Export collected training data
        
        Args:
            output_dir: Output directory
            formats: List of formats ('json', 'csv', 'ml')
            
        Returns:
            Dict with exported file paths
        """
        exported = {
            'formats': formats,
            'files': []
        }
        
        if 'json' in formats:
            json_file = self.collector.export_to_json(table='all')
            exported['files'].append(json_file)
        
        if 'csv' in formats:
            csv_files = self.collector.export_to_csv(output_dir=output_dir, table='all')
            exported['files'].extend(csv_files)
        
        if 'ml' in formats:
            ml_labeled = self.collector.export_to_ml_format(format_type='labeled')
            ml_features = self.collector.export_to_ml_format(format_type='features')
            exported['files'].extend([ml_labeled, ml_features])
        
        return exported
    
    def get_statistics(self):
        """Get training data statistics"""
        return self.collector.get_statistics()


def create_integration(config_manager, ai_manager=None):
    """Factory function to create integration instance
    
    Args:
        config_manager: ConfigManager instance
        ai_manager: AIManager instance (optional)
        
    Returns:
        DecoderTrainingIntegration instance
    """
    return DecoderTrainingIntegration(config_manager, ai_manager)
