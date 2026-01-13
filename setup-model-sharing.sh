#!/bin/bash
# Model Sharing Setup Script
# Enables LM Studio to access Ollama models via symlinks

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=============================================="
echo "LM Studio ↔ Ollama Model Sharing Setup"
echo "=============================================="
echo ""

# Get actual user (not root if using sudo)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
else
    ACTUAL_USER="$USER"
    ACTUAL_HOME="$HOME"
fi

# Define directories
OLLAMA_MODELS_DIR="$ACTUAL_HOME/.ollama/models"
OLLAMA_BLOBS_DIR="$OLLAMA_MODELS_DIR/blobs"
OLLAMA_MANIFESTS_DIR="$OLLAMA_MODELS_DIR/manifests/registry.ollama.ai/library"
LMSTUDIO_MODELS_DIR="$ACTUAL_HOME/.cache/lm-studio/models"
BACKUP_DIR="$ACTUAL_HOME/.cache/lm-studio/models.backup.$(date +%Y%m%d_%H%M%S)"

# Parse command-line arguments
VERIFY_ONLY=false
ROLLBACK=false
FORCE=false

for arg in "$@"; do
    case $arg in
        --verify)
            VERIFY_ONLY=true
            ;;
        --rollback)
            ROLLBACK=true
            ;;
        --force)
            FORCE=true
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --verify    Only verify the setup, don't make changes"
            echo "  --rollback  Remove symlinks and restore from backup"
            echo "  --force     Force setup even if already configured"
            echo "  --help      Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Verification function
verify_setup() {
    echo -e "${BLUE}Verifying model sharing setup...${NC}"
    echo ""
    
    local errors=0
    
    # Check Ollama installation
    if [ ! -d "$OLLAMA_MODELS_DIR" ]; then
        echo -e "${RED}✗ Ollama models directory not found: $OLLAMA_MODELS_DIR${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✓ Ollama models directory exists${NC}"
    fi
    
    # Check for Ollama models
    if [ ! -d "$OLLAMA_BLOBS_DIR" ] || [ -z "$(ls -A "$OLLAMA_BLOBS_DIR" 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠ No Ollama models found${NC}"
        echo "  Download models with: ollama pull <model-name>"
    else
        local blob_count=$(ls -1 "$OLLAMA_BLOBS_DIR" | wc -l)
        echo -e "${GREEN}✓ Found $blob_count Ollama model blob(s)${NC}"
    fi
    
    # Check LM Studio directory
    if [ ! -d "$LMSTUDIO_MODELS_DIR" ]; then
        echo -e "${YELLOW}⚠ LM Studio models directory not found${NC}"
        echo "  Will be created during setup"
    else
        echo -e "${GREEN}✓ LM Studio models directory exists${NC}"
        
        # Check for symlinks
        local symlink_count=$(find "$LMSTUDIO_MODELS_DIR" -type l 2>/dev/null | wc -l)
        if [ "$symlink_count" -gt 0 ]; then
            echo -e "${GREEN}✓ Found $symlink_count symlink(s) to Ollama models${NC}"
        else
            echo -e "${YELLOW}⚠ No symlinks found (not yet configured)${NC}"
        fi
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ Verification complete - ready for setup${NC}"
        return 0
    else
        echo -e "${RED}❌ Verification failed with $errors error(s)${NC}"
        return 1
    fi
}

# Rollback function
rollback_setup() {
    echo -e "${BLUE}Rolling back model sharing setup...${NC}"
    echo ""
    
    # Find most recent backup
    local latest_backup=$(ls -dt "$ACTUAL_HOME/.cache/lm-studio/models.backup."* 2>/dev/null | head -1)
    
    if [ -z "$latest_backup" ]; then
        echo -e "${YELLOW}⚠ No backup found${NC}"
        echo "  Nothing to rollback"
        return 1
    fi
    
    echo "Found backup: $latest_backup"
    echo ""
    read -p "Restore from this backup? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Rollback cancelled"
        return 0
    fi
    
    # Remove current LM Studio models directory
    if [ -d "$LMSTUDIO_MODELS_DIR" ]; then
        echo "Removing current models directory..."
        rm -rf "$LMSTUDIO_MODELS_DIR"
    fi
    
    # Restore from backup
    echo "Restoring from backup..."
    cp -r "$latest_backup" "$LMSTUDIO_MODELS_DIR"
    
    echo -e "${GREEN}✓ Rollback complete${NC}"
    echo ""
    echo "Original LM Studio models restored"
    echo "You can now delete the backup: $latest_backup"
    
    return 0
}

# Main setup function
setup_model_sharing() {
    echo -e "${BLUE}Setting up model sharing...${NC}"
    echo ""
    
    # Check Ollama is installed
    if [ ! -d "$OLLAMA_MODELS_DIR" ]; then
        echo -e "${RED}✗ Ollama not found${NC}"
        echo ""
        echo "Ollama must be installed first."
        echo "Install with: curl -fsSL https://ollama.ai/install.sh | sh"
        echo ""
        exit 1
    fi
    
    # Check for Ollama models
    if [ ! -d "$OLLAMA_BLOBS_DIR" ] || [ -z "$(ls -A "$OLLAMA_BLOBS_DIR" 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠ No Ollama models found${NC}"
        echo ""
        echo "Download at least one model first:"
        echo "  ollama pull starcoder:3b"
        echo "  ollama pull codellama:7b"
        echo "  ollama pull mistral:7b"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Setup cancelled"
            exit 0
        fi
    fi
    
    # Create LM Studio models directory if it doesn't exist
    echo "Checking LM Studio models directory..."
    if [ ! -d "$LMSTUDIO_MODELS_DIR" ]; then
        echo "Creating $LMSTUDIO_MODELS_DIR"
        mkdir -p "$LMSTUDIO_MODELS_DIR"
        chown "$ACTUAL_USER:$ACTUAL_USER" "$LMSTUDIO_MODELS_DIR" 2>/dev/null || true
    fi
    
    # Backup existing LM Studio models if any
    if [ -d "$LMSTUDIO_MODELS_DIR" ] && [ "$(ls -A "$LMSTUDIO_MODELS_DIR" 2>/dev/null)" ]; then
        echo -e "${BLUE}Backing up existing LM Studio models...${NC}"
        mkdir -p "$BACKUP_DIR"
        cp -r "$LMSTUDIO_MODELS_DIR/"* "$BACKUP_DIR/" 2>/dev/null || true
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$BACKUP_DIR" 2>/dev/null || true
        echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
    fi
    
    # Get list of Ollama models from manifests
    echo ""
    echo -e "${BLUE}Discovering Ollama models...${NC}"
    
    if [ ! -d "$OLLAMA_MANIFESTS_DIR" ]; then
        echo -e "${YELLOW}⚠ No Ollama model manifests found${NC}"
        echo "  Manifests directory: $OLLAMA_MANIFESTS_DIR"
        echo ""
        echo "Falling back to creating generic symlinks..."
        
        # Create generic symlinks for all blobs
        if [ -d "$OLLAMA_BLOBS_DIR" ]; then
            local count=0
            for blob in "$OLLAMA_BLOBS_DIR"/sha256-*; do
                if [ -f "$blob" ]; then
                    local blob_hash=$(basename "$blob" | sed 's/sha256-//')
                    local short_hash=${blob_hash:0:8}
                    local link_name="ollama-model-${short_hash}.gguf"
                    
                    ln -sf "$blob" "$LMSTUDIO_MODELS_DIR/$link_name"
                    echo "  → $link_name"
                    count=$((count + 1))
                fi
            done
            echo -e "${GREEN}✓ Created $count symlink(s)${NC}"
        fi
    else
        # Parse manifests and create named symlinks
        local model_count=0
        
        for model_dir in "$OLLAMA_MANIFESTS_DIR"/*; do
            if [ ! -d "$model_dir" ]; then
                continue
            fi
            
            local model_name=$(basename "$model_dir")
            
            for variant_file in "$model_dir"/*; do
                if [ ! -f "$variant_file" ]; then
                    continue
                fi
                
                local variant=$(basename "$variant_file")
                
                # Parse the manifest to get the blob hash (portable approach)
                local blob_hash=$(grep '"digest":' "$variant_file" 2>/dev/null | head -1 | sed -n 's/.*"sha256:\([a-f0-9]*\)".*/\1/p')
                
                if [ -z "$blob_hash" ]; then
                    continue
                fi
                
                local blob_file="$OLLAMA_BLOBS_DIR/sha256-$blob_hash"
                
                if [ ! -f "$blob_file" ]; then
                    echo -e "${YELLOW}  ⚠ Blob not found for $model_name:$variant${NC}"
                    continue
                fi
                
                # Create symlink with descriptive name
                local link_name="${model_name}-${variant}.gguf"
                local link_path="$LMSTUDIO_MODELS_DIR/$link_name"
                
                # Remove existing symlink if present
                if [ -L "$link_path" ]; then
                    rm "$link_path"
                fi
                
                # Create new symlink
                ln -s "$blob_file" "$link_path"
                
                echo -e "${GREEN}  ✓${NC} $model_name:$variant → $link_name"
                model_count=$((model_count + 1))
            done
        done
        
        echo ""
        echo -e "${GREEN}✓ Created $model_count model symlink(s)${NC}"
    fi
    
    # Fix permissions
    chown -R "$ACTUAL_USER:$ACTUAL_USER" "$LMSTUDIO_MODELS_DIR" 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}✅ Model sharing setup complete!${NC}"
    echo ""
    echo "📝 Summary:"
    echo "  • Ollama models: $OLLAMA_MODELS_DIR"
    echo "  • LM Studio models: $LMSTUDIO_MODELS_DIR"
    echo "  • Backup: $BACKUP_DIR"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Launch LM Studio"
    echo "  2. Go to 'Local Server' tab"
    echo "  3. Select a shared model from the dropdown"
    echo "  4. Click 'Start Server'"
    echo "  5. Launch driver-mgt: driver-mgt-lmstudio"
    echo ""
    echo "📋 Model management:"
    echo "  • Download new models: ollama pull <model-name>"
    echo "  • List models: ollama list"
    echo "  • Re-run this script to sync: bash setup-model-sharing.sh"
    echo ""
}

# Main execution
if [ "$VERIFY_ONLY" = true ]; then
    verify_setup
    exit $?
fi

if [ "$ROLLBACK" = true ]; then
    rollback_setup
    exit $?
fi

# Run verification first
verify_setup || {
    echo ""
    read -p "Verification found issues. Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 1
    fi
}

echo ""

# Check if already set up
if [ -d "$LMSTUDIO_MODELS_DIR" ] && [ "$(find "$LMSTUDIO_MODELS_DIR" -type l 2>/dev/null | wc -l)" -gt 0 ] && [ "$FORCE" != true ]; then
    echo -e "${YELLOW}Model sharing appears to be already configured${NC}"
    echo ""
    read -p "Re-configure anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Use --force to override."
        exit 0
    fi
fi

# Run setup
setup_model_sharing

echo ""
echo "For more information, see:"
echo "  📖 LMSTUDIO_OLLAMA_MODEL_SHARING.md"
echo ""
