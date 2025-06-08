"""
Main entry point for the educational optimizing compiler.
Orchestrates the complete compilation pipeline from source code to x86-64 assembly.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from semantic import SemanticAnalyzer, SemanticError
from optimizer import IRGenerator, Optimizer
from codegen import CodeGenerator

class CompilerError(Exception):
    """Base exception for compiler errors."""
    pass

class Compiler:
    """
    Main compiler class that orchestrates the compilation pipeline.
    
    Pipeline stages:
    1. Lexical Analysis (Tokenization)
    2. Syntax Analysis (Parsing)
    3. Semantic Analysis (Type checking, variable validation)
    4. Intermediate Representation Generation (TAC)
    5. Optimization (Multiple passes)
    6. Code Generation (x86-64 Assembly)
    """
    
    def __init__(self, verbose: bool = False, optimization_level: int = 2):
        """
        Initialize the compiler.
        
        Args:
            verbose: Enable verbose output
            optimization_level: Optimization level (0-3)
        """
        self.verbose = verbose
        self.optimization_level = optimization_level
        
        # Initialize compiler components
        self.lexer: Optional[Lexer] = None
        self.parser: Optional[Parser] = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.ir_generator = IRGenerator()
        self.optimizer = Optimizer()
        self.code_generator = CodeGenerator()
    
    def compile_file(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """
        Compile a source file to assembly.
        
        Args:
            input_file: Path to source file
            output_file: Path to output assembly file (optional)
            
        Returns:
            True if compilation succeeds, False otherwise
        """
        try:
            # Read source file
            source_code = self.read_source_file(input_file)
            
            # Determine output file name
            if not output_file:
                input_path = Path(input_file)
                output_file = input_path.with_suffix('.asm').name
            
            # Compile source code
            return self.compile_source(source_code, output_file)
            
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def compile_source(self, source_code: str, output_file: str) -> bool:
        """
        Compile source code to assembly.
        
        Args:
            source_code: Source code string
            output_file: Output assembly file path
            
        Returns:
            True if compilation succeeds, False otherwise
        """
        try:
            if self.verbose:
                print("Starting compilation pipeline...")
                print("=" * 50)
            
            # Stage 1: Lexical Analysis
            if self.verbose:
                print("Stage 1: Lexical Analysis")
                print("-" * 30)
            
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            if self.verbose:
                print(f"Generated {len(tokens)} tokens")
                self.lexer.print_tokens()
                print()
            
            # Stage 2: Syntax Analysis
            if self.verbose:
                print("Stage 2: Syntax Analysis")
                print("-" * 30)
            
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            if self.verbose:
                print("AST generated successfully")
                from parser import print_ast
                print_ast(ast)
                print()
            
            # Stage 3: Semantic Analysis
            if self.verbose:
                print("Stage 3: Semantic Analysis")
                print("-" * 30)
            
            success = self.semantic_analyzer.analyze(ast)
            
            if not success:
                print("Semantic analysis failed!")
                self.semantic_analyzer.print_errors()
                return False
            
            if self.verbose:
                print("Semantic analysis passed")
                if self.semantic_analyzer.warnings:
                    self.semantic_analyzer.print_errors()
                print()
            
            # Stage 4: IR Generation
            if self.verbose:
                print("Stage 4: Intermediate Representation Generation")
                print("-" * 30)
            
            tac_program = self.ir_generator.generate(ast)
            
            if self.verbose:
                print("Generated TAC:")
                print(tac_program)
                print()
            
            # Stage 5: Optimization
            if self.verbose:
                print("Stage 5: Optimization")
                print("-" * 30)
            
            if self.optimization_level > 0:
                optimized_tac = self.optimizer.optimize(tac_program, passes=self.optimization_level)
                
                if self.verbose:
                    print("Optimized TAC:")
                    print(optimized_tac)
                    print()
            else:
                optimized_tac = tac_program
                if self.verbose:
                    print("Optimization disabled")
                    print()
            
            # Stage 6: Code Generation
            if self.verbose:
                print("Stage 6: Code Generation")
                print("-" * 30)
            
            assembly_code = self.code_generator.generate(optimized_tac)
            
            # Save assembly to file
            self.code_generator.save_assembly(assembly_code, output_file)
            
            if self.verbose:
                print(f"\nGenerated assembly saved to {output_file}")
                print("\nAssembly code:")
                print("-" * 40)
                print(assembly_code)
            
            print(f"\nCompilation successful! Output: {output_file}")
            return True
            
        except LexerError as e:
            print(f"Lexical error: {e}")
            return False
        except ParseError as e:
            print(f"Parse error: {e}")
            return False
        except SemanticError as e:
            print(f"Semantic error: {e}")
            return False
        except Exception as e:
            print(f"Compilation error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def read_source_file(self, filename: str) -> str:
        """Read source code from file."""
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Educational Optimizing Compiler - Compiles minimal C-like language to x86-64 assembly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test_program.txt                 # Compile with default settings
  python main.py input.txt -o output.asm         # Specify output file
  python main.py input.txt -v -O3                # Verbose output with max optimization
  python main.py input.txt -O0                   # No optimization
  
Supported language features:
  - Variable declarations (let x = expr;)
  - Arithmetic expressions (+, -, *, /)
  - Print statements (print(expr);)
  - Integer literals
  - Basic optimizations (constant folding, propagation, dead code elimination)
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input source file to compile'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output assembly file (default: input file with .asm extension)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output showing all compilation stages'
    )
    
    parser.add_argument(
        '-O', '--optimize',
        dest='optimization_level',
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help='Optimization level (0=none, 1=basic, 2=standard, 3=aggressive)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Educational Compiler v1.0'
    )
    
    return parser

def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Create compiler instance
    compiler = Compiler(
        verbose=args.verbose,
        optimization_level=args.optimization_level
    )
    
    # Compile file
    success = compiler.compile_file(args.input_file, args.output_file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

def demo():
    """Demonstration function showing compiler usage."""
    print("Educational Optimizing Compiler Demo")
    print("=" * 40)
    
    # Demo source code
    demo_code = """
    let x = 5 + 3;
    let y = x * 2;
    let z = y + 0;  # This will be optimized away
    print(z);
    """
    
    print("Demo source code:")
    print(demo_code)
    print()
    
    # Create compiler and compile
    compiler = Compiler(verbose=True, optimization_level=2)
    success = compiler.compile_source(demo_code, "demo_output.asm")
    
    if success:
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("Generated files:")
        print("  - demo_output.asm (x86-64 assembly)")
        print("\nTo test the generated assembly:")
        print("  1. nasm -f elf64 demo_output.asm")
        print("  2. gcc -o demo_program demo_output.o")
        print("  3. ./demo_program")
    else:
        print("Demo compilation failed!")

if __name__ == "__main__":
    # If no arguments provided, run demo
    if len(sys.argv) == 1:
        demo()
    else:
        main()
