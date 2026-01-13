# LM Studio Installation and Setup Guide

## Overview

LM Studio is a local AI model runtime that provides an OpenAI-compatible API for running large language models on your machine. This guide will help you install LM Studio, configure it for localhost access, and enable it to download additional models from online servers.

## System Requirements

- **Operating System**: Linux (x64 architecture)
- **RAM**: Minimum 8GB (16GB+ recommended for larger models)
- **Disk Space**: At least 20GB free for models
- **CPU**: Modern multi-core processor (AVX2 support recommended)
- **GPU**: Optional but recommended (NVIDIA/AMD with CUDA/ROCm support)

## Installation

### Step 1: Download LM Studio

Download the latest Linux version from the official website:

```bash
# Download LM Studio for Linux x64
wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio-linux-x64.AppImage

# Or use curl
curl -L https://lmstudio.ai/download/latest/linux/x64 -o lm-studio-linux-x64.AppImage
```

**Note**: The download link will automatically get the latest version for Linux x64 systems.

### Step 2: Make the AppImage Executable

```bash
# Make the downloaded file executable
chmod +x lm-studio-linux-x64.AppImage
```

### Step 3: Install AppImage Support (if needed)

If you haven't run AppImages before, you may need FUSE:

```bash
# For Debian/Ubuntu
sudo apt-get install fuse libfuse2

# For Fedora/RHEL
sudo dnf install fuse fuse-libs

# For Arch Linux
sudo pacman -S fuse2
```

### Step 4: Optional - Move to System Location

For easier access, you can move LM Studio to a standard location:

```bash
# Create applications directory if it doesn't exist
mkdir -p ~/.local/bin

# Move the AppImage
mv lm-studio-linux-x64.AppImage ~/.local/bin/lm-studio

# Or install system-wide (requires sudo)
sudo mv lm-studio-linux-x64.AppImage /opt/lm-studio
sudo ln -s /opt/lm-studio /usr/local/bin/lm-studio
```

### Step 5: Launch LM Studio

```bash
# If installed in ~/.local/bin (make sure it's in your PATH)
lm-studio

# If installed system-wide
/usr/local/bin/lm-studio

# Or run directly
./lm-studio-linux-x64.AppImage
```

## Localhost Configuration

### Step 1: Start the Server

1. Launch LM Studio application
2. Navigate to the **"Local Server"** tab in the left sidebar
3. Click **"Start Server"** button

The server will start on `http://localhost:1234` by default.

### Step 2: Configure Server Settings

In the Local Server tab:

1. **Port Configuration**:
   - Default port: `1234`
   - To use a different port, change the port number in settings
   - Click "Restart Server" to apply changes

2. **CORS Settings**:
   - Enable "Allow CORS" for local applications
   - This allows driver-mgt to communicate with LM Studio

3. **Auto-start Option**:
   - Check "Start server on launch" for automatic startup
   - Server will be ready when LM Studio opens

### Step 3: Verify Server is Running

Test the server connection:

```bash
# Check server status
curl http://localhost:1234/v1/models

# Should return JSON with available models
# Example response:
# {"object":"list","data":[...]}
```

### Step 4: Configure Multiple Instances (Optional)

driver-mgt supports up to 3 concurrent LM Studio instances:

1. **Primary instance**: Port 1234 (default)
2. **Additional instances**: Ports 1235, 1236

To run multiple instances:
```bash
# Instance 1 (default)
lm-studio --port 1234

# Instance 2 (separate terminal)
lm-studio --port 1235

# Instance 3 (separate terminal)
lm-studio --port 1236
```

**Note**: Check LM Studio documentation for exact command-line syntax as it may vary.

## Downloading Additional Models

LM Studio includes a built-in model downloader with access to various model repositories.

### Step 1: Access Model Search

1. In LM Studio, click the **"🔍 Search"** tab (usually the home/first tab)
2. You'll see the model search interface

### Step 2: Browse Available Models

LM Studio provides access to models from:
- **Hugging Face** - Largest repository of open-source models
- **LM Studio Community** - Curated collection of optimized models
- **Direct GGUF files** - Import your own quantized models

### Step 3: Search for Models

Use the search bar to find models:

```
Popular models for driver management:
- starcoder - Code-focused model (recommended)
- codellama - Meta's code model
- mistral - General-purpose, fast
- llama2 - Versatile, well-tested
- phi-2 - Compact, efficient
```

### Step 4: Select and Download

1. Click on a model card to view details
2. Choose quantization level (affects size vs. quality):
   - **Q4_K_M** - Good balance (recommended for most systems)
   - **Q5_K_M** - Higher quality, larger size
   - **Q8_0** - Very high quality, requires more RAM
   - **Q2_K** - Smallest, faster but lower quality

3. Click **"Download"** button
4. Monitor download progress in the interface

### Step 5: Load Downloaded Models

Once downloaded:
1. Navigate to **"Local Server"** tab
2. Click the model dropdown at the top
3. Select your downloaded model from the list
4. The model will load into memory (may take 10-30 seconds)

### Step 6: Verify Model is Loaded

Test the loaded model:

```bash
# Check available models
curl http://localhost:1234/v1/models

# Test chat completion
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "starcoder",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

## Enabling Online Model Downloads

LM Studio's model download capability is enabled by default. However, here's how to ensure it works properly:

### Network Configuration

1. **Firewall Settings**:
   - Ensure outbound HTTPS (port 443) is allowed
   - LM Studio needs access to Hugging Face and model repositories

```bash
# Check if you can reach Hugging Face
curl -I https://huggingface.co

# Should return HTTP 200 or 301
```

2. **Proxy Configuration** (if behind corporate proxy):
   
   Set environment variables before launching LM Studio:
   ```bash
   export HTTP_PROXY="http://proxy.example.com:8080"
   export HTTPS_PROXY="http://proxy.example.com:8080"
   lm-studio
   ```

3. **DNS Resolution**:
   ```bash
   # Verify DNS works
   nslookup huggingface.co
   ```

### Download Location

By default, LM Studio stores models in:
```
~/.cache/lm-studio/models/
```

To change the download location:
1. Open LM Studio Settings (gear icon)
2. Navigate to "Storage" section
3. Change "Model Storage Path"
4. Click "Apply"

### Sharing Models with Ollama

**💡 Save disk space by sharing models between LM Studio and Ollama!**

Both LM Studio and Ollama use the same GGUF model format, so they can share models. This avoids downloading the same models twice (saving 4-50GB per model).

**📖 Complete Guide**: [LMSTUDIO_OLLAMA_MODEL_SHARING.md](LMSTUDIO_OLLAMA_MODEL_SHARING.md)

**Quick Setup**:
```bash
# Run the automated setup script
bash setup-model-sharing.sh

# This creates symlinks so LM Studio can access Ollama models
# No duplication, no conversion needed!
```

**Benefits**:
- ✅ Save 50% or more disk space
- ✅ Use models downloaded via Ollama in LM Studio
- ✅ Seamless switching between backends
- ✅ Single source of truth for model management

See [LMSTUDIO_OLLAMA_MODEL_SHARING.md](LMSTUDIO_OLLAMA_MODEL_SHARING.md) for detailed instructions.

### Managing Downloaded Models

View and manage your models:
```bash
# List downloaded models
ls -lh ~/.cache/lm-studio/models/

# Check disk usage
du -sh ~/.cache/lm-studio/models/

# Remove unused models (via LM Studio GUI)
# Right-click model -> Delete
```

## Integration with driver-mgt

### Automatic Integration

driver-mgt will automatically detect LM Studio if it's running:

```bash
# Check if LM Studio is detected
driver-mgt ai-status

# Launch driver-mgt with LM Studio
driver-mgt-lmstudio
```

### Manual Configuration

If automatic detection fails, configure manually:

1. Edit `~/.config/driver-mgt/ai-config.json`:
```json
{
  "backend": "lmstudio",
  "lmstudio": {
    "host": "localhost",
    "port": 1234,
    "additional_ports": [1235, 1236]
  }
}
```

2. Restart driver-mgt:
```bash
driver-mgt-lmstudio
```

### Using the LM Studio Launcher

driver-mgt includes a dedicated launcher for LM Studio mode:

**Desktop Launcher**:
- Search for "Driver Manager (LLM Studio)" in applications menu
- Click to launch

**Command Line**:
```bash
driver-mgt-lmstudio
```

The launcher will:
- ✓ Check if LM Studio is running
- ✓ Verify server connectivity
- ✓ Configure environment variables
- ✓ Launch driver-mgt in LM Studio mode
- ✓ Enable VM bridge features
- ✓ Disable telemetry for privacy

## Troubleshooting

### LM Studio Won't Start

**Issue**: AppImage doesn't launch

**Solutions**:
```bash
# Check FUSE is installed
which fusermount

# If not installed (Debian/Ubuntu)
sudo apt-get install fuse libfuse2

# Try running with --appimage-extract-and-run
./lm-studio-linux-x64.AppImage --appimage-extract-and-run
```

### Server Not Starting

**Issue**: Local server fails to start

**Solutions**:
1. Check if port 1234 is already in use:
```bash
sudo netstat -tulpn | grep 1234
# or
sudo ss -tulpn | grep 1234
```

2. Kill process using the port:
```bash
sudo kill -9 <PID>
```

3. Use a different port in LM Studio settings

### Model Downloads Fail

**Issue**: Cannot download models

**Solutions**:
1. **Check internet connection**:
```bash
ping -c 4 huggingface.co
```

2. **Check disk space**:
```bash
df -h ~/.cache/lm-studio/
```

3. **Clear download cache**:
```bash
rm -rf ~/.cache/lm-studio/downloads/*
```

4. **Check firewall**:
```bash
# Temporarily disable to test (Debian/Ubuntu)
sudo ufw status
sudo ufw allow out 443/tcp

# Fedora
sudo firewall-cmd --list-all
```

### driver-mgt Cannot Connect

**Issue**: driver-mgt can't detect LM Studio

**Solutions**:
1. **Verify LM Studio server is running**:
```bash
curl http://localhost:1234/v1/models
```

2. **Check LM Studio server settings**:
   - Ensure "Start Server" is clicked
   - Verify port is 1234
   - Enable CORS if disabled

3. **Test with driver-mgt**:
```bash
driver-mgt ai-status
```

4. **Check logs**:
```bash
cat ~/.config/driver-mgt/logs/driver-mgt.log
```

### Models Not Appearing

**Issue**: Downloaded models don't show in driver-mgt

**Solutions**:
1. Ensure model is loaded in LM Studio:
   - Go to "Local Server" tab
   - Select model from dropdown
   - Wait for loading to complete

2. Refresh model list in driver-mgt:
   - Open "AI Settings" tab
   - Click "Refresh Models"

3. Restart LM Studio server

### High Resource Usage

**Issue**: LM Studio consuming too much RAM/CPU

**Solutions**:
1. **Use smaller quantization**:
   - Switch to Q4_K_M or Q2_K models
   - These use less RAM

2. **Unload unused models**:
   - Only keep one model loaded at a time

3. **Adjust context size**:
   - In LM Studio, reduce "Context Length"
   - Lower values use less memory

4. **Enable GPU acceleration** (if available):
   - Check LM Studio settings for GPU options
   - Offload layers to GPU

## Performance Optimization

### GPU Acceleration

If you have an NVIDIA or AMD GPU:

1. **NVIDIA (CUDA)**:
```bash
# Check if CUDA is available
nvidia-smi

# LM Studio will auto-detect and use CUDA
```

2. **AMD (ROCm)**:
```bash
# Check ROCm
rocm-smi

# LM Studio may support ROCm (check version)
```

### Memory Management

Optimize RAM usage:
```
Recommended quantization by RAM:
- 8GB RAM:  Q2_K or Q4_K_M (7B models)
- 16GB RAM: Q4_K_M or Q5_K_M (7B-13B models)
- 32GB RAM: Q5_K_M or Q8_0 (13B-33B models)
- 64GB RAM: Q8_0 (70B models possible)
```

### Model Selection for driver-mgt

Best models for driver management tasks:
1. **starcoder** (3B-7B) - Specialized for code/drivers
2. **codellama** (7B-13B) - Good balance
3. **mistral** (7B) - Fast, general-purpose
4. **phi-2** (2.7B) - Compact, efficient

## Security Considerations

### Local-Only Operation

LM Studio runs entirely on localhost:
- ✓ No data sent to external servers
- ✓ All processing is local
- ✓ Complete privacy

### driver-mgt Security Features

When using LM Studio with driver-mgt:
- ✓ Domain whitelist enforced
- ✓ Filesystem access restricted
- ✓ No telemetry when launched via `driver-mgt-lmstudio`
- ✓ Audit logging enabled
- ✓ Security violations logged

### Disabling Telemetry

The `driver-mgt-lmstudio` launcher automatically disables LM Studio telemetry:
```bash
# Launches with DRIVER_MGT_DISABLE_TELEMETRY=true
driver-mgt-lmstudio
```

Or manually:
```bash
export DRIVER_MGT_DISABLE_TELEMETRY=true
driver-mgt
```

## Advanced Configuration

### Custom Model Repositories

Add custom model sources in LM Studio:
1. Settings → Model Sources
2. Add custom URL or Hugging Face organization
3. Models from these sources will appear in search

### API Key Configuration (if needed)

Some models may require API keys:
1. Get API key from model provider
2. In LM Studio: Settings → API Keys
3. Add key for specific provider

### Multiple Concurrent Models

Run multiple models on different ports:
```bash
# Terminal 1: Primary model on 1234
lm-studio --port 1234 --model starcoder

# Terminal 2: Secondary model on 1235
lm-studio --port 1235 --model mistral
```

driver-mgt will detect all instances automatically.

## Model Recommendations

### For Low-End Systems (8-16GB RAM)
- **starcoder:3b-Q4_K_M** - Fast, code-focused
- **phi-2-Q4_K_M** - Compact, efficient
- **mistral-7b-Q2_K** - Smallest viable

### For Mid-Range Systems (16-32GB RAM)
- **codellama-7b-Q5_K_M** - Balanced
- **mistral-7b-Q5_K_M** - Fast, accurate
- **starcoder-7b-Q5_K_M** - Best for drivers

### For High-End Systems (32GB+ RAM)
- **codellama-13b-Q8_0** - High quality
- **deepseek-coder-33b-Q5_K_M** - Advanced
- **mixtral-8x7b-Q4_K_M** - State-of-the-art

## Additional Resources

### Official Documentation
- LM Studio Website: https://lmstudio.ai/
- LM Studio Docs: https://lmstudio.ai/docs
- Model Hub: https://huggingface.co/

### driver-mgt Documentation
- Main README: [README.md](README.md)
- Quick Start: [QUICKSTART_UPDATED.md](QUICKSTART_UPDATED.md)
- LM Studio Features: [LLM_STUDIO_FEATURES.md](LLM_STUDIO_FEATURES.md)
- VM Bridge Docs: [VM_DRIVER_BRIDGE_DOCS.md](VM_DRIVER_BRIDGE_DOCS.md)

### Community Resources
- Hugging Face Forums: https://discuss.huggingface.co/
- Model Leaderboard: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- GGUF Quantization Guide: https://github.com/ggerganov/llama.cpp

## Support

### Getting Help

1. **Check logs**:
```bash
# LM Studio logs (if available)
cat ~/.cache/lm-studio/logs/lm-studio.log

# driver-mgt logs
cat ~/.config/driver-mgt/logs/driver-mgt.log
```

2. **Test connectivity**:
```bash
# Verify LM Studio API
curl -v http://localhost:1234/v1/models

# Check driver-mgt status
driver-mgt ai-status
```

3. **Report issues**:
   - driver-mgt issues: https://github.com/jameshroop-art/driver-mgt/issues
   - LM Studio issues: https://lmstudio.ai/support

---

## Quick Reference

### Essential Commands

```bash
# Download LM Studio
wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio.AppImage
chmod +x lm-studio.AppImage

# Launch LM Studio
./lm-studio.AppImage

# Test LM Studio server
curl http://localhost:1234/v1/models

# Launch driver-mgt with LM Studio
driver-mgt-lmstudio

# Check AI status
driver-mgt ai-status

# View logs
cat ~/.config/driver-mgt/logs/driver-mgt.log
```

### Default Locations

```
LM Studio AppImage:    ~/Downloads/lm-studio-linux-x64.AppImage
LM Studio Config:      ~/.cache/lm-studio/
Downloaded Models:     ~/.cache/lm-studio/models/
driver-mgt Config:     ~/.config/driver-mgt/
driver-mgt Logs:       ~/.config/driver-mgt/logs/
```

### Default Ports

```
LM Studio Primary:     http://localhost:1234
LM Studio Instance 2:  http://localhost:1235
LM Studio Instance 3:  http://localhost:1236
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-13  
**Compatible with**: driver-mgt v1.0+, LM Studio 0.2.0+
