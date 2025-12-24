import ply.lex as lex

tokens = (
    "ID",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "SEMICOLON",
)

t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'

t_ignore = " \t\n"

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

def t_comment(t):
    r'(//.*)|(/\*(.|\n)*?\*/)'
    pass

def t_error(t):
    t.lexer.skip(1)

def build():
    return lex.lex()

