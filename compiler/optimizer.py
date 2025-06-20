import re
import logging

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """Handles different levels of assembly code optimization"""
    
    def __init__(self):
        self.optimization_passes = {
            'none': [],
            'basic': [self._remove_redundant, self._basic_peephole],
            'standard': [self._remove_redundant, self._basic_peephole, self._constant_folding, self._register_reuse],
            'aggressive': [self._remove_redundant, self._basic_peephole, self._constant_folding, 
                          self._register_reuse, self._loop_optimization, self._instruction_reordering]
        }
    
    def optimize(self, code_lines, level='none'):
        """Apply optimization passes based on level"""
        if level not in self.optimization_passes:
            level = 'none'
        
        optimized = code_lines.copy()
        passes = self.optimization_passes[level]
        
        logger.info(f"Applying {len(passes)} optimization passes for level: {level}")
        
        for optimization_pass in passes:
            optimized = optimization_pass(optimized)
        
        return optimized
    
    def _remove_redundant(self, code_lines):
        """Remove redundant instructions"""
        optimized = []
        prev_line = None
        
        for line in code_lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip duplicate consecutive instructions
            if line != prev_line:
                # Check for redundant moves
                if line.startswith('mov') and prev_line and prev_line.startswith('mov'):
                    # Check if moving same value to same register
                    if self._is_redundant_mov(prev_line, line):
                        optimized.append(f"; Removed redundant: {line}")
                        continue
                
                optimized.append(line)
                prev_line = line
        
        return optimized
    
    def _basic_peephole(self, code_lines):
        """Basic peephole optimizations"""
        optimized = []
        i = 0
        
        while i < len(code_lines):
            line = code_lines[i].strip()
            
            # Look for push/pop pairs that can be optimized
            if i < len(code_lines) - 1:
                next_line = code_lines[i + 1].strip()
                
                # Optimize push followed by immediate pop
                if line.startswith('push') and next_line.startswith('pop'):
                    reg1 = self._extract_register(line)
                    reg2 = self._extract_register(next_line)
                    
                    if reg1 and reg2 and reg1 != reg2:
                        # Convert push/pop to mov
                        optimized.append(f"mov {reg2}, {reg1}  ; Optimized push/pop pair")
                        i += 2
                        continue
            
            optimized.append(line)
            i += 1
        
        return optimized
    
    def _constant_folding(self, code_lines):
        """Fold constants and simplify expressions"""
        optimized = []
        
        for line in code_lines:
            line = line.strip()
            
            # Look for arithmetic with constants
            if any(op in line for op in ['add', 'sub', 'mul']) and re.search(r', \d+', line):
                parts = line.split()
                if len(parts) >= 3:
                    instruction = parts[0]
                    operands = ' '.join(parts[1:])
                    
                    # Simple constant folding for add/sub with 0
                    if ', 0' in operands:
                        if instruction in ['add', 'sub']:
                            optimized.append(f"; Constant folded: {line}")
                            continue
                    
                    # Multiply by 1 optimization
                    if instruction == 'mul' and ', 1' in operands:
                        optimized.append(f"; Constant folded: {line}")
                        continue
            
            optimized.append(line)
        
        return optimized
    
    def _register_reuse(self, code_lines):
        """Optimize register usage"""
        optimized = []
        register_values = {}
        
        for line in code_lines:
            line = line.strip()
            
            # Track register assignments
            if line.startswith('mov'):
                parts = line.split(',')
                if len(parts) == 2:
                    dest = parts[0].replace('mov', '').strip()
                    src = parts[1].strip()
                    
                    # Check if source value is already in another register
                    for reg, value in register_values.items():
                        if value == src and reg != dest:
                            optimized.append(f"mov {dest}, {reg}  ; Reused register value")
                            register_values[dest] = src
                            break
                    else:
                        optimized.append(line)
                        register_values[dest] = src
                else:
                    optimized.append(line)
            else:
                optimized.append(line)
                # Invalidate registers that might be modified
                if any(reg in line for reg in register_values.keys()):
                    register_values.clear()
        
        return optimized
    
    def _loop_optimization(self, code_lines):
        """Basic loop optimizations"""
        optimized = []
        in_loop = False
        loop_start = -1
        
        for i, line in enumerate(code_lines):
            line = line.strip()
            
            # Detect simple loops
            if 'loop' in line.lower() or 'jmp' in line.lower():
                if not in_loop:
                    in_loop = True
                    loop_start = i
                    optimized.append(f"; Loop optimization opportunity at line {i}")
            
            optimized.append(line)
        
        return optimized
    
    def _instruction_reordering(self, code_lines):
        """Reorder instructions for better performance"""
        optimized = []
        
        # Simple instruction scheduling
        for i, line in enumerate(code_lines):
            line = line.strip()
            
            # Look for opportunities to reorder independent instructions
            if i < len(code_lines) - 1:
                next_line = code_lines[i + 1].strip()
                
                # If current instruction doesn't depend on next, consider reordering
                if self._are_independent(line, next_line):
                    # For now, just add a comment about the opportunity
                    optimized.append(f"; Reordering opportunity: {line}")
                    optimized.append(line)
                else:
                    optimized.append(line)
            else:
                optimized.append(line)
        
        return optimized
    
    def _is_redundant_mov(self, line1, line2):
        """Check if two mov instructions are redundant"""
        # Extract operands from both lines
        try:
            op1 = line1.split('mov')[1].strip()
            op2 = line2.split('mov')[1].strip()
            return op1 == op2
        except:
            return False
    
    def _extract_register(self, line):
        """Extract register name from instruction"""
        try:
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].replace(',', '').strip()
        except:
            return None
        return None
    
    def _are_independent(self, line1, line2):
        """Check if two instructions are independent"""
        # Simple heuristic: check if they use different registers
        reg1 = self._extract_register(line1)
        reg2 = self._extract_register(line2)
        
        if reg1 and reg2:
            return reg1 != reg2
        
        return False
