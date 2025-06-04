import unittest
import os
import tempfile

from semantic_analyzer import (Symbol, DataType)
from intermediate_code import (
    ThreeAddressCodeGenerator, ThreeAddressInstruction
)
from syntax_analyzer import (
    Program, VariableDeclaration, ExpressionStatement,
    BinaryOperation, AssignmentExpression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral
)

class TestThreeAddressInstruction(unittest.TestCase):
    def testDeclareInstruction(self):
        """Test string representation of declare instruction"""
        instr = ThreeAddressInstruction("declare", "x")
        self.assertEqual(str(instr), "declare x")
    
    def testBinaryOperationInstruction(self):
        """Test string representation of binary operation instruction"""
        instr = ThreeAddressInstruction("+", "t1", "x", "y")
        self.assertEqual(str(instr), "t1 = x + y")
    
    def testAssignmentInstruction(self):
        """Test string representation of assignment instruction"""
        instr = ThreeAddressInstruction("=", "x", "42")
        self.assertEqual(str(instr), "x = 42")
    
    def testSimpleOperation(self):
        """Test string representation of simple operation"""
        instr = ThreeAddressInstruction("jump")
        self.assertEqual(str(instr), "jump")


class TestThreeAddressCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.createTestComponents()
    
    def createTestComponents(self):
        """Create common test components"""
        self.symbol_table = {"x": Symbol("x", DataType.INT, True)}
        self.int_literal = IntegerLiteral(value=42)
        self.identifier_x = Identifier(name="x")
    
    def testGenerateTemp(self):
        """Test temporary variable generation"""
        program = Program(declarations=[])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        temp1 = generator.generateTemp()
        temp2 = generator.generateTemp()
        
        self.assertEqual(temp1, "t1")
        self.assertEqual(temp2, "t2")
        self.assertNotEqual(temp1, temp2)
    
    def testGenerateVariableDeclarationNoInitializer(self):
        """Test generating code for variable declaration without initializer"""
        var_decl = VariableDeclaration(typeSpec="int", identifier="x", initializer=None)
        program = Program(declarations=[var_decl])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].operation, "declare")
        self.assertEqual(instructions[0].result, "x")
    
    def testGenerateVariableDeclarationWithInitializer(self):
        """Test generating code for variable declaration with initializer"""
        var_decl = VariableDeclaration(
            typeSpec="int", 
            identifier="x", 
            initializer=self.int_literal
        )
        program = Program(declarations=[var_decl])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[0].operation, "declare")
        self.assertEqual(instructions[1].operation, "=")  # temp assignment
        self.assertEqual(instructions[2].operation, "=")  # variable assignment
    
    def testGenerateIntegerLiteral(self):
        """Test generating code for integer literal"""
        program = Program(declarations=[
            ExpressionStatement(expression=self.int_literal)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].operation, "=")
        self.assertEqual(instructions[0].operand1, "42")
    
    def testGenerateFloatLiteral(self):
        """Test generating code for float literal"""
        float_literal = FloatLiteral(value=3.14)
        program = Program(declarations=[
            ExpressionStatement(expression=float_literal)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].operation, "=")
        self.assertEqual(instructions[0].operand1, "3.14")
    
    def testGenerateStringLiteral(self):
        """Test generating code for string literal"""
        string_literal = StringLiteral(value="hello")
        program = Program(declarations=[
            ExpressionStatement(expression=string_literal)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].operation, "=")
        self.assertEqual(instructions[0].operand1, '"hello"')
    
    def testGenerateBooleanLiteral(self):
        """Test generating code for boolean literal"""
        bool_literal = BooleanLiteral(value=True)
        program = Program(declarations=[
            ExpressionStatement(expression=bool_literal)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].operation, "=")
        self.assertEqual(instructions[0].operand1, "true")
    
    def testGenerateIdentifier(self):
        """Test generating code for identifier"""
        program = Program(declarations=[
            ExpressionStatement(expression=self.identifier_x)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        temp = generator.generateExpression(self.identifier_x)
        self.assertEqual(temp, "x")
    
    def testGenerateBinaryOperation(self):
        """Test generating code for binary operation"""
        binary_op = BinaryOperation(
            left=self.int_literal,
            operator="+",
            right=IntegerLiteral(value=10)
        )
        program = Program(declarations=[
            ExpressionStatement(expression=binary_op)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        # Should have: temp1 = 42, temp2 = 10, temp3 = temp1 + temp2
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[2].operation, "+")
        self.assertEqual(instructions[2].operand1, "t1")
        self.assertEqual(instructions[2].operand2, "t2")
    
    def testGenerateSimpleAssignment(self):
        """Test generating code for simple assignment"""
        assignment = AssignmentExpression(
            left=self.identifier_x,
            operator="=",
            right=self.int_literal
        )
        program = Program(declarations=[
            ExpressionStatement(expression=assignment)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        # Should have: temp = 42, x = temp
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[1].operation, "=")
        self.assertEqual(instructions[1].result, "x")
    
    def testGenerateCompoundAssignment(self):
        """Test generating code for compound assignment"""
        assignment = AssignmentExpression(
            left=self.identifier_x,
            operator="+=",
            right=IntegerLiteral(value=5)
        )
        program = Program(declarations=[
            ExpressionStatement(expression=assignment)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        # Should have: temp1 = 5, temp2 = x + temp1, x = temp2
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[1].operation, "+")
        self.assertEqual(instructions[2].operation, "=")
        self.assertEqual(instructions[2].result, "x")
    
    def testGenerateInvalidAssignment(self):
        """Test generating code for invalid assignment (non-identifier left side)"""
        assignment = AssignmentExpression(
            left=self.int_literal,  # Invalid: not an identifier
            operator="=",
            right=IntegerLiteral(value=5)
        )
        program = Program(declarations=[
            ExpressionStatement(expression=assignment)
        ])
        generator = ThreeAddressCodeGenerator(program, self.symbol_table)
        
        instructions = generator.generate()
        
        # Should generate error code
        self.assertTrue(any("ERROR" in str(instr) for instr in instructions))



if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestThreeAddressInstruction,
        TestThreeAddressCodeGenerator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)