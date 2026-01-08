"""
Test suite for starcoder domain boundary enforcement
Tests that starcoder can only access whitelisted domains
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import ConfigManager
from utils.security import DomainValidator


def test_domain_validator_init():
    """Test DomainValidator initialization"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    assert validator is not None
    assert len(validator.domain_whitelist) > 0
    print("✓ DomainValidator initialized successfully")


def test_allowed_domains():
    """Test that whitelisted domains are allowed"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Test ASUS support URLs
    allowed, reason = validator.is_url_allowed('https://www.asus.com/support/download-center/')
    assert allowed, f"ASUS support URL should be allowed: {reason}"
    print("✓ ASUS support URL allowed")
    
    allowed, reason = validator.is_url_allowed('https://asus.com/support/drivers/')
    assert allowed, f"ASUS download URL should be allowed: {reason}"
    print("✓ ASUS download URL allowed")
    
    # Test Phoronix review URLs
    allowed, reason = validator.is_url_allowed('https://www.phoronix.com/review/amd-ryzen-7-9800x3d-linux')
    assert allowed, f"Phoronix review URL should be allowed: {reason}"
    print("✓ Phoronix review URL allowed")
    
    # Test Dev.to article URLs
    allowed, reason = validator.is_url_allowed('https://dev.to/nolunchbreaks_22/linux-kernel-613-breaking-new-ground-in-hardware-support-and-system-performance-15g1')
    assert allowed, f"Dev.to article URL should be allowed: {reason}"
    print("✓ Dev.to article URL allowed")
    
    # Test GitHub URLs
    allowed, reason = validator.is_url_allowed('https://github.com/some-user/some-repo')
    assert allowed, f"GitHub URL should be allowed: {reason}"
    print("✓ GitHub URL allowed")
    
    allowed, reason = validator.is_url_allowed('https://api.github.com/search/repositories')
    assert allowed, f"GitHub API URL should be allowed: {reason}"
    print("✓ GitHub API URL allowed")
    
    # Test HuggingFace URLs
    allowed, reason = validator.is_url_allowed('https://huggingface.co/models')
    assert allowed, f"HuggingFace URL should be allowed: {reason}"
    print("✓ HuggingFace URL allowed")


def test_blocked_domains():
    """Test that non-whitelisted domains are blocked"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Test random external domains
    blocked, reason = validator.is_url_allowed('https://www.google.com')
    assert not blocked, f"Google should be blocked"
    print("✓ Google URL blocked")
    
    blocked, reason = validator.is_url_allowed('https://www.reddit.com')
    assert not blocked, f"Reddit should be blocked"
    print("✓ Reddit URL blocked")
    
    blocked, reason = validator.is_url_allowed('https://www.twitter.com')
    assert not blocked, f"Twitter should be blocked"
    print("✓ Twitter URL blocked")
    
    blocked, reason = validator.is_url_allowed('https://example.com')
    assert not blocked, f"Example.com should be blocked"
    print("✓ Example.com URL blocked")


def test_github_search_validation():
    """Test GitHub search query validation"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Valid searches (driver/chipset related)
    allowed, reason = validator.validate_github_search('nvidia linux driver')
    assert allowed, f"Driver search should be allowed: {reason}"
    print("✓ Driver search allowed")
    
    allowed, reason = validator.validate_github_search('ASUS motherboard chipset linux')
    assert allowed, f"Chipset search should be allowed: {reason}"
    print("✓ Chipset search allowed")
    
    allowed, reason = validator.validate_github_search('linux firmware')
    assert allowed, f"Firmware search should be allowed: {reason}"
    print("✓ Firmware search allowed")
    
    # Invalid searches (not driver/chipset related)
    blocked, reason = validator.validate_github_search('javascript tutorial')
    assert not blocked, f"Non-driver search should be blocked: {reason}"
    print("✓ Non-driver search blocked")


def test_huggingface_search_validation():
    """Test HuggingFace search query validation"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Valid searches (driver/hardware related)
    allowed, reason = validator.validate_huggingface_search('AMD linux driver')
    assert allowed, f"Driver search should be allowed: {reason}"
    print("✓ HuggingFace driver search allowed")
    
    allowed, reason = validator.validate_huggingface_search('hardware firmware linux')
    assert allowed, f"Hardware search should be allowed: {reason}"
    print("✓ HuggingFace hardware search allowed")
    
    # Invalid searches
    blocked, reason = validator.validate_huggingface_search('text generation model')
    assert not blocked, f"Non-hardware search should be blocked: {reason}"
    print("✓ HuggingFace non-hardware search blocked")


def test_filesystem_access():
    """Test filesystem access restrictions"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Test allowed directories (with critical error)
    allowed, reason = validator.is_filesystem_access_allowed(
        '~/.config/driver-mgt/logs/error.log', 
        is_critical_error=True
    )
    assert allowed, f"Logs directory should be allowed for critical errors: {reason}"
    print("✓ Critical error filesystem access allowed")
    
    # Test blocked without critical error
    blocked, reason = validator.is_filesystem_access_allowed(
        '~/.config/driver-mgt/logs/error.log', 
        is_critical_error=False
    )
    assert not blocked, f"Filesystem access should be blocked without critical error: {reason}"
    print("✓ Non-critical filesystem access blocked")
    
    # Test blocked directory (even with critical error)
    blocked, reason = validator.is_filesystem_access_allowed(
        '/etc/passwd', 
        is_critical_error=True
    )
    assert not blocked, f"Unauthorized directory should be blocked: {reason}"
    print("✓ Unauthorized directory blocked")


def test_asus_path_validation():
    """Test that ASUS URLs require support/download paths"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Valid ASUS paths
    allowed, reason = validator.is_url_allowed('https://www.asus.com/support/download-center/')
    assert allowed, f"ASUS support path should be allowed: {reason}"
    print("✓ ASUS support path allowed")
    
    # Invalid ASUS paths (not support/download)
    blocked, reason = validator.is_url_allowed('https://www.asus.com/products/laptops/')
    assert not blocked, f"ASUS product pages should be blocked: {reason}"
    print("✓ ASUS product page blocked")


def test_phoronix_path_validation():
    """Test that Phoronix URLs require review paths"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    # Valid Phoronix paths
    allowed, reason = validator.is_url_allowed('https://www.phoronix.com/review/some-hardware-review')
    assert allowed, f"Phoronix review path should be allowed: {reason}"
    print("✓ Phoronix review path allowed")
    
    # Invalid Phoronix paths
    blocked, reason = validator.is_url_allowed('https://www.phoronix.com/forums/')
    assert not blocked, f"Phoronix forums should be blocked: {reason}"
    print("✓ Phoronix forums blocked")


def test_get_whitelisted_domains():
    """Test retrieving whitelist"""
    config = ConfigManager()
    validator = DomainValidator(config)
    
    domains = validator.get_whitelisted_domains()
    assert len(domains) > 0, "Should return domains"
    assert 'github.com' in domains, "Should include GitHub"
    assert 'huggingface.co' in domains, "Should include HuggingFace"
    assert 'www.asus.com' in domains, "Should include ASUS"
    print("✓ Whitelist retrieval works")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing Starcoder Domain Boundary Enforcement")
    print("="*60 + "\n")
    
    tests = [
        ("Validator Initialization", test_domain_validator_init),
        ("Allowed Domains", test_allowed_domains),
        ("Blocked Domains", test_blocked_domains),
        ("GitHub Search Validation", test_github_search_validation),
        ("HuggingFace Search Validation", test_huggingface_search_validation),
        ("Filesystem Access", test_filesystem_access),
        ("ASUS Path Validation", test_asus_path_validation),
        ("Phoronix Path Validation", test_phoronix_path_validation),
        ("Whitelist Retrieval", test_get_whitelisted_domains),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            test_func()
            passed += 1
            print(f"✓ {test_name} PASSED")
        except AssertionError as e:
            failed += 1
            print(f"✗ {test_name} FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
