"""
Lexer module for the educational compiler.
Tokenizes source code into a stream of tokens for parsing.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    """Enumeration of all token types in our language."""
    # Literals
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    
    # Keywords
    LET = "LET"
    PRINT = "PRINT"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    ASSIGN = "ASSIGN"
    
    # Delimiters
    SEMICOLON = "SEMICOLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    
    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"

@dataclass
class Token:
    """Represents a single token with its type, value, and position."""
    type: TokenType
    value: str
    line: int
    column: int

class LexerError(Exception):
    """Exception raised for lexical analysis errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")

class Lexer:
    """
    Lexical analyzer that converts source code into tokens.
    
    Supports a minimal C-like language with:
    - Variable declarations (let)
    - Arithmetic expressions (+, -, *, /)
    - Print statements
    - Numbers and identifiers
    """
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Keywords mapping
        self.keywords = {
            'let': TokenType.LET,
            'print': TokenType.PRINT,
        }
        
        # Single character tokens
        self.single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.ASSIGN,
            ';': TokenType.SEMICOLON,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
        }
    
    def current_char(self) -> Optional[str]:
        """Get the current character being processed."""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead at the character at current position + offset."""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        """Move to the next character and update position tracking."""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters except newlines."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_number(self) -> Token:
        """Read a numeric literal."""
        start_column = self.column
        value = ''
        
        while self.current_char() and self.current_char().isdigit():
            value += self.current_char()
            self.advance()
        
        # Handle decimal numbers
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            value += self.current_char()
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                value += self.current_char()
                self.advance()
        
        return Token(TokenType.NUMBER, value, self.line, start_column)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_column = self.column
        value = ''
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            value += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        
        return Token(token_type, value, self.line, start_column)
    
    def tokenize(self) -> List[Token]:
        """
        Convert the entire source code into a list of tokens.
        
        Returns:
            List of tokens representing the source code
            
        Raises:
            LexerError: If an invalid character is encountered
        """
        while self.position < len(self.source):
            self.skip_whitespace()
            
            char = self.current_char()
            if not char:
                break
            
            # Handle newlines
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
                continue
            
            # Handle numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Handle single character tokens
            if char in self.single_char_tokens:
                token_type = self.single_char_tokens[char]
                self.tokens.append(Token(token_type, char, self.line, self.column))
                self.advance()
                continue
            
            # Handle comments (optional feature)
            if char == '#':
                # Skip until end of line
                while self.current_char() and self.current_char() != '\n':
                    self.advance()
                continue
            
            # Unknown character
            raise LexerError(f"Unexpected character '{char}'", self.line, self.column)
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def print_tokens(self) -> None:
        """Print all tokens for debugging purposes."""
        for token in self.tokens:
            print(f"{token.type.value:12} | {token.value:10} | Line {token.line}, Col {token.column}")

# Example usage and testing
if __name__ == "__main__":
    # Test the lexer with sample code
    sample_code = """
    let x = 5 + 3;
    let y = x * 2;
    print(y);
    """
    
    try:
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        print("Lexical Analysis Results:")
        print("-" * 40)
        lexer.print_tokens()
    except LexerError as e:
        print(f"Lexer Error: {e}")
