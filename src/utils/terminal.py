"""
Terminal utilities for driver-mgt
Provides functions for keeping terminal open and managing subprocess output
"""

import subprocess
import sys
from typing import List, Optional, Any


def wait_for_user(message: str = "Press Enter to close...", timeout: Optional[int] = None):
    """
    Wait for user input before continuing
    
    Args:
        message: Message to display to user
        timeout: Optional timeout in seconds (None = no timeout)
    """
    try:
        if timeout:
            import select
            print(f"\n{message} (timeout in {timeout}s)")
            # Use select for timeout on Unix-like systems
            if hasattr(select, 'select'):
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    sys.stdin.readline()
            else:
                # Fallback for Windows
                input(f"\n{message}")
        else:
            input(f"\n{message}")
    except (EOFError, KeyboardInterrupt):
        print("\n")
    except Exception as e:
        print(f"\nError waiting for input: {e}")


def run_with_output(
    command: List[str],
    show_output: bool = True,
    timeout: Optional[int] = None,
    check: bool = False
) -> subprocess.CompletedProcess:
    """
    Run a subprocess command with optional output display
    
    Args:
        command: Command and arguments as list
        show_output: If True, show command output in terminal
        timeout: Optional timeout in seconds
        check: If True, raise CalledProcessError on non-zero exit
        
    Returns:
        CompletedProcess object with stdout/stderr
    """
    if show_output:
        # Run with output visible in terminal
        print(f"\n{'='*60}")
        print(f"Running: {' '.join(command)}")
        print(f"{'='*60}\n")
        
        result = subprocess.run(
            command,
            timeout=timeout,
            check=check,
            text=True
        )
        
        print(f"\n{'='*60}")
        print(f"Command completed with exit code: {result.returncode}")
        print(f"{'='*60}\n")
        
        return result
    else:
        # Capture output for programmatic use
        return subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            check=check,
            text=True
        )


def run_interactive(
    command: List[str],
    message: str = "Command completed. Press Enter to continue..."
) -> int:
    """
    Run a command interactively and wait for user before continuing
    
    Args:
        command: Command and arguments as list
        message: Message to show after command completes
        
    Returns:
        Exit code of the command
    """
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, text=True)
        exit_code = result.returncode
        
        print(f"\n{'='*60}")
        print(f"Command completed with exit code: {exit_code}")
        print(f"{'='*60}")
        
        wait_for_user(message)
        return exit_code
    except Exception as e:
        print(f"\nError running command: {e}")
        wait_for_user("Press Enter to continue...")
        return 1


def keep_terminal_open(func):
    """
    Decorator to keep terminal open after function execution
    
    Usage:
        @keep_terminal_open
        def my_function():
            # function code
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            wait_for_user()
            return result
        except Exception as e:
            print(f"\nError: {e}")
            wait_for_user()
            raise
    return wrapper


def clear_terminal():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str, width: int = 60):
    """
    Print a formatted header in terminal
    
    Args:
        text: Header text
        width: Width of the header box
    """
    print(f"\n{'='*width}")
    print(f"{text:^{width}}")
    print(f"{'='*width}\n")


def print_section(title: str, content: List[str], width: int = 60):
    """
    Print a formatted section with title and content
    
    Args:
        title: Section title
        content: List of content lines
        width: Width of the section
    """
    print(f"\n{title}")
    print(f"{'-'*len(title)}")
    for line in content:
        print(f"  {line}")
    print()
