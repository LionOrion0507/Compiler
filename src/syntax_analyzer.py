import json
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

# Aquí se definen las clases que representan los nodos del AST (Árbol de Sintaxis Abstracta).
# clase base para todos los nodos del AST
@dataclass
class ASTNode:
  pass

# Clase base para todos los nodos del AST que no tienen hijos
@dataclass
class Program(ASTNode):
  declarations: List['Declaration']

# Clase base para todos los nodos del AST que representan declaraciones
@dataclass
class VariableDeclaration(ASTNode):
  typeSpec: str
  identifier: str
  initializer: Optional['Expression'] = None

# Clase base para todos los nodos del AST que representan funciones
@dataclass
class FunctionDeclaration(ASTNode):
  returnType: str
  identifier: str
  parameters: List['Parameter']
  body: 'CompoundStatement'

# Clase base para todos los nodos del AST que representan parámetros de funciones
@dataclass
class Parameter(ASTNode):
  typeSpec: str
  identifier: str

# Clase base para todos los nodos del AST que representan sentencias compuestas (están entre llaves {})
@dataclass
class CompoundStatement(ASTNode):
  statements: List['Statement']

# Clase base para todos los nodos del AST que representan sentencias condicionales (If)
@dataclass
class IfStatement(ASTNode):
  condition: 'Expression'
  thenStatement: 'Statement'
  elseStatement: Optional['Statement'] = None

# Clase base para todos los nodos del AST que representan sentencias de bucle (While)
@dataclass
class WhileStatement(ASTNode):
  condition: 'Expression'
  body: 'Statement'

# Clase base para todos los nodos del AST que representan sentencias de bucle (For)
@dataclass
class ForStatement(ASTNode):
  initialization: Optional['Expression']
  condition: Optional['Expression']
  increment: Optional['Expression']
  body: 'Statement'

# Clase base para todos los nodos del AST que representan sentencias de retorno
@dataclass
class ReturnStatement(ASTNode):
  expression: Optional['Expression'] = None

# Clase base para todos los nodos del AST que representan sentencias de expresión
@dataclass
class ExpressionStatement(ASTNode):
  expression: 'Expression'

# Clase base para todos los nodos del AST que representan expresiones binarias (como suma, resta, etc.)
@dataclass
class BinaryOperation(ASTNode):
  left: 'Expression'
  operator: str
  right: 'Expression'

# Clase base para todos los nodos del AST que representan asignaciones (como x = 5)
@dataclass
class AssignmentExpression(ASTNode):
  left: 'Expression'
  operator: str
  right: 'Expression'

# Clase base para todos los nodos del AST que representan identificadores (como variables)
@dataclass
class Identifier(ASTNode):
  name: str

# Clase base para todos los nodos del AST que representan literales integers
@dataclass
class IntegerLiteral(ASTNode):
  value: int

# Clase base para todos los nodos del AST que representan literales de floats
@dataclass
class FloatLiteral(ASTNode):
  value: float

# Clase base para todos los nodos del AST que representan literales de strings
@dataclass
class StringLiteral(ASTNode):
  value: str

# Clase base para todos los nodos del AST que representan literales booleanos
@dataclass
class BooleanLiteral(ASTNode):
  value: bool

# Aquí se definen los tipos de nodos del AST que se pueden encontrar en el código.
# Estos tipos se utilizan para definir las declaraciones y sentencias en el AST.
Declaration = Union[VariableDeclaration, FunctionDeclaration]
Statement = Union[CompoundStatement, IfStatement, WhileStatement, ForStatement, 
                 ReturnStatement, ExpressionStatement, VariableDeclaration]
Expression = Union[BinaryOperation, AssignmentExpression, Identifier, 
                  IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral]

# Esta función carga los tokens desde un archivo JSON generado por el lexer.
def loadTokensFromFile(filename):
  try:
    with open(filename, 'r') as file:
      tokensJson = json.load(file)
      tokens = json.loads(tokensJson)
      return tokens
  except FileNotFoundError:
    print(f"Error: {filename} no encontrado. Primero hay que correr lexer.py.")
    return None
  except json.JSONDecodeError:
    print(f"Error: JSON inálido en {filename}")
    return None
    
# Esta función guarda el AST en un archivo JSON (ast.json).
def saveAstToJson(ast, filename="ast.json"):
  def astToDict(node):
    if isinstance(node, ASTNode):
      result = {"type": type(node).__name__}
      for key, value in node.__dict__.items():
        if isinstance(value, list):
          result[key] = [astToDict(item) for item in value]
        elif isinstance(value, ASTNode):
          result[key] = astToDict(value)
        else:
          result[key] = value
      return result
    return node
  
  astDict = astToDict(ast)
  with open(filename, 'w') as file:
    json.dump(astDict, file, indent=2)
    
# Esta clase es el analizador sintáctico que procesa los tokens y construye el AST.
class SyntaxAnalyzer:
  def __init__(self, tokens):
    self.tokens = tokens
    self.currentPos = 0
    self.currentToken = self.tokens[0] if tokens else None
    self.errors = []

  # Inicia el análisis sintáctico y construye el AST.
  def parse(self):
    program = self.program()
    if not program:
      return False, None, "Error al analizar el programa"

    if self.errors:
      return False, None, "Errores encontrados durante el análisis sintáctico"
    
    if self.currentToken is not None:
      self.errors.append(f"Token inesperado al final del archivo: {self.currentToken}")
    
    return True, program, "Análisis sintáctico exitoso"
  
# Analiza el programa completo, que consiste en declaraciones de variables y funciones.
  def program(self):
    declarations = []
    while self.currentToken is not None:
      if self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL'):
        declaration = self.variableDeclaration()
        if declaration:
          declarations.append(declaration)
        else:
          self.errors.append("Error al analizar la declaración de variable")
      elif self.currentToken['type'] == 'FUNCTION':
        declaration = self.functionDeclaration()
        if declaration:
          declarations.append(declaration)
        else:
          self.errors.append("Error al analizar la declaración de función")
      else:
        self.errors.append(f"Token inesperado: {self.currentToken}")
        return None
    
    return Program(declarations=declarations)

  # Avanza al siguiente token en la lista de tokens.
  def advance(self):
    self.currentPos += 1
    if self.currentPos < len(self.tokens):
      self.currentToken = self.tokens[self.currentPos]
    else:
      self.currentToken = None

  # Analiza una declaración de variable y devuelve un nodo VariableDeclaration.
  def variableDeclaration(self):
    if self.currentToken and self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL'):
      typeSpec = self.currentToken['value']
      self.advance()
      
      if not (self.currentToken and self.currentToken['type'] == 'IDENTIFIER'):
        self.errors.append("Se esperaba un identificador después del tipo de variable")
        return None
      
      identifier = self.currentToken['value']
      self.advance()
      
      initializer = None
      if self.currentToken and self.currentToken['type'] == 'ASSIGN':
        self.advance()
        initializer = self.equalityExpression()
        if not initializer:
          self.errors.append("Error al analizar la expresión de inicialización")
          return None
      if self.currentToken and self.currentToken['type'] == 'SEMICOLON':
        self.advance()
      else:
        self.errors.append("Se esperaba un punto y coma ';' al final de la declaración de variable")
        return None
      return VariableDeclaration(typeSpec=typeSpec, identifier=identifier, initializer=initializer)
    
  # Analiza una declaración de función y devuelve un nodo FunctionDeclaration.
  def functionDeclaration(self):
    if self.currentToken and self.currentToken['type'] == 'FUNCTION':
      self.advance()
      
      if not (self.currentToken and self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL')):
        self.errors.append("Se esperaba un tipo de retorno para la función")
        return None
      
      returnType = self.currentToken['value']
      self.advance()
      
      if not (self.currentToken and self.currentToken['type'] == 'IDENTIFIER'):
        self.errors.append("Se esperaba un identificador para la función")
        return None
      
      identifier = self.currentToken['value']
      self.advance()
      
      if not (self.currentToken and self.currentToken['type'] == 'LPAREN'):
        self.errors.append("Se esperaba un paréntesis de apertura '(' después del identificador de la función")
        return None
      
      self.advance()
      
      parameters = []
      while self.currentToken and self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL'):
        typeSpec = self.currentToken['value']
        self.advance()
        
        if not (self.currentToken and self.currentToken['type'] == 'IDENTIFIER'):
          self.errors.append("Se esperaba un identificador para el parámetro de la función")
          return None
        
        paramIdentifier = self.currentToken['value']
        parameters.append(Parameter(typeSpec=typeSpec, identifier=paramIdentifier))
        self.advance()
        
        if not (self.currentToken and self.currentToken['type'] in ('COMMA', 'RPAREN')):
          self.errors.append("Se esperaba una coma ',' o un paréntesis de cierre ')' después del parámetro de la función")
          return None
        
        if self.currentToken['type'] == 'COMMA':
          self.advance()
      
      if not (self.currentToken and self.currentToken['type'] == 'RPAREN'):
        self.errors.append("Se esperaba un paréntesis de cierre ')' al final de los parámetros de la función")
        return None
      
      self.advance()
      
      if not (self.currentToken and self.currentToken['type'] == 'LBRACE'):
        self.errors.append("Se esperaba una llave de apertura '{' al inicio del cuerpo de la función")
        return None
      
      body = self.compoundStatement()
      
      return FunctionDeclaration(returnType=returnType, identifier=identifier, parameters=parameters, body=body)
  
  # Analiza el cuerpo de una función y devuelve un nodo CompoundStatement que contiene las sentencias.
  def compoundStatement(self):
    body = CompoundStatement(statements=[])
    self.advance()
    while self.currentToken and self.currentToken['type'] != 'RBRACE':
      if self.currentToken['type'] == 'SEMICOLON':
        self.advance()
        continue
      
      if self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL'):
        statement = self.variableDeclaration()
      elif self.currentToken['type'] == 'FUNCTION':
        statement = self.functionDeclaration()
      elif self.currentToken['type'] in ('IF', 'WHILE', 'FOR', 'RETURN'):
        statement = self.blockStatement()
      else:
        statement = self.expressionStatement()
      if statement:
        body.statements.append(statement)
      else:
        self.errors.append("Error al analizar la sentencia en el cuerpo de la función")
        return None

    if not (self.currentToken and self.currentToken['type'] == 'RBRACE'):
      self.errors.append("Se esperaba una llave de cierre '}' al final del cuerpo de la función")
      return None
    self.advance()
    return body

  # Analiza una sentencia de bloque, que puede ser una sentencia if, while, for, return o una sentencia de expresión.
  def blockStatement(self):
    if self.currentToken and self.currentToken['type'] == 'IF':
      return self.ifStatement()
    elif self.currentToken and self.currentToken['type'] == 'WHILE':
      return self.whileStatement()
    elif self.currentToken and self.currentToken['type'] == 'FOR':
      return self.forStatement()
    elif self.currentToken and self.currentToken['type'] == 'RETURN':
      return self.returnStatement()
    else:
      return self.expressionStatement()
  
  # Analiza una sentencia if y devuelve un nodo IfStatement.
  def ifStatement(self):
    if not (self.currentToken and self.currentToken['type'] == 'IF'):
      self.errors.append("Se esperaba 'if' al inicio de la sentencia if")
      return None
    
    self.advance()
    
    if not (self.currentToken and self.currentToken['type'] == 'LPAREN'):
      self.errors.append("Se esperaba un paréntesis de apertura '(' después de 'if'")
      return None
    
    self.advance()
    
    condition = self.equalityExpression()
    if not condition:
      self.errors.append("Error al analizar la condición del if")
      return None
    
    if not (self.currentToken and self.currentToken['type'] == 'RPAREN'):
      self.errors.append("Se esperaba un paréntesis de cierre ')' después de la condición del if")
      return None
    
    self.advance()
    
    thenStatement = self.compoundStatement()
    
    elseStatement = None
    if self.currentToken and self.currentToken['type'] == 'ELSE':
      self.advance()
      else_statement = self.compoundStatement()
    
    return IfStatement(condition=condition, thenStatement=thenStatement, elseStatement=elseStatement)
  
  # Analiza una sentencia while y devuelve un nodo WhileStatement.
  def whileStatement(self):
    if not (self.currentToken and self.currentToken['type'] == 'WHILE'):
      self.errors.append("Se esperaba 'while' al inicio de la sentencia while")
      return None
    
    self.advance()
    
    if not (self.currentToken and self.currentToken['type'] == 'LPAREN'):
      self.errors.append("Se esperaba un paréntesis de apertura '(' después de 'while'")
      return None
    
    self.advance()
    
    condition = self.equalityExpression()
    if not condition:
      self.errors.append("Error al analizar la condición del while")
      return None
    
    if not (self.currentToken and self.currentToken['type'] == 'RPAREN'):
      self.errors.append("Se esperaba un paréntesis de cierre ')' después de la condición del while")
      return None
    
    self.advance()
    
    body = self.compoundStatement()
    
    return WhileStatement(condition=condition, body=body)
  
  # Analiza una sentencia for y devuelve un nodo ForStatement.
  def forStatement(self):
    if not (self.currentToken and self.currentToken['type'] == 'FOR'):
      self.errors.append("Se esperaba 'for' al inicio de la sentencia for")
      return None
    
    self.advance()
    
    if not (self.currentToken and self.currentToken['type'] == 'LPAREN'):
      self.errors.append("Se esperaba un paréntesis de apertura '(' después de 'for'")
      return None
    
    self.advance()
    
    initialization = None
    if self.currentToken and self.currentToken['type'] in ('KEYWORD_INT', 'KEYWORD_FLOAT', 'KEYWORD_STRING', 'KEYWORD_BOOL'):
      initialization = self.variableDeclaration()
    elif self.currentToken and self.currentToken['type'] == 'IDENTIFIER':
      identifier = Identifier(name=self.currentToken['value'])
      self.advance()
      if not (self.currentToken and self.currentToken['type'] in ('ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MULTIPLY_ASSIGN')):
        self.errors.append("Se esperaba un operador de asignación en la inicialización del for")
        return None
      operator = self.currentToken['value']
      self.advance()
      right = self.equalityExpression()
      initialization = AssignmentExpression(left=identifier, operator=operator, right=right)
    
    condition = None
    if self.currentToken and self.currentToken['type'] != 'SEMICOLON':
      condition = self.equalityExpression()
    
    self.advance()

    increment = None
    if self.currentToken and self.currentToken['type'] != 'SEMICOLON':
      increment = self.assignmentExpression()

    self.advance
    
    if not (self.currentToken and self.currentToken['type'] == 'RPAREN'):
      self.errors.append("Se esperaba un paréntesis de cierre ')' después de la condición del for")
      return None
    
    self.advance()
    
    body = self.compoundStatement()
    
    return ForStatement(initialization=initialization, condition=condition, increment=increment, body=body)
  
  # Analiza una sentencia de retorno y devuelve un nodo ReturnStatement.
  def returnStatement(self):
    if not (self.currentToken and self.currentToken['type'] == 'RETURN'):
      self.errors.append("Se esperaba 'return' al inicio de la sentencia de retorno")
      return None
    
    self.advance()
    
    expression = None
    if self.currentToken and self.currentToken['type'] != 'SEMICOLON':
      expression = self.equalityExpression()
    
    if not (self.currentToken and self.currentToken['type'] == 'SEMICOLON'):
      self.errors.append("Se esperaba un punto y coma ';' al final de la sentencia de retorno")
      return None
    
    self.advance()
    return ReturnStatement(expression=expression)
  
  # Analiza una sentencia de expresión y devuelve un nodo ExpressionStatement.
  def expressionStatement(self):
    expression = self.assignmentExpression()
    if not expression:
      self.errors.append("Error al analizar la expresión en la sentencia de expresión")
      return None
    
    if not (self.currentToken and self.currentToken['type'] == 'SEMICOLON'):
      self.errors.append("Se esperaba un punto y coma ';' al final de la sentencia de expresión")
      return None
    
    self.advance()
    return ExpressionStatement(expression=expression)
    
  # Analiza una expresión de asignación y devuelve un nodo AssignmentExpression.
  def assignmentExpression(self):
    if not (self.currentToken and self.currentToken['type'] == 'IDENTIFIER'):
      self.errors.append("Se esperaba un identificador para la expresión de asignación")
      return None
    
    identifier = Identifier(name=self.currentToken['value'])
    self.advance()
    
    if not (self.currentToken and self.currentToken['type'] in ('ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MULTIPLY_ASSIGN')):
      self.errors.append("Se esperaba un operador de asignación después del identificador")
      return None
    
    operator = self.currentToken['value']
    self.advance()
    
    right = self.equalityExpression()
    if not right:
      self.errors.append("Error al analizar la expresión de la derecha en la asignación")
      return None
    
    return AssignmentExpression(left=identifier, operator=operator, right=right)
  
  # Analiza una expresión de igualdad y devuelve un nodo BinaryOperation.
  def equalityExpression(self):
    left = self.sumOrDifferenceExpression()
    while self.currentToken and self.currentToken['type'] in ('EQUAL', 'NOT_EQUALS', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL_THAN', 'GREATER_EQUAL_THAN'):
      operator = self.currentToken['value']
      self.advance()
      right = self.sumOrDifferenceExpression()
      left = BinaryOperation(left=left, operator=operator, right=right)
    return left
  
  # Analiza una expresión de suma o resta y devuelve un nodo BinaryOperation.
  def sumOrDifferenceExpression(self):
    left = self.multiplicationOrDivisionExpression()
    while self.currentToken and self.currentToken['type'] in ('PLUS', 'MINUS'):
      operator = self.currentToken['value']
      self.advance()
      right = self.multiplicationOrDivisionExpression()
      left = BinaryOperation(left, operator, right)
    return left
  
  # Analiza una expresión de multiplicación o división y devuelve un nodo BinaryOperation.
  def multiplicationOrDivisionExpression(self):
    left = self.unitaryExpression()
    while self.currentToken and self.currentToken['type'] in ('MULTIPLY', 'DIVIDE'):
      operator = self.currentToken['value']
      self.advance()
      right = self.unitaryExpression()
      left = BinaryOperation(left, operator, right)
    return left
  
  # Analiza una expresión unitaria, que puede ser un identificador, un literal o una expresión entre paréntesis.
  def unitaryExpression(self):
    if self.currentToken and self.currentToken['type'] == 'MINUS':
      operator = self.currentToken['value']
      self.advance()
      operand = self.unitaryExpression()
      return BinaryOperation(left=IntegerLiteral(0), operator=operator, right=operand)
    
    if self.currentToken and self.currentToken['type'] == 'LPAREN':
      self.advance()
      expr = self.equalityExpression()
      if not (self.currentToken and self.currentToken['type'] == 'RPAREN'):
        self.errors.append("Se esperaba un paréntesis de cierre ')'")
        return None
      self.advance()
      return expr
    
    if self.currentToken and self.currentToken['type'] == 'IDENTIFIER':
      identifier = Identifier(name=self.currentToken['value'])
      self.advance()
      return identifier
    
    if self.currentToken and self.currentToken['type'] == 'INTEGER':
      value = int(self.currentToken['value'])
      self.advance()
      return IntegerLiteral(value=value)
    
    if self.currentToken and self.currentToken['type'] == 'FLOAT':
      value = float(self.currentToken['value'])
      self.advance()
      return FloatLiteral(value=value)
    
    if self.currentToken and self.currentToken['type'] == 'STRING':
      value = str(self.currentToken['value'])
      self.advance()
      return StringLiteral(value=value)
    
    if self.currentToken and self.currentToken['type'] == 'TRUE':
      value = True
      self.advance()
      return BooleanLiteral(value=value)
    
    if self.currentToken and self.currentToken['type'] == 'FALSE':
      value = False
      self.advance()
      return BooleanLiteral(value=value)
    
    # Si no se reconoce el token, se agrega un error
    errorMessage = f"Token inesperado: {self.currentToken}"
    self.errors.append(errorMessage)
    return None

# Este es el punto de entrada del programa. Carga los tokens desde un archivo JSON y ejecuta el analizador sintáctico.
def main():
  tokens = loadTokensFromFile("lexer.json")

  if tokens:
    print(f"Tokens cargados: {len(tokens)}")
    for token in tokens:
      print(f"  - {token['type']}: {token['value']}")
  
  if tokens is None:
    return
  
  analyzer = SyntaxAnalyzer(tokens)
  success, ast, message = analyzer.parse()

  if not success:
    print("\nErrores encontrados:")
    for error in analyzer.errors:
      print(f"  - {error}")
  else:
    saveAstToJson(ast)
    print(message)

if __name__ == "__main__":
  main()