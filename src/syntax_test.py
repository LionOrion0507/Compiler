import unittest

from syntax_analyzer import (
    SyntaxAnalyzer, Program, VariableDeclaration, FunctionDeclaration,
    Parameter, CompoundStatement, IfStatement, WhileStatement, ForStatement,
    ReturnStatement, ExpressionStatement, BinaryOperation, AssignmentExpression,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)

class TestSyntaxAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.maxDiff = None  # Show full diff for failed assertions
    
    def createTokens(self, token_list):
        """Helper method to create token dictionaries."""
        return token_list
    
    def testVariableDeclarationInt(self):
        """Test parsing of integer variable declaration."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.declarations), 1)
        
        var_decl = ast.declarations[0]
        self.assertIsInstance(var_decl, VariableDeclaration)
        self.assertEqual(var_decl.typeSpec, 'int')
        self.assertEqual(var_decl.identifier, 'x')
        self.assertIsNone(var_decl.initializer)
    
    def testVariableDeclarationWithInitialization(self):
        """Test parsing of variable declaration with initialization."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'INTEGER', 'value': '42'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        var_decl = ast.declarations[0]
        self.assertIsInstance(var_decl.initializer, IntegerLiteral)
        self.assertEqual(var_decl.initializer.value, 42)
    
    def testFunctionDeclarationNoParams(self):
        """Test parsing of function declaration without parameters."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'main'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        self.assertIsInstance(func_decl, FunctionDeclaration)
        self.assertEqual(func_decl.returnType, 'int')
        self.assertEqual(func_decl.identifier, 'main')
        self.assertEqual(len(func_decl.parameters), 0)
        self.assertIsInstance(func_decl.body, CompoundStatement)
    
    def testFunctionDeclarationWithParams(self):
        """Test parsing of function declaration with parameters."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'add'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'a'},
            {'type': 'COMMA', 'value': ','},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'b'},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        self.assertEqual(len(func_decl.parameters), 2)
        
        param1 = func_decl.parameters[0]
        self.assertIsInstance(param1, Parameter)
        self.assertEqual(param1.typeSpec, 'int')
        self.assertEqual(param1.identifier, 'a')
        
        param2 = func_decl.parameters[1]
        self.assertEqual(param2.typeSpec, 'int')
        self.assertEqual(param2.identifier, 'b')
    
    def testIfStatement(self):
        """Test parsing of if statement."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'test'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'IF', 'value': 'if'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'EQUAL', 'value': '=='},
            {'type': 'INTEGER', 'value': '5'},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RBRACE', 'value': '}'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        if_stmt = func_decl.body.statements[0]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(if_stmt.condition, BinaryOperation)
        self.assertEqual(if_stmt.condition.operator, '==')
    
    def testWhileStatement(self):
        """Test parsing of while statement."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'test'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'WHILE', 'value': 'while'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'LESS_THAN', 'value': '<'},
            {'type': 'INTEGER', 'value': '10'},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RBRACE', 'value': '}'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        while_stmt = func_decl.body.statements[0]
        self.assertIsInstance(while_stmt, WhileStatement)
        self.assertIsInstance(while_stmt.condition, BinaryOperation)
        self.assertEqual(while_stmt.condition.operator, '<')
    
    def testForStatement(self):
        """Test parsing of for statement."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'test'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'FOR', 'value': 'for'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'i'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'INTEGER', 'value': '0'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'IDENTIFIER', 'value': 'i'},
            {'type': 'LESS_THAN', 'value': '<'},
            {'type': 'INTEGER', 'value': '10'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'IDENTIFIER', 'value': 'i'},
            {'type': 'PLUS_ASSIGN', 'value': '+='},
            {'type': 'INTEGER', 'value': '1'},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RBRACE', 'value': '}'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        for_stmt = func_decl.body.statements[0]
        self.assertIsInstance(for_stmt, ForStatement)
        self.assertIsInstance(for_stmt.initialization, VariableDeclaration)
        self.assertIsInstance(for_stmt.condition, BinaryOperation)
        self.assertIsInstance(for_stmt.increment, AssignmentExpression)
    
    def testReturnStatement(self):
        """Test parsing of return statement."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'test'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'RETURN', 'value': 'return'},
            {'type': 'INTEGER', 'value': '42'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        return_stmt = func_decl.body.statements[0]
        self.assertIsInstance(return_stmt, ReturnStatement)
        self.assertIsInstance(return_stmt.expression, IntegerLiteral)
        self.assertEqual(return_stmt.expression.value, 42)
    
    def testBinaryOperations(self):
        """Test parsing of binary operations."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'result'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'INTEGER', 'value': '5'},
            {'type': 'PLUS', 'value': '+'},
            {'type': 'INTEGER', 'value': '3'},
            {'type': 'MULTIPLY', 'value': '*'},
            {'type': 'INTEGER', 'value': '2'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        var_decl = ast.declarations[0]
        # Should parse as: 5 + (3 * 2) due to operator precedence
        self.assertIsInstance(var_decl.initializer, BinaryOperation)
        self.assertEqual(var_decl.initializer.operator, '+')
        
        # Right side should be multiplication
        right_side = var_decl.initializer.right
        self.assertIsInstance(right_side, BinaryOperation)
        self.assertEqual(right_side.operator, '*')
    
    def testAssignmentExpression(self):
        """Test parsing of assignment expression."""
        tokens = self.createTokens([
            {'type': 'FUNCTION', 'value': 'function'},
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'test'},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'LBRACE', 'value': '{'},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'INTEGER', 'value': '10'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'RBRACE', 'value': '}'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        func_decl = ast.declarations[0]
        expr_stmt = func_decl.body.statements[0]
        self.assertIsInstance(expr_stmt, ExpressionStatement)
        self.assertIsInstance(expr_stmt.expression, AssignmentExpression)
        self.assertEqual(expr_stmt.expression.operator, '=')
    
    def testDifferentLiterals(self):
        """Test parsing of different literal types."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_FLOAT', 'value': 'float'},
            {'type': 'IDENTIFIER', 'value': 'f'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'FLOAT', 'value': '3.14'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'KEYWORD_STRING', 'value': 'string'},
            {'type': 'IDENTIFIER', 'value': 's'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'STRING', 'value': 'hello'},
            {'type': 'SEMICOLON', 'value': ';'},
            {'type': 'KEYWORD_BOOL', 'value': 'bool'},
            {'type': 'IDENTIFIER', 'value': 'b'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'TRUE', 'value': 'true'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        self.assertEqual(len(ast.declarations), 3)
        
        # Float literal
        float_decl = ast.declarations[0]
        self.assertIsInstance(float_decl.initializer, FloatLiteral)
        self.assertEqual(float_decl.initializer.value, 3.14)
        
        # String literal
        string_decl = ast.declarations[1]
        self.assertIsInstance(string_decl.initializer, StringLiteral)
        self.assertEqual(string_decl.initializer.value, 'hello')
        
        # Boolean literal
        bool_decl = ast.declarations[2]
        self.assertIsInstance(bool_decl.initializer, BooleanLiteral)
        self.assertTrue(bool_decl.initializer.value)
    
    def testSyntaxErrors(self):
        """Test handling of syntax errors."""
        # Missing semicolon
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'x'}
            # Missing semicolon
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertFalse(success)
        self.assertTrue(len(analyzer.errors) > 0)
    
    def testEmptyProgram(self):
        """Test parsing of empty program."""
        tokens = []
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.declarations), 0)
    
    def testParenthesizedExpression(self):
        """Test parsing of parenthesized expressions."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'result'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'LPAREN', 'value': '('},
            {'type': 'INTEGER', 'value': '5'},
            {'type': 'PLUS', 'value': '+'},
            {'type': 'INTEGER', 'value': '3'},
            {'type': 'RPAREN', 'value': ')'},
            {'type': 'MULTIPLY', 'value': '*'},
            {'type': 'INTEGER', 'value': '2'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        var_decl = ast.declarations[0]
        # Should parse as: (5 + 3) * 2 due to parentheses
        self.assertIsInstance(var_decl.initializer, BinaryOperation)
        self.assertEqual(var_decl.initializer.operator, '*')
    
    def testUnaryMinus(self):
        """Test parsing of unary minus expression."""
        tokens = self.createTokens([
            {'type': 'KEYWORD_INT', 'value': 'int'},
            {'type': 'IDENTIFIER', 'value': 'x'},
            {'type': 'ASSIGN', 'value': '='},
            {'type': 'MINUS', 'value': '-'},
            {'type': 'INTEGER', 'value': '5'},
            {'type': 'SEMICOLON', 'value': ';'}
        ])
        
        analyzer = SyntaxAnalyzer(tokens)
        success, ast, message = analyzer.parse()
        
        self.assertTrue(success)
        var_decl = ast.declarations[0]
        # Unary minus is represented as: 0 - 5
        self.assertIsInstance(var_decl.initializer, BinaryOperation)
        self.assertEqual(var_decl.initializer.operator, '-')
        self.assertIsInstance(var_decl.initializer.left, IntegerLiteral)
        self.assertEqual(var_decl.initializer.left.value, 0)

if __name__ == '__main__':
  unittest.main()
