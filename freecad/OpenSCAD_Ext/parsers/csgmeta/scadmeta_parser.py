import ply.yacc as yacc

from .scadmeta_lexer import build as build_lexer
from .scadmeta_model import ScadMeta

# parser state (rebuilt per parse)
_meta = None


def p_program(p):
    """program : program statement
               | statement"""
    pass


def p_statement_var(p):
    """statement : ID ASSIGN expression SEMICOLON"""
    _meta.variables[p[1]] = p[3]


def p_statement_module(p):
    """statement : MODULE ID LPAREN param_list RPAREN block"""
    _meta.modules[p[2]] = p[4]


def p_statement_include(p):
    """statement : INCLUDE STRING"""
    _meta.includes.append(p[2])


def p_statement_use(p):
    """statement : USE STRING"""
    _meta.uses[p[2]] = []


def p_param_list(p):
    """param_list : param_list COMMA ID
                  | ID
                  | empty"""
    if len(p) == 2 and p[1]:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []


def p_expression(p):
    """expression : expression ID
                  | expression NUMBER
                  | expression STRING
                  | ID
                  | NUMBER
                  | STRING"""
    if len(p) == 2:
        p[0] = str(p[1])
    else:
        p[0] = f"{p[1]}{p[2]}"


def p_block(p):
    """block : LBRACE block_content RBRACE"""
    pass


def p_block_content(p):
    """block_content : block_content block
                     | block_content statement
                     | empty"""
    pass


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    pass


def parse_scadmeta(path):
    """
    Parse OpenSCAD metadata only (vars, modules, includes, use)
    """
    global _meta
    _meta = ScadMeta()

    lexer = build_lexer()
    parser = yacc.yacc(start="program", write_tables=False)

    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    parser.parse(data, lexer=lexer)
    return _meta

