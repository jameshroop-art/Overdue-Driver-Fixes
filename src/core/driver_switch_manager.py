"""
Driver Switching Manager with Safety Confirmation
Allows safe driver switching with automatic rollback on timeout
"""

import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime, timedelta

class DriverSwitchManager:
    """
    Manages driver switching with safety confirmation and automatic rollback
    Implements 20-second countdown with automatic revert if unconfirmed
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.driver_history_file = config_manager.get_config_dir() / 'driver_history.json'
        self.driver_history = self._load_driver_history()
        
        # Active switch tracking
        self.active_switch = None
        self.switch_timer = None
        self.confirmation_timeout = 20  # 20 seconds
    
    def _load_driver_history(self) -> Dict[str, List[Dict]]:
        """Load driver usage history from disk"""
        if self.driver_history_file.exists():
            try:
                with open(self.driver_history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_driver_history(self):
        """Save driver history to disk"""
        try:
            with open(self.driver_history_file, 'w') as f:
                json.dump(self.driver_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save driver history: {e}")
    
    def record_driver_usage(self, device_id: str, driver_name: str, driver_version: str):
        """
        Record when a driver is used for a device
        
        Args:
            device_id: Unique device identifier
            driver_name: Name of the driver
            driver_version: Version of the driver
        """
        if device_id not in self.driver_history:
            self.driver_history[device_id] = []
        
        # Record this usage
        entry = {
            'driver_name': driver_name,
            'driver_version': driver_version,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': 0  # Will be updated when driver is changed
        }
        
        # Update duration of previous entry
        if self.driver_history[device_id]:
            last_entry = self.driver_history[device_id][-1]
            if 'timestamp' in last_entry:
                start_time = datetime.fromisoformat(last_entry['timestamp'])
                duration = (datetime.now() - start_time).total_seconds()
                last_entry['duration_seconds'] = duration
        
        self.driver_history[device_id].append(entry)
        self._save_driver_history()
    
    def get_longest_used_driver(self, device_id: str) -> Optional[Dict[str, str]]:
        """
        Get the driver that has been assigned the longest for a device
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            Dict with driver_name and driver_version, or None if no history
        """
        if device_id not in self.driver_history or not self.driver_history[device_id]:
            return None
        
        # Calculate total duration for each unique driver
        driver_durations = {}
        for entry in self.driver_history[device_id]:
            key = f"{entry['driver_name']}:{entry['driver_version']}"
            duration = entry.get('duration_seconds', 0)
            driver_durations[key] = driver_durations.get(key, 0) + duration
        
        # Find the driver with longest total duration
        if not driver_durations:
            return None
        
        longest_key = max(driver_durations, key=driver_durations.get)
        driver_name, driver_version = longest_key.split(':', 1)
        
        return {
            'driver_name': driver_name,
            'driver_version': driver_version,
            'total_duration_seconds': driver_durations[longest_key]
        }
    
    def initiate_driver_switch(self, device_id: str, device_name: str, 
                              old_driver: Dict[str, str], new_driver: Dict[str, str]) -> Dict[str, Any]:
        """
        Initiate a driver switch with safety confirmation requirement
        
        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            old_driver: Current driver info (name, version)
            new_driver: New driver to switch to (name, version)
            
        Returns:
            Dict with switch_id and status
        """
        # Create switch record
        switch_id = f"{device_id}_{int(time.time())}"
        
        self.active_switch = {
            'switch_id': switch_id,
            'device_id': device_id,
            'device_name': device_name,
            'old_driver': old_driver,
            'new_driver': new_driver,
            'start_time': time.time(),
            'timeout_time': time.time() + self.confirmation_timeout,
            'status': 'pending_confirmation',
            'confirmed': False
        }
        
        print(f"Initiated driver switch for {device_name}")
        print(f"  From: {old_driver['name']} {old_driver['version']}")
        print(f"  To: {new_driver['name']} {new_driver['version']}")
        print(f"  Confirmation required within {self.confirmation_timeout} seconds")
        
        return {
            'switch_id': switch_id,
            'status': 'pending_confirmation',
            'timeout_seconds': self.confirmation_timeout,
            'message': f'Driver switch initiated. Please confirm within {self.confirmation_timeout} seconds.'
        }
    
    def get_switch_status(self) -> Optional[Dict[str, Any]]:
        """
        Get status of active driver switch
        
        Returns:
            Dict with switch status and countdown, or None if no active switch
        """
        if not self.active_switch:
            return None
        
        current_time = time.time()
        remaining_time = max(0, self.active_switch['timeout_time'] - current_time)
        
        return {
            'switch_id': self.active_switch['switch_id'],
            'device_name': self.active_switch['device_name'],
            'old_driver': self.active_switch['old_driver'],
            'new_driver': self.active_switch['new_driver'],
            'status': self.active_switch['status'],
            'confirmed': self.active_switch['confirmed'],
            'remaining_seconds': int(remaining_time),
            'expired': remaining_time <= 0
        }
    
    def confirm_driver_switch(self, switch_id: str) -> Dict[str, Any]:
        """
        Confirm a pending driver switch
        
        Args:
            switch_id: ID of the switch to confirm
            
        Returns:
            Dict with confirmation result
        """
        if not self.active_switch or self.active_switch['switch_id'] != switch_id:
            return {
                'success': False,
                'error': 'No active switch with that ID'
            }
        
        current_time = time.time()
        if current_time > self.active_switch['timeout_time']:
            return {
                'success': False,
                'error': 'Switch confirmation timeout expired'
            }
        
        # Mark as confirmed
        self.active_switch['confirmed'] = True
        self.active_switch['status'] = 'confirmed'
        self.active_switch['confirmed_time'] = current_time
        
        # Record the new driver usage
        device_id = self.active_switch['device_id']
        new_driver = self.active_switch['new_driver']
        self.record_driver_usage(device_id, new_driver['name'], new_driver['version'])
        
        print(f"✓ Driver switch confirmed for {self.active_switch['device_name']}")
        
        result = {
            'success': True,
            'message': 'Driver switch confirmed',
            'device_id': device_id,
            'new_driver': new_driver
        }
        
        # Clear active switch
        self.active_switch = None
        
        return result
    
    def check_and_revert_expired_switch(self) -> Optional[Dict[str, Any]]:
        """
        Check if active switch has expired and revert if necessary
        
        Returns:
            Dict with revert result if switch expired, None otherwise
        """
        if not self.active_switch:
            return None
        
        current_time = time.time()
        
        # Check if switch has expired without confirmation
        if current_time > self.active_switch['timeout_time'] and not self.active_switch['confirmed']:
            device_id = self.active_switch['device_id']
            device_name = self.active_switch['device_name']
            old_driver = self.active_switch['old_driver']
            new_driver = self.active_switch['new_driver']
            
            print(f"⚠ Driver switch timeout expired for {device_name}")
            print(f"  Reverting from: {new_driver['name']} {new_driver['version']}")
            print(f"  Back to: {old_driver['name']} {old_driver['version']}")
            
            # Get longest used driver as ultimate fallback
            longest_driver = self.get_longest_used_driver(device_id)
            if longest_driver:
                fallback_driver = {
                    'name': longest_driver['driver_name'],
                    'version': longest_driver['driver_version']
                }
                print(f"  (Longest used driver: {fallback_driver['name']} {fallback_driver['version']})")
            else:
                fallback_driver = old_driver
            
            result = {
                'reverted': True,
                'device_id': device_id,
                'device_name': device_name,
                'attempted_driver': new_driver,
                'reverted_to': fallback_driver,
                'reason': 'Confirmation timeout expired',
                'timeout_seconds': self.confirmation_timeout
            }
            
            # Clear active switch
            self.active_switch = None
            
            return result
        
        return None
    
    def cancel_driver_switch(self, switch_id: str) -> Dict[str, Any]:
        """
        Manually cancel a pending driver switch
        
        Args:
            switch_id: ID of the switch to cancel
            
        Returns:
            Dict with cancellation result
        """
        if not self.active_switch or self.active_switch['switch_id'] != switch_id:
            return {
                'success': False,
                'error': 'No active switch with that ID'
            }
        
        device_name = self.active_switch['device_name']
        old_driver = self.active_switch['old_driver']
        
        print(f"✗ Driver switch cancelled for {device_name}")
        print(f"  Remaining on: {old_driver['name']} {old_driver['version']}")
        
        result = {
            'success': True,
            'message': 'Driver switch cancelled',
            'device_name': device_name,
            'driver': old_driver
        }
        
        # Clear active switch
        self.active_switch = None
        
        return result
    
    def get_driver_history_for_device(self, device_id: str) -> List[Dict]:
        """Get complete driver usage history for a device"""
        return self.driver_history.get(device_id, [])
    
    def get_driver_statistics(self, device_id: str) -> Dict[str, Any]:
        """
        Get statistics about driver usage for a device
        
        Returns:
            Dict with statistics including most used driver, total switches, etc.
        """
        if device_id not in self.driver_history:
            return {
                'total_switches': 0,
                'drivers_used': [],
                'longest_used_driver': None
            }
        
        history = self.driver_history[device_id]
        
        # Get unique drivers
        drivers_used = set()
        for entry in history:
            drivers_used.add(f"{entry['driver_name']} {entry['driver_version']}")
        
        # Get longest used
        longest = self.get_longest_used_driver(device_id)
        
        return {
            'total_switches': len(history),
            'drivers_used': list(drivers_used),
            'longest_used_driver': longest,
            'current_driver': history[-1] if history else None
        }
