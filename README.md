# LexicalAnalizer

Este proyecto es un analizador léxico simple basado en el compilador de Basic Programming Language (o la opción 2 de la actividad).

# Requisitos

- Python v3.8.8 o mayor.
- la librería de unittest para correr las pruebas

`pip install unittest`

# Tokens

La lista de tokens válidos es la siguiente:

| Token              | Ejemplo           | Descripción                                                       |
| ------------------ | ----------------- | ----------------------------------------------------------------- |
| COMMENT            | /_ hello world _/ | Cualquier texto entre /\* \*/                                     |
| IF                 | if                | Palabra reservada if                                              |
| ELSE               | else              | Palabra reservada else                                            |
| WHILE              | while             | Palabra reservada while                                           |
| FOR                | for               | Palabra reservada for                                             |
| RETURN             | return            | Palabra reservada return                                          |
| FUNCTION           | function          | Palabra reservada function                                        |
| KEYWORD_INT        | int               | Identificador int para variables                                  |
| KEYWORD_STR        | str               | Identificador str para variables                                  |
| KEYWORD_FLOAT      | float             | Identificador float para variables                                |
| KEYWORD_BOOL       | bool              | Identificador bool para variables                                 |
| TRUE               | true              | Valor booleano verdadero                                          |
| FALSE              | false             | Valor booleano falso                                              |
| FLOAT              | 1.1               | Valor numérico con decimales                                      |
| INTEGER            | 10                | Valor numérico entero                                             |
| STRING             | " hello world "   | Conjunto de caractéres entre " "                                  |
| IDENTIFIER         | variable          | Cualquier valor alfanumérico que no empiece con número            |
| PLUS_ASSIGN        | +=                | Operador para sumar un valor a una variable y reasignarlo         |
| MINUS_ASSIGN       | -=                | Operador para restar un valor a una variable y reasignarlo        |
| MULTIPLY_ASSIGN    | \*=               | Operador para multiplicar una variable por un valor y reasignarlo |
| EQUALS             | ==                | Operador para verificar que dos valores sean iguales              |
| NOT_EQUALS         | !=                | Operador para verificar que dos valores no sean iguales           |
| LESS_EQUAL_THAN    | <=                | Operador para verificar que un valor sea menor o igual que otro   |
| GREATER_EQUAL_THAN | >=                | Operador para verificar que un valor sea mayor o igual que otro   |
| PLUS               | +                 | Operador para sumar valores                                       |
| MINUS              | -                 | Operador para restar valores                                      |
| MULTIPLY           | \*                | Operador para multiplicar valores                                 |
| DIVIDE             | /                 | Operador para dividir valores                                     |
| LESS_THAN          | <                 | Operador para verificar que un valor sea menor que otro           |
| GREATER_THAN       | >                 | Operador para verificar que un valor sea mayor o igual que otro   |
| ASSIGN             | =                 | Operador para asignar un valor                                    |
| LPAREN             | (                 | Delimitador de paréntesis izquierdo                               |
| RPAREN             | )                 | Delimitador de paréntesis derecho                                 |
| LBRACE             | {                 | Delimitador de llave izquierda                                    |
| RBRACE             | }                 | Delimitador de llave derecha                                      |
| SEMICOLON          | ;                 | Punto y coma para terminar una expresión                          |
| COMMA              | ,                 | Coma para separar elementos                                       |
| WHITESPACE         |                   | Espacios en blanco                                                |

Cualquier caractér que no esté incluido en esta lista resulta en un token de INVALIDTOKEN para todo su lexema.

# Como correr el codigo

`python .\src\lexer.py`
`python .\src\syntax_analyzer.py`

# Flujo de código del analizador léxico

1. Se definen los tokens y sus patrones de expresiones regulares.
2. Se define la clase de Tokens, en donde se guarda cada token con su tipo y valor.
3. El usuario ingresa su código para analizar.
4. Se llama la función de Tokenize.

- Se compilan los patrones de cana tipo de token para su uso en el análisis.
- El ciclo que itera por el código revisa a qué patrón se parece la posición actual en el código.
- Si se parece a un patrón que NO sea WHITESPACE o COMMENT, se agrega a la lista y se continua analizando.
- Si no se parece a un patrón, se agrega un INVALIDTOKEN a la lista y se continua analizando.

5. Al acabar de analizar, la lista de tokens se añade en un archivo llamado lexer.json

# Flujo de código del analizador sintáctico

1. Se definen las clases de las sentencias y declaraciones para el AST.
2. Se reciben los tokens de lexer.json.
3. Se inicia el parseo de los tokens.
4. Se revisa primero si es una declaración de variable o de una función.
5. Si es de variable, se revisa que tipo de sentencia es y las expresiones que incluye.
6. Si es de función, lo que le sigue dentro de las llaves se revisa como una sentencia compuesta.
7. Dentro de una sentencia compuesta, pueden haber declaraciones de variables, bucles while, for, ifs y otras expresiones.
8. Al acabar de analizar todo, se escribe el AST en un archivo llamado ast.json
