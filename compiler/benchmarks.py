import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class BenchmarkRunner:
    """Runs benchmarks to measure compilation and optimization effectiveness"""
    
    def __init__(self):
        self.benchmark_stages = [
            'code_size_analysis',
            'compile_time_measurement', 
            'optimization_effectiveness',
            'x64_feature_utilization'
        ]
    
    def run_benchmarks(self, original_code: str, compiled_code: str, optimization_level: str) -> Dict:
        """Run all benchmark stages and return results"""
        results = {
            'optimization_level': optimization_level,
            'timestamp': time.time(),
            'stages': {}
        }
        
        try:
            # Stage 1: Code Size Analysis
            results['stages']['code_size'] = self._analyze_code_size(original_code, compiled_code)
            
            # Stage 2: Compilation Time (simulated)
            results['stages']['compile_time'] = self._measure_compile_time(optimization_level)
            
            # Stage 3: Optimization Effectiveness
            results['stages']['optimization'] = self._analyze_optimization_effectiveness(
                original_code, compiled_code, optimization_level
            )
            
            # Stage 4: x64 Feature Utilization
            results['stages']['x64_features'] = self._analyze_x64_features(compiled_code)
            
            # Calculate overall performance score
            results['overall_score'] = self._calculate_overall_score(results['stages'])
            
        except Exception as e:
            logger.error(f"Benchmark error: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_code_size(self, original: str, compiled: str) -> Dict:
        """Analyze code size reduction and efficiency"""
        original_lines = [l.strip() for l in original.split('\n') if l.strip() and not l.strip().startswith(';')]
        compiled_lines = [l.strip() for l in compiled.split('\n') if l.strip() and not l.strip().startswith(';')]
        
        original_count = len(original_lines)
        compiled_count = len(compiled_lines)
        
        size_reduction = ((original_count - compiled_count) / original_count * 100) if original_count > 0 else 0
        
        return {
            'original_instructions': original_count,
            'compiled_instructions': compiled_count,
            'size_reduction_percent': round(size_reduction, 2),
            'efficiency_rating': self._calculate_efficiency_rating(size_reduction)
        }
    
    def _measure_compile_time(self, optimization_level: str) -> Dict:
        """Simulate compilation time measurement"""
        # Simulate different compilation times based on optimization level
        base_time = 0.1  # Base compilation time in seconds
        
        multipliers = {
            'none': 1.0,
            'basic': 1.2,
            'standard': 1.5,
            'aggressive': 2.0
        }
        
        simulated_time = base_time * multipliers.get(optimization_level, 1.0)
        
        return {
            'compilation_time_ms': round(simulated_time * 1000, 2),
            'optimization_overhead': round((simulated_time - base_time) * 1000, 2),
            'performance_rating': self._rate_compile_time(simulated_time)
        }
    
    def _analyze_optimization_effectiveness(self, original: str, compiled: str, level: str) -> Dict:
        """Analyze how effective the optimization was"""
        
        # Count optimization indicators
        optimizations_applied = compiled.count('; Optimized') + compiled.count('; Removed')
        total_instructions = len([l for l in original.split('\n') if l.strip()])
        
        effectiveness_percent = (optimizations_applied / total_instructions * 100) if total_instructions > 0 else 0
        
        # Expected performance improvements by level
        expected_improvements = {
            'none': 0,
            'basic': 5,
            'standard': 15,
            'aggressive': 30
        }
        
        expected = expected_improvements.get(level, 0)
        actual_improvement = min(effectiveness_percent * 2, 50)  # Estimate actual improvement
        
        return {
            'optimizations_applied': optimizations_applied,
            'effectiveness_percent': round(effectiveness_percent, 2),
            'expected_improvement': expected,
            'estimated_actual_improvement': round(actual_improvement, 2),
            'optimization_score': self._calculate_optimization_score(effectiveness_percent, level)
        }
    
    def _analyze_x64_features(self, compiled_code: str) -> Dict:
        """Analyze x86_64 specific features utilized"""
        features_detected = []
        code_lower = compiled_code.lower()
        
        # Check for x86_64 features
        x64_checks = {
            '64-bit registers': ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rsp', 'rbp'],
            'Extended registers': ['r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'],
            'Advanced instructions': ['movzx', 'movsx', 'lea'],
            'Optimized operations': ['shl', 'shr', 'sal', 'sar'],
            'SIMD potential': ['xmm', 'ymm', 'zmm']
        }
        
        feature_count = 0
        for feature_name, indicators in x64_checks.items():
            if any(indicator in code_lower for indicator in indicators):
                features_detected.append(feature_name)
                feature_count += 1
        
        utilization_score = (feature_count / len(x64_checks)) * 100
        
        return {
            'features_detected': features_detected,
            'feature_count': feature_count,
            'utilization_percent': round(utilization_score, 2),
            'x64_readiness_score': self._calculate_x64_readiness(utilization_score)
        }
    
    def _calculate_overall_score(self, stages: Dict) -> Dict:
        """Calculate overall performance score"""
        try:
            size_score = stages['code_size']['efficiency_rating']
            time_score = stages['compile_time']['performance_rating']
            opt_score = stages['optimization']['optimization_score']
            x64_score = stages['x64_features']['x64_readiness_score']
            
            overall = (size_score + time_score + opt_score + x64_score) / 4
            
            return {
                'overall_rating': round(overall, 1),
                'performance_grade': self._get_performance_grade(overall),
                'recommendations': self._generate_recommendations(stages)
            }
        except Exception as e:
            logger.error(f"Score calculation error: {str(e)}")
            return {
                'overall_rating': 0,
                'performance_grade': 'N/A',
                'recommendations': ['Unable to calculate performance metrics']
            }
    
    def _calculate_efficiency_rating(self, size_reduction: float) -> float:
        """Calculate efficiency rating based on size reduction"""
        if size_reduction >= 20:
            return 9.0
        elif size_reduction >= 10:
            return 7.5
        elif size_reduction >= 5:
            return 6.0
        elif size_reduction > 0:
            return 4.0
        else:
            return 2.0
    
    def _rate_compile_time(self, time_seconds: float) -> float:
        """Rate compilation time performance"""
        if time_seconds <= 0.1:
            return 9.0
        elif time_seconds <= 0.2:
            return 7.5
        elif time_seconds <= 0.3:
            return 6.0
        else:
            return 4.0
    
    def _calculate_optimization_score(self, effectiveness: float, level: str) -> float:
        """Calculate optimization score"""
        level_multipliers = {
            'none': 1.0,
            'basic': 1.2,
            'standard': 1.5,
            'aggressive': 2.0
        }
        
        base_score = min(effectiveness / 10, 8.0)
        multiplier = level_multipliers.get(level, 1.0)
        return min(base_score * multiplier, 10.0)
    
    def _calculate_x64_readiness(self, utilization: float) -> float:
        """Calculate x86_64 readiness score"""
        if utilization >= 80:
            return 9.5
        elif utilization >= 60:
            return 8.0
        elif utilization >= 40:
            return 6.5
        elif utilization >= 20:
            return 5.0
        else:
            return 3.0
    
    def _get_performance_grade(self, score: float) -> str:
        """Get letter grade for performance"""
        if score >= 9.0:
            return 'A+'
        elif score >= 8.5:
            return 'A'
        elif score >= 8.0:
            return 'A-'
        elif score >= 7.5:
            return 'B+'
        elif score >= 7.0:
            return 'B'
        elif score >= 6.5:
            return 'B-'
        elif score >= 6.0:
            return 'C+'
        elif score >= 5.5:
            return 'C'
        else:
            return 'D'
    
    def _generate_recommendations(self, stages: Dict) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        try:
            # Size-based recommendations
            if stages['code_size']['size_reduction_percent'] < 5:
                recommendations.append("Consider using higher optimization levels for better code size reduction")
            
            # Optimization recommendations
            if stages['optimization']['effectiveness_percent'] < 10:
                recommendations.append("Try aggressive optimization for more performance improvements")
            
            # x64 feature recommendations
            if stages['x64_features']['utilization_percent'] < 50:
                recommendations.append("Consider utilizing more x86_64 specific features for better performance")
            
            if not recommendations:
                recommendations.append("Great optimization results! Your code is well-optimized for x86_64")
                
        except Exception:
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations
