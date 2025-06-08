"""
Code generator module for the educational compiler.
Converts optimized TAC (Three-Address Code) to x86-64 assembly.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from optimizer import TACProgram, TACInstruction, TACAssignment, TACPrint

class RegisterAllocator:
    """
    Simple register allocator for x86-64.
    Uses a basic strategy for educational purposes.
    """
    
    def __init__(self):
        # Available general-purpose registers (excluding rsp, rbp)
        self.available_registers = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11']
        self.variable_to_register: Dict[str, str] = {}
        self.register_to_variable: Dict[str, str] = {}
        self.next_register_index = 0
    
    def allocate_register(self, variable: str) -> str:
        """
        Allocate a register for a variable.
        
        Args:
            variable: Variable name to allocate register for
            
        Returns:
            Register name (e.g., 'rax')
        """
        if variable in self.variable_to_register:
            return self.variable_to_register[variable]
        
        # Simple allocation: just use next available register
        if self.next_register_index < len(self.available_registers):
            register = self.available_registers[self.next_register_index]
            self.next_register_index += 1
        else:
            # For simplicity, reuse registers (in real compiler, would spill to memory)
            register = self.available_registers[self.next_register_index % len(self.available_registers)]
            self.next_register_index += 1
        
        # Update mappings
        if register in self.register_to_variable:
            old_var = self.register_to_variable[register]
            del self.variable_to_register[old_var]
        
        self.variable_to_register[variable] = register
        self.register_to_variable[register] = variable
        
        return register
    
    def get_register(self, variable: str) -> Optional[str]:
        """Get the register assigned to a variable."""
        return self.variable_to_register.get(variable)
    
    def is_register(self, name: str) -> bool:
        """Check if a name is a register."""
        return name in self.available_registers

class X86CodeGenerator:
    """
    Generates x86-64 assembly code from TAC.
    """
    
    def __init__(self):
        self.register_allocator = RegisterAllocator()
        self.assembly_lines: List[str] = []
        self.data_section: List[str] = []
        self.string_literals: Dict[str, str] = {}
        self.string_counter = 0
    
    def generate(self, tac_program: TACProgram) -> str:
        """
        Generate x86-64 assembly from TAC program.
        
        Args:
            tac_program: TAC program to convert
            
        Returns:
            x86-64 assembly code as string
        """
        self.assembly_lines = []
        self.data_section = []
        self.string_literals = {}
        self.string_counter = 0
        
        # Generate assembly for each instruction
        for instruction in tac_program.instructions:
            self.generate_instruction(instruction)
        
        # Build complete assembly file
        return self.build_assembly_file()
    
    def generate_instruction(self, instruction: TACInstruction) -> None:
        """Generate assembly for a single TAC instruction."""
        if isinstance(instruction, TACAssignment):
            self.generate_assignment(instruction)
        elif isinstance(instruction, TACPrint):
            self.generate_print(instruction)
        else:
            self.add_comment(f"Unknown instruction: {instruction}")
    
    def generate_assignment(self, assignment: TACAssignment) -> None:
        """Generate assembly for an assignment instruction."""
        self.add_comment(f"Assignment: {assignment}")
        
        if assignment.operator is None:
            # Simple assignment: result = operand1
            self.generate_simple_assignment(assignment.result, assignment.operand1)
        else:
            # Binary operation: result = operand1 op operand2
            self.generate_binary_operation(assignment)
    
    def generate_simple_assignment(self, result: str, operand) -> None:
        """Generate assembly for simple assignment."""
        result_reg = self.register_allocator.allocate_register(result)
        
        if isinstance(operand, (int, float)):
            # Move immediate value to register
            self.add_instruction(f"mov {result_reg}, {int(operand)}")
        else:
            # Move from another variable's register
            operand_reg = self.register_allocator.get_register(str(operand))
            if operand_reg:
                if operand_reg != result_reg:
                    self.add_instruction(f"mov {result_reg}, {operand_reg}")
            else:
                # Operand not in register, allocate one
                operand_reg = self.register_allocator.allocate_register(str(operand))
                if operand_reg != result_reg:
                    self.add_instruction(f"mov {result_reg}, {operand_reg}")
    
    def generate_binary_operation(self, assignment: TACAssignment) -> None:
        """Generate assembly for binary operations."""
        result_reg = self.register_allocator.allocate_register(assignment.result)
        
        # Get operands
        operand1 = assignment.operand1
        operand2 = assignment.operand2
        
        # Load first operand into result register
        if isinstance(operand1, (int, float)):
            self.add_instruction(f"mov {result_reg}, {int(operand1)}")
        else:
            operand1_reg = self.register_allocator.get_register(str(operand1))
            if operand1_reg and operand1_reg != result_reg:
                self.add_instruction(f"mov {result_reg}, {operand1_reg}")
            elif not operand1_reg:
                operand1_reg = self.register_allocator.allocate_register(str(operand1))
                if operand1_reg != result_reg:
                    self.add_instruction(f"mov {result_reg}, {operand1_reg}")
        
        # Apply operation with second operand
        if assignment.operator == '+':
            if isinstance(operand2, (int, float)):
                self.add_instruction(f"add {result_reg}, {int(operand2)}")
            else:
                operand2_reg = self.register_allocator.get_register(str(operand2))
                if operand2_reg:
                    self.add_instruction(f"add {result_reg}, {operand2_reg}")
                else:
                    # Use a temporary register for operand2
                    temp_reg = 'r11'  # Use r11 as scratch register
                    operand2_reg = self.register_allocator.allocate_register(str(operand2))
                    self.add_instruction(f"add {result_reg}, {operand2_reg}")
        
        elif assignment.operator == '-':
            if isinstance(operand2, (int, float)):
                self.add_instruction(f"sub {result_reg}, {int(operand2)}")
            else:
                operand2_reg = self.register_allocator.get_register(str(operand2))
                if operand2_reg:
                    self.add_instruction(f"sub {result_reg}, {operand2_reg}")
                else:
                    operand2_reg = self.register_allocator.allocate_register(str(operand2))
                    self.add_instruction(f"sub {result_reg}, {operand2_reg}")
        
        elif assignment.operator == '*':
            if isinstance(operand2, (int, float)):
                # For immediate multiplication, use imul with immediate
                self.add_instruction(f"imul {result_reg}, {result_reg}, {int(operand2)}")
            else:
                operand2_reg = self.register_allocator.get_register(str(operand2))
                if operand2_reg:
                    self.add_instruction(f"imul {result_reg}, {operand2_reg}")
                else:
                    operand2_reg = self.register_allocator.allocate_register(str(operand2))
                    self.add_instruction(f"imul {result_reg}, {operand2_reg}")
        
        elif assignment.operator == '/':
            # Division is more complex in x86-64
            self.add_comment("Division operation")
            # Move dividend to rax
            if result_reg != 'rax':
                self.add_instruction(f"mov rax, {result_reg}")
            
            # Clear rdx for division
            self.add_instruction("xor rdx, rdx")
            
            if isinstance(operand2, (int, float)):
                # Move divisor to a register
                self.add_instruction(f"mov rbx, {int(operand2)}")
                self.add_instruction("idiv rbx")
            else:
                operand2_reg = self.register_allocator.get_register(str(operand2))
                if operand2_reg:
                    self.add_instruction(f"idiv {operand2_reg}")
                else:
                    operand2_reg = self.register_allocator.allocate_register(str(operand2))
                    self.add_instruction(f"idiv {operand2_reg}")
            
            # Move result back if needed
            if result_reg != 'rax':
                self.add_instruction(f"mov {result_reg}, rax")
    
    def generate_print(self, print_instr: TACPrint) -> None:
        """Generate assembly for print instruction."""
        self.add_comment(f"Print: {print_instr}")
        
        # Move value to print into rdi (first argument register)
        if isinstance(print_instr.operand, (int, float)):
            self.add_instruction(f"mov rdi, {int(print_instr.operand)}")
        else:
            operand_reg = self.register_allocator.get_register(str(print_instr.operand))
            if operand_reg:
                if operand_reg != 'rdi':
                    self.add_instruction(f"mov rdi, {operand_reg}")
            else:
                # Allocate register for operand
                operand_reg = self.register_allocator.allocate_register(str(print_instr.operand))
                if operand_reg != 'rdi':
                    self.add_instruction(f"mov rdi, {operand_reg}")
        
        # Call print function
        self.add_instruction("call print_int")
    
    def add_instruction(self, instruction: str) -> None:
        """Add an assembly instruction."""
        self.assembly_lines.append(f"    {instruction}")
    
    def add_comment(self, comment: str) -> None:
        """Add a comment to the assembly."""
        self.assembly_lines.append(f"    ; {comment}")
    
    def add_label(self, label: str) -> None:
        """Add a label to the assembly."""
        self.assembly_lines.append(f"{label}:")
    
    def build_assembly_file(self) -> str:
        """Build the complete assembly file with all sections."""
        lines = []
        
        # Add file header
        lines.append("; Generated x86-64 assembly code")
        lines.append("; Compile with: nasm -f elf64 output.asm && gcc -o program output.o")
        lines.append("")
        
        # External declarations
        lines.append("extern printf")
        lines.append("extern exit")
        lines.append("")
        
        # Data section
        lines.append("section .data")
        lines.append("    print_fmt db '%d', 10, 0    ; Format string for printing integers")
        
        # Add any string literals
        for label, value in self.string_literals.items():
            lines.append(f"    {label} db {value}, 0")
        
        lines.append("")
        
        # Text section
        lines.append("section .text")
        lines.append("global _start")
        lines.append("")
        
        # Print function
        lines.append("print_int:")
        lines.append("    ; Print integer in rdi")
        lines.append("    push rbp")
        lines.append("    mov rbp, rsp")
        lines.append("    ")
        lines.append("    ; Set up printf call")
        lines.append("    mov rsi, rdi          ; Move integer to second argument")
        lines.append("    mov rdi, print_fmt    ; Move format string to first argument")
        lines.append("    xor rax, rax          ; Clear rax (no floating point args)")
        lines.append("    call printf")
        lines.append("    ")
        lines.append("    pop rbp")
        lines.append("    ret")
        lines.append("")
        
        # Main program
        lines.append("_start:")
        lines.append("    ; Main program")
        
        # Add generated instructions
        lines.extend(self.assembly_lines)
        
        # Program exit
        lines.append("")
        lines.append("    ; Exit program")
        lines.append("    mov rdi, 0    ; Exit status")
        lines.append("    call exit")
        
        return '\n'.join(lines)

class CodeGenerator:
    """
    Main code generator that orchestrates assembly generation.
    """
    
    def __init__(self):
        self.x86_generator = X86CodeGenerator()
    
    def generate(self, tac_program: TACProgram) -> str:
        """
        Generate assembly code from TAC program.
        
        Args:
            tac_program: TAC program to convert
            
        Returns:
            x86-64 assembly code
        """
        return self.x86_generator.generate(tac_program)
    
    def save_assembly(self, assembly_code: str, filename: str = "output.asm") -> None:
        """
        Save assembly code to file.
        
        Args:
            assembly_code: Assembly code to save
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write(assembly_code)
        
        print(f"Assembly code saved to {filename}")
        print("\nTo compile and run:")
        print(f"1. nasm -f elf64 {filename}")
        print(f"2. gcc -o program {filename.replace('.asm', '.o')}")
        print("3. ./program")

# Example usage and testing
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    from optimizer import IRGenerator, Optimizer
    
    # Test code generation with sample code
    sample_code = """
    let x = 5 + 3;
    let y = x * 2;
    print(y);
    """
    
    try:
        # Complete compilation pipeline
        print("Compiling code:")
        print("-" * 40)
        print(sample_code)
        print("-" * 40)
        
        # Tokenize and parse
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Generate and optimize IR
        ir_gen = IRGenerator()
        tac_program = ir_gen.generate(ast)
        
        print("Generated TAC:")
        print(tac_program)
        print()
        
        optimizer = Optimizer()
        optimized_tac = optimizer.optimize(tac_program)
        
        print("Optimized TAC:")
        print(optimized_tac)
        print()
        
        # Generate assembly
        codegen = CodeGenerator()
        assembly = codegen.generate(optimized_tac)
        
        print("Generated Assembly:")
        print("-" * 40)
        print(assembly)
        
        # Save to file
        codegen.save_assembly(assembly)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
