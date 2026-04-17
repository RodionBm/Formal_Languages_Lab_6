import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Any
from abc import ABC, abstractmethod
import json
import sys

class TokenType(Enum):
    LET = 'LET'
    PRINT = 'PRINT'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FUNCTION = 'FUNCTION'
    RETURN = 'RETURN'
    
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'
    BOOLEAN = 'BOOLEAN'
    
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    ASSIGN = 'ASSIGN'
    EQUALS = 'EQUALS'
    NOT_EQUALS = 'NOT_EQUALS'
    LESS_THAN = 'LESS_THAN'
    GREATER_THAN = 'GREATER_THAN'
    LESS_EQUAL = 'LESS_EQUAL'
    GREATER_EQUAL = 'GREATER_EQUAL'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'
    
    EOF = 'EOF'
    UNKNOWN = 'UNKNOWN'


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', line={self.line}, col={self.column})"
    
    def to_dict(self):
        return {
            'type': self.type.value,
            'value': self.value,
            'line': self.line,
            'column': self.column
        }


class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.token_patterns = [
            (r'\blet\b', TokenType.LET),
            (r'\bprint\b', TokenType.PRINT),
            (r'\bif\b', TokenType.IF),
            (r'\belse\b', TokenType.ELSE),
            (r'\bwhile\b', TokenType.WHILE),
            (r'\bfunction\b', TokenType.FUNCTION),
            (r'\breturn\b', TokenType.RETURN),
            (r'\btrue\b|\bfalse\b', TokenType.BOOLEAN),
            
            (r'==', TokenType.EQUALS),
            (r'!=', TokenType.NOT_EQUALS),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),
            
            (r'=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),
            (r'!', TokenType.NOT),
            
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            
            (r'"[^"\\]*(\\.[^"\\]*)*"', TokenType.STRING),  
            (r'\d+(\.\d+)?', TokenType.NUMBER),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            (r'\s+', None),
        ]
        
        self.patterns = [(re.compile(pattern), token_type) for pattern, token_type in self.token_patterns]
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.position < len(self.source_code):
            match = None
            
            for pattern, token_type in self.patterns:
                match = pattern.match(self.source_code, self.position)
                if match:
                    value = match.group(0)
                    
                    if token_type is None:
                        newline_count = value.count('\n')
                        if newline_count > 0:
                            self.line += newline_count
                            self.column = 1
                        else:
                            self.column += len(value)
                        
                        self.position = match.end()
                        break
                    
                    token = Token(token_type, value, self.line, self.column)
                    tokens.append(token)
                    
                    self.position = match.end()
                    self.column += len(value)
                    break
            
            if not match:
                char = self.source_code[self.position]
                token = Token(TokenType.UNKNOWN, char, self.line, self.column)
                tokens.append(token)
                print(f"Warning: Unknown character '{char}' at line {self.line}, column {self.column}")
                self.position += 1
                self.column += 1
        
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens


class ASTNode(ABC):
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        pass


class BinaryOperator(Enum):
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    EQUALS = '=='
    NOT_EQUALS = '!='
    LESS_THAN = '<'
    GREATER_THAN = '>'
    LESS_EQUAL = '<='
    GREATER_EQUAL = '>='
    AND = '&&'
    OR = '||'


class UnaryOperator(Enum):
    NOT = '!'
    MINUS = '-'


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    
    def __str__(self) -> str:
        if not self.statements:
            return "Program(empty)"
        statements_str = '\n  '.join(str(stmt) for stmt in self.statements)
        return f"Program(\n  {statements_str}\n)"
    
    def to_dict(self) -> dict:
        return {
            'type': 'Program',
            'statements': [stmt.to_dict() for stmt in self.statements]
        }


@dataclass
class NumberLiteral(ASTNode):
    value: float
    
    def __str__(self) -> str:
        return f"NumberLiteral({self.value})"
    
    def to_dict(self) -> dict:
        return {'type': 'NumberLiteral', 'value': self.value}


@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def __str__(self) -> str:
        return f"StringLiteral('{self.value}')"
    
    def to_dict(self) -> dict:
        return {'type': 'StringLiteral', 'value': self.value}


@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def __str__(self) -> str:
        return f"BooleanLiteral({self.value})"
    
    def to_dict(self) -> dict:
        return {'type': 'BooleanLiteral', 'value': self.value}


@dataclass
class Identifier(ASTNode):
    name: str
    
    def __str__(self) -> str:
        return f"Identifier('{self.name}')"
    
    def to_dict(self) -> dict:
        return {'type': 'Identifier', 'name': self.name}


@dataclass
class BinaryExpression(ASTNode):
    left: ASTNode
    operator: BinaryOperator
    right: ASTNode
    
    def __str__(self) -> str:
        return f"BinaryExpression({self.left}, {self.operator.value}, {self.right})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'BinaryExpression',
            'left': self.left.to_dict(),
            'operator': self.operator.value,
            'right': self.right.to_dict()
        }


@dataclass
class UnaryExpression(ASTNode):
    operator: UnaryOperator
    operand: ASTNode
    
    def __str__(self) -> str:
        return f"UnaryExpression({self.operator.value}, {self.operand})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'UnaryExpression',
            'operator': self.operator.value,
            'operand': self.operand.to_dict()
        }


@dataclass
class AssignmentStatement(ASTNode):
    identifier: Identifier
    value: ASTNode
    
    def __str__(self) -> str:
        return f"Assignment({self.identifier}, {self.value})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'Assignment',
            'identifier': self.identifier.to_dict(),
            'value': self.value.to_dict()
        }


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode
    
    def __str__(self) -> str:
        return f"Print({self.expression})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'Print',
            'expression': self.expression.to_dict()
        }


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode]
    
    def __str__(self) -> str:
        else_str = f", else={self.else_branch}" if self.else_branch else ""
        return f"IfStatement({self.condition}, then={self.then_branch}{else_str})"
    
    def to_dict(self) -> dict:
        result = {
            'type': 'IfStatement',
            'condition': self.condition.to_dict(),
            'then_branch': self.then_branch.to_dict()
        }
        if self.else_branch:
            result['else_branch'] = self.else_branch.to_dict()
        return result


@dataclass
class WhileLoop(ASTNode):
    condition: ASTNode
    body: ASTNode
    
    def __str__(self) -> str:
        return f"WhileLoop({self.condition}, {self.body})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'WhileLoop',
            'condition': self.condition.to_dict(),
            'body': self.body.to_dict()
        }


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]
    
    def __str__(self) -> str:
        if not self.statements:
            return "Block(empty)"
        statements_str = '; '.join(str(stmt) for stmt in self.statements)
        return f"Block({statements_str})"
    
    def to_dict(self) -> dict:
        return {
            'type': 'Block',
            'statements': [stmt.to_dict() for stmt in self.statements]
        }

class Parser:
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0
    
    def current_token(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return Token(TokenType.EOF, '', 0, 0)
    
    def peek(self) -> TokenType:
        return self.current_token().type
    
    def consume(self, expected_type: TokenType) -> Token:
        token = self.current_token()
        if token.type == expected_type:
            self.current_token_index += 1
            return token
        raise SyntaxError(f"Expected {expected_type.value}, got {token.type.value} at line {token.line}, column {token.column}")
    
    def parse(self) -> Program:
        statements = []
        
        while self.peek() != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> ASTNode:
        token_type = self.peek()
        
        if token_type == TokenType.LET:
            return self.parse_assignment()
        elif token_type == TokenType.PRINT:
            return self.parse_print_statement()
        elif token_type == TokenType.IF:
            return self.parse_if_statement()
        elif token_type == TokenType.WHILE:
            return self.parse_while_loop()
        elif token_type == TokenType.LBRACE:
            return self.parse_block()
        else:
            raise SyntaxError(f"Unexpected token {token_type.value} at line {self.current_token().line}, column {self.current_token().column}")
    
    def parse_assignment(self) -> AssignmentStatement:
        self.consume(TokenType.LET)
        id_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.ASSIGN)
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        
        return AssignmentStatement(
            identifier=Identifier(id_token.value),
            value=expr
        )
    
    def parse_print_statement(self) -> PrintStatement:
        """Parse: print expression ;"""
        self.consume(TokenType.PRINT)
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        
        return PrintStatement(expression=expr)
    
    def parse_if_statement(self) -> IfStatement:
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        then_branch = self.parse_statement()
        
        else_branch = None
        if self.peek() == TokenType.ELSE:
            self.consume(TokenType.ELSE)
            else_branch = self.parse_statement()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def parse_while_loop(self) -> WhileLoop:
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        body = self.parse_statement()
        
        return WhileLoop(condition, body)
    
    def parse_block(self) -> Block:
        self.consume(TokenType.LBRACE)
        statements = []
        
        while self.peek() != TokenType.RBRACE and self.peek() != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        
        self.consume(TokenType.RBRACE)
        return Block(statements)
    
    def parse_expression(self, precedence: int = 0) -> ASTNode:
        left = self.parse_primary()
        
        while True:
            token_type = self.peek()
            
            current_precedence = self.get_precedence(token_type)
            
            if current_precedence <= precedence:
                break
            
            self.current_token_index += 1
            
            right = self.parse_expression(current_precedence)
            
            operator = self.token_to_operator(token_type)
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_primary(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.current_token_index += 1
            return NumberLiteral(float(token.value))
        
        elif token.type == TokenType.STRING:
            self.current_token_index += 1
            value = token.value[1:-1]
            value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return StringLiteral(value)
        
        elif token.type == TokenType.BOOLEAN:
            self.current_token_index += 1
            value = token.value.lower() == 'true'
            return BooleanLiteral(value)
        
        elif token.type == TokenType.IDENTIFIER:
            self.current_token_index += 1
            return Identifier(token.value)
        
        elif token.type == TokenType.LPAREN:
            self.current_token_index += 1
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        elif token.type == TokenType.NOT:
            self.current_token_index += 1
            operand = self.parse_primary()
            return UnaryExpression(UnaryOperator.NOT, operand)
        
        elif token.type == TokenType.MINUS:
            self.current_token_index += 1
            operand = self.parse_primary()
            return UnaryExpression(UnaryOperator.MINUS, operand)
        
        else:
            raise SyntaxError(f"Unexpected token {token.type.value} at line {token.line}, column {token.column}")
    
    def get_precedence(self, token_type: TokenType) -> int:
        precedence_map = {
            TokenType.OR: 1,
            TokenType.AND: 2,
            TokenType.EQUALS: 3,
            TokenType.NOT_EQUALS: 3,
            TokenType.LESS_THAN: 4,
            TokenType.GREATER_THAN: 4,
            TokenType.LESS_EQUAL: 4,
            TokenType.GREATER_EQUAL: 4,
            TokenType.PLUS: 5,
            TokenType.MINUS: 5,
            TokenType.MULTIPLY: 6,
            TokenType.DIVIDE: 6,
        }
        return precedence_map.get(token_type, 0)
    
    def token_to_operator(self, token_type: TokenType) -> BinaryOperator:
        operator_map = {
            TokenType.PLUS: BinaryOperator.PLUS,
            TokenType.MINUS: BinaryOperator.MINUS,
            TokenType.MULTIPLY: BinaryOperator.MULTIPLY,
            TokenType.DIVIDE: BinaryOperator.DIVIDE,
            TokenType.EQUALS: BinaryOperator.EQUALS,
            TokenType.NOT_EQUALS: BinaryOperator.NOT_EQUALS,
            TokenType.LESS_THAN: BinaryOperator.LESS_THAN,
            TokenType.GREATER_THAN: BinaryOperator.GREATER_THAN,
            TokenType.LESS_EQUAL: BinaryOperator.LESS_EQUAL,
            TokenType.GREATER_EQUAL: BinaryOperator.GREATER_EQUAL,
            TokenType.AND: BinaryOperator.AND,
            TokenType.OR: BinaryOperator.OR,
        }
        return operator_map[token_type]

def print_section_header(title: str, char: str = '='):
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")


def demonstrate_lexer():
    print_section_header("PART 1: LEXER DEMONSTRATION")
    
    test_code = """
    let x = 42;
    let name = "John Doe";
    let is_valid = true;
    
    if (x > 10) {
        print name;
        let x = x - 5;
    } else {
        print "x is small";
    }
    
    while (x > 0) {
        print x;
        let x = x - 1;
    }
    """
    
    print("Source Code:")
    print("-" * 40)
    print(test_code)
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    print("\nGenerated Tokens:")
    print("-" * 40)
    for token in tokens:
        if token.type != TokenType.EOF:
            print(f"  {token}")
    
    return tokens

def demonstrate_ast_building():
    print_section_header("PART 2: AST DATA STRUCTURES DEMONSTRATION")
    
    program = Program([
        AssignmentStatement(
            Identifier("x"),
            NumberLiteral(10.0)
        ),
        AssignmentStatement(
            Identifier("y"),
            BinaryExpression(
                NumberLiteral(5.0),
                BinaryOperator.PLUS,
                NumberLiteral(3.0)
            )
        ),
        IfStatement(
            BinaryExpression(
                Identifier("x"),
                BinaryOperator.GREATER_THAN,
                Identifier("y")
            ),
            PrintStatement(StringLiteral("x is greater")),
            PrintStatement(StringLiteral("y is greater"))
        ),
        WhileLoop(
            BinaryExpression(
                Identifier("x"),
                BinaryOperator.GREATER_THAN,
                NumberLiteral(0.0)
            ),
            Block([
                PrintStatement(Identifier("x")),
                AssignmentStatement(
                    Identifier("x"),
                    BinaryExpression(
                        Identifier("x"),
                        BinaryOperator.MINUS,
                        NumberLiteral(1.0)
                    )
                )
            ])
        )
    ])
    
    print("Manually Created AST Structure:")
    print("-" * 40)
    print(program)
    
    print("\nAST as JSON:")
    print("-" * 40)
    print(json.dumps(program.to_dict(), indent=2))

def demonstrate_parser():
    print_section_header("PART 3: PARSER AND AST GENERATION DEMONSTRATION")
    
    test_program = """
    let x = 10;
    let y = 20;
    let result = x + y * 2;
    print result;
    
    if (x < y) {
        print "x is less than y";
        let z = y - x;
        print z;
    } else {
        print "x is greater or equal";
    }
    
    let counter = 0;
    while (counter < 3) {
        print counter;
        let counter = counter + 1;
    }
    """
    
    print("Input Source Code:")
    print("-" * 40)
    print(test_program)
    
    print("\n1. Lexical Analysis (Token Generation):")
    print("-" * 40)
    lexer = Lexer(test_program)
    tokens = lexer.tokenize()
    
    for token in tokens:
        if token.type != TokenType.EOF:
            print(f"   {token}")
    
    print("\n2. Syntactic Analysis (AST Generation):")
    print("-" * 40)
    parser = Parser(tokens)
    
    try:
        ast = parser.parse()
        print(ast)
        
        print("\n3. AST as JSON Format:")
        print("-" * 40)
        print(json.dumps(ast.to_dict(), indent=2))
        
        print("\n Parsing completed successfully!")
        
    except SyntaxError as e:
        print(f" Syntax Error: {e}")
        return False

    return True

def demonstrate_with_custom_file():
    if len(sys.argv) > 1:
        print_section_header(f"PARSING FILE: {sys.argv[1]}")
        
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            print("Source Code:")
            print("-" * 40)
            print(source_code)
            
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            print("\nTokens:")
            print("-" * 40)
            for token in tokens:
                if token.type != TokenType.EOF:
                    print(f"  {token}")
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            print("\nAbstract Syntax Tree (AST):")
            print("-" * 40)
            print(ast)
            
            print("\nAST as JSON:")
            print("-" * 40)
            print(json.dumps(ast.to_dict(), indent=2))
            
            print("\n File parsed successfully!")
            return True
            
        except FileNotFoundError:
            print(f" File not found: {sys.argv[1]}")
            return False
        except SyntaxError as e:
            print(f" Syntax Error in file: {e}")
            return False
    
    return False


def print_summary():
    print_section_header("LABORATORY WORK SUMMARY")
    
    print("""
 Implemented Features:
────────────────────────────────────────────────────────────
1. TokenType Enum
   • Defined all token categories (keywords, operators, literals, delimiters)
   • Used for lexical analysis categorization

2. Regular Expression-based Lexer
   • Compiled regex patterns for efficient token matching
   • Handles whitespace and tracks line/column numbers
   • Supports string literals with escape sequences

3. Abstract Syntax Tree (AST) Data Structures
   • Hierarchical node classes (Program, Expressions, Statements)
   • Support for binary/unary operations
   • Support for control flow (if-else, while loops)
   • JSON serialization capability

4. Recursive Descent Parser
   • Operator precedence handling (Pratt parsing)
   • Error reporting with line/column information
   • Support for all language constructs

5. Complete Language Features
   • Variables (let statements)
   • Arithmetic expressions (+, -, *, /)
   • Comparison operators (==, !=, <, >, <=, >=)
   • Logical operators (&&, ||, !)
   • Conditional statements (if-else)
   • Loops (while)
   • Print statements
   • Code blocks

6. Demonstrations
   • Lexer output visualization
   • AST structure visualization
   • JSON output format
   • File input support
────────────────────────────────────────────────────────────
    """)


def main():
    print_section_header("FORMAL LANGUAGES PARSER & AST", "=")
    print("Course: Formal Languages & Finite Automata")
    print("Topic: Parser & Building an Abstract Syntax Tree")
    print("=" * 60)
    
    demonstrate_lexer()
    demonstrate_ast_building()
    
    if not demonstrate_with_custom_file():
        demonstrate_parser()
    
    print_summary()
    
    print("\n" + "=" * 60)
    print("PROGRAM EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()