"""
IDE Configuration Module
Configures VS Codium (not VS Code) for development tasks
"""

import os
import subprocess
import json
from typing import Dict, List, Optional

class IDEManager:
    """Manages IDE configuration - uses VS Codium instead of VS Code"""
    
    def __init__(self):
        self.ide_name = "VSCodium"
        self.ide_command = "codium"  # VS Codium command
        self.config_dir = os.path.expanduser("~/.config/VSCodium")
        self.is_installed = self.check_installation()
    
    def check_installation(self) -> bool:
        """Check if VS Codium is installed"""
        try:
            result = subprocess.run(
                ['which', self.ide_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_version(self) -> Optional[str]:
        """Get VS Codium version"""
        if not self.is_installed:
            return None
        
        try:
            result = subprocess.run(
                [self.ide_command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # First line is version
                return result.stdout.split('\n')[0]
        except Exception:
            pass
        
        return None
    
    def install_extensions(self, extensions: List[str]) -> Dict[str, bool]:
        """Install VS Codium extensions
        
        Args:
            extensions: List of extension IDs to install
            
        Returns:
            Dict mapping extension ID to success status
        """
        if not self.is_installed:
            return {ext: False for ext in extensions}
        
        results = {}
        for ext in extensions:
            try:
                result = subprocess.run(
                    [self.ide_command, '--install-extension', ext],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results[ext] = result.returncode == 0
            except Exception:
                results[ext] = False
        
        return results
    
    def configure_cuda_support(self, cuda_version: str, cuda_path: str) -> bool:
        """Configure VS Codium for CUDA development
        
        Args:
            cuda_version: CUDA version (e.g., '12.4')
            cuda_path: Path to CUDA installation
            
        Returns:
            True if configuration successful
        """
        if not self.is_installed:
            return False
        
        # Recommended extensions for CUDA development
        cuda_extensions = [
            'ms-vscode.cpptools',  # C/C++ support
            'nvidia.nsight-vscode-edition',  # NVIDIA Nsight (if available on open-vsx)
        ]
        
        # Install extensions
        self.install_extensions(cuda_extensions)
        
        # Create workspace settings
        workspace_settings = {
            "C_Cpp.default.includePath": [
                f"{cuda_path}/include",
                "/usr/include",
                "/usr/local/include"
            ],
            "C_Cpp.default.defines": [
                f"CUDA_VERSION={cuda_version.replace('.', '')}"
            ],
            "C_Cpp.default.compilerPath": f"{cuda_path}/bin/nvcc",
            "files.associations": {
                "*.cu": "cuda-cpp",
                "*.cuh": "cuda-cpp"
            },
            "terminal.integrated.env.linux": {
                "CUDA_HOME": cuda_path,
                "PATH": f"{cuda_path}/bin:${{env:PATH}}",
                "LD_LIBRARY_PATH": f"{cuda_path}/lib64:${{env:LD_LIBRARY_PATH}}"
            }
        }
        
        return True
    
    def configure_python_support(self) -> bool:
        """Configure VS Codium for Python development"""
        if not self.is_installed:
            return False
        
        python_extensions = [
            'ms-python.python',
            'ms-python.vscode-pylance',
        ]
        
        self.install_extensions(python_extensions)
        return True
    
    def open_project(self, project_path: str) -> bool:
        """Open a project in VS Codium
        
        Args:
            project_path: Path to project directory
            
        Returns:
            True if opened successfully
        """
        if not self.is_installed:
            return False
        
        try:
            subprocess.Popen(
                [self.ide_command, project_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            return False
    
    def create_cuda_project_template(self, project_path: str, cuda_version: str) -> bool:
        """Create a CUDA project template
        
        Args:
            project_path: Path where project should be created
            cuda_version: CUDA version to target
            
        Returns:
            True if created successfully
        """
        try:
            os.makedirs(project_path, exist_ok=True)
            
            # Create sample CUDA file
            sample_cu = os.path.join(project_path, "hello_cuda.cu")
            with open(sample_cu, 'w') as f:
                f.write(f"""/*
 * Sample CUDA Program
 * CUDA Version: {cuda_version}
 * Generated by Driver Management Tool using VS Codium
 */

#include <stdio.h>
#include <cuda_runtime.h>

__global__ void hello_cuda() {{
    printf("Hello from GPU thread %d!\\n", threadIdx.x);
}}

int main() {{
    printf("CUDA Version: %d.%d\\n", CUDART_VERSION / 1000, (CUDART_VERSION % 1000) / 10);
    
    // Launch kernel with 10 threads
    hello_cuda<<<1, 10>>>();
    
    // Wait for GPU to finish
    cudaDeviceSynchronize();
    
    return 0;
}}
""")
            
            # Create Makefile
            makefile = os.path.join(project_path, "Makefile")
            with open(makefile, 'w') as f:
                f.write(f"""# CUDA {cuda_version} Project Makefile
# Generated for VS Codium

NVCC = nvcc
CUDA_PATH = /usr/local/cuda-{cuda_version}
CFLAGS = -I$(CUDA_PATH)/include
LDFLAGS = -L$(CUDA_PATH)/lib64 -lcudart

TARGET = hello_cuda
SOURCES = hello_cuda.cu

all: $(TARGET)

$(TARGET): $(SOURCES)
\t$(NVCC) $(CFLAGS) $(LDFLAGS) -o $(TARGET) $(SOURCES)

clean:
\trm -f $(TARGET)

run: $(TARGET)
\t./$(TARGET)

.PHONY: all clean run
""")
            
            # Create README
            readme = os.path.join(project_path, "README.md")
            with open(readme, 'w') as f:
                f.write(f"""# CUDA {cuda_version} Project

This project was generated by the Driver Management Tool.

## Requirements

- CUDA Toolkit {cuda_version}
- NVIDIA Driver (compatible version)
- VS Codium (configured automatically)

## Building

```bash
make
```

## Running

```bash
make run
```

## Development

Open this project in VS Codium:
```bash
codium .
```

The IDE is pre-configured with:
- CUDA IntelliSense
- NVCC compiler integration
- CUDA environment variables
- C/C++ debugging support
""")
            
            # Create VS Codium workspace settings
            vscode_dir = os.path.join(project_path, ".vscode")
            os.makedirs(vscode_dir, exist_ok=True)
            
            settings_file = os.path.join(vscode_dir, "settings.json")
            with open(settings_file, 'w') as f:
                json.dump({
                    "C_Cpp.default.includePath": [
                        f"/usr/local/cuda-{cuda_version}/include"
                    ],
                    "C_Cpp.default.compilerPath": f"/usr/local/cuda-{cuda_version}/bin/nvcc",
                    "files.associations": {
                        "*.cu": "cuda-cpp",
                        "*.cuh": "cuda-cpp"
                    }
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error creating CUDA project: {e}")
            return False
    
    def get_installation_instructions(self) -> str:
        """Get instructions for installing VS Codium"""
        return """
VS Codium Installation Instructions:

VS Codium is an open-source build of VS Code without telemetry.

Install on Ubuntu/Debian:
  wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | gpg --dearmor | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
  echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' | sudo tee /etc/apt/sources.list.d/vscodium.list
  sudo apt update && sudo apt install codium

Install on Fedora/RHEL:
  sudo rpmkeys --import https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg
  printf "[gitlab.com_paulcarroty_vscodium_repo]\\nname=download.vscodium.com\\nbaseurl=https://download.vscodium.com/rpms/\\nenabled=1\\ngpgcheck=1\\nrepo_gpgcheck=1\\ngpgkey=https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg\\nmetadata_expire=1h" | sudo tee -a /etc/yum.repos.d/vscodium.repo
  sudo dnf install codium

Install via Snap:
  sudo snap install codium --classic

Install via Flatpak:
  flatpak install flathub com.vscodium.codium

After installation, the command 'codium' will be available.
"""


# Global IDE manager instance
ide_manager = IDEManager()
