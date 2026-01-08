"""
Virtual Environment Manager for driver-mgt
Automatically creates and manages Python virtual environment
"""

import os
import sys
import subprocess
from pathlib import Path


# Installation directory for system-wide install
SYSTEM_INSTALL_DIR = '/opt/driver-mgt'

def get_venv_path():
    """Get the path to the virtual environment"""
    # Check for installed location first
    installed_venv = Path(SYSTEM_INSTALL_DIR) / 'venv'
    if installed_venv.exists() and (installed_venv / 'bin' / 'python').exists():
        return installed_venv
    
    # Find the application root directory (where driver-mgt script is)
    current_file = Path(__file__).resolve()
    
    # Navigate up to find the root (where driver-mgt script exists)
    app_dir = current_file.parent
    while app_dir.parent != app_dir:
        if (app_dir / 'driver-mgt').exists() or (app_dir / 'requirements.txt').exists():
            break
        app_dir = app_dir.parent
    
    venv_path = app_dir / 'venv'
    return venv_path


def get_venv_python():
    """Get path to Python interpreter in venv"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return venv_path / 'Scripts' / 'python.exe'
    else:  # Unix-like
        return venv_path / 'bin' / 'python'


def get_venv_pip():
    """Get path to pip in venv"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return venv_path / 'Scripts' / 'pip.exe'
    else:  # Unix-like
        return venv_path / 'bin' / 'pip'


def is_venv_active():
    """Check if we're running in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def venv_exists():
    """Check if venv directory exists and is valid"""
    venv_python = get_venv_python()
    return venv_python.exists() and venv_python.is_file()


def create_venv():
    """Create a new virtual environment"""
    venv_path = get_venv_path()
    
    print(f"Creating virtual environment at {venv_path}...")
    
    try:
        # Create venv using Python's venv module
        subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        print(f"Error output: {e.stderr}")
        return False


def install_requirements():
    """Install requirements into the virtual environment"""
    venv_pip = get_venv_pip()
    
    # Find requirements.txt in application root
    venv_path = get_venv_path()
    app_dir = venv_path.parent
    requirements_file = app_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print(f"✗ Requirements file not found: {requirements_file}")
        return False
    
    print(f"Installing requirements from {requirements_file}...")
    
    try:
        # Upgrade pip first
        subprocess.run(
            [str(venv_pip), 'install', '--upgrade', 'pip'],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Install requirements
        result = subprocess.run(
            [str(venv_pip), 'install', '-r', str(requirements_file)],
            check=True,
            capture_output=False,  # Show output
            text=True
        )
        
        print(f"✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False


def restart_in_venv():
    """Restart the script using the venv Python interpreter"""
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print(f"✗ Virtual environment Python not found: {venv_python}")
        return False
    
    print(f"Restarting with virtual environment Python...")
    
    # Get the original script path and arguments
    script_path = sys.argv[0]
    script_args = sys.argv[1:]
    
    # Execute the script with venv Python
    os.execv(str(venv_python), [str(venv_python), script_path] + script_args)


def ensure_venv():
    """
    Ensure virtual environment exists and is active
    
    This function should be called at the start of the application.
    It will:
    1. Check if we're already in a venv
    2. If not, check if venv exists
    3. If not, create it and install requirements
    4. Restart the script in the venv
    
    Returns:
        bool: True if already in venv or successfully set up
    """
    # If we're already in a venv, we're good
    if is_venv_active():
        return True
    
    # Check if venv exists
    if not venv_exists():
        print("Virtual environment not found. Creating...")
        if not create_venv():
            print("✗ Failed to create virtual environment")
            return False
        
        # Install requirements
        if not install_requirements():
            print("✗ Failed to install requirements")
            return False
    
    # Restart in venv
    print("Starting application in virtual environment...")
    restart_in_venv()
    
    # This line should not be reached as restart_in_venv uses exec
    return False


def check_requirements():
    """Check if all required packages are installed"""
    # Find requirements.txt in application root
    venv_path = get_venv_path()
    app_dir = venv_path.parent
    requirements_file = app_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        return True
    
    missing_packages = []
    
    try:
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before >= or ==)
                    package = line.split('>=')[0].split('==')[0].strip()
                    try:
                        __import__(package.replace('-', '_').lower())
                    except ImportError:
                        missing_packages.append(package)
    except Exception as e:
        print(f"Error checking requirements: {e}")
        return False
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        return False
    
    return True


def get_venv_info():
    """Get information about the virtual environment"""
    info = {
        'venv_path': str(get_venv_path()),
        'venv_exists': venv_exists(),
        'venv_active': is_venv_active(),
        'python_path': sys.executable,
        'python_version': sys.version,
    }
    
    return info


if __name__ == '__main__':
    # Test the venv manager
    info = get_venv_info()
    print("Virtual Environment Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    if not is_venv_active():
        print("\nNot running in virtual environment. Setting up...")
        ensure_venv()
