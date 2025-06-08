"""
Parser module for the educational compiler.
Builds an Abstract Syntax Tree (AST) from tokens using recursive descent parsing.
"""

from typing import List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from lexer import Token, TokenType, Lexer

# AST Node Base Classes
class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass

class Expression(ASTNode):
    """Base class for all expression nodes."""
    pass

class Statement(ASTNode):
    """Base class for all statement nodes."""
    pass

# Expression Nodes
@dataclass
class NumberLiteral(Expression):
    """Represents a numeric literal."""
    value: float
    
    def __str__(self):
        return f"NumberLiteral({self.value})"

@dataclass
class Identifier(Expression):
    """Represents a variable identifier."""
    name: str
    
    def __str__(self):
        return f"Identifier({self.name})"

@dataclass
class BinaryOperation(Expression):
    """Represents a binary operation (e.g., +, -, *, /)."""
    left: Expression
    operator: str
    right: Expression
    
    def __str__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"

@dataclass
class UnaryOperation(Expression):
    """Represents a unary operation (e.g., -x)."""
    operator: str
    operand: Expression
    
    def __str__(self):
        return f"UnaryOp({self.operator}{self.operand})"

# Statement Nodes
@dataclass
class VariableDeclaration(Statement):
    """Represents a variable declaration (let x = expr;)."""
    name: str
    value: Expression
    
    def __str__(self):
        return f"VarDecl({self.name} = {self.value})"

@dataclass
class PrintStatement(Statement):
    """Represents a print statement."""
    expression: Expression
    
    def __str__(self):
        return f"Print({self.expression})"

@dataclass
class Program(ASTNode):
    """Represents the entire program as a list of statements."""
    statements: List[Statement]
    
    def __str__(self):
        return f"Program({[str(s) for s in self.statements]})"

class ParseError(Exception):
    """Exception raised for parsing errors."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")

class Parser:
    """
    Recursive descent parser for our minimal language.
    
    Grammar:
    program := statement*
    statement := var_declaration | print_statement
    var_declaration := 'let' IDENTIFIER '=' expression ';'
    print_statement := 'print' '(' expression ')' ';'
    expression := term (('+' | '-') term)*
    term := factor (('*' | '/') factor)*
    factor := NUMBER | IDENTIFIER | '(' expression ')' | ('-' | '+') factor
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self) -> None:
        """Move to the next token."""
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at token at current position + offset."""
        peek_pos = self.position + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """
        Consume and return token if it matches expected type.
        
        Args:
            token_type: Expected token type
            
        Returns:
            The consumed token
            
        Raises:
            ParseError: If token doesn't match expected type
        """
        if not self.current_token or self.current_token.type != token_type:
            expected = token_type.value
            actual = self.current_token.type.value if self.current_token else "EOF"
            raise ParseError(f"Expected {expected}, got {actual}", 
                           self.current_token or Token(TokenType.EOF, "", 0, 0))
        
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self) -> None:
        """Skip over newline tokens."""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """
        Parse the entire program.
        
        Returns:
            Program AST node containing all statements
            
        Raises:
            ParseError: If parsing fails
        """
        statements = []
        
        self.skip_newlines()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Skip empty lines
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            
            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Statement:
        """
        Parse a single statement.
        
        Returns:
            Statement AST node
            
        Raises:
            ParseError: If statement is invalid
        """
        if not self.current_token:
            raise ParseError("Unexpected end of file", 
                           Token(TokenType.EOF, "", 0, 0))
        
        if self.current_token.type == TokenType.LET:
            return self.parse_variable_declaration()
        elif self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        else:
            raise ParseError(f"Unexpected token '{self.current_token.value}'", 
                           self.current_token)
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parse a variable declaration: let x = expr;"""
        self.expect(TokenType.LET)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        return VariableDeclaration(name_token.value, value)
    
    def parse_print_statement(self) -> PrintStatement:
        """Parse a print statement: print(expr);"""
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        expr = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        
        return PrintStatement(expr)
    
    def parse_expression(self) -> Expression:
        """Parse an expression with addition and subtraction."""
        left = self.parse_term()
        
        while (self.current_token and 
               self.current_token.type in [TokenType.PLUS, TokenType.MINUS]):
            operator = self.current_token.value
            self.advance()
            right = self.parse_term()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_term(self) -> Expression:
        """Parse a term with multiplication and division."""
        left = self.parse_factor()
        
        while (self.current_token and 
               self.current_token.type in [TokenType.MULTIPLY, TokenType.DIVIDE]):
            operator = self.current_token.value
            self.advance()
            right = self.parse_factor()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_factor(self) -> Expression:
        """Parse a factor (primary expression)."""
        if not self.current_token:
            raise ParseError("Unexpected end of file in expression", 
                           Token(TokenType.EOF, "", 0, 0))
        
        # Handle numbers
        if self.current_token.type == TokenType.NUMBER:
            value = float(self.current_token.value)
            self.advance()
            return NumberLiteral(value)
        
        # Handle identifiers
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        # Handle parenthesized expressions
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Handle unary operators
        elif self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.current_token.value
            self.advance()
            operand = self.parse_factor()
            return UnaryOperation(operator, operand)
        
        else:
            raise ParseError(f"Unexpected token '{self.current_token.value}' in expression", 
                           self.current_token)

def print_ast(node: ASTNode, indent: int = 0) -> None:
    """Pretty print the AST for debugging."""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, VariableDeclaration):
        print(f"{prefix}VariableDeclaration: {node.name}")
        print_ast(node.value, indent + 1)
    
    elif isinstance(node, PrintStatement):
        print(f"{prefix}PrintStatement:")
        print_ast(node.expression, indent + 1)
    
    elif isinstance(node, BinaryOperation):
        print(f"{prefix}BinaryOperation: {node.operator}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    
    elif isinstance(node, UnaryOperation):
        print(f"{prefix}UnaryOperation: {node.operator}")
        print_ast(node.operand, indent + 1)
    
    elif isinstance(node, NumberLiteral):
        print(f"{prefix}NumberLiteral: {node.value}")
    
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier: {node.name}")

# Example usage and testing
if __name__ == "__main__":
    # Test the parser with sample code
    sample_code = """
    let x = 5 + 3;
    let y = x * 2;
    print(y);
    """
    
    try:
        # Tokenize
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        print("Parsing Results:")
        print("-" * 40)
        print_ast(ast)
        
    except (ParseError, Exception) as e:
        print(f"Parser Error: {e}")
