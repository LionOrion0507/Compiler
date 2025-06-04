import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

from syntax_analyzer import (
    ASTNode, Program, VariableDeclaration, ExpressionStatement,
    BinaryOperation, AssignmentExpression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral
)

class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "str"
    BOOL = "bool"
    VOID = "void"
    ERROR = "error"

@dataclass
class Symbol:
    name: str
    dataType: DataType
    initialized: bool = False
    line: Optional[int] = None

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
    
    # Declara un nuevo símbolo en la tabla de símbolos.
    def declare(self, name: str, dataType: DataType, line: Optional[int] = None) -> bool:
        if name in self.symbols:
            return False
        self.symbols[name] = Symbol(name, dataType, False, line)
        return True
    
    # Busca un símbolo por su nombre y devuelve el símbolo si existe.
    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    
    # Asigna un valor a una variable, marcándola como inicializada.
    def assign(self, name: str) -> bool:
        if name not in self.symbols:
            return False
        self.symbols[name].initialized = True
        return True

class SemanticAnalyzer:
    def __init__(self, ast: Program):
        self.ast = ast
        self.symbolTable = SymbolTable()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    # Realiza el análisis semántico del AST y devuelve un resultado.
    def analyze(self) -> Tuple[bool, List[str], List[str]]:
        self.analyzeProgram(self.ast)
        return len(self.errors) == 0, self.errors, self.warnings
    
    # Analiza el programa y sus declaraciones.
    def analyzeProgram(self, node: Program):
        for declaration in node.declarations:
            if isinstance(declaration, VariableDeclaration):
                self.analyzeVariableDeclaration(declaration)
            elif isinstance(declaration, ExpressionStatement):
                self.analyzeExpressionStatement(declaration)
    
    # Analiza una declaración de variable.
    def analyzeVariableDeclaration(self, node: VariableDeclaration):
        typeMapping = {
            'int': DataType.INT,
            'float': DataType.FLOAT,
            'str': DataType.STRING,
            'bool': DataType.BOOL
        }
        
        dataType = typeMapping.get(node.typeSpec)
        if not dataType:
            self.errors.append(f"Tipo invalido '{node.typeSpec}' para '{node.identifier}'")
            return
        
        if not self.symbolTable.declare(node.identifier, dataType):
            self.errors.append(f"Variable '{node.identifier}' ya está declarada")
            return
        
        if node.initializer:
            init_type = self.analyzeExpression(node.initializer)
            if init_type != DataType.ERROR:
                if not self.areTypesCompatible(dataType, init_type):
                    self.errors.append(
                        f"No se puede asignar {init_type.value} al tipo {dataType.value} "
                        f"variable '{node.identifier}'"
                    )
                else:
                    self.symbolTable.assign(node.identifier)
    
    # Analiza una declaración de expresión.
    def analyzeExpressionStatement(self, node: ExpressionStatement):
        self.analyzeExpression(node.expression)
    
    # Analiza una expresión y devuelve su tipo.
    def analyzeExpression(self, node) -> DataType:
        if isinstance(node, IntegerLiteral):
            return DataType.INT
        
        elif isinstance(node, FloatLiteral):
            return DataType.FLOAT
        
        elif isinstance(node, StringLiteral):
            return DataType.STRING
        
        elif isinstance(node, BooleanLiteral):
            return DataType.BOOL
        
        elif isinstance(node, Identifier):
            symbol = self.symbolTable.lookup(node.name)
            if not symbol:
                self.errors.append(f"Variable no definida '{node.name}'")
                return DataType.ERROR
            
            if not symbol.initialized:
                self.warnings.append(f"Variable '{node.name}' usada sin inicializar")
            
            return symbol.dataType
        
        elif isinstance(node, AssignmentExpression):
            return self.analyzeAssignment(node)
        
        elif isinstance(node, BinaryOperation):
            return self.analyzeBinaryOperation(node)
        
        else:
            self.errors.append(f"Tipo de expresión desconocido: {type(node)}")
            return DataType.ERROR
    
    # Analiza una expresión de asignación y devuelve su tipo.
    def analyzeAssignment(self, node: AssignmentExpression) -> DataType:
        if not isinstance(node.left, Identifier):
            self.errors.append("El lado izquierdo de la asignación debe ser un identificador")
            return DataType.ERROR
        
        varName = node.left.name
        
        symbol = self.symbolTable.lookup(varName)
        if not symbol:
            self.errors.append(f"Variable no definida '{varName}'")
            return DataType.ERROR
        
        rightType = self.analyzeExpression(node.right)
        if rightType == DataType.ERROR:
            return DataType.ERROR
        
        if node.operator == '=':
            if not self.areTypesCompatible(symbol.dataType, rightType):
                self.errors.append(
                    f"No se puede asignar {rightType.value} al tipo {symbol.dataType.value} "
                    f"variable '{varName}'"
                )
                return DataType.ERROR
        elif node.operator in ['+=', '-=', '*=']:
            if not self.isNumericType(symbol.dataType) or not self.isNumericType(rightType):
                self.errors.append(
                    f"Tipos invalidos para el operador '{node.operator}': {symbol.dataType.value} y {rightType.value}"
                )
                return DataType.ERROR
        
        self.symbolTable.assign(varName)
        return symbol.dataType
    
    # Analiza una operación binaria y devuelve su tipo.
    def analyzeBinaryOperation(self, node: BinaryOperation) -> DataType:
        leftType = self.analyzeExpression(node.left)
        rightType = self.analyzeExpression(node.right)
        
        if leftType == DataType.ERROR or rightType == DataType.ERROR:
            return DataType.ERROR
        
        if node.operator in ['+', '-', '*', '/']:
            if node.operator == '+' and (leftType == DataType.STRING or rightType == DataType.STRING):
                return DataType.STRING
            elif self.isNumericType(leftType) and self.isNumericType(rightType):
                if leftType == DataType.FLOAT or rightType == DataType.FLOAT:
                    return DataType.FLOAT
                return DataType.INT
            else:
                self.errors.append(
                    f"Tipos invalidos para el operador '{node.operator}': {leftType.value} y {rightType.value}"
                )
                return DataType.ERROR
        
        elif node.operator in ['==', '!=', '<', '>', '<=', '>=']:
            if self.areTypesCompatible(leftType, rightType):
                return DataType.BOOL
            else:
                self.errors.append(
                    f"No se pueden comparar {leftType.value} y {rightType.value}"
                )
                return DataType.ERROR
        
        else:
            self.errors.append(f"Operador desconocido: {node.operator}")
            return DataType.ERROR
    
    # Checa si dos tipos de datos son compatibles.
    def areTypesCompatible(self, type1: DataType, type2: DataType) -> bool:
        if type1 == type2:
            return True
        
        if (type1 == DataType.INT and type2 == DataType.FLOAT) or \
           (type1 == DataType.FLOAT and type2 == DataType.INT):
            return True
        
        return False
    
    # Checa si un tipo de dato es numérico (int o float).
    def isNumericType(self, dataType: DataType) -> bool:
        return dataType in [DataType.INT, DataType.FLOAT]

# Carga el AST desde un archivo JSON y lo convierte a un objeto ASTNode.
def loadAstFromFile(filename: str = "ast.json") -> Optional[Program]:
    try:
        with open(filename, 'r') as file:
            astDict = json.load(file)
        
        return dictToAst(astDict)
    
    except FileNotFoundError:
        print(f"Error: {filename} no encontrado. Corra syntax_analyzer.py antes.")
        return None
    except json.JSONDecodeError:
        print(f"Error: JSON inválido en {filename}")
        return None

# Convierte el AST a un objeto ASTNode a partir de un diccionario.
def dictToAst(nodeDict) -> ASTNode:
    if not isinstance(nodeDict, dict) or 'type' not in nodeDict:
        return nodeDict
    
    nodeType = nodeDict['type']
    
    if nodeType == 'Program':
        declarations = [dictToAst(decl) for decl in nodeDict['declarations']]
        return Program(declarations=declarations)
    
    elif nodeType == 'VariableDeclaration':
        initializer = dictToAst(nodeDict['initializer']) if nodeDict.get('initializer') else None
        return VariableDeclaration(
            typeSpec=nodeDict['typeSpec'],
            identifier=nodeDict['identifier'],
            initializer=initializer
        )
    
    elif nodeType == 'ExpressionStatement':
        return ExpressionStatement(expression=dictToAst(nodeDict['expression']))
    
    elif nodeType == 'BinaryOperation':
        return BinaryOperation(
            left=dictToAst(nodeDict['left']),
            operator=nodeDict['operator'],
            right=dictToAst(nodeDict['right'])
        )
    
    elif nodeType == 'AssignmentExpression':
        return AssignmentExpression(
            left=dictToAst(nodeDict['left']),
            operator=nodeDict['operator'],
            right=dictToAst(nodeDict['right'])
        )
    
    elif nodeType == 'Identifier':
        return Identifier(name=nodeDict['name'])
    
    elif nodeType == 'IntegerLiteral':
        return IntegerLiteral(value=nodeDict['value'])
    
    elif nodeType == 'FloatLiteral':
        return FloatLiteral(value=nodeDict['value'])
    
    elif nodeType == 'StringLiteral':
        return StringLiteral(value=nodeDict['value'])
    
    elif nodeType == 'BooleanLiteral':
        return BooleanLiteral(value=nodeDict['value'])
    
    else:
        print(f"Tipo de nodo desconocido: {nodeType}")
        return None

# Este es el punto de entrada principal del programa. Carga el AST desde un archivo y realiza el análisis semántico.
def main():
    ast = loadAstFromFile()
    if not ast:
        return
    
    print("Iniciando análisis semántico...")
    
    analyzer = SemanticAnalyzer(ast)
    success, errors, warnings = analyzer.analyze()
    
    if warnings:
        print("\nAdvertencias:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print("\nErrores:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nAnálisis semántico completado")
    
    return success, analyzer

if __name__ == "__main__":
    main()