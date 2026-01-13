#!/usr/bin/env python3
"""
driver-mgt - Advanced Linux Driver & Hardware Management System
Main entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path
import atexit

# Set Qt platform plugin environment variable for headless/CI environments
# This allows the application to run without X11 or Wayland display server
if ('DISPLAY' not in os.environ and 'WAYLAND_DISPLAY' not in os.environ 
    and 'QT_QPA_PLATFORM' not in os.environ):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Ensure we're running in a virtual environment
# This must be done before importing other modules
try:
    from utils.venv_manager import ensure_venv
    
    # Check if --no-venv flag is present (for debugging/development)
    if '--no-venv' not in sys.argv:
        ensure_venv()
except Exception as e:
    print(f"Warning: Failed to set up virtual environment: {e}")
    print("Continuing with system Python...")

from core.config import ConfigManager
from core.hardware_detector import HardwareDetector
from core.driver_manager import DriverManager
from utils.logger import setup_logger

# Global AI manager instance for cleanup
_ai_manager = None

def cleanup_ai_backend():
    """Cleanup AI backend on exit - restores LLM Studio config if needed"""
    global _ai_manager
    if _ai_manager:
        _ai_manager.shutdown()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='driver-mgt - Advanced Linux Driver & Hardware Management System'
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies')
    parser.add_argument('--gui', action='store_true', default=True, help='Launch GUI (default)')
    parser.add_argument('--keep-open', dest='keep_open', action='store_true', default=True, 
                       help='Keep terminal open after command completion (default)')
    parser.add_argument('--no-keep-open', dest='keep_open', action='store_false',
                       help='Close terminal immediately after command completion')
    parser.add_argument('--show-output', dest='show_output', action='store_true', default=True,
                       help='Show subprocess output in terminal (default)')
    parser.add_argument('--no-show-output', dest='show_output', action='store_false',
                       help='Hide subprocess output (quiet mode)')
    parser.add_argument('--no-venv', action='store_true',
                       help='Skip virtual environment setup (for development)')
    parser.add_argument('command', nargs='?', help='Command to execute')
    
    # Sub-commands
    subparsers = parser.add_subparsers(dest='subcommand', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Check system status')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for hardware and drivers')
    scan_parser.add_argument('--all', action='store_true', help='Scan all devices')
    
    # AI status command
    subparsers.add_parser('ai-status', help='Check AI assistant status')
    
    # AI signin command
    subparsers.add_parser('ai-signin', help='Sign in to Ollama with Google authentication')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Driver monitoring control')
    monitor_parser.add_argument('--enable', action='store_true', help='Enable monitoring')
    monitor_parser.add_argument('--disable', action='store_true', help='Disable monitoring')
    monitor_parser.add_argument('--status', action='store_true', help='Check monitoring status')
    
    # Risk assessment command
    risk_parser = subparsers.add_parser('risk-assess', help='Perform risk assessment')
    risk_parser.add_argument('--device', help='Assess specific device')
    
    return parser.parse_args()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    dependencies = {
        'PyQt6': 'PyQt6',
        'psutil': 'psutil',
        'requests': 'requests',
        'yaml': 'pyyaml'
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All dependencies installed")
    return True

def wait_for_user_input(message="Press Enter to close..."):
    """Wait for user input before closing terminal"""
    try:
        input(f"\n{message}")
    except (EOFError, KeyboardInterrupt):
        print("\n")
        pass

def can_use_gui():
    """Check if GUI can be initialized"""
    # If offscreen platform is set, we can't show GUI
    if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
        return False
    
    # If no DISPLAY and no QT_QPA_PLATFORM, can't use GUI
    if 'DISPLAY' not in os.environ and 'WAYLAND_DISPLAY' not in os.environ:
        return False
    
    return True

def main():
    """Main application entry point"""
    global _ai_manager
    
    args = parse_arguments()
    
    # Setup logger
    log_level = 'DEBUG' if args.debug else 'INFO'
    logger = setup_logger(log_level)
    
    logger.info("Starting driver-mgt...")
    
    # Check dependencies if requested
    if args.check_deps:
        result = check_dependencies()
        if args.keep_open:
            wait_for_user_input()
        sys.exit(0 if result else 1)
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Check if we should use LLM Studio backend (via environment variable)
    ai_backend = os.environ.get('DRIVER_MGT_AI_BACKEND', None)
    if ai_backend:
        logger.info(f"Using AI backend from environment: {ai_backend}")
        config_manager.set_ai('backend', ai_backend)
    else:
        ai_backend = config_manager.get_ai('backend', 'ollama')
    
    # Initialize AI manager with selected backend
    from ai.ai_manager import AIManager
    _ai_manager = AIManager(config_manager, backend=ai_backend)
    
    # Register cleanup handler to restore LLM Studio config on exit
    atexit.register(cleanup_ai_backend)
    
    # Configure AI backend if using LLM Studio
    if ai_backend == 'lmstudio':
        logger.info("Configuring LLM Studio backend...")
        if not _ai_manager.configure_for_driver_mgt():
            print("Warning: Failed to configure LLM Studio backend")
            print("Continuing anyway...")
    
    logger.info(f"Using AI backend: {ai_backend}")
    
    # Set CLI configuration for subprocess output visibility
    config_manager.set('cli.show_subprocess_output', args.show_output)
    
    # Handle commands
    if args.subcommand == 'status':
        print("Checking system status...")
        detector = HardwareDetector(config_manager)
        hardware = detector.detect_all()
        print(f"\nDetected {len(hardware)} hardware components:")
        for hw in hardware:
            print(f"  - {hw['type']}: {hw['name']}")
        if args.keep_open:
            wait_for_user_input()
        return
    
    elif args.subcommand == 'scan':
        detector = HardwareDetector(config_manager)
        driver_manager = DriverManager(config_manager)
        print("Scanning for hardware and drivers...")
        hardware = detector.detect_all()
        for hw in hardware:
            print(f"\n{hw['name']}:")
            drivers = driver_manager.find_drivers(hw)
            for driver in drivers:
                print(f"  - {driver['name']} (source: {driver['source']})")
        if args.keep_open:
            wait_for_user_input()
        return
    
    elif args.subcommand == 'ai-status':
        from ai.ai_manager import AIManager
        print("Checking AI assistant status...")
        ai_manager = AIManager(config_manager)
        status = ai_manager.get_status()
        print(f"AI Backend: {status.get('backend', 'unknown')}")
        print(f"Status: {status['status']}")
        print(f"Model: {status.get('model', 'N/A')}")
        if args.keep_open:
            wait_for_user_input()
        return
    
    elif args.subcommand == 'ai-signin':
        from ai.ollama_manager import OllamaManager
        print("Starting Ollama sign-in process...")
        print("Note: This is only for Ollama backend")
        ollama = OllamaManager(config_manager)
        result = ollama.signin()
        if not result.get('success'):
            sys.exit(1)
        if args.keep_open:
            wait_for_user_input()
        return
    
    elif args.subcommand == 'monitor':
        print("Monitor command not yet implemented")
        if args.keep_open:
            wait_for_user_input()
        return
    
    elif args.subcommand == 'risk-assess':
        print("Risk assessment command not yet implemented")
        if args.keep_open:
            wait_for_user_input()
        return
    
    # Launch GUI by default
    if not can_use_gui():
        print("GUI cannot be initialized (no display server detected).")
        print("Running in CLI mode. Available commands:")
        print("  driver-mgt status       - Check system status")
        print("  driver-mgt scan         - Scan for hardware and drivers")
        print("  driver-mgt ai-status    - Check AI assistant status")
        print("  driver-mgt ai-signin    - Sign in to Ollama (required for some models)")
        print("  driver-mgt --check-deps - Check dependencies")
        print("")
        print("To use GUI mode:")
        print("  1. Ensure X11 or Wayland is running")
        print("  2. Set DISPLAY environment variable")
        if args.keep_open:
            wait_for_user_input()
        sys.exit(0)
    
    try:
        # Try to import and create QApplication
        # This will fail if Qt platform plugin can't be initialized
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("driver-mgt")
        app.setOrganizationName("driver-mgt")
        
        window = MainWindow(config_manager)
        window.show()
        
        sys.exit(app.exec())
    except ImportError as e:
        print("PyQt6 is not installed. Install it with: pip3 install PyQt6")
        print("Or use CLI mode with commands like: driver-mgt status")
        if args.keep_open:
            wait_for_user_input()
        sys.exit(1)
    except SystemExit:
        # Re-raise SystemExit to allow proper exit
        raise
    except Exception as e:
        error_msg = str(e).lower()
        # Check for Qt platform plugin related errors
        qt_error_patterns = ['xcb', 'platform plugin', 'qt.qpa', 'libegl', 'libxcb']
        is_qt_error = any(pattern in error_msg for pattern in qt_error_patterns)
        
        if is_qt_error:
            print("Qt platform plugin error detected.")
            print("This may be due to missing system libraries or running in a headless environment.")
            print("")
            print("To fix:")
            print("  1. Install required libraries:")
            print("     Debian/Ubuntu: sudo apt-get install libxcb-cursor0 libxkbcommon-x11-0 libegl1")
            print("     Fedora: sudo dnf install libxcb xcb-util-cursor libxkbcommon-x11 mesa-libEGL")
            print("     Arch: sudo pacman -S libxcb xcb-util-cursor libxkbcommon-x11 libglvnd")
            print("  2. Or run in CLI mode with commands like: driver-mgt status")
            print("  3. For headless/CI environments, set: export QT_QPA_PLATFORM=offscreen")
            print("")
            print(f"Error details: {e}")
        else:
            print(f"Error launching GUI: {e}")
            print("Try running in CLI mode with commands like: driver-mgt status")
        if args.keep_open:
            wait_for_user_input()
        sys.exit(1)

if __name__ == '__main__':
    main()
