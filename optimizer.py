"""
Optimizer module for the educational compiler.
Implements basic optimizations on three-address code (TAC) intermediate representation.
"""

from typing import List, Dict, Set, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from parser import (
    ASTNode, Program, Statement, Expression,
    VariableDeclaration, PrintStatement,
    BinaryOperation, UnaryOperation, NumberLiteral, Identifier
)

# Three-Address Code (TAC) Instructions
@dataclass
class TACInstruction(ABC):
    """Base class for all TAC instructions."""
    pass

@dataclass
class TACAssignment(TACInstruction):
    """TAC assignment: result = operand1 op operand2"""
    result: str
    operand1: Union[str, float]
    operator: Optional[str]
    operand2: Optional[Union[str, float]]
    
    def __str__(self):
        if self.operator and self.operand2 is not None:
            return f"{self.result} = {self.operand1} {self.operator} {self.operand2}"
        else:
            return f"{self.result} = {self.operand1}"

@dataclass
class TACPrint(TACInstruction):
    """TAC print instruction."""
    operand: Union[str, float]
    
    def __str__(self):
        return f"print {self.operand}"

@dataclass
class TACProgram:
    """Container for TAC instructions."""
    instructions: List[TACInstruction]
    
    def __str__(self):
        return '\n'.join(str(instr) for instr in self.instructions)

class IRGenerator:
    """
    Generates Three-Address Code (TAC) from AST.
    """
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.variable_map: Dict[str, str] = {}
    
    def new_temp(self) -> str:
        """Generate a new temporary variable name."""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name
    
    def generate(self, ast: Program) -> TACProgram:
        """Generate TAC from AST."""
        self.instructions = []
        self.temp_counter = 0
        self.variable_map = {}
        
        for statement in ast.statements:
            self.generate_statement(statement)
        
        return TACProgram(self.instructions)
    
    def generate_statement(self, stmt: Statement) -> None:
        """Generate TAC for a statement."""
        if isinstance(stmt, VariableDeclaration):
            # Generate code for the expression
            expr_result = self.generate_expression(stmt.value)
            
            # Map variable name to its value
            self.variable_map[stmt.name] = expr_result
            
            # Create assignment instruction
            self.instructions.append(TACAssignment(stmt.name, expr_result, None, None))
        
        elif isinstance(stmt, PrintStatement):
            expr_result = self.generate_expression(stmt.expression)
            self.instructions.append(TACPrint(expr_result))
    
    def generate_expression(self, expr: Expression) -> Union[str, float]:
        """Generate TAC for an expression and return the result variable/value."""
        if isinstance(expr, NumberLiteral):
            return expr.value
        
        elif isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, BinaryOperation):
            left_result = self.generate_expression(expr.left)
            right_result = self.generate_expression(expr.right)
            
            temp = self.new_temp()
            self.instructions.append(TACAssignment(temp, left_result, expr.operator, right_result))
            return temp
        
        elif isinstance(expr, UnaryOperation):
            operand_result = self.generate_expression(expr.operand)
            
            if expr.operator == '-':
                temp = self.new_temp()
                self.instructions.append(TACAssignment(temp, 0, '-', operand_result))
                return temp
            elif expr.operator == '+':
                # Unary plus doesn't change the value
                return operand_result
        
        raise ValueError(f"Unknown expression type: {type(expr)}")

class ConstantFolder:
    """
    Performs constant folding optimization.
    Evaluates constant expressions at compile time.
    """
    
    def optimize(self, program: TACProgram) -> TACProgram:
        """Apply constant folding to TAC program."""
        optimized_instructions = []
        
        for instr in program.instructions:
            if isinstance(instr, TACAssignment):
                optimized_instr = self.fold_assignment(instr)
                optimized_instructions.append(optimized_instr)
            else:
                optimized_instructions.append(instr)
        
        return TACProgram(optimized_instructions)
    
    def fold_assignment(self, instr: TACAssignment) -> TACAssignment:
        """Fold constants in an assignment instruction."""
        if instr.operator and instr.operand2 is not None:
            # Check if both operands are constants
            if isinstance(instr.operand1, (int, float)) and isinstance(instr.operand2, (int, float)):
                result = self.evaluate_operation(instr.operand1, instr.operator, instr.operand2)
                return TACAssignment(instr.result, result, None, None)
        
        return instr
    
    def evaluate_operation(self, left: float, operator: str, right: float) -> float:
        """Evaluate a constant operation."""
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise ValueError("Division by zero in constant folding")
            return left / right
        else:
            raise ValueError(f"Unknown operator: {operator}")

class ConstantPropagator:
    """
    Performs constant propagation optimization.
    Replaces variable uses with their constant values when possible.
    """
    
    def optimize(self, program: TACProgram) -> TACProgram:
        """Apply constant propagation to TAC program."""
        constants: Dict[str, float] = {}
        optimized_instructions = []
        
        for instr in program.instructions:
            if isinstance(instr, TACAssignment):
                # Propagate constants in operands
                operand1 = self.propagate_operand(instr.operand1, constants)
                operand2 = self.propagate_operand(instr.operand2, constants) if instr.operand2 is not None else None
                
                new_instr = TACAssignment(instr.result, operand1, instr.operator, operand2)
                
                # If this assignment creates a constant, track it
                if instr.operator is None and isinstance(operand1, (int, float)):
                    constants[instr.result] = operand1
                elif instr.operator and isinstance(operand1, (int, float)) and isinstance(operand2, (int, float)):
                    # Result of constant operation is also constant
                    folder = ConstantFolder()
                    result_value = folder.evaluate_operation(operand1, instr.operator, operand2)
                    constants[instr.result] = result_value
                
                optimized_instructions.append(new_instr)
            
            elif isinstance(instr, TACPrint):
                propagated_operand = self.propagate_operand(instr.operand, constants)
                optimized_instructions.append(TACPrint(propagated_operand))
            
            else:
                optimized_instructions.append(instr)
        
        return TACProgram(optimized_instructions)
    
    def propagate_operand(self, operand: Union[str, float, None], constants: Dict[str, float]) -> Union[str, float, None]:
        """Replace variable with constant value if available."""
        if operand is None:
            return None
        
        if isinstance(operand, str) and operand in constants:
            return constants[operand]
        
        return operand

class DeadCodeEliminator:
    """
    Performs dead code elimination.
    Removes assignments to variables that are never used.
    """
    
    def optimize(self, program: TACProgram) -> TACProgram:
        """Apply dead code elimination to TAC program."""
        # Find all used variables
        used_vars = self.find_used_variables(program)
        
        # Keep only instructions that define used variables or have side effects
        optimized_instructions = []
        
        for instr in program.instructions:
            if isinstance(instr, TACAssignment):
                # Keep assignment if the result variable is used
                if instr.result in used_vars:
                    optimized_instructions.append(instr)
            else:
                # Keep all non-assignment instructions (they have side effects)
                optimized_instructions.append(instr)
        
        return TACProgram(optimized_instructions)
    
    def find_used_variables(self, program: TACProgram) -> Set[str]:
        """Find all variables that are used (not just defined)."""
        used_vars = set()
        
        for instr in program.instructions:
            if isinstance(instr, TACAssignment):
                # Add operands to used set
                if isinstance(instr.operand1, str):
                    used_vars.add(instr.operand1)
                if isinstance(instr.operand2, str):
                    used_vars.add(instr.operand2)
            
            elif isinstance(instr, TACPrint):
                if isinstance(instr.operand, str):
                    used_vars.add(instr.operand)
        
        return used_vars

class PeepholeOptimizer:
    """
    Performs peephole optimizations on TAC.
    Looks for small patterns that can be optimized.
    """
    
    def optimize(self, program: TACProgram) -> TACProgram:
        """Apply peephole optimizations."""
        instructions = program.instructions[:]
        changed = True
        
        # Repeat until no more changes
        while changed:
            changed = False
            new_instructions = []
            i = 0
            
            while i < len(instructions):
                # Look for optimization patterns
                optimized, consumed = self.try_optimize_at(instructions, i)
                
                if optimized:
                    new_instructions.extend(optimized)
                    i += consumed
                    changed = True
                else:
                    new_instructions.append(instructions[i])
                    i += 1
            
            instructions = new_instructions
        
        return TACProgram(instructions)
    
    def try_optimize_at(self, instructions: List[TACInstruction], index: int) -> tuple[List[TACInstruction], int]:
        """Try to optimize at given index. Returns (optimized_instructions, consumed_count)."""
        if index >= len(instructions):
            return [], 0
        
        # Pattern: x = y; z = x; -> z = y; (if x is not used elsewhere)
        if (index + 1 < len(instructions) and
            isinstance(instructions[index], TACAssignment) and
            isinstance(instructions[index + 1], TACAssignment)):
            
            first = instructions[index]
            second = instructions[index + 1]
            
            # Check if first assigns to a temp that's only used in second
            if (first.operator is None and  # Simple assignment
                isinstance(second.operand1, str) and
                first.result == second.operand1 and
                first.result.startswith('t')):  # Temporary variable
                
                # Replace second instruction's operand with first's operand
                optimized = TACAssignment(second.result, first.operand1, second.operator, second.operand2)
                return [optimized], 2
        
        # Pattern: x = y + 0; -> x = y;
        if isinstance(instructions[index], TACAssignment):
            instr = instructions[index]
            if (instr.operator == '+' and instr.operand2 == 0):
                optimized = TACAssignment(instr.result, instr.operand1, None, None)
                return [optimized], 1
            elif (instr.operator == '*' and instr.operand2 == 1):
                optimized = TACAssignment(instr.result, instr.operand1, None, None)
                return [optimized], 1
        
        return [], 0

class Optimizer:
    """
    Main optimizer that applies all optimization passes.
    """
    
    def __init__(self):
        self.constant_folder = ConstantFolder()
        self.constant_propagator = ConstantPropagator()
        self.dead_code_eliminator = DeadCodeEliminator()
        self.peephole_optimizer = PeepholeOptimizer()
    
    def optimize(self, program: TACProgram, passes: int = 3) -> TACProgram:
        """
        Apply all optimization passes multiple times.
        
        Args:
            program: TAC program to optimize
            passes: Number of optimization passes to perform
            
        Returns:
            Optimized TAC program
        """
        current = program
        
        for pass_num in range(passes):
            # Apply optimizations in order
            current = self.constant_folder.optimize(current)
            current = self.constant_propagator.optimize(current)
            current = self.dead_code_eliminator.optimize(current)
            current = self.peephole_optimizer.optimize(current)
        
        return current

# Example usage and testing
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Test optimization with sample code
    sample_code = """
    let x = 5 + 3;
    let y = x * 2;
    let z = y + 0;
    print(z);
    """
    
    try:
        # Parse code
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Generate IR
        ir_gen = IRGenerator()
        tac_program = ir_gen.generate(ast)
        
        print("Original TAC:")
        print("-" * 40)
        print(tac_program)
        
        # Optimize
        optimizer = Optimizer()
        optimized = optimizer.optimize(tac_program)
        
        print("\nOptimized TAC:")
        print("-" * 40)
        print(optimized)
        
    except Exception as e:
        print(f"Error: {e}")
