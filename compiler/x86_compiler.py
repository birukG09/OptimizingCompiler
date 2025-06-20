import re
import logging
from .optimizer import OptimizationEngine

logger = logging.getLogger(__name__)

class X86Compiler:
    """Custom x86 to x86_64 assembly compiler with optimization support"""
    
    def __init__(self):
        self.optimizer = OptimizationEngine()
        
        # x86 to x86_64 register mapping
        self.register_map = {
            'eax': 'rax', 'ebx': 'rbx', 'ecx': 'rcx', 'edx': 'rdx',
            'esi': 'rsi', 'edi': 'rdi', 'esp': 'rsp', 'ebp': 'rbp',
            'ax': 'ax', 'bx': 'bx', 'cx': 'cx', 'dx': 'dx',
            'al': 'al', 'bl': 'bl', 'cl': 'cl', 'dl': 'dl',
            'ah': 'ah', 'bh': 'bh', 'ch': 'ch', 'dh': 'dh'
        }
        
        # x86_64 specific improvements
        self.x64_enhancements = {
            'mov': self._optimize_mov,
            'add': self._optimize_arithmetic,
            'sub': self._optimize_arithmetic,
            'mul': self._optimize_multiply,
            'push': self._optimize_stack,
            'pop': self._optimize_stack
        }
    
    def compile(self, assembly_code, optimization_level='none'):
        """Main compilation method"""
        try:
            logger.info(f"Starting compilation with optimization level: {optimization_level}")
            
            # Clean and parse input
            lines = self._clean_input(assembly_code)
            if not lines:
                return {
                    'success': False,
                    'error': 'No valid assembly instructions found'
                }
            
            # Translate x86 to x86_64
            translated_code = self._translate_to_x64(lines)
            
            # Apply optimizations based on level
            optimized_code = self.optimizer.optimize(translated_code, optimization_level)
            
            # Generate output
            result = {
                'success': True,
                'original_code': assembly_code,
                'compiled_code': '\n'.join(optimized_code),
                'optimization_level': optimization_level,
                'instruction_count': {
                    'original': len(lines),
                    'optimized': len(optimized_code)
                },
                'improvements': self._calculate_improvements(lines, optimized_code)
            }
            
            logger.info("Compilation successful")
            return result
            
        except Exception as e:
            logger.error(f"Compilation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_input(self, code):
        """Clean and validate input assembly code"""
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):  # Skip empty lines and comments
                lines.append(line)
        return lines
    
    def _translate_to_x64(self, lines):
        """Translate x86 instructions to x86_64"""
        translated = []
        
        for line in lines:
            # Parse instruction
            parts = line.split()
            if not parts:
                continue
                
            instruction = parts[0].lower()
            operands = ' '.join(parts[1:]) if len(parts) > 1 else ''
            
            # Translate registers
            translated_operands = self._translate_registers(operands)
            
            # Apply x86_64 specific enhancements
            if instruction in self.x64_enhancements:
                enhanced_line = self.x64_enhancements[instruction](instruction, translated_operands)
                translated.append(enhanced_line)
            else:
                translated.append(f"{instruction} {translated_operands}".strip())
        
        return translated
    
    def _translate_registers(self, operands):
        """Translate x86 registers to x86_64 equivalents"""
        if not operands:
            return operands
            
        # Replace registers using mapping
        result = operands
        for x86_reg, x64_reg in self.register_map.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(x86_reg) + r'\b'
            result = re.sub(pattern, x64_reg, result, flags=re.IGNORECASE)
        
        return result
    
    def _optimize_mov(self, instruction, operands):
        """Optimize MOV instructions for x86_64"""
        if 'rax' in operands and 'rax' in operands.split(',')[0]:
            # Optimize self-assignment
            parts = operands.split(',')
            if len(parts) == 2 and parts[0].strip() == parts[1].strip():
                return f"; Optimized out redundant mov {operands}"
        return f"{instruction} {operands}"
    
    def _optimize_arithmetic(self, instruction, operands):
        """Optimize arithmetic instructions"""
        # Add x86_64 specific optimizations
        if '0' in operands:
            if instruction == 'add' and ', 0' in operands:
                return f"; Optimized out add with zero: {operands}"
            elif instruction == 'sub' and ', 0' in operands:
                return f"; Optimized out sub with zero: {operands}"
        return f"{instruction} {operands}"
    
    def _optimize_multiply(self, instruction, operands):
        """Optimize multiplication instructions"""
        if ', 1' in operands:
            return f"; Optimized out multiply by one: {operands}"
        elif ', 2' in operands:
            # Replace multiply by 2 with left shift
            reg = operands.split(',')[0].strip()
            return f"shl {reg}, 1  ; Optimized multiply by 2"
        return f"{instruction} {operands}"
    
    def _optimize_stack(self, instruction, operands):
        """Optimize stack operations"""
        # x86_64 has more efficient stack operations
        return f"{instruction} {operands}"
    
    def _calculate_improvements(self, original, optimized):
        """Calculate performance improvements"""
        original_size = len(original)
        optimized_size = len([line for line in optimized if not line.strip().startswith(';')])
        
        size_reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
        
        return {
            'size_reduction_percent': round(size_reduction, 2),
            'estimated_performance_gain': min(size_reduction * 0.8, 50),  # Estimate based on size reduction
            'x64_features_utilized': self._count_x64_features(optimized)
        }
    
    def _count_x64_features(self, code):
        """Count x86_64 specific features utilized"""
        features = []
        code_str = '\n'.join(code).lower()
        
        if 'r8' in code_str or 'r9' in code_str or 'r10' in code_str:
            features.append('Extended registers')
        if 'shl' in code_str:
            features.append('Bit shifting optimization')
        if 'rax' in code_str or 'rbx' in code_str:
            features.append('64-bit registers')
            
        return features
