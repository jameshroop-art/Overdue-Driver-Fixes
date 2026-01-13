# LM Studio and Ollama Model Sharing Guide

## Overview

LM Studio and Ollama both use the GGUF (GPT-Generated Unified Format) model format, which means they can share models! This guide explains how to configure LM Studio to access models downloaded via Ollama, avoiding duplicate downloads and saving disk space.

## Benefits of Model Sharing

✅ **Save Disk Space** - No duplicate model downloads (models can be 4-50GB each)
✅ **Faster Setup** - Use existing Ollama models immediately in LM Studio
✅ **Seamless Switching** - Switch between Ollama and LM Studio backends effortlessly
✅ **Single Source of Truth** - Manage models in one place

## Model Storage Locations

### Ollama Model Directory
```bash
# Primary location (user models)
~/.ollama/models/

# System location (if installed system-wide)
/usr/share/ollama/.ollama/models/

# Check which location is used
ls -la ~/.ollama/models/ 2>/dev/null && echo "User location exists" || echo "User location not found"
```

### LM Studio Model Directory
```bash
# Default location
~/.cache/lm-studio/models/

# Can be changed in LM Studio Settings → Storage
```

## Model Format Compatibility

Both systems use **GGUF format** (llama.cpp):
- ✅ Fully compatible between Ollama and LM Studio
- ✅ No conversion needed
- ✅ Same quantization levels (Q4_K_M, Q5_K_M, Q8_0, etc.)

## Method 1: Symlink Ollama Models to LM Studio (Recommended)

This method creates symbolic links from LM Studio's model directory to Ollama's models, making them appear in LM Studio.

### Automatic Setup Script

We provide a script to automate this process:

```bash
# Run the model sharing setup
bash setup-model-sharing.sh
```

### Manual Setup

```bash
# 1. Create LM Studio models directory if it doesn't exist
mkdir -p ~/.cache/lm-studio/models/

# 2. Find Ollama models
OLLAMA_MODELS=~/.ollama/models/manifests/registry.ollama.ai/library/

# 3. For each Ollama model, create a symlink
# Example for starcoder:3b
cd ~/.cache/lm-studio/models/
ln -s ~/.ollama/models/blobs/<blob-hash> starcoder-3b.gguf

# 4. Restart LM Studio to detect new models
```

**Note**: Ollama stores models with blob hashes, so we'll need to identify the correct blob for each model.

## Method 2: Configure LM Studio Model Path

LM Studio can be configured to use custom model directories.

### Via LM Studio GUI

1. Open LM Studio
2. Click Settings (gear icon)
3. Navigate to **Storage** section
4. Under "Model Directories":
   - Click **"Add Directory"**
   - Browse to: `~/.ollama/models/`
   - Click **"Apply"**
5. Restart LM Studio
6. Models from Ollama should now appear in LM Studio's model list

### Via Configuration File

Edit LM Studio's configuration directly:

```bash
# LM Studio config location
~/.cache/lm-studio/config.json

# Add Ollama model path
{
  "modelPaths": [
    "~/.cache/lm-studio/models",
    "~/.ollama/models"
  ]
}
```

## Method 3: Environment Variable (Advanced)

Set environment variable to specify additional model paths:

```bash
# Add to ~/.bashrc or ~/.zshrc
export LM_STUDIO_MODEL_PATH="$HOME/.cache/lm-studio/models:$HOME/.ollama/models"

# Launch LM Studio
lm-studio
```

## Automated Setup Script

### Using setup-model-sharing.sh

```bash
# Download and run the setup script
bash setup-model-sharing.sh

# What it does:
# 1. Detects Ollama installation and models
# 2. Identifies Ollama model locations
# 3. Creates organized symlinks in LM Studio's model directory
# 4. Provides human-readable names for models
# 5. Tests accessibility
# 6. Reports available models
```

### Script Features

- ✅ Automatic Ollama model discovery
- ✅ Intelligent blob-to-model mapping
- ✅ Human-readable filenames
- ✅ Backup existing LM Studio models
- ✅ Verification and testing
- ✅ Rollback option if issues occur

## Model Management

### List Available Models

```bash
# List Ollama models
ollama list

# List LM Studio models (after sharing setup)
ls -lh ~/.cache/lm-studio/models/

# Check symlinks
ls -la ~/.cache/lm-studio/models/ | grep ^l
```

### Verify Model Sharing

```bash
# In LM Studio:
# 1. Open "Search" or "Models" tab
# 2. Look for models you downloaded via Ollama
# 3. Try loading one to verify it works

# Or test via CLI
curl http://localhost:1234/v1/models
# Should show both LM Studio and Ollama models
```

### Download New Models

You can download models using either tool:

**Via Ollama**:
```bash
ollama pull starcoder:3b
# Model is immediately available in LM Studio (if sharing is set up)
```

**Via LM Studio**:
```bash
# In LM Studio GUI:
# Search → Download model → Automatically available to both
```

## Model Naming Conventions

Ollama and LM Studio use different naming conventions:

### Ollama Format
```
starcoder:3b
codellama:7b-instruct
mistral:7b-instruct-v0.2
```

### LM Studio Format
```
starcoder-3b-Q4_K_M.gguf
codellama-7b-instruct-Q5_K_M.gguf
mistral-7b-instruct-v0.2-Q4_K_M.gguf
```

The setup script handles these naming differences automatically.

## Ollama Model Blob Structure

Ollama stores models as content-addressed blobs:

```
~/.ollama/models/
├── blobs/
│   └── sha256-<hash>       # Actual model files
└── manifests/
    └── registry.ollama.ai/
        └── library/
            └── starcoder/
                └── 3b       # Model manifest
```

To find which blob corresponds to a model:

```bash
# Check model manifest
cat ~/.ollama/models/manifests/registry.ollama.ai/library/starcoder/3b

# Look for the "digest" field - this is the blob hash
# Example: "digest": "sha256:abc123..."
```

## Troubleshooting

### Models Not Appearing in LM Studio

**Issue**: Ollama models don't show up in LM Studio

**Solutions**:
1. Restart LM Studio after setting up model sharing
2. Check symlinks are valid:
```bash
ls -la ~/.cache/lm-studio/models/
# Should show symlinks pointing to ~/.ollama/models/
```

3. Verify file permissions:
```bash
ls -l ~/.ollama/models/blobs/
# Should be readable by your user
```

4. Check LM Studio logs:
```bash
cat ~/.cache/lm-studio/logs/*.log
```

### Broken Symlinks

**Issue**: Symlinks pointing to non-existent files

**Solution**:
```bash
# Remove broken symlinks
find ~/.cache/lm-studio/models/ -xtype l -delete

# Re-run setup
bash setup-model-sharing.sh
```

### Model Format Issues

**Issue**: LM Studio says model format is incompatible

**Solution**:
- Verify model is GGUF format:
```bash
file ~/.ollama/models/blobs/sha256-*
# Should mention "GGUF" or show as binary data
```

- Some very old models might use older formats (GGML)
- Download latest version of the model via Ollama

### Permission Denied

**Issue**: Cannot access Ollama models

**Solution**:
```bash
# Fix permissions on Ollama models
chmod -R u+r ~/.ollama/models/

# If models are in system directory
sudo chmod -R a+r /usr/share/ollama/.ollama/models/
```

### Disk Space Still Used

**Issue**: Symlinks don't seem to save space

**Check**:
```bash
# Verify symlinks (not copies)
ls -la ~/.cache/lm-studio/models/ | grep ^l

# If showing regular files (not symlinks), something went wrong
# Models were copied instead of linked
```

**Fix**:
```bash
# Remove copies from LM Studio
rm ~/.cache/lm-studio/models/*.gguf

# Re-run setup script with symlink option
bash setup-model-sharing.sh --symlink
```

## Disk Space Savings Example

Without model sharing:
```
Ollama models:    ~/.ollama/models/         (20GB)
LM Studio models: ~/.cache/lm-studio/       (20GB)
Total:                                       40GB ❌
```

With model sharing:
```
Ollama models:    ~/.ollama/models/         (20GB)
LM Studio models: ~/.cache/lm-studio/       (symlinks, ~0GB)
Total:                                       20GB ✅
```

**Savings: 20GB (50% reduction)**

## Best Practices

### 1. Use Ollama as Primary Model Manager
- Download models via Ollama CLI
- Organize and manage through Ollama
- LM Studio automatically sees new models

### 2. Regular Cleanup
```bash
# Remove unused models from Ollama
ollama rm <model-name>

# Sync LM Studio (re-run setup)
bash setup-model-sharing.sh
```

### 3. Consistent Naming
- Use Ollama's naming convention for organization
- Setup script handles conversion to LM Studio format

### 4. Backup Before Major Changes
```bash
# Backup LM Studio config
cp -r ~/.cache/lm-studio ~/.cache/lm-studio.backup

# Backup Ollama models manifest
cp -r ~/.ollama/models/manifests ~/.ollama/models/manifests.backup
```

## Integration with driver-mgt

driver-mgt automatically handles both backends:

```bash
# Works with Ollama
driver-mgt

# Works with LM Studio (using shared models)
driver-mgt-lmstudio

# Check which models are available
driver-mgt ai-status
```

driver-mgt will:
- ✅ Detect models from both backends
- ✅ Use shared models transparently
- ✅ Report available models correctly
- ✅ No configuration needed if model sharing is set up

## Advanced: Bidirectional Sync

For truly seamless operation, you can set up bidirectional synchronization:

```bash
# Create a shared models directory
mkdir -p ~/ai-models

# Symlink both to shared directory
rm -rf ~/.ollama/models/blobs
ln -s ~/ai-models/blobs ~/.ollama/models/blobs

rm -rf ~/.cache/lm-studio/models
ln -s ~/ai-models/lmstudio ~/.cache/lm-studio/models

# Both tools now share the same model storage
```

**Warning**: This is advanced and may require adjusting Ollama and LM Studio configurations.

## Model Conversion (If Needed)

In rare cases, you might need to convert between formats:

```bash
# Convert GGML (old) to GGUF (new)
# Install llama.cpp tools
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Convert model
./convert.py <model-path>
```

**Note**: Most modern models are already in GGUF format.

## Security Considerations

✅ **Safe**: Symlinks don't duplicate sensitive data
✅ **Isolated**: Each tool maintains its own configuration
✅ **Auditable**: Easy to see what's shared (ls -la)
⚠️ **Permissions**: Ensure proper file permissions on shared models

## Future Enhancements

Potential improvements:
- Automatic model sync daemon
- Unified model management CLI
- Model version tracking
- Automatic cleanup of unused models

## Additional Resources

- **Ollama Model Library**: https://ollama.ai/library
- **LM Studio Documentation**: https://lmstudio.ai/docs
- **GGUF Format Spec**: https://github.com/ggerganov/llama.cpp/blob/master/gguf-py/README.md
- **driver-mgt AI Docs**: [LLM_STUDIO_FEATURES.md](LLM_STUDIO_FEATURES.md)

## Support

If you encounter issues with model sharing:

1. Check logs:
```bash
cat ~/.config/driver-mgt/logs/driver-mgt.log
cat ~/.cache/lm-studio/logs/*.log
```

2. Verify setup:
```bash
bash setup-model-sharing.sh --verify
```

3. Report issues:
   - driver-mgt: https://github.com/jameshroop-art/driver-mgt/issues
   - Include output of verification script

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-13  
**Tested with**: Ollama 0.1.20+, LM Studio 0.2.0+
