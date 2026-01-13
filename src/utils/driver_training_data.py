"""
AI Training Data Collector for Driver Operations
Collects and exports driver operation data for AI model training
"""

import json
import csv
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib


class DriverTrainingDataCollector:
    """Collects driver operation data for AI training"""
    
    def __init__(self, data_dir: str = None):
        """Initialize training data collector
        
        Args:
            data_dir: Directory to store training data
        """
        if data_dir is None:
            data_dir = str(Path.home() / '.config' / 'driver-mgt' / 'training-data')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database for structured data
        self.db_path = self.data_dir / 'training_data.db'
        self._init_database()
        
        # Counters for statistics
        self.samples_collected = 0
        self.session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _init_database(self):
        """Initialize SQLite database for training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Driver operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS driver_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                driver_name TEXT,
                hardware_type TEXT,
                hardware_vendor TEXT,
                operation_type TEXT,
                operation_name TEXT,
                operation_command TEXT,
                success BOOLEAN,
                execution_time_ms REAL,
                metadata TEXT
            )
        ''')
        
        # Device information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                device_name TEXT,
                device_type TEXT,
                vendor TEXT,
                vendor_id TEXT,
                device_id TEXT,
                driver_name TEXT,
                driver_version TEXT,
                operations_json TEXT,
                capabilities_json TEXT
            )
        ''')
        
        # Driver conversions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS driver_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                source_driver TEXT,
                source_os TEXT,
                target_os TEXT,
                hardware_type TEXT,
                feasible BOOLEAN,
                confidence REAL,
                complexity TEXT,
                ai_analysis TEXT,
                success BOOLEAN
            )
        ''')
        
        # Process information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS driver_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                driver_name TEXT,
                process_id INTEGER,
                process_name TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                operation_context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_operation_sample(self, operation: Dict[str, Any]) -> int:
        """Collect a driver operation sample for training
        
        Args:
            operation: Dictionary with operation details
            
        Returns:
            Sample ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO driver_operations (
                timestamp, session_id, driver_name, hardware_type, hardware_vendor,
                operation_type, operation_name, operation_command, success,
                execution_time_ms, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.session_id,
            operation.get('driver_name'),
            operation.get('hardware_type'),
            operation.get('hardware_vendor'),
            operation.get('operation_type'),
            operation.get('operation_name'),
            operation.get('operation_command'),
            operation.get('success', True),
            operation.get('execution_time_ms', 0.0),
            json.dumps(operation.get('metadata', {}))
        ))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.samples_collected += 1
        return sample_id
    
    def collect_device_sample(self, device: Dict[str, Any]) -> int:
        """Collect device information sample
        
        Args:
            device: Device information dictionary
            
        Returns:
            Sample ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO devices (
                timestamp, session_id, device_name, device_type, vendor,
                vendor_id, device_id, driver_name, driver_version,
                operations_json, capabilities_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.session_id,
            device.get('name'),
            device.get('type'),
            device.get('vendor'),
            device.get('vendor_id'),
            device.get('device_id'),
            device.get('driver'),
            device.get('driver_version'),
            json.dumps(device.get('operations', [])),
            json.dumps(device.get('capabilities', []))
        ))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.samples_collected += 1
        return sample_id
    
    def collect_conversion_sample(self, conversion: Dict[str, Any]) -> int:
        """Collect driver conversion sample
        
        Args:
            conversion: Conversion attempt details
            
        Returns:
            Sample ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO driver_conversions (
                timestamp, session_id, source_driver, source_os, target_os,
                hardware_type, feasible, confidence, complexity, ai_analysis, success
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.session_id,
            conversion.get('source_driver'),
            conversion.get('source_os'),
            conversion.get('target_os'),
            conversion.get('hardware_type'),
            conversion.get('feasible', False),
            conversion.get('confidence', 0.0),
            conversion.get('complexity'),
            conversion.get('ai_analysis'),
            conversion.get('success', False)
        ))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.samples_collected += 1
        return sample_id
    
    def collect_process_sample(self, process_info: Dict[str, Any]) -> int:
        """Collect driver process information
        
        Args:
            process_info: Process information dictionary
            
        Returns:
            Sample ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO driver_processes (
                timestamp, session_id, driver_name, process_id, process_name,
                cpu_usage, memory_usage, operation_context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.session_id,
            process_info.get('driver_name'),
            process_info.get('pid'),
            process_info.get('process_name'),
            process_info.get('cpu_usage', 0.0),
            process_info.get('memory_usage', 0.0),
            json.dumps(process_info.get('context', {}))
        ))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.samples_collected += 1
        return sample_id
    
    def export_to_json(self, output_file: str = None, table: str = 'all') -> str:
        """Export training data to JSON format
        
        Args:
            output_file: Output file path (default: auto-generated)
            table: Table to export ('all', 'driver_operations', 'devices', etc.)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = str(self.data_dir / f'training_data_{table}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data = {'metadata': {
            'export_date': datetime.now().isoformat(),
            'session_id': self.session_id,
            'total_samples': self.samples_collected
        }}
        
        tables = ['driver_operations', 'devices', 'driver_conversions', 'driver_processes'] if table == 'all' else [table]
        
        for tbl in tables:
            cursor.execute(f'SELECT * FROM {tbl}')
            rows = cursor.fetchall()
            data[tbl] = [dict(row) for row in rows]
        
        conn.close()
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_file
    
    def export_to_csv(self, output_dir: str = None, table: str = 'all') -> List[str]:
        """Export training data to CSV format
        
        Args:
            output_dir: Output directory (default: data_dir/csv)
            table: Table to export
            
        Returns:
            List of exported file paths
        """
        if output_dir is None:
            output_dir = str(self.data_dir / 'csv')
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        exported_files = []
        tables = ['driver_operations', 'devices', 'driver_conversions', 'driver_processes'] if table == 'all' else [table]
        
        for tbl in tables:
            cursor.execute(f'SELECT * FROM {tbl}')
            rows = cursor.fetchall()
            
            if rows:
                output_file = Path(output_dir) / f'{tbl}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows([dict(row) for row in rows])
                
                exported_files.append(str(output_file))
        
        conn.close()
        return exported_files
    
    def export_to_ml_format(self, output_file: str = None, format_type: str = 'labeled') -> str:
        """Export data in ML-ready format (labeled pairs for training)
        
        Args:
            output_file: Output file path
            format_type: 'labeled' (input-output pairs) or 'features' (feature vectors)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = str(self.data_dir / f'ml_training_data_{format_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create training pairs: input (device/hardware info) -> output (operations/commands)
        cursor.execute('''
            SELECT d.device_name, d.device_type, d.vendor, d.driver_name,
                   o.operation_name, o.operation_command, o.success
            FROM devices d
            LEFT JOIN driver_operations o ON d.driver_name = o.driver_name
            WHERE o.operation_name IS NOT NULL
        ''')
        
        with open(output_file, 'w') as f:
            for row in cursor.fetchall():
                if format_type == 'labeled':
                    # Input-output pairs for supervised learning
                    sample = {
                        'input': {
                            'device': row['device_name'],
                            'type': row['device_type'],
                            'vendor': row['vendor'],
                            'driver': row['driver_name']
                        },
                        'output': {
                            'operation': row['operation_name'],
                            'command': row['operation_command'],
                            'success': bool(row['success'])
                        }
                    }
                else:  # features
                    # Feature vectors for unsupervised learning
                    sample = {
                        'features': {
                            'device_name': row['device_name'],
                            'device_type': row['device_type'],
                            'vendor': row['vendor'],
                            'driver_name': row['driver_name'],
                            'operation_name': row['operation_name'],
                            'has_command': bool(row['operation_command']),
                            'success_rate': 1.0 if row['success'] else 0.0
                        }
                    }
                
                f.write(json.dumps(sample) + '\n')
        
        conn.close()
        return output_file
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training data statistics
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'session_id': self.session_id,
            'samples_collected': self.samples_collected,
            'tables': {}
        }
        
        for table in ['driver_operations', 'devices', 'driver_conversions', 'driver_processes']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats['tables'][table] = count
        
        # Get unique drivers
        cursor.execute('SELECT COUNT(DISTINCT driver_name) FROM devices WHERE driver_name IS NOT NULL')
        stats['unique_drivers'] = cursor.fetchone()[0]
        
        # Get unique hardware types
        cursor.execute('SELECT COUNT(DISTINCT device_type) FROM devices WHERE device_type IS NOT NULL')
        stats['unique_hardware_types'] = cursor.fetchone()[0]
        
        # Get success rate for operations
        cursor.execute('SELECT AVG(CAST(success AS FLOAT)) FROM driver_operations')
        result = cursor.fetchone()[0]
        stats['operation_success_rate'] = result if result else 0.0
        
        conn.close()
        return stats
    
    def create_training_dataset(self, decoder=None, converter=None) -> Dict[str, Any]:
        """Create a comprehensive training dataset from current system
        
        Args:
            decoder: DriverOperationDecoder instance
            converter: DriverConverter instance
            
        Returns:
            Summary of created dataset
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'samples_created': 0,
            'devices_scanned': 0,
            'operations_collected': 0
        }
        
        if decoder:
            # Scan all devices
            devices = decoder.scan_all_devices()
            summary['devices_scanned'] = len(devices)
            
            for device in devices:
                # Collect device sample
                self.collect_device_sample(device)
                summary['samples_created'] += 1
                
                # Collect operations for this device
                if device.get('driver'):
                    hardware_info = {
                        'type': device.get('device_type', 'Unknown'),
                        'vendor': device.get('vendor'),
                        'driver': device.get('driver')
                    }
                    
                    commands = decoder.translate_hardware_to_driver_commands(hardware_info)
                    
                    for cmd in commands:
                        operation_sample = {
                            'driver_name': device.get('driver'),
                            'hardware_type': device.get('device_type'),
                            'hardware_vendor': device.get('vendor'),
                            'operation_type': 'driver_command',
                            'operation_name': cmd['operation'],
                            'operation_command': cmd['command'],
                            'success': True,
                            'metadata': {
                                'device_name': device.get('device'),
                                'vendor_id': device.get('vendor_id'),
                                'device_id': device.get('device_id')
                            }
                        }
                        self.collect_operation_sample(operation_sample)
                        summary['operations_collected'] += 1
        
        summary['samples_created'] = self.samples_collected
        return summary
