import unittest
from lexer import Tokenize

class TestLexer(unittest.TestCase):
  def testSingleToken(self):
    code = "if"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 1)
    self.assertEqual(tokens[0].type, "IF")
    self.assertEqual(tokens[0].value, "if")

  def testMultipleTokens(self):
    code = "if else while for"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 4)
    self.assertEqual(tokens[0].type, "IF")
    self.assertEqual(tokens[1].type, "ELSE")
    self.assertEqual(tokens[2].type, "WHILE")
    self.assertEqual(tokens[3].type, "FOR")

  def testDifferentTokenTypes(self):
    code = "x = 42 y = 3.14"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 6)
    self.assertEqual(tokens[0].type, "IDENTIFIER")
    self.assertEqual(tokens[1].type, "ASSIGN")
    self.assertEqual(tokens[2].type, "INTEGER")
    self.assertEqual(tokens[3].type, "IDENTIFIER")
    self.assertEqual(tokens[4].type, "ASSIGN")
    self.assertEqual(tokens[5].type, "FLOAT")

  def testStringToken(self):
    code = 'message = "Hello, World!"'
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 3)
    self.assertEqual(tokens[0].type, "IDENTIFIER")
    self.assertEqual(tokens[1].type, "ASSIGN")
    self.assertEqual(tokens[2].type, "STRING")

  def testInvalidToken(self):
    code = "@invalid"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 1)
    self.assertEqual(tokens[0].type, "INVALIDTOKEN")
    self.assertEqual(tokens[0].value, "@invalid")

  def testCommentToken(self):
    code = "int x; /* this is a comment */"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 3)
    self.assertEqual(tokens[0].type, "KEYWORD_INT")
    self.assertEqual(tokens[1].type, "IDENTIFIER")
    self.assertEqual(tokens[2].type, "SEMICOLON")
    self.assertEqual("COMMENT" not in tokens, True)

  def testWhitespaceToken(self):
    code = "int x;  "
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 3)
    self.assertEqual(tokens[0].type, "KEYWORD_INT")
    self.assertEqual(tokens[1].type, "IDENTIFIER")
    self.assertEqual(tokens[2].type, "SEMICOLON")
    self.assertEqual("WHITESPACE" not in tokens, True)

  def testFullCode(self):
    code = "if (x <= 10) { /* foo bar */ y += 2; } else { z = 3.14; }"
    tokens = Tokenize(code)
    self.assertEqual(len(tokens), 19)
    self.assertEqual(tokens[0].type, "IF")
    self.assertEqual(tokens[1].type, "LPAREN")
    self.assertEqual(tokens[2].type, "IDENTIFIER")
    self.assertEqual(tokens[3].type, "LESS_EQUAL_THAN")
    self.assertEqual(tokens[4].type, "INTEGER")
    self.assertEqual(tokens[5].type, "RPAREN")
    self.assertEqual(tokens[6].type, "LBRACE")
    self.assertEqual(tokens[7].type, "IDENTIFIER")
    self.assertEqual(tokens[8].type, "PLUS_ASSIGN")
    self.assertEqual(tokens[9].type, "INTEGER")
    self.assertEqual(tokens[10].type, "SEMICOLON")
    self.assertEqual(tokens[11].type, "RBRACE")
    self.assertEqual(tokens[12].type, "ELSE")
    self.assertEqual(tokens[13].type, "LBRACE")
    self.assertEqual(tokens[14].type, "IDENTIFIER")
    self.assertEqual(tokens[15].type, "ASSIGN")
    self.assertEqual(tokens[16].type, "FLOAT")
    self.assertEqual(tokens[17].type, "SEMICOLON")
    self.assertEqual(tokens[18].type, "RBRACE")

if __name__ == "__main__":
  unittest.main()