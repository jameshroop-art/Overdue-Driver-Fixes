"""
AI Driver Converter Module
Attempts to convert Windows/Other OS drivers to Linux drivers using AI analysis
"""

from typing import Dict, Any, List
import os
from datetime import datetime

class DriverConverter:
    """Converts cross-OS drivers to Linux using AI assistance"""
    
    def __init__(self, config_manager, ai_manager):
        self.config = config_manager
        self.ai_manager = ai_manager
        self.conversion_logs = []
    
    def can_convert(self, driver: Dict[str, Any]) -> bool:
        """Check if a driver can be converted"""
        target_os = driver.get('target_os', 'linux').lower()
        
        # Only non-Linux drivers can be converted
        if target_os == 'linux':
            return False
        
        # Driver must have source URL
        if not driver.get('source_url'):
            return False
        
        return True
    
    def analyze_driver(self, driver: Dict[str, Any], hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a cross-OS driver for conversion feasibility
        
        Args:
            driver: Driver information dictionary
            hardware: Hardware information dictionary
            
        Returns:
            Analysis results with feasibility score and recommendations
        """
        result = {
            'feasible': False,
            'confidence': 0,
            'complexity': 'unknown',
            'estimated_effort': 'unknown',
            'required_components': [],
            'potential_issues': [],
            'recommendations': [],
            'ai_analysis': None
        }
        
        target_os = driver.get('target_os', 'unknown').upper()
        driver_name = driver.get('name', 'Unknown')
        hw_type = hardware.get('type', 'Unknown')
        hw_vendor = hardware.get('vendor', 'Unknown')
        
        # Check if AI is available
        if not self.ai_manager or not self.ai_manager.is_available():
            result['potential_issues'].append('AI assistant not available for analysis')
            result['recommendations'].append('Install Ollama and starcoder:3b model')
            return result
        
        # Prepare analysis prompt for AI
        analysis_prompt = f"""Analyze this {target_os} driver for potential Linux conversion:

Hardware Type: {hw_type}
Hardware Vendor: {hw_vendor}
Driver Name: {driver_name}
Driver Version: {driver.get('version', 'Unknown')}
Source OS: {target_os}
Source: {driver.get('source', 'Unknown')}

Task: Determine if this driver can be converted/adapted to Linux and estimate the effort required.

Consider:
1. Hardware interface standards (PCI, USB, etc.)
2. Existing Linux kernel support for similar hardware
3. Driver architecture differences between {target_os} and Linux
4. Complexity of features and functionality
5. Availability of documentation and specifications

Provide analysis in this format:
FEASIBLE: [YES/NO]
CONFIDENCE: [0-100]%
COMPLEXITY: [LOW/MEDIUM/HIGH/VERY_HIGH]
EFFORT: [MINIMAL/MODERATE/SIGNIFICANT/EXTENSIVE]
COMPONENTS: [List key components needed]
ISSUES: [List potential blockers or challenges]
RECOMMENDATIONS: [Specific steps to attempt conversion]
"""
        
        try:
            # Use AI to analyze driver
            ai_result = self.ai_manager.analyze_text(analysis_prompt)
            
            if ai_result.get('success'):
                analysis = ai_result.get('analysis', '')
                result['ai_analysis'] = analysis
                
                # Parse AI response
                result = self._parse_ai_analysis(analysis, result)
            else:
                result['potential_issues'].append('AI analysis failed')
        except Exception as e:
            result['potential_issues'].append(f'Analysis error: {str(e)}')
        
        return result
    
    def _parse_ai_analysis(self, analysis: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI analysis response"""
        lines = analysis.upper().split('\n')
        
        for line in lines:
            if 'FEASIBLE:' in line:
                result['feasible'] = 'YES' in line
            elif 'CONFIDENCE:' in line:
                # Extract percentage
                import re
                match = re.search(r'(\d+)', line)
                if match:
                    result['confidence'] = int(match.group(1))
            elif 'COMPLEXITY:' in line:
                if 'LOW' in line:
                    result['complexity'] = 'low'
                elif 'MEDIUM' in line:
                    result['complexity'] = 'medium'
                elif 'HIGH' in line and 'VERY' not in line:
                    result['complexity'] = 'high'
                elif 'VERY_HIGH' in line or 'VERY HIGH' in line:
                    result['complexity'] = 'very_high'
            elif 'EFFORT:' in line:
                if 'MINIMAL' in line:
                    result['estimated_effort'] = 'minimal'
                elif 'MODERATE' in line:
                    result['estimated_effort'] = 'moderate'
                elif 'SIGNIFICANT' in line:
                    result['estimated_effort'] = 'significant'
                elif 'EXTENSIVE' in line:
                    result['estimated_effort'] = 'extensive'
        
        return result
    
    def attempt_conversion(self, driver: Dict[str, Any], hardware: Dict[str, Any], 
                          analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to convert a cross-OS driver to Linux
        
        Args:
            driver: Driver information dictionary
            hardware: Hardware information dictionary
            analysis: Analysis results from analyze_driver()
            
        Returns:
            Conversion results dictionary
        """
        result = {
            'success': False,
            'converted_driver': None,
            'conversion_log': [],
            'warnings': [],
            'next_steps': []
        }
        
        # Add initial log entry
        log_entry = f"Starting conversion attempt at {datetime.now().isoformat()}"
        result['conversion_log'].append(log_entry)
        
        # Check if conversion is feasible
        if not analysis.get('feasible'):
            result['conversion_log'].append('Conversion not feasible based on analysis')
            result['warnings'].append('AI analysis indicates conversion is not feasible')
            result['next_steps'].append('Consider alternative drivers or hardware')
            return result
        
        # Check AI availability
        if not self.ai_manager or not self.ai_manager.is_available():
            result['conversion_log'].append('AI assistant not available')
            result['warnings'].append('Cannot proceed without AI assistance')
            return result
        
        # Prepare conversion prompt
        target_os = driver.get('target_os', 'unknown').upper()
        conversion_prompt = f"""Attempt to create a Linux driver based on this {target_os} driver:

Driver: {driver.get('name')}
Version: {driver.get('version')}
Hardware: {hardware.get('name')} ({hardware.get('vendor')})

Analysis Results:
- Feasibility: {analysis.get('feasible')}
- Confidence: {analysis.get('confidence')}%
- Complexity: {analysis.get('complexity')}
- Effort: {analysis.get('estimated_effort')}

Task: Generate a Linux kernel module or user-space driver that provides equivalent functionality.

Requirements:
1. Use standard Linux kernel APIs
2. Support all key hardware features
3. Include error handling and logging
4. Follow Linux driver best practices
5. Provide clear comments and documentation

Generate the driver code and explain the conversion approach.
"""
        
        result['conversion_log'].append('Requesting AI to generate Linux driver code...')
        
        try:
            # Request AI conversion
            ai_result = self.ai_manager.analyze_text(conversion_prompt)
            
            if ai_result.get('success'):
                conversion_response = ai_result.get('analysis', '')
                result['conversion_log'].append('AI generated conversion response')
                
                # Create converted driver info
                result['converted_driver'] = {
                    'name': f"{driver.get('name', 'unknown')}-linux-converted",
                    'version': f"{driver.get('version', 'unknown')}-ai-converted",
                    'source': 'ai_converted',
                    'stability': 'experimental',
                    'description': f"AI-converted Linux driver from {target_os} {driver.get('name')}",
                    'target_os': 'linux',
                    'original_driver': driver.get('name'),
                    'original_os': target_os.lower(),
                    'conversion_date': datetime.now().isoformat(),
                    'ai_generated_code': conversion_response,
                    'risk_percentage': 75,  # High risk for experimental conversion
                    'requires_testing': True,
                    'experimental': True
                }
                
                result['success'] = True
                result['conversion_log'].append('Conversion completed successfully')
                result['warnings'].append('This is an AI-generated experimental driver')
                result['warnings'].append('Extensive testing required before use')
                result['warnings'].append('May not include all original features')
                result['next_steps'].append('Review generated code carefully')
                result['next_steps'].append('Test in safe/virtual environment')
                result['next_steps'].append('Report issues and provide feedback')
            else:
                result['conversion_log'].append('AI conversion failed')
                result['warnings'].append('AI could not generate driver code')
        except Exception as e:
            result['conversion_log'].append(f'Conversion error: {str(e)}')
            result['warnings'].append(f'Error during conversion: {str(e)}')
        
        # Save conversion log
        self.conversion_logs.append({
            'timestamp': datetime.now().isoformat(),
            'driver': driver.get('name'),
            'hardware': hardware.get('name'),
            'result': result
        })
        
        return result
    
    def save_conversion_log(self, log_path: str = None) -> bool:
        """Save conversion logs to file"""
        if not log_path:
            # Default to user config directory
            config_dir = os.path.expanduser('~/.config/driver-mgt/conversions/')
            os.makedirs(config_dir, exist_ok=True)
            log_path = os.path.join(config_dir, f"conversion-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
        
        try:
            with open(log_path, 'w') as f:
                f.write("Driver Conversion Log\n")
                f.write("=" * 80 + "\n\n")
                
                for entry in self.conversion_logs:
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Driver: {entry['driver']}\n")
                    f.write(f"Hardware: {entry['hardware']}\n")
                    f.write(f"Success: {entry['result'].get('success')}\n")
                    f.write("\nConversion Log:\n")
                    for log_line in entry['result'].get('conversion_log', []):
                        f.write(f"  - {log_line}\n")
                    f.write("\n" + "-" * 80 + "\n\n")
            
            return True
        except Exception as e:
            print(f"Failed to save conversion log: {e}")
            return False
