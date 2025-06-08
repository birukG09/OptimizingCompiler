"""
Semantic analyzer module for the educational compiler.
Performs type checking, variable declaration validation, and other semantic analysis.
"""

from typing import Dict, Set, List, Optional
from dataclasses import dataclass
from parser import (
    ASTNode, Program, Statement, Expression,
    VariableDeclaration, PrintStatement,
    BinaryOperation, UnaryOperation, NumberLiteral, Identifier
)

class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        super().__init__(f"Semantic error: {message}")

@dataclass
class VariableInfo:
    """Information about a declared variable."""
    name: str
    type: str
    is_initialized: bool = True
    line: Optional[int] = None

class SymbolTable:
    """
    Symbol table for tracking variable declarations and scopes.
    For our simple language, we only have global scope.
    """
    
    def __init__(self):
        self.variables: Dict[str, VariableInfo] = {}
    
    def declare_variable(self, name: str, var_type: str, line: Optional[int] = None) -> None:
        """
        Declare a new variable.
        
        Args:
            name: Variable name
            var_type: Variable type
            line: Line number for error reporting
            
        Raises:
            SemanticError: If variable is already declared
        """
        if name in self.variables:
            raise SemanticError(f"Variable '{name}' is already declared")
        
        self.variables[name] = VariableInfo(name, var_type, True, line)
    
    def lookup_variable(self, name: str) -> Optional[VariableInfo]:
        """Look up a variable by name."""
        return self.variables.get(name)
    
    def is_declared(self, name: str) -> bool:
        """Check if a variable is declared."""
        return name in self.variables
    
    def get_all_variables(self) -> List[VariableInfo]:
        """Get all declared variables."""
        return list(self.variables.values())

class TypeChecker:
    """
    Type checker for our minimal language.
    Currently supports only numeric types (int/float).
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.used_variables: Set[str] = set()
    
    def infer_type(self, expr: Expression) -> str:
        """
        Infer the type of an expression.
        
        Args:
            expr: Expression to analyze
            
        Returns:
            Type string ("number")
            
        Raises:
            SemanticError: If type cannot be determined or is invalid
        """
        if isinstance(expr, NumberLiteral):
            return "number"
        
        elif isinstance(expr, Identifier):
            var_info = self.symbol_table.lookup_variable(expr.name)
            if not var_info:
                raise SemanticError(f"Undefined variable '{expr.name}'")
            
            self.used_variables.add(expr.name)
            return var_info.type
        
        elif isinstance(expr, BinaryOperation):
            left_type = self.infer_type(expr.left)
            right_type = self.infer_type(expr.right)
            
            # For our simple language, all arithmetic operations work on numbers
            if left_type != "number" or right_type != "number":
                raise SemanticError(f"Cannot apply operator '{expr.operator}' to types {left_type} and {right_type}")
            
            return "number"
        
        elif isinstance(expr, UnaryOperation):
            operand_type = self.infer_type(expr.operand)
            
            if operand_type != "number":
                raise SemanticError(f"Cannot apply unary operator '{expr.operator}' to type {operand_type}")
            
            return "number"
        
        else:
            raise SemanticError(f"Unknown expression type: {type(expr)}")

class SemanticAnalyzer:
    """
    Main semantic analyzer that orchestrates all semantic checks.
    """
    
    def __init__(self):
        self.type_checker = TypeChecker()
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
    
    def analyze(self, ast: Program) -> bool:
        """
        Perform semantic analysis on the entire program.
        
        Args:
            ast: Program AST to analyze
            
        Returns:
            True if analysis succeeds, False if errors are found
        """
        try:
            self.analyze_program(ast)
            self.check_unused_variables()
            return len(self.errors) == 0
        except SemanticError as e:
            self.errors.append(e)
            return False
    
    def analyze_program(self, program: Program) -> None:
        """Analyze all statements in the program."""
        for statement in program.statements:
            self.analyze_statement(statement)
    
    def analyze_statement(self, stmt: Statement) -> None:
        """
        Analyze a single statement.
        
        Args:
            stmt: Statement to analyze
            
        Raises:
            SemanticError: If statement has semantic errors
        """
        if isinstance(stmt, VariableDeclaration):
            self.analyze_variable_declaration(stmt)
        elif isinstance(stmt, PrintStatement):
            self.analyze_print_statement(stmt)
        else:
            raise SemanticError(f"Unknown statement type: {type(stmt)}")
    
    def analyze_variable_declaration(self, decl: VariableDeclaration) -> None:
        """
        Analyze a variable declaration.
        
        Args:
            decl: Variable declaration to analyze
            
        Raises:
            SemanticError: If declaration is invalid
        """
        # Check if variable is already declared
        if self.type_checker.symbol_table.is_declared(decl.name):
            raise SemanticError(f"Variable '{decl.name}' is already declared")
        
        # Analyze the initialization expression
        expr_type = self.type_checker.infer_type(decl.value)
        
        # Declare the variable in symbol table
        self.type_checker.symbol_table.declare_variable(decl.name, expr_type)
    
    def analyze_print_statement(self, stmt: PrintStatement) -> None:
        """
        Analyze a print statement.
        
        Args:
            stmt: Print statement to analyze
        """
        # Just check that the expression is valid
        self.type_checker.infer_type(stmt.expression)
    
    def check_unused_variables(self) -> None:
        """Check for unused variables and generate warnings."""
        all_vars = self.type_checker.symbol_table.get_all_variables()
        
        for var in all_vars:
            if var.name not in self.type_checker.used_variables:
                self.warnings.append(f"Variable '{var.name}' is declared but never used")
    
    def get_symbol_table(self) -> SymbolTable:
        """Get the symbol table for use by other phases."""
        return self.type_checker.symbol_table
    
    def print_errors(self) -> None:
        """Print all semantic errors."""
        if self.errors:
            print("Semantic Errors:")
            print("-" * 40)
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\nWarnings:")
            print("-" * 40)
            for warning in self.warnings:
                print(f"  {warning}")
    
    def has_errors(self) -> bool:
        """Check if there are any semantic errors."""
        return len(self.errors) > 0

def validate_program(ast: Program) -> tuple[bool, SymbolTable]:
    """
    Convenience function to validate a program and return results.
    
    Args:
        ast: Program AST to validate
        
    Returns:
        Tuple of (success, symbol_table)
    """
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if not success or analyzer.warnings:
        analyzer.print_errors()
    
    return success, analyzer.get_symbol_table()

# Example usage and testing
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Test with valid code
    valid_code = """
    let x = 5 + 3;
    let y = x * 2;
    print(y);
    """
    
    # Test with invalid code (undefined variable)
    invalid_code = """
    let x = 5 + z;  # z is undefined
    print(x);
    """
    
    # Test with redeclaration
    redeclaration_code = """
    let x = 5;
    let x = 10;  # redeclaration error
    """
    
    test_cases = [
        ("Valid Code", valid_code),
        ("Invalid Code (Undefined Variable)", invalid_code),
        ("Invalid Code (Redeclaration)", redeclaration_code)
    ]
    
    for name, code in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {name}")
        print('='*50)
        
        try:
            # Tokenize and parse
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Semantic analysis
            success, symbol_table = validate_program(ast)
            
            if success:
                print("✓ Semantic analysis passed!")
                print("\nDeclared variables:")
                for var in symbol_table.get_all_variables():
                    print(f"  {var.name}: {var.type}")
            else:
                print("✗ Semantic analysis failed!")
                
        except Exception as e:
            print(f"Error: {e}")
