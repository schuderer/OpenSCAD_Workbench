import ply.yacc as yacc

from .csgmeta_lexer import build as build_lexer
from .csgmeta_model import CsgMeta

_meta = None
_depth = 0


def p_program(p):
    """program : program statement
               | statement"""
    pass


def p_statement_hull(p):
    """statement : ID LPAREN RPAREN block"""
    global _depth

    name = p[1]
    if name == "hull" and _depth == 0:
        _meta.top_level_hulls.append("hull")
    elif name == "minkowski" and _depth == 0:
        _meta.top_level_minkowski.append("minkowski")


def p_block(p):
    """block : LBRACE enter block_content leave RBRACE"""
    pass


def p_enter(p):
    "enter :"
    global _depth
    _depth += 1


def p_leave(p):
    "leave :"
    global _depth
    _depth -= 1


def p_block_content(p):
    """block_content : block_content statement
                     | empty"""
    pass


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    pass


def parse_csgmeta(path):
    """
    Parse only hull/minkowski structure
    """
    global _meta, _depth
    _meta = CsgMeta()
    _depth = 0

    lexer = build_lexer()
    parser = yacc.yacc(start="program", write_tables=False)

    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    parser.parse(data, lexer=lexer)
    return _meta

