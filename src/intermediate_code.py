import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from enum import Enum

from semantic_analyzer import SemanticAnalyzer, loadAstFromFile
from syntax_analyzer import (
    Program, VariableDeclaration, ExpressionStatement,
    BinaryOperation, AssignmentExpression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral
)

# Definición de las instrucciones de tres direcciones
@dataclass
class ThreeAddressInstruction:
    operation: str
    result: Optional[str] = None
    operand1: Optional[str] = None
    operand2: Optional[str] = None
    
    def __str__(self):
        if self.operation == "declare":
            return f"declare {self.result}"
        elif self.operand2 is not None:
            return f"{self.result} = {self.operand1} {self.operation} {self.operand2}"
        elif self.operand1 is not None:
            return f"{self.result} = {self.operand1}"
        else:
            return self.operation

class ThreeAddressCodeGenerator:
    def __init__(self, ast: Program, symbolTable: Dict[str, any]):
        self.ast = ast
        self.symbolTable = symbolTable
        self.instructions: List[ThreeAddressInstruction] = []
        self.tempCounter = 0
    
    # Método principal para generar el código intermedio
    def generate(self) -> List[ThreeAddressInstruction]:
        self.generateProgram(self.ast)
        return self.instructions
    
    # Generar un nombre temporal único
    def generateTemp(self) -> str:
        self.tempCounter += 1
        return f"t{self.tempCounter}"
    
    # Generar código para el programa
    def generateProgram(self, node: Program):
        for declaration in node.declarations:
            if isinstance(declaration, VariableDeclaration):
                self.generateVariableDeclaration(declaration)
            elif isinstance(declaration, ExpressionStatement):
                self.generateExpressionStatement(declaration)
    
    # Generar código para una declaración de variable
    def generateVariableDeclaration(self, node: VariableDeclaration):
        self.emitDeclare(node.identifier)
        
        if node.initializer:
            initTemp = self.generateExpression(node.initializer)
            self.emitAssignment(node.identifier, initTemp)
    
    # Generar código para una declaración de expresión
    def generateExpressionStatement(self, node: ExpressionStatement):
        self.generateExpression(node.expression)
    
    # Generar código para una expresión
    def generateExpression(self, node) -> str:
        if isinstance(node, IntegerLiteral):
            temp = self.generateTemp()
            self.emitAssignment(temp, str(node.value))
            return temp
        
        elif isinstance(node, FloatLiteral):
            temp = self.generateTemp()
            self.emitAssignment(temp, str(node.value))
            return temp
        
        elif isinstance(node, StringLiteral):
            temp = self.generateTemp()
            self.emitAssignment(temp, f'"{node.value}"')
            return temp
        
        elif isinstance(node, BooleanLiteral):
            temp = self.generateTemp()
            self.emitAssignment(temp, str(node.value).lower())
            return temp
        
        elif isinstance(node, Identifier):
            return node.name
        
        elif isinstance(node, AssignmentExpression):
            return self.generateAssignment(node)
        
        elif isinstance(node, BinaryOperation):
            return self.generateBinaryOperation(node)
        
        else:
            temp = self.generateTemp()
            self.emitAssignment(temp, "ERROR")
            return temp
    
    # Generar código para una asignación
    def generateAssignment(self, node: AssignmentExpression) -> str:
        if not isinstance(node.left, Identifier):
            temp = self.generateTemp()
            self.emitAssignment(temp, "ERROR")
            return temp
        
        varName = node.left.name
        
        if node.operator == '=':
            rightTemp = self.generateExpression(node.right)
            self.emitAssignment(varName, rightTemp)
            return varName
        
        elif node.operator in ['+=', '-=', '*=']:
            rightTemp = self.generateExpression(node.right)
            resultTemp = self.generateTemp()
            
            opMap = {'+=': '+', '-=': '-', '*=': '*'}
            binaryOp = opMap[node.operator]
            
            self.emitBinaryOp(resultTemp, varName, binaryOp, rightTemp)
            
            self.emitAssignment(varName, resultTemp)
            
            return varName
        
        else:
            temp = self.generateTemp()
            self.emitAssignment(temp, "ERROR")
            return temp
    
    # Generar código para operaciones binarias
    def generateBinaryOperation(self, node: BinaryOperation) -> str:
        leftTemp = self.generateExpression(node.left)
        rightTemp = self.generateExpression(node.right)
        resultTemp = self.generateTemp()
        
        self.emitBinaryOp(resultTemp, leftTemp, node.operator, rightTemp)
        
        return resultTemp
    
    # Emitir una declaración de variable
    def emitDeclare(self, varName: str):
        instruction = ThreeAddressInstruction("declare", varName)
        self.instructions.append(instruction)
    
    # Emitir una asignación simple
    def emitAssignment(self, result: str, operand: str):
        instruction = ThreeAddressInstruction("=", result, operand)
        self.instructions.append(instruction)
    
    # Emitir una operación binaria
    def emitBinaryOp(self, result: str, operand1: str, operator: str, operand2: str):
        instruction = ThreeAddressInstruction(operator, result, operand1, operand2)
        self.instructions.append(instruction)
    
    # Guardar el código generado en un archivo
    def saveCode(self, filename: str = "intermediate_code.txt"):
        with open(filename, 'w') as file:
            for instruction in self.instructions:
                file.write(f"{instruction}\n")

# Este es el punto de entrada del programa, donde se carga el AST y se ejecuta el análisis semántico, luego se genera el código intermedio.
def main():
    ast = loadAstFromFile()
    if not ast:
        return
    
    analyzer = SemanticAnalyzer(ast)
    success, errors, warnings = analyzer.analyze()
    
    if not success:
        print("Análisis semántico fallido. Errores encontrados:")
        print("\nErrores:")
        for error in errors:
            print(f"  - {error}")
        print("\nAdvertencias:")
        for warning in warnings:
            print(f"  - {warning}")
        return
    
    print("\nGenerando código intermedio...")
    codeGen = ThreeAddressCodeGenerator(ast, analyzer.symbolTable.symbols)
    codeGen.generate()
    
    codeGen.saveCode()
    
    return codeGen

if __name__ == "__main__":
    main()