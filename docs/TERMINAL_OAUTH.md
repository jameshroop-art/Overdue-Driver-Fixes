# Terminal OAuth Authentication for Ollama

## Overview

The application now supports direct terminal-to-website OAuth authentication for Ollama, allowing seamless Google sign-in through the terminal with browser verification.

## How It Works

### Authentication Flow

1. **Terminal Connection**: The terminal establishes a connection with Ollama's authentication service
2. **Browser Launch**: Ollama opens your default browser to Google OAuth page
3. **Real-Time Feedback**: Terminal shows authentication URL and progress
4. **Verification**: After browser sign-in, verification callback is handled through terminal
5. **Credential Caching**: Successful authentication stores tokens locally

### Terminal Output Example

```
============================================================
Ollama Sign-In - Google OAuth Authentication
============================================================

This will communicate with Ollama's authentication service
and open your browser for Google sign-in.
The verification will be handled through this terminal.

Authentication flow:
  1. Terminal connects to Ollama auth service
  2. Browser opens for Google OAuth
  3. After sign-in, verification code is sent to terminal
  4. Credentials cached locally for future use

Press Enter to continue or Ctrl+C to cancel...

Initiating OAuth flow...
Connecting to Ollama authentication service...

------------------------------------------------------------
Opening browser for authentication...
→ Browser window should open automatically
→ If not, copy the URL above and open it manually

→ Waiting for verification from browser...
------------------------------------------------------------

✓ Successfully signed in to Ollama!
✓ Credentials cached locally
✓ You can now pull models that require authentication
```

## Usage

### During Installation

The install script now prompts for Ollama sign-in:

```bash
sudo ./install.sh
```

When prompted:
```
============================================
Ollama Sign-In Required
============================================
The starcoder:3b model requires authentication.
This will open your browser for Google sign-in.

Sign in to Ollama now? (Y/n): 
```

Press `Y` or Enter to proceed with authentication.

### Manual Sign-In (CLI)

Sign in anytime using the CLI:

```bash
./driver-mgt ai-signin
```

Or directly with Ollama:

```bash
ollama signin
```

### Programmatic Sign-In (Python API)

```python
from ai.ollama_manager import OllamaManager
from core.config import ConfigManager

config = ConfigManager()
ollama = OllamaManager(config)

# Interactive mode (default)
result = ollama.signin(interactive=True)

# Non-interactive mode (auto-proceed)
result = ollama.signin(interactive=False)

if result['success']:
    print("✓ Signed in successfully")
else:
    print(f"✗ Error: {result['error']}")
```

## Features

### Real-Time Output Streaming

- Shows OAuth URL in terminal immediately
- Displays verification status updates
- Streams all authentication service messages
- Progress indicators for each step

### Intelligent Error Handling

**Browser Not Opening:**
```
→ Browser window should open automatically
→ If not, copy the URL above and open it manually
```

**Authentication Timeout:**
```
✗ Sign-in timed out after 5 minutes.
Please try again and complete the authentication faster.
```

**Ollama Not Installed:**
```
✗ 'ollama' command not found. Please install Ollama first.
Install with: curl -fsSL https://ollama.ai/install.sh | sh
```

**User Cancellation:**
```
Sign-in cancelled by user.
```

### Security Features

- **Credentials Stored Locally**: Tokens cached in `~/.ollama/` directory
- **Google OAuth**: Uses standard Google OAuth 2.0 protocol
- **No Password Storage**: Your Google password is never stored
- **User Context**: Authentication runs as actual user, not root

## Installation Script Integration

The installation script automatically:

1. Installs Ollama if not present
2. Starts Ollama service
3. **Prompts for OAuth sign-in** (new)
4. **Runs authentication as actual user** (not root)
5. Pulls starcoder:3b model

This ensures proper credential storage and permissions.

## Troubleshooting

### Browser Doesn't Open

**Problem**: Terminal shows auth URL but browser doesn't open automatically

**Solution**:
1. Copy the URL from terminal output
2. Paste into browser manually
3. Complete Google sign-in
4. Terminal will detect verification automatically

### Verification Timeout

**Problem**: Browser sign-in completed but terminal still waiting

**Solution**:
1. Check firewall/network settings
2. Ensure Ollama service is running: `systemctl status ollama`
3. Try again with: `ollama signin`

### Permission Errors

**Problem**: Authentication fails with permission errors

**Solution**:
Run as your user account (not root):
```bash
ollama signin
```

During installation, the script automatically runs as the actual user.

### Already Signed In

If already authenticated, you don't need to sign in again:
```bash
ollama list  # Check available models
ollama pull starcoder:3b  # Pull models directly
```

## API Reference

### `signin(interactive: bool = True) -> Dict[str, Any]`

Sign in to Ollama using Google OAuth.

**Parameters:**
- `interactive` (bool): If True, prompts user before proceeding. Default: True

**Returns:**
```python
{
    'success': bool,
    'message': str,  # If successful
    'error': str,    # If failed
    'output': str    # Raw output from auth service
}
```

**Example:**
```python
result = ollama.signin()
if result['success']:
    print(result['message'])
    # Pull models that require auth
    ollama.install_model()
```

## Technical Details

### Implementation

Uses `subprocess.Popen` with real-time output streaming:

```python
process = subprocess.Popen(
    ['ollama', 'signin'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# Stream output in real-time
for line in iter(process.stdout.readline, ''):
    if line:
        print(line.rstrip())
        # Detect URLs, verification requests, etc.
```

### OAuth Flow

1. **Initiate**: `ollama signin` starts OAuth flow
2. **Generate**: Ollama generates unique auth URL
3. **Display**: URL shown in terminal output
4. **Launch**: System default browser opens URL
5. **Authenticate**: User signs in with Google
6. **Callback**: Google redirects to Ollama callback URL
7. **Verify**: Ollama receives verification, notifies terminal
8. **Store**: Tokens saved to `~/.ollama/credentials`

### Credential Storage

Location: `~/.ollama/` (user's home directory)

Files:
- OAuth tokens
- Session information
- Model access permissions

Permissions: User-only read/write (0600)

## Related Documentation

- `docs/OLLAMA_SIGNIN.md`: General Ollama sign-in guide
- `install.sh`: Installation script with OAuth integration
- `driver-mgt`: CLI tool with ai-signin command

## Support

If authentication issues persist:
1. Check Ollama version: `ollama --version`
2. Verify service status: `systemctl status ollama`
3. Check logs: `journalctl -u ollama -n 50`
4. Visit: https://ollama.ai/docs/authentication
