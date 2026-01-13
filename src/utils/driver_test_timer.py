"""
Driver Test Timer
Manages timed driver testing with automatic rollback
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from threading import Thread, Event

class DriverTestTimer:
    """Manages timed testing of newly installed drivers"""
    
    def __init__(self, test_duration_minutes: int = 5):
        """Initialize test timer
        
        Args:
            test_duration_minutes: Duration of test period in minutes (default: 5)
        """
        self.test_duration_minutes = test_duration_minutes
        self.test_duration_seconds = test_duration_minutes * 60
        self.timer_thread = None
        self.stop_event = Event()
        self.test_passed = False
        self.test_start_time = None
        self.test_end_time = None
    
    def start_test_timer(self, 
                        driver: Dict[str, Any],
                        hardware: Dict[str, Any],
                        on_timeout: Callable,
                        on_progress: Optional[Callable] = None) -> bool:
        """Start the test timer
        
        Args:
            driver: Driver information
            hardware: Hardware information
            on_timeout: Callback function to call when timer expires
            on_progress: Optional callback for progress updates (receives elapsed_seconds, remaining_seconds)
            
        Returns:
            True if timer started successfully
        """
        if self.timer_thread and self.timer_thread.is_alive():
            print("Test timer already running")
            return False
        
        self.test_passed = False
        self.stop_event.clear()
        self.test_start_time = datetime.now()
        self.test_end_time = self.test_start_time + timedelta(minutes=self.test_duration_minutes)
        
        # Start timer thread
        self.timer_thread = Thread(
            target=self._run_timer,
            args=(driver, hardware, on_timeout, on_progress),
            daemon=True
        )
        self.timer_thread.start()
        
        print(f"✓ Started {self.test_duration_minutes}-minute test timer")
        print(f"  Test will complete at: {self.test_end_time.strftime('%H:%M:%S')}")
        
        return True
    
    def _run_timer(self, 
                   driver: Dict[str, Any],
                   hardware: Dict[str, Any],
                   on_timeout: Callable,
                   on_progress: Optional[Callable]):
        """Internal timer loop"""
        elapsed = 0
        
        while elapsed < self.test_duration_seconds and not self.stop_event.is_set():
            time.sleep(1)
            elapsed += 1
            remaining = self.test_duration_seconds - elapsed
            
            # Call progress callback if provided
            if on_progress and elapsed % 10 == 0:  # Update every 10 seconds
                on_progress(elapsed, remaining)
        
        # Check if timer completed without being stopped
        if not self.stop_event.is_set():
            print(f"⏰ Test timer expired after {self.test_duration_minutes} minutes")
            
            if not self.test_passed:
                print("⚠ Driver test not confirmed - initiating automatic rollback")
                on_timeout(driver, hardware)
            else:
                print("✓ Driver test completed successfully")
    
    def confirm_test_passed(self) -> bool:
        """User confirms that driver is working correctly
        
        Returns:
            True if confirmation accepted
        """
        if not self.timer_thread or not self.timer_thread.is_alive():
            print("No active test timer")
            return False
        
        self.test_passed = True
        self.stop_event.set()
        
        elapsed = (datetime.now() - self.test_start_time).total_seconds()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        print(f"✓ User confirmed driver is working after {minutes}m {seconds}s")
        return True
    
    def cancel_test(self) -> bool:
        """Cancel the test and trigger immediate rollback
        
        Returns:
            True if test was cancelled
        """
        if not self.timer_thread or not self.timer_thread.is_alive():
            print("No active test timer")
            return False
        
        self.test_passed = False
        self.stop_event.set()
        
        print("✗ User cancelled driver test - rollback required")
        return True
    
    def get_remaining_time(self) -> tuple:
        """Get remaining test time
        
        Returns:
            Tuple of (minutes, seconds) remaining, or (0, 0) if no active test
        """
        if not self.timer_thread or not self.timer_thread.is_alive():
            return (0, 0)
        
        if self.test_end_time is None:
            return (0, 0)
        
        remaining = (self.test_end_time - datetime.now()).total_seconds()
        
        if remaining < 0:
            return (0, 0)
        
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        return (minutes, seconds)
    
    def is_test_active(self) -> bool:
        """Check if a test is currently active
        
        Returns:
            True if test timer is running
        """
        return self.timer_thread is not None and self.timer_thread.is_alive()
    
    def get_elapsed_time(self) -> tuple:
        """Get elapsed test time
        
        Returns:
            Tuple of (minutes, seconds) elapsed, or (0, 0) if no active test
        """
        if self.test_start_time is None:
            return (0, 0)
        
        elapsed = (datetime.now() - self.test_start_time).total_seconds()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        return (minutes, seconds)
