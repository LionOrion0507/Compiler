import unittest

from semantic_analyzer import (
    SemanticAnalyzer, SymbolTable, DataType
)
from syntax_analyzer import (
    Program, VariableDeclaration, ExpressionStatement,
    BinaryOperation, AssignmentExpression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral
)

class TestSymbolTable(unittest.TestCase):
    def setUp(self):
        self.symbol_table = SymbolTable()
    
    def testDeclareNewSymbol(self):
        """Test declaring a new symbol"""
        result = self.symbol_table.declare("x", DataType.INT, 1)
        self.assertTrue(result)
        self.assertIn("x", self.symbol_table.symbols)
        
        symbol = self.symbol_table.lookup("x")
        self.assertEqual(symbol.name, "x")
        self.assertEqual(symbol.dataType, DataType.INT)
        self.assertFalse(symbol.initialized)
        self.assertEqual(symbol.line, 1)
    
    def testDeclareDuplicateSymbol(self):
        """Test declaring a symbol that already exists"""
        self.symbol_table.declare("x", DataType.INT)
        result = self.symbol_table.declare("x", DataType.FLOAT)
        self.assertFalse(result)
    
    def testLookupExistingSymbol(self):
        """Test looking up an existing symbol"""
        self.symbol_table.declare("y", DataType.STRING)
        symbol = self.symbol_table.lookup("y")
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.name, "y")
        self.assertEqual(symbol.dataType, DataType.STRING)
    
    def testLookupNonexistentSymbol(self):
        """Test looking up a symbol that doesn't exist"""
        symbol = self.symbol_table.lookup("nonexistent")
        self.assertIsNone(symbol)
    
    def testAssignExistingSymbol(self):
        """Test assigning to an existing symbol"""
        self.symbol_table.declare("z", DataType.BOOL)
        result = self.symbol_table.assign("z")
        self.assertTrue(result)
        
        symbol = self.symbol_table.lookup("z")
        self.assertTrue(symbol.initialized)
    
    def testAssignNonexistentSymbol(self):
        """Test assigning to a symbol that doesn't exist"""
        result = self.symbol_table.assign("nonexistent")
        self.assertFalse(result)


class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.createTestNodes()
    
    def createTestNodes(self):
        """Create common test AST nodes"""
        self.int_literal = IntegerLiteral(value=42)
        self.float_literal = FloatLiteral(value=3.14)
        self.string_literal = StringLiteral(value="hello")
        self.bool_literal = BooleanLiteral(value=True)
        self.identifier_x = Identifier(name="x")
        self.identifier_y = Identifier(name="y")
    
    def testAnalyzeIntegerLiteral(self):
        """Test analyzing integer literals"""
        program = Program(declarations=[
            ExpressionStatement(expression=self.int_literal)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(warnings), 0)
    
    def testAnalyzeVariableDeclarationValid(self):
        """Test valid variable declaration"""
        var_decl = VariableDeclaration(
            typeSpec="int",
            identifier="x",
            initializer=self.int_literal
        )
        program = Program(declarations=[var_decl])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        self.assertIn("x", analyzer.symbolTable.symbols)
        self.assertTrue(analyzer.symbolTable.symbols["x"].initialized)
    
    def testAnalyzeVariableDeclarationInvalidType(self):
        """Test variable declaration with invalid type"""
        var_decl = VariableDeclaration(
            typeSpec="invalid_type",
            identifier="x",
            initializer=None
        )
        program = Program(declarations=[var_decl])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
        self.assertIn("Tipo invalido", errors[0])
    
    def testAnalyzeVariableDeclarationTypeMismatch(self):
        """Test variable declaration with type mismatch"""
        var_decl = VariableDeclaration(
            typeSpec="int",
            identifier="x",
            initializer=self.string_literal
        )
        program = Program(declarations=[var_decl])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
        self.assertIn("No se puede asignar", errors[0])
    
    def testAnalyzeDuplicateVariableDeclaration(self):
        """Test duplicate variable declaration"""
        var_decl1 = VariableDeclaration(typeSpec="int", identifier="x", initializer=None)
        var_decl2 = VariableDeclaration(typeSpec="float", identifier="x", initializer=None)
        program = Program(declarations=[var_decl1, var_decl2])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
        self.assertIn("ya está declarada", errors[0])
    
    def testAnalyzeUndefinedVariable(self):
        """Test using an undefined variable"""
        program = Program(declarations=[
            ExpressionStatement(expression=self.identifier_x)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
        self.assertIn("Variable no definida", errors[0])
    
    def testAnalyzeUninitializedVariableWarning(self):
        """Test warning for using uninitialized variable"""
        var_decl = VariableDeclaration(typeSpec="int", identifier="x", initializer=None)
        expr_stmt = ExpressionStatement(expression=self.identifier_x)
        program = Program(declarations=[var_decl, expr_stmt])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(warnings), 1)
        self.assertIn("usada sin inicializar", warnings[0])
    
    def testAnalyzeBinaryOperationValid(self):
        """Test valid binary operations"""
        binary_op = BinaryOperation(
            left=self.int_literal,
            operator="+",
            right=IntegerLiteral(value=10)
        )
        program = Program(declarations=[
            ExpressionStatement(expression=binary_op)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def testAnalyzeBinaryOperationTypeMismatch(self):
        """Test binary operation with incompatible types"""
        binary_op = BinaryOperation(
            left=self.int_literal,
            operator="+",
            right=self.bool_literal
        )
        program = Program(declarations=[
            ExpressionStatement(expression=binary_op)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
        self.assertIn("Tipos invalidos", errors[0])
    
    def testAnalyzeStringConcatenation(self):
        """Test string concatenation with + operator"""
        binary_op = BinaryOperation(
            left=self.string_literal,
            operator="+",
            right=StringLiteral(value=" world")
        )
        program = Program(declarations=[
            ExpressionStatement(expression=binary_op)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def testAnalyzeAssignmentValid(self):
        """Test valid assignment"""
        var_decl = VariableDeclaration(typeSpec="int", identifier="x", initializer=None)
        assignment = AssignmentExpression(
            left=self.identifier_x,
            operator="=",
            right=self.int_literal
        )
        program = Program(declarations=[
            var_decl,
            ExpressionStatement(expression=assignment)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def testAnalyzeCompoundAssignment(self):
        """Test compound assignment operators"""
        var_decl = VariableDeclaration(typeSpec="int", identifier="x", initializer=self.int_literal)
        assignment = AssignmentExpression(
            left=self.identifier_x,
            operator="+=",
            right=IntegerLiteral(value=5)
        )
        program = Program(declarations=[
            var_decl,
            ExpressionStatement(expression=assignment)
        ])
        analyzer = SemanticAnalyzer(program)
        success, errors, warnings = analyzer.analyze()
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def testTypeCompatibility(self):
        """Test type compatibility checks"""
        analyzer = SemanticAnalyzer(Program(declarations=[]))
        
        # Same types should be compatible
        self.assertTrue(analyzer.areTypesCompatible(DataType.INT, DataType.INT))
        
        # Int and float should be compatible
        self.assertTrue(analyzer.areTypesCompatible(DataType.INT, DataType.FLOAT))
        self.assertTrue(analyzer.areTypesCompatible(DataType.FLOAT, DataType.INT))
        
        # String and int should not be compatible
        self.assertFalse(analyzer.areTypesCompatible(DataType.STRING, DataType.INT))
    
    def testNumericTypeCheck(self):
        """Test numeric type checking"""
        analyzer = SemanticAnalyzer(Program(declarations=[]))
        
        self.assertTrue(analyzer.isNumericType(DataType.INT))
        self.assertTrue(analyzer.isNumericType(DataType.FLOAT))
        self.assertFalse(analyzer.isNumericType(DataType.STRING))
        self.assertFalse(analyzer.isNumericType(DataType.BOOL))


if __name__ == '__main__':
    # Create a test suite
    testSuite = unittest.TestSuite()
    
    # Add all test classes
    testClasses = [
        TestSymbolTable,
        TestSemanticAnalyzer
    ]
    
    for testClass in testClasses:
        tests = unittest.TestLoader().loadTestsFromTestCase(testClass)
        testSuite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(testSuite)
