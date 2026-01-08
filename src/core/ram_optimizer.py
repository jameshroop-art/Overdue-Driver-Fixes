"""
RAM Optimization Module
AI-powered RAM optimization to determine best stable settings
"""

from typing import Dict, Any, List

class RAMOptimizer:
    """Optimizes RAM settings using AI analysis"""
    
    def __init__(self, config_manager, ollama_manager=None):
        self.config = config_manager
        self.ollama_manager = ollama_manager
    
    def optimize_ram_settings(self, ram_info: Dict[str, Any], cpu_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Determine optimal RAM settings based on hardware configuration
        
        Args:
            ram_info: RAM hardware information
            cpu_info: CPU information (optional, for better recommendations)
        
        Returns:
            Dictionary with optimized settings and recommendations
        """
        optimization_result = {
            'ram_info': ram_info,
            'optimized_settings': {},
            'recommendations': [],
            'stability_score': 0,
            'ai_analysis': None
        }
        
        # Get baseline settings based on heuristics
        baseline_settings = self._get_baseline_settings(ram_info, cpu_info)
        optimization_result['optimized_settings'] = baseline_settings
        
        # Use AI to enhance optimization if available
        ai_enabled = self.config.get_ai('risk_assessment.enabled', True)
        if ai_enabled and self.ollama_manager and self.ollama_manager.is_available():
            ai_optimization = self._get_ai_optimized_settings(ram_info, cpu_info, baseline_settings)
            if ai_optimization:
                optimization_result['optimized_settings'].update(ai_optimization.get('settings', {}))
                optimization_result['recommendations'].extend(ai_optimization.get('recommendations', []))
                optimization_result['ai_analysis'] = ai_optimization.get('analysis', '')
                optimization_result['stability_score'] = ai_optimization.get('stability_score', 0)
        else:
            # Use heuristic stability score
            optimization_result['stability_score'] = self._calculate_stability_score(baseline_settings)
            optimization_result['recommendations'] = self._generate_heuristic_recommendations(ram_info, cpu_info)
        
        return optimization_result
    
    def _get_baseline_settings(self, ram_info: Dict[str, Any], cpu_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get baseline RAM settings based on heuristics"""
        settings = {}
        
        total_gb = ram_info.get('total_gb', 0)
        ram_type = ram_info.get('ram_type', 'Unknown')
        speed_mhz = ram_info.get('speed_mhz', 0)
        
        # Memory frequency recommendations
        if ram_type == 'DDR4':
            settings['recommended_frequency'] = min(speed_mhz, 3200) if speed_mhz > 0 else 3200
            settings['safe_frequency'] = min(speed_mhz, 2666) if speed_mhz > 0 else 2666
        elif ram_type == 'DDR5':
            settings['recommended_frequency'] = min(speed_mhz, 6000) if speed_mhz > 0 else 5200
            settings['safe_frequency'] = min(speed_mhz, 4800) if speed_mhz > 0 else 4800
        else:
            settings['recommended_frequency'] = speed_mhz if speed_mhz > 0 else 'Auto'
            settings['safe_frequency'] = speed_mhz if speed_mhz > 0 else 'Auto'
        
        # Voltage settings (conservative)
        if ram_type == 'DDR4':
            settings['voltage'] = 1.35  # Standard DDR4
        elif ram_type == 'DDR5':
            settings['voltage'] = 1.1   # Standard DDR5
        
        # Timing recommendations (conservative)
        settings['xmp_profile'] = 'Profile 1' if speed_mhz > 2666 else 'Auto'
        settings['command_rate'] = '1T' if total_gb <= 32 else '2T'
        
        # Special considerations for AMD X3D CPUs
        if cpu_info and cpu_info.get('has_3d_vcache', False):
            settings['notes'] = 'AMD X3D detected: Use EXPO/XMP carefully, 3D V-Cache can be sensitive to memory overclocking'
            # More conservative settings for X3D
            if ram_type == 'DDR5':
                settings['recommended_frequency'] = min(settings.get('recommended_frequency', 5200), 5600)
        
        return settings
    
    def _get_ai_optimized_settings(self, ram_info: Dict[str, Any], cpu_info: Dict[str, Any], 
                                   baseline_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to optimize RAM settings"""
        if not self.ollama_manager:
            return None
        
        # Prepare context for AI
        cpu_context = ""
        if cpu_info:
            cpu_name = cpu_info.get('name', 'Unknown')
            has_3d_vcache = cpu_info.get('has_3d_vcache', False)
            cpu_context = f"""
CPU: {cpu_name}
3D V-Cache Enabled: {'Yes' if has_3d_vcache else 'No'}
"""
        
        ram_type = ram_info.get('ram_type', 'Unknown')
        total_gb = ram_info.get('total_gb', 0)
        speed_mhz = ram_info.get('speed_mhz', 0)
        manufacturer = ram_info.get('manufacturer', 'Unknown')
        
        context = f"""Analyze and optimize RAM settings for maximum stability:

RAM Configuration:
- Type: {ram_type}
- Total Capacity: {total_gb} GB
- Speed: {speed_mhz} MHz
- Manufacturer: {manufacturer}
{cpu_context}
Baseline Settings (Heuristic):
- Recommended Frequency: {baseline_settings.get('recommended_frequency', 'N/A')} MHz
- Safe Frequency: {baseline_settings.get('safe_frequency', 'N/A')} MHz
- Voltage: {baseline_settings.get('voltage', 'N/A')} V
- XMP Profile: {baseline_settings.get('xmp_profile', 'N/A')}

Provide optimized settings considering:
1. Stability vs Performance trade-offs
2. CPU compatibility (especially AMD X3D 3D V-Cache sensitivity)
3. Memory type specifications
4. Safe voltage ranges
5. Timing optimizations

Response format (provide ONLY these values):
FREQUENCY: <optimal_mhz>
VOLTAGE: <optimal_voltage>
TIMING: <suggested_timings>
STABILITY_SCORE: <0-100>
RECOMMENDATION: <one key recommendation>"""
        
        try:
            result = self.ollama_manager.analyze_text(context)
            if result.get('success'):
                analysis = result.get('analysis', '')
                
                # Parse AI response
                import re
                settings = {}
                recommendations = []
                
                freq_match = re.search(r'FREQUENCY:\s*(\d+)', analysis)
                if freq_match:
                    settings['ai_recommended_frequency'] = int(freq_match.group(1))
                
                voltage_match = re.search(r'VOLTAGE:\s*([\d.]+)', analysis)
                if voltage_match:
                    settings['ai_recommended_voltage'] = float(voltage_match.group(1))
                
                timing_match = re.search(r'TIMING:\s*(.+?)(?:\n|$)', analysis)
                if timing_match:
                    settings['ai_recommended_timings'] = timing_match.group(1).strip()
                
                stability_match = re.search(r'STABILITY_SCORE:\s*(\d+)', analysis)
                stability_score = int(stability_match.group(1)) if stability_match else 75
                
                recommendation_match = re.search(r'RECOMMENDATION:\s*(.+?)(?:\n|$)', analysis, re.IGNORECASE)
                if recommendation_match:
                    recommendations.append(recommendation_match.group(1).strip())
                
                return {
                    'settings': settings,
                    'recommendations': recommendations,
                    'analysis': analysis,
                    'stability_score': stability_score
                }
        
        except Exception as e:
            print(f"Error getting AI RAM optimization: {e}")
        
        return None
    
    def _calculate_stability_score(self, settings: Dict[str, Any]) -> int:
        """Calculate stability score based on heuristic settings"""
        score = 80  # Base conservative score
        
        # Adjust based on settings
        if settings.get('xmp_profile') == 'Auto':
            score += 10  # More stable
        
        if settings.get('command_rate') == '2T':
            score += 5   # More stable
        
        return min(score, 100)
    
    def _generate_heuristic_recommendations(self, ram_info: Dict[str, Any], 
                                           cpu_info: Dict[str, Any] = None) -> List[str]:
        """Generate recommendations without AI"""
        recommendations = []
        
        total_gb = ram_info.get('total_gb', 0)
        ram_type = ram_info.get('ram_type', 'Unknown')
        
        if total_gb < 16:
            recommendations.append("Consider upgrading to at least 16GB RAM for better performance")
        
        if ram_type == 'DDR4':
            recommendations.append("Enable XMP Profile 1 in BIOS for optimal performance")
        elif ram_type == 'DDR5':
            recommendations.append("Enable EXPO/XMP for DDR5 optimal performance")
        
        if cpu_info and cpu_info.get('has_3d_vcache', False):
            recommendations.append("AMD X3D detected: Test stability after enabling memory profiles")
            recommendations.append("Consider BIOS update for better X3D + memory compatibility")
        
        recommendations.append("Run memory stress test (memtest86+) after any changes")
        
        return recommendations
