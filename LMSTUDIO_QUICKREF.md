# LM Studio Quick Reference Card

## Installation (One-Time Setup)

```bash
# Option 1: Use setup script (Recommended)
bash setup-lmstudio.sh

# Option 2: Manual installation
wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio.AppImage
chmod +x lm-studio.AppImage
./lm-studio.AppImage
```

## First-Time Configuration

### 1. Download Models
```
In LM Studio GUI:
→ Click "Search" tab (🔍)
→ Search for: starcoder, codellama, or mistral
→ Select Q4_K_M or Q5_K_M version
→ Click "Download"
```

### 2. Start Server
```
In LM Studio GUI:
→ Click "Local Server" tab
→ Click "Start Server" button
→ Server starts on http://localhost:1234
```

### 3. Load Model
```
In LM Studio GUI:
→ In "Local Server" tab
→ Click model dropdown at top
→ Select downloaded model
→ Wait for loading (10-30 seconds)
```

### 4. Launch driver-mgt
```bash
driver-mgt-lmstudio
# Or use desktop: "Driver Manager (LLM Studio)"
```

## Daily Usage

```bash
# 1. Start LM Studio
lm-studio  # or ./lm-studio.AppImage

# 2. Ensure server is running (in LM Studio GUI)
#    → "Local Server" tab → "Start Server"

# 3. Launch driver-mgt
driver-mgt-lmstudio
```

## Model Sharing (Save Disk Space!)

```bash
# One-time setup to share models with Ollama
bash setup-model-sharing.sh

# Download models via Ollama (they appear in LM Studio automatically)
ollama pull starcoder:3b

# Verify sharing
ls -la ~/.cache/lm-studio/models/ | grep ^l  # Shows symlinks

# See: LMSTUDIO_OLLAMA_MODEL_SHARING.md for details
```

## Quick Commands

```bash
# Check if LM Studio server is running
curl http://localhost:1234/v1/models

# Check AI status in driver-mgt
driver-mgt ai-status

# View logs
cat ~/.config/driver-mgt/logs/driver-mgt.log

# List downloaded models
ls -lh ~/.cache/lm-studio/models/

# Verify model sharing setup
bash setup-model-sharing.sh --verify
```

## Recommended Models

| Model | Size | Use Case | RAM Required |
|-------|------|----------|--------------|
| starcoder:3b-Q4_K_M | ~2GB | Code/drivers (fast) | 8GB+ |
| codellama:7b-Q4_K_M | ~4GB | Balanced | 8GB+ |
| mistral:7b-Q5_K_M | ~5GB | General purpose | 16GB+ |
| codellama:13b-Q5_K_M | ~9GB | High quality | 16GB+ |
| phi-2-Q4_K_M | ~1.5GB | Lightweight | 8GB+ |

## Troubleshooting

### LM Studio won't start
```bash
# Install FUSE
sudo apt-get install fuse libfuse2

# Or run with extract mode
./lm-studio.AppImage --appimage-extract-and-run
```

### Server not running
```bash
# Check port 1234
sudo netstat -tulpn | grep 1234

# Restart server in LM Studio GUI
# "Local Server" → "Stop Server" → "Start Server"
```

### driver-mgt can't connect
```bash
# 1. Verify LM Studio server
curl http://localhost:1234/v1/models

# 2. Check driver-mgt status
driver-mgt ai-status

# 3. Check logs
cat ~/.config/driver-mgt/logs/driver-mgt.log | tail -50
```

### Model won't download
```bash
# Check internet
ping huggingface.co

# Check disk space
df -h ~/.cache/lm-studio/

# Try different model mirror in LM Studio settings
```

### High RAM usage
```bash
# In LM Studio:
# → Use smaller quantization (Q2_K or Q4_K_M)
# → Reduce context length in settings
# → Unload model when not in use
```

## Configuration Files

```
LM Studio:
  ~/.cache/lm-studio/          # LM Studio config
  ~/.cache/lm-studio/models/   # Downloaded models

driver-mgt:
  ~/.config/driver-mgt/ai-config.json  # AI backend config
  ~/.config/driver-mgt/logs/           # Application logs
```

## Environment Variables

```bash
# Force LM Studio backend
export DRIVER_MGT_AI_BACKEND=lmstudio

# Enable VM bridge
export DRIVER_MGT_ENABLE_VM=true

# Disable telemetry
export DRIVER_MGT_DISABLE_TELEMETRY=true
```

## Ports

```
Default:     http://localhost:1234  (primary)
Additional:  http://localhost:1235  (optional)
Additional:  http://localhost:1236  (optional)
```

## Key Files

```
Launcher:           /usr/local/bin/driver-mgt-lmstudio
Desktop Entry:      /usr/share/applications/driver-mgt-lmstudio.desktop
Setup Script:       ./setup-lmstudio.sh
Full Guide:         ./LMSTUDIO_SETUP.md
```

## Support Links

- **Full Setup Guide**: [LMSTUDIO_SETUP.md](LMSTUDIO_SETUP.md)
- **LM Studio Docs**: https://lmstudio.ai/docs
- **driver-mgt Issues**: https://github.com/jameshroop-art/driver-mgt/issues
- **Model Hub**: https://huggingface.co/models

## Security Notes

✓ All processing is local (localhost only)
✓ No data sent to external servers
✓ Telemetry disabled by driver-mgt launcher
✓ Models downloaded directly from repositories
✓ Complete privacy for driver operations

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-13  
**Print this**: Keep handy for quick reference
