# GitHub Repository Search for Motherboard Updates

## Overview

The motherboard detection feature now includes automatic GitHub repository search to find Linux-compatible drivers, BIOS updates, and firmware from both official manufacturers and the community.

## Features

### Automatic Repository Discovery

When a motherboard is detected, the system automatically searches for:

1. **Official Manufacturer Repositories**
   - ASUS, MSI, Gigabyte, ASRock official GitHub accounts
   - Manufacturer-maintained Linux drivers
   - Official BIOS/firmware update tools

2. **Community Repositories**
   - User-maintained driver packages
   - Third-party BIOS utilities
   - Linux compatibility tools
   - Fan/RGB control software

3. **BIOS Update Checks**
   - Searches for firmware update repos
   - Identifies tools for flashing BIOS
   - Finds compatibility information

### Search Strategy

The system uses multiple search queries to maximize results:

```
Search Terms:
1. "{vendor} linux driver"
2. "{vendor} linux bios"
3. "{vendor} motherboard linux"
4. "{vendor} chipset linux"
```

Each query returns up to 5 repositories, ranked by relevance.

## How It Works

### Detection Flow

```
1. Detect Motherboard
   ├─ Read DMI information (vendor, model)
   ├─ Detect BIOS (version, date)
   └─ Detect Chipset (Intel/AMD model)

2. Check Built-in Database
   ├─ Match vendor to known manufacturers
   ├─ Get official support URLs
   └─ Retrieve compatibility rating

3. Search GitHub Repositories
   ├─ Query GitHub API for repos
   ├─ Filter by relevance
   ├─ Rank by official status + stars
   └─ Return top 10 results

4. Check for BIOS Updates
   ├─ Search for firmware repos
   ├─ Compare versions if possible
   └─ Provide update instructions
```

### Relevance Filtering

Repositories are considered relevant if they contain:
- Vendor name in repo name or description
- Keywords: "driver", "bios", "linux", "motherboard"
- High star count (community validation)
- Recent activity

### Ranking Algorithm

```python
# Ranking priority:
1. Official manufacturer repos (highest)
2. High star count (community trust)
3. Recent updates (active maintenance)
4. Relevance score (keyword matching)
```

## API Usage

### Python API

```python
from core.hardware_detector import HardwareDetector
from core.config import ConfigManager

config = ConfigManager()
detector = HardwareDetector(config)

# Search for repos
vendor = "ASUS"
model = "ROG STRIX X570-E GAMING"

repos = detector._search_manufacturer_repos(vendor, model)

for repo in repos:
    print(f"{'[OFFICIAL]' if repo['official'] else '[COMMUNITY]'}")
    print(f"  Name: {repo['name']}")
    print(f"  URL: {repo['url']}")
    print(f"  Stars: {repo['stars']}")
    print(f"  Description: {repo['description']}\n")
```

### Check BIOS Updates

```python
# Check for BIOS updates
bios_info = detector.check_bios_updates(
    vendor="ASUS",
    model="ROG STRIX X570-E GAMING", 
    current_version="4602"
)

print(f"Current BIOS: {bios_info['current_version']}")
print(f"Check URL: {bios_info.get('check_url')}")

if bios_info.get('community_repos'):
    print(f"\nFound {len(bios_info['community_repos'])} BIOS repos:")
    for repo in bios_info['community_repos']:
        print(f"  - {repo['name']}: {repo['url']}")
```

## Example Output

### Motherboard Detection with Repos

```
Motherboard Found:
  Vendor: ASUS
  Model: ROG STRIX X570-E GAMING
  BIOS Version: 4602
  BIOS Date: 11/18/2023
  Chipset: X570 (AMD)

Linux Compatibility:
  Status: supported
  Support Level: Good
  Manufacturer: ASUS
  
Found Repositories:
  [OFFICIAL] asus-linux-drivers (★ 234)
    Official ASUS Linux driver package
    https://github.com/asus/asus-linux-drivers

  [COMMUNITY] asus-wmi-sensors (★ 512)  
    Linux kernel module for ASUS WMI sensors
    https://github.com/electrified/asus-wmi-sensors
    
  [COMMUNITY] rogauracore (★ 389)
    RGB control for ASUS ROG motherboards
    https://github.com/wroberts/rogauracore

BIOS Update Check:
  Current Version: 4602
  Check URL: https://www.asus.com/support/download-center/
  Notes: Visit ASUS support site to check for BIOS updates
  
  Found 2 community repos with BIOS tools:
    - asus-bios-flasher: https://github.com/...
    - rog-bios-tools: https://github.com/...
```

## GUI Integration

### Display in Motherboard Tab

The GUI automatically displays found repositories:

1. **Device Information Section**
   - Shows motherboard details
   - Displays BIOS version and date
   - Shows chipset information

2. **Linux Compatibility Section**
   - Support level indicator
   - Official manufacturer links
   - **List of found repositories** (NEW)

3. **Repository List**
   - Official repos marked with badge
   - Star count displayed
   - Clickable links to each repo
   - Short description

4. **BIOS Update Section** (NEW)
   - Current version display
   - Link to check for updates
   - Community BIOS tools listed

## Search Limitations

### GitHub API Limits

- **Unauthenticated**: 60 requests/hour per IP
- **Authenticated**: 5,000 requests/hour (future enhancement)

The system is designed to minimize API calls:
- Searches only when motherboard is detected
- Caches results for the session
- Uses efficient query strategies

### Rate Limiting

If API limit is reached:
```
⚠ GitHub API rate limit reached
Results may be incomplete
Try again in 1 hour or authenticate with GitHub token
```

## Configuration

### Enable/Disable Repo Search

Edit `config/app_config.yaml`:

```yaml
motherboard:
  search_repos: true        # Enable GitHub repo search
  max_repos: 10             # Maximum repos to return
  search_timeout: 10        # Timeout for API calls (seconds)
  cache_results: true       # Cache results for session
```

### Custom Search Terms

Add custom search terms in configuration:

```yaml
motherboard:
  search_terms:
    - "{vendor} linux driver"
    - "{vendor} linux bios"
    - "{vendor} motherboard linux"
    - "{vendor} chipset linux"
    # Add custom terms:
    - "{vendor} rgb control linux"
    - "{vendor} fan control linux"
```

## Security Considerations

### Data Privacy

- **No Personal Information Sent**: Only vendor and model names
- **Public API**: Uses GitHub's public API
- **Read-Only**: No modifications to repositories
- **No Authentication Required**: Works without GitHub token

### Verification

Always verify repositories before using:

1. **Check Official Status**: Look for verified accounts
2. **Review Code**: Read source before running
3. **Check Activity**: Prefer actively maintained repos
4. **Read Issues**: See if others report problems
5. **Test Safely**: Use in VM or test environment first

## Common Repositories Found

### ASUS Motherboards

- **asus-linux**: Official ASUS Linux drivers
- **asus-wmi-sensors**: Sensor monitoring
- **rogauracore**: RGB control
- **asusctl**: ROG laptop/motherboard control

### MSI Motherboards

- **msi-rgb**: RGB LED control
- **msi-fan-control**: Fan curve management
- **liquidctl**: AIO cooler control

### Gigabyte Motherboards

- **OpenRGB**: Universal RGB control (supports Gigabyte)
- **gigabyte-rgb-fusion**: RGB Fusion for Linux
- **it87**: Super I/O chip driver

### Generic/Multi-Vendor

- **lm-sensors**: Hardware monitoring
- **OpenRGB**: Universal RGB control
- **liquidctl**: Cooler and pump control
- **CoreCtrl**: AMD GPU/CPU control

## Troubleshooting

### No Repositories Found

**Possible Reasons:**
1. Manufacturer not popular on GitHub
2. No Linux-specific tools needed (good native support)
3. API rate limit reached
4. Network connectivity issues

**Solution:**
- Check manufacturer's official website manually
- Search GitHub directly for vendor name
- Wait if rate limited (resets after 1 hour)

### Irrelevant Results

The system filters results but may occasionally include unrelated repos.

**How to Identify Relevant Repos:**
- ✓ Official vendor account
- ✓ High star count (>100)
- ✓ Recent commits (within last year)
- ✓ Clear description mentioning vendor/model
- ✓ Active issues/pull requests

### False Official Status

Community repos in official-looking org names may be marked as official.

**Verify Official Status:**
1. Check GitHub org name exactly matches vendor
2. Look for verification badge
3. Visit manufacturer website for GitHub links
4. Check repo ownership history

## Future Enhancements

### Planned Features

1. **GitHub Authentication**
   - Increase API rate limit
   - Access private repos
   - Better search capabilities

2. **Local Repo Cache**
   - Store search results locally
   - Offline browsing
   - Periodic updates

3. **Update Notifications**
   - Check for repo updates
   - Notify when new BIOS released
   - Track installed community tools

4. **Automated Testing**
   - Test compatibility automatically
   - Report results to community
   - Build compatibility database

## Related Documentation

- `docs/MOTHERBOARD_DETECTION.md`: Main motherboard feature guide
- `src/core/hardware_detector.py`: Implementation details
- GitHub API: https://docs.github.com/en/rest

## Support

For issues with repository search:
1. Check network connectivity
2. Verify GitHub API status: https://githubstatus.com
3. Check rate limit: https://api.github.com/rate_limit
4. Report false positives/negatives on GitHub
