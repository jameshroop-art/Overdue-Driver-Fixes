# Ollama Sign-In Guide

## Overview

Some AI models in Ollama (like starcoder:3b) may require authentication before you can download them. This guide explains how to sign in to Ollama using Google authentication.

## Why Sign-In is Required

- **Private/Restricted Models**: Some models require authentication to access
- **Cloud Features**: Certain Ollama cloud features need authentication
- **Publishing Models**: If you want to publish your own models to Ollama

## How to Sign In

### Method 1: Using the GUI

1. **Open driver-mgt application**
   ```bash
   ./driver-mgt
   ```

2. **Navigate to any device tab** that has the AI Chat interface

3. **Click "Sign In to Ollama"** button (located next to "Enable Chat" checkbox)

4. **Follow the prompts**:
   - A confirmation dialog will appear
   - Click "Yes" to proceed
   - Your browser will open for Google authentication
   - Sign in with your Google account
   - Authorization will be cached locally

5. **After successful sign-in**:
   - You'll see a success message in the GUI
   - You can now install models that require authentication

### Method 2: Using the Command Line

1. **Run the sign-in command**:
   ```bash
   ./driver-mgt ai-signin
   ```

2. **Follow the terminal prompts**:
   - Press Enter to continue
   - Your browser will open for authentication
   - Sign in with your Google account
   - Return to the terminal to see the result

3. **Alternative: Direct ollama command**:
   ```bash
   ollama signin
   ```

## After Signing In

Once you're signed in, you can:

1. **Install the starcoder model**:
   ```bash
   ollama pull starcoder:3b
   ```

2. **Or let the application do it automatically** when enabling AI chat

## Troubleshooting

### "ollama command not found"

**Problem**: Ollama is not installed or not in your PATH

**Solution**:
1. Install Ollama: Visit https://ollama.ai/
2. Or install via script:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

### "Ollama is not running"

**Problem**: The Ollama service isn't started

**Solution**:
```bash
# Start Ollama service
sudo systemctl start ollama

# Or run Ollama manually
ollama serve
```

### "Sign-in timed out"

**Problem**: The authentication process took too long

**Solution**:
- Try again and complete the authentication faster
- Check your internet connection
- Ensure your browser isn't blocking the authentication page

### "Authentication error" during model pull

**Problem**: Credentials may have expired or weren't saved properly

**Solution**:
1. Sign in again:
   ```bash
   ./driver-mgt ai-signin
   ```
2. Try pulling the model again

### Browser doesn't open

**Problem**: No default browser is set or browser is blocked

**Solution**:
1. The terminal will show a URL
2. Manually copy and paste the URL into your browser
3. Complete the authentication
4. Return to the terminal

## Privacy & Security

- **Credentials Storage**: Authentication tokens are stored locally by Ollama
- **Location**: Typically in `~/.ollama/` directory
- **Google OAuth**: Uses standard Google OAuth 2.0 flow
- **No Password Storage**: Your Google password is never stored

## Checking Sign-In Status

To check if you're currently signed in and view available models:

```bash
# Check Ollama status
./driver-mgt ai-status

# List installed models
ollama list
```

## Sign Out

To sign out and remove stored credentials:

```bash
# Remove Ollama credentials
rm -rf ~/.ollama/credentials
```

## Additional Resources

- **Ollama Documentation**: https://docs.ollama.com/
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Google OAuth**: https://developers.google.com/identity/protocols/oauth2

## Common Workflows

### First-Time Setup

1. Install Ollama
2. Start Ollama service
3. Sign in: `./driver-mgt ai-signin`
4. Install model: `ollama pull starcoder:3b`
5. Enable AI chat in driver-mgt

### Using AI Chat After Sign-In

1. Open driver-mgt GUI
2. Go to any device tab
3. Check "Enable Chat" checkbox
4. Start chatting with the AI assistant

### Troubleshooting Installation Issues

If you see "HTTP 404" errors in the chat:

1. Check if model is installed: `ollama list`
2. If not installed, try: `ollama pull starcoder:3b`
3. If authentication error, run: `./driver-mgt ai-signin`
4. Retry model installation

## Support

If you continue to experience issues:

1. Check the main README.md
2. Review logs in `~/.config/driver-mgt/logs/`
3. Report issues on GitHub with detailed error messages
