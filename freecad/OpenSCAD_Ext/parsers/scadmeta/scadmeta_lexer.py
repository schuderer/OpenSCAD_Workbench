import ply.lex as lex

tokens = (
    "ID",
    "NUMBER",
    "STRING",
    "ASSIGN",
    "SEMICOLON",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "LBRACE",
    "RBRACE",
    "MODULE",
    "INCLUDE",
    "USE",
)

t_ASSIGN    = r'='
t_SEMICOLON = r';'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'

reserved = {
    "module": "MODULE",
    "include": "INCLUDE",
    "use": "USE",
}

t_ignore = " \t"

def t_STRING(t):
    r'\"([^\\\"]|\\.)*\"'
    t.value = t.value.strip('"')
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    return t

def t_ID(t):
    r'[\$]?[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, "ID")
    return t

def t_comment(t):
    r'(//.*)|(/\*(.|\n)*?\*/)'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    t.lexer.skip(1)

def build():
    return lex.lex()

