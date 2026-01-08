"""
Risk Assessment Module
Handles error risk assessment and prediction
"""

from typing import Dict, Any, List
from datetime import datetime

class RiskAssessor:
    """Assesses risk for driver installations"""
    
    def __init__(self, config_manager, ollama_manager=None):
        self.config = config_manager
        self.ollama_manager = ollama_manager
        self.error_database = {}  # Would be loaded from a database
    
    def assess_hardware(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for a hardware component"""
        risk_data = {
            'hardware_id': hardware.get('id'),
            'hardware_name': hardware.get('name'),
            'current_driver': hardware.get('driver'),
            'risk_percentage': 0,
            'risk_level': 'unknown',
            'known_issues': [],
            'ai_can_remediate': False,
            'recommendations': []
        }
        
        # Calculate base risk using heuristics
        base_risk = self._calculate_risk_score(hardware)
        
        # Use AI to enhance risk assessment if enabled and available
        ai_enabled = self.config.get_ai('risk_assessment.enabled', True)
        if ai_enabled and self.ollama_manager and self.ollama_manager.is_available():
            ai_risk = self._calculate_ai_risk(hardware, base_risk)
            # Combine heuristic and AI risk (weighted average: 40% heuristic, 60% AI)
            risk_score = int(base_risk * 0.4 + ai_risk * 0.6)
        else:
            risk_score = base_risk
        
        risk_data['risk_percentage'] = risk_score
        risk_data['risk_level'] = self._get_risk_level(risk_score)
        
        # Check for known issues
        known_issues = self._check_error_database(hardware)
        risk_data['known_issues'] = known_issues
        
        # Assess AI remediation capability
        risk_data['ai_can_remediate'] = self._assess_ai_remediation(hardware, known_issues)
        
        # Generate recommendations
        risk_data['recommendations'] = self._generate_recommendations(hardware, risk_score)
        
        return risk_data
    
    def assess_driver(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for installing a specific driver"""
        risk_data = {
            'driver_name': driver.get('name'),
            'driver_version': driver.get('version'),
            'hardware_name': hardware.get('name'),
            'risk_percentage': 0,
            'risk_level': 'unknown',
            'compatibility_score': 0,
            'known_issues': [],
            'ai_can_remediate': False
        }
        
        # Calculate base driver-specific risk
        base_risk = self._calculate_driver_risk(hardware, driver)
        
        # Use AI to enhance driver risk assessment if enabled and available
        ai_enabled = self.config.get_ai('risk_assessment.enabled', True)
        if ai_enabled and self.ollama_manager and self.ollama_manager.is_available():
            ai_risk = self._calculate_ai_driver_risk(hardware, driver, base_risk)
            # Combine heuristic and AI risk (weighted average: 40% heuristic, 60% AI)
            risk_score = int(base_risk * 0.4 + ai_risk * 0.6)
        else:
            risk_score = base_risk
        
        risk_data['risk_percentage'] = risk_score
        risk_data['risk_level'] = self._get_risk_level(risk_score)
        
        # Calculate compatibility
        risk_data['compatibility_score'] = 100 - risk_score
        
        # Check for driver-specific issues
        issues = self._check_driver_issues(hardware, driver)
        risk_data['known_issues'] = issues
        
        # AI remediation check
        risk_data['ai_can_remediate'] = len(issues) > 0 and risk_score < 30
        
        return risk_data
    
    def _calculate_risk_score(self, hardware: Dict[str, Any]) -> int:
        """Calculate risk score (0-100)"""
        base_risk = 5  # Base risk for any hardware
        
        # Add risk based on vendor
        vendor = hardware.get('vendor', '').lower()
        if vendor in ['nvidia', 'amd']:
            base_risk += 10  # GPU drivers are more complex
        elif vendor in ['broadcom']:
            base_risk += 15  # Broadcom has known issues
        
        # Add risk if no current driver
        if not hardware.get('driver'):
            base_risk += 10
        
        # Cap at 100
        return min(base_risk, 100)
    
    def _calculate_driver_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> int:
        """Calculate risk for specific driver"""
        base_risk = self._calculate_risk_score(hardware)
        
        # Adjust based on driver source
        source = driver.get('source', '').lower()
        if source == 'official':
            base_risk -= 5
        elif source == 'community':
            base_risk += 5
        
        # Adjust based on stability
        stability = driver.get('stability', '').lower()
        if stability == 'stable':
            base_risk -= 5
        elif stability == 'beta':
            base_risk += 10
        elif stability == 'experimental':
            base_risk += 20
        
        return max(0, min(base_risk, 100))
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Convert risk score to level"""
        if risk_score < 10:
            return 'very_low'
        elif risk_score < 20:
            return 'low'
        elif risk_score < 40:
            return 'medium'
        elif risk_score < 70:
            return 'high'
        else:
            return 'critical'
    
    def _check_error_database(self, hardware: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for known errors in database"""
        # Placeholder - would query actual error database
        return []
    
    def _check_driver_issues(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for known driver-specific issues"""
        # Placeholder - would query actual issue database
        return []
    
    def _assess_ai_remediation(self, hardware: Dict[str, Any], known_issues: List[Dict[str, Any]]) -> bool:
        """Assess if AI can remediate known issues"""
        if not known_issues:
            return True  # No issues to remediate
        
        # Check if AI assistant is available
        if not self.config.get_ai('risk_assessment.ai_remediation_check', True):
            return False
        
        # Most common driver issues can be remediated
        return True
    
    def _generate_recommendations(self, hardware: Dict[str, Any], risk_score: int) -> List[str]:
        """Generate recommendations based on risk"""
        recommendations = []
        
        if risk_score > 30:
            recommendations.append("Consider enabling AI-assisted installation")
            recommendations.append("Backup current driver before updating")
        
        if risk_score > 50:
            recommendations.append("Use official drivers only")
            recommendations.append("Enable rollback on failure")
        
        if not hardware.get('driver'):
            recommendations.append("Install a driver to enable hardware functionality")
        
        return recommendations
    
    def update_error_database(self) -> bool:
        """Update error database from remote source"""
        # Placeholder for database update
        return True
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get error database status"""
        return {
            'last_update': datetime.now().isoformat(),
            'entries': 0,
            'status': 'not_implemented'
        }
    
    def _calculate_ai_risk(self, hardware: Dict[str, Any], base_risk: int) -> int:
        """Use AI to calculate risk for hardware"""
        if not self.ollama_manager:
            return base_risk
        
        # Prepare context for AI
        context = f"""Analyze the risk of using this hardware configuration:
Hardware: {hardware.get('name', 'Unknown')}
Vendor: {hardware.get('vendor', 'Unknown')}
Current Driver: {hardware.get('driver', 'None')}
Base Risk Score: {base_risk}/100

Consider:
1. Known compatibility issues with this vendor/model
2. Driver maturity and stability
3. Common failure patterns
4. Community feedback and bug reports

Provide a risk score from 0-100 where:
- 0-20: Very low risk (well-supported hardware)
- 21-40: Low risk (generally stable)
- 41-60: Medium risk (some known issues)
- 61-80: High risk (frequent problems reported)
- 81-100: Critical risk (major compatibility issues)

Respond with ONLY the numeric risk score (0-100), nothing else."""
        
        try:
            # Use OllamaManager to assess risk
            result = self.ollama_manager.analyze_text(context)
            if result.get('success'):
                response = result.get('analysis', '').strip()
                # Extract numeric value from response
                import re
                match = re.search(r'\b(\d+)\b', response)
                if match:
                    ai_risk = int(match.group(1))
                    # Ensure within valid range
                    return max(0, min(ai_risk, 100))
        except Exception as e:
            # If AI fails, return base risk
            pass
        
        return base_risk
    
    def _calculate_ai_driver_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any], base_risk: int) -> int:
        """Use AI to calculate risk for specific driver installation"""
        if not self.ollama_manager:
            return base_risk
        
        # Prepare context for AI
        context = f"""Analyze the risk of installing this driver:
Hardware: {hardware.get('name', 'Unknown')}
Vendor: {hardware.get('vendor', 'Unknown')}
Driver: {driver.get('name', 'Unknown')}
Driver Version: {driver.get('version', 'Unknown')}
Driver Source: {driver.get('source', 'Unknown')}
Driver Stability: {driver.get('stability', 'Unknown')}
Current Driver: {hardware.get('driver', 'None')}
Base Risk Score: {base_risk}/100

Consider:
1. Driver compatibility with this specific hardware
2. Known bugs or issues with this driver version
3. Stability of the driver source (official vs community)
4. Installation failure rates
5. Post-installation problems

Provide a risk score from 0-100 where:
- 0-20: Very low risk (well-tested, stable driver)
- 21-40: Low risk (generally safe to install)
- 41-60: Medium risk (proceed with caution)
- 61-80: High risk (backup recommended)
- 81-100: Critical risk (installation likely to fail)

Respond with ONLY the numeric risk score (0-100), nothing else."""
        
        try:
            # Use OllamaManager to assess risk
            result = self.ollama_manager.analyze_text(context)
            if result.get('success'):
                response = result.get('analysis', '').strip()
                # Extract numeric value from response
                import re
                match = re.search(r'\b(\d+)\b', response)
                if match:
                    ai_risk = int(match.group(1))
                    # Ensure within valid range
                    return max(0, min(ai_risk, 100))
        except Exception as e:
            # If AI fails, return base risk
            pass
        
        return base_risk
