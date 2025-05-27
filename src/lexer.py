import re
import json

# Aqui se definen los tipos de tokens y sus patrones regex
TokenTypes = [
  ('COMMENT', r'/\*.*?\*/'),
  ("IF", r'\bif\b'),
  ("ELSE", r'\belse\b'),
  ("WHILE", r'\bwhile\b'),
  ("FOR", r'\bfor\b'),
  ("RETURN", r'\breturn\b'),
  ("FUNCTION", r'\bfunction\b'),
  ("KEYWORD_INT", r'\bint\b'),
  ("KEYWORD_STR", r'\bstr\b'),
  ("KEYWORD_FLOAT", r'\bfloat\b'),
  ("KEYWORD_BOOL", r'\bbool\b'),
  ("TRUE", r'\btrue\b'),
  ("FALSE", r'\bfalse\b'),
  ("FLOAT", r'\d+\.\d+'),
  ("INTEGER", r'\d+'),
  ("STRING", r'"[^"\n]*"'),
  ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),
  ("PLUS_ASSIGN", r'\+='),
  ("MINUS_ASSIGN", r'-='),
  ("MULTIPLY_ASSIGN", r'\*='),
  ("EQUALS", r'=='),
  ("NOT_EQUALS", r'!='),
  ("LESS_EQUAL_THAN", r'<='),
  ("GREATER_EQUAL_THAN", r'>='),
  ("PLUS", r'\+'),
  ("MINUS", r'-'),
  ("MULTIPLY", r'\*'),
  ("DIVIDE", r'/'),
  ("LESS_THAN", r'<'),
  ("GREATER_THAN", r'>'),
  ("ASSIGN", r'='),
  ("LPAREN", r'\('),
  ("RPAREN", r'\)'),
  ("LBRACE", r'\{'),
  ("RBRACE", r'\}'),
  ("SEMICOLON", r';'),
  ("COMMA", r','),
  ("WHITESPACE", r'\s+'),
]

# La clase de los tokens donde se guarda su tipo y valor.
class Token:
  def __init__(self, tokenType, value):
    self.type = tokenType
    self.value = value
   
def Tokenize(source_code):
  # Aquí se crea la posición inicial de donde empezar a analizar el código. También se compilan los strings de los patrones regex
  position = 0
  regexPatterns = [(tokenType, re.compile(pattern)) for tokenType, pattern in TokenTypes]
  tokens = []
    
  # Inica el ciclo donde se va avanzando por cada caracter del código
  while position < len(source_code):
    matchFound = False
    currentText = source_code[position:]
    
    for tokenType, regex in regexPatterns:
      # Se revisa el inicio del string si queda con algun regex
      match = regex.match(currentText)
      if match:
        lexeme = match.group(0)

        # Ignorar espacios en blanco y comentarios
        if tokenType != "WHITESPACE" and tokenType != "COMMENT":
          token = Token(tokenType, lexeme)
          tokens.append(token)
        
        # Avanzar a la siguiente posición
        for _ in range(len(lexeme)):
          position += 1
        
        matchFound = True
        break
    # Si se encuentra que esta posición no queda con ningun tipo de token, se agrega un token de INVALIDTOKEN
    if not matchFound:
      invalidText = currentText[:currentText.find(' ') if ' ' in currentText else len(currentText)]
      errorToken = Token('INVALIDTOKEN', invalidText)
      tokens.append(errorToken)
      # Avanzar a la siguiente posición
      for _ in range(len(invalidText)):
        position += 1
  
  return tokens

# Main, en donde se acepta el input del usuario.
if __name__ == "__main__":
  code = input('Input your code: ')
  
  tokens = Tokenize(code)
  jsonSerializedTokens = json.dumps(tokens, default=lambda token: token.__dict__)
  
  with open("lexer.json", "w") as file:
    json.dump(jsonSerializedTokens, file)