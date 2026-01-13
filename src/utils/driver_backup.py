"""
Driver Backup Manager
Handles backup and restoration of driver configurations
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class DriverBackupManager:
    """Manages driver backups and restoration"""
    
    def __init__(self, backup_dir: str = None):
        """Initialize backup manager
        
        Args:
            backup_dir: Directory to store backups (default: /root/driver-backups/)
        """
        if backup_dir is None:
            # Store in root directory as requested
            backup_dir = '/root/driver-backups'
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, hardware: Dict[str, Any], current_driver: Dict[str, Any] = None) -> str:
        """Create a backup of current driver configuration
        
        Args:
            hardware: Hardware information
            current_driver: Current driver information
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get current driver info
        if current_driver is None:
            current_driver = {
                'name': hardware.get('driver', 'unknown'),
                'version': 'unknown',
                'source': 'system'
            }
        
        # Create backup filename
        driver_name = current_driver.get('name', 'unknown').replace('/', '_')
        hardware_name = hardware.get('name', 'unknown').replace('/', '_').replace(' ', '_')
        backup_filename = f"{hardware_name}_{driver_name}_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename
        
        # Backup data
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'timestamp': timestamp,
            'hardware': {
                'name': hardware.get('name'),
                'type': hardware.get('type'),
                'vendor': hardware.get('vendor'),
                'id': hardware.get('id')
            },
            'driver': {
                'name': current_driver.get('name'),
                'version': current_driver.get('version'),
                'source': current_driver.get('source'),
                'stability': current_driver.get('stability'),
                'description': current_driver.get('description')
            },
            'system_info': {
                'backup_path': str(backup_path),
                'backup_filename': backup_filename
            }
        }
        
        # Write backup file
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Driver backup created: {backup_path}")
        return str(backup_path)
    
    def get_latest_backup(self, hardware: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the most recent backup for hardware
        
        Args:
            hardware: Hardware information
            
        Returns:
            Backup data or None if no backup exists
        """
        hardware_name = hardware.get('name', 'unknown').replace('/', '_').replace(' ', '_')
        
        # Find all backups for this hardware
        backups = sorted(
            self.backup_dir.glob(f"{hardware_name}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not backups:
            return None
        
        # Load most recent backup
        with open(backups[0], 'r') as f:
            return json.load(f)
    
    def restore_from_backup(self, backup_path: str, driver_manager) -> bool:
        """Restore driver from backup
        
        Args:
            backup_path: Path to backup file
            driver_manager: DriverManager instance
            
        Returns:
            True if restoration successful
        """
        try:
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            hardware = backup_data['hardware']
            driver = backup_data['driver']
            
            print(f"Restoring driver: {driver['name']} for {hardware['name']}")
            
            # Attempt restoration
            success = driver_manager.restore_driver(driver, hardware)
            
            if success:
                print(f"✓ Driver restored successfully from backup")
            else:
                print(f"✗ Failed to restore driver from backup")
            
            return success
        except Exception as e:
            print(f"✗ Error restoring from backup: {e}")
            return False
    
    def list_backups(self, hardware: Dict[str, Any] = None) -> list:
        """List all backups, optionally filtered by hardware
        
        Args:
            hardware: Optional hardware to filter by
            
        Returns:
            List of backup file paths
        """
        if hardware:
            hardware_name = hardware.get('name', 'unknown').replace('/', '_').replace(' ', '_')
            pattern = f"{hardware_name}_*.json"
        else:
            pattern = "*.json"
        
        backups = sorted(
            self.backup_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return [str(b) for b in backups]
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Remove old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep per hardware device
        """
        # Group backups by hardware
        hardware_backups = {}
        
        for backup_file in self.backup_dir.glob("*.json"):
            # Extract hardware name from filename (format: hardware_driver_timestamp.json)
            parts = backup_file.stem.split('_')
            if len(parts) >= 2:
                # Hardware name might contain underscores, so take everything except last 2 parts
                hardware_key = '_'.join(parts[:-2])
                
                if hardware_key not in hardware_backups:
                    hardware_backups[hardware_key] = []
                
                hardware_backups[hardware_key].append(backup_file)
        
        # Keep only recent backups for each hardware
        for hardware_key, backups in hardware_backups.items():
            # Sort by modification time
            backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for old_backup in backups[keep_count:]:
                try:
                    old_backup.unlink()
                    print(f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    print(f"Failed to remove old backup {old_backup.name}: {e}")
