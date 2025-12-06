# newImportCSG.py
# FreeCAD OpenSCAD CSG importer with PLY

import FreeCAD
import Part
import ply.lex as lex
import ply.yacc as yacc
from dataclasses import dataclass, field
from typing import List, Optional, Any

# ----------------------------------------------------
# AST NODES
# ----------------------------------------------------

@dataclass
class Node:
    pass

@dataclass
class OpNode(Node):
    name: str
    args: List[Any] = field(default_factory=list)
    children: List[Node] = field(default_factory=list)
    lineno: int = 0
    parent: Optional[Node] = None

    def to_scad(self, indent=0):
        pad = "  " * indent
        args_s = ", ".join(str(a) for a in self.args)
        if self.children:
            body = "\n".join(c.to_scad(indent + 1) if isinstance(c, Node) else str(c)
                             for c in self.children)
            return f"{pad}{self.name}({args_s}) {{\n{body}\n{pad}}}"
        return f"{pad}{self.name}({args_s});"

@dataclass
class RawStmt(Node):
    text: str
    lineno: int = 0

    def to_scad(self, indent=0):
        return ("  " * indent) + self.text

@dataclass
class Program(Node):
    statements: List[Node] = field(default_factory=list)

# ----------------------------------------------------
# LEXER
# ----------------------------------------------------

reserved = {
    'cube': 'CUBE',
    'sphere': 'SPHERE',
    'hull': 'HULL',
    'minkowski': 'MINKOWSKI',
    'translate': 'TRANSLATE',
    'rotate': 'ROTATE',
    'scale': 'SCALE',
    'multmatrix': 'MULTMATRIX'
}

tokens = [
    'NUMBER', 'IDENT', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA'
] + list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','

t_ignore = ' \t'

def t_NUMBER(t):
    r'\d+(\.\d*)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_IDENT(t):
    r'[A-Za-z_][A-Za-z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENT')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'//.*|/\*(.|\n)*?\*/'
    pass

def t_error(t):
    # Treat unrecognized characters as raw statement tokens
    t.value = t.value[0]
    t.type = 'RAW'
    t.lexer.skip(1)
    return t

# include RAW token
tokens.append('RAW')

lexer = lex.lex()

# ----------------------------------------------------
# PARSER
# ----------------------------------------------------

def p_program(p):
    'program : statements'
    p[0] = Program(p[1])

def p_statements_multi(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]

def p_statement_op(p):
    '''statement : operation'''
    p[0] = p[1]

def p_statement_raw(p):
    '''statement : RAW'''
    p[0] = RawStmt(p[1], p.lineno(1))

def p_operation(p):
    '''operation : CUBE LPAREN arg_list RPAREN
                 | SPHERE LPAREN arg_list RPAREN
                 | HULL LBRACE statements RBRACE
                 | MINKOWSKI LBRACE statements RBRACE
                 | TRANSLATE LPAREN arg_list RPAREN LBRACE statements RBRACE
                 | ROTATE LPAREN arg_list RPAREN LBRACE statements RBRACE
                 | SCALE LPAREN arg_list RPAREN LBRACE statements RBRACE
                 | MULTMATRIX LPAREN arg_list RPAREN LBRACE statements RBRACE'''
    name = p[1].lower()
    if name in ('cube', 'sphere'):
        p[0] = OpNode(name, p[3], [])
    elif name in ('hull', 'minkowski'):
        p[0] = OpNode(name, [], p[3])
    else:
        p[0] = OpNode(name, p[3], p[6])

def p_arg_list(p):
    '''arg_list : args
                | empty'''
    p[0] = p[1]

def p_args_multi(p):
    'args : args COMMA arg'
    p[0] = p[1] + [p[3]]

def p_args_single(p):
    'args : arg'
    p[0] = [p[1]]

def p_arg(p):
    '''arg : NUMBER
           | IDENT'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        print(f"Parse error at '{p.value}' line {p.lineno}")
    else:
        print("Parse error at EOF")

parser = yacc.yacc()

# ----------------------------------------------------
# AST WALKER
# ----------------------------------------------------

COMPOUND_SET = {'hull', 'minkowski'}
TRANSFORM_SET = {'translate', 'rotate', 'scale', 'multmatrix'}

def walk_csg_ast_fc(ast_root, is_brep_convertible, handle_brep_fc, handle_openscad_fc):
    FCprint("walk_csg_fc/n")
    for stmt in ast_root.statements:
        _walk_node_fc(stmt, None, is_brep_convertible, handle_brep_fc, handle_openscad_fc)

def _walk_node_fc(node, inherited_compound, is_brep_convertible, handle_brep_fc, handle_openscad_fc):
    if isinstance(node, OpNode):
        is_compound = node.name in COMPOUND_SET
        if is_compound:
            FCprint("Compound/n")
            if is_brep_convertible(node):
                FCprint("Brep/n")
                for c in node.children:
                    _walk_node_fc(c, True, is_brep_convertible, handle_brep_fc, handle_openscad_fc)
            else:
                handle_openscad_fc(node)
            return
        if node.name in TRANSFORM_SET:
            for c in node.children:
                _walk_node_fc(c, inherited_compound, is_brep_convertible, handle_brep_fc, handle_openscad_fc)
            handle_brep_fc(node)
            return
        handle_brep_fc(node)
        for c in node.children:
            _walk_node_fc(c, False, is_brep_convertible, handle_brep_fc, handle_openscad_fc)
    else:
        handle_brep_fc(node)

# ----------------------------------------------------
# EXAMPLE FreeCAD HANDLERS
# ----------------------------------------------------

def example_handle_brep_fc(node):
    FCprint(f"FC Brep {node}/n")
    doc = FreeCAD.ActiveDocument
    if not isinstance(node, OpNode):
        return
    if node.name == 'cube':
        size = node.args[0] if node.args else [1,1,1]
        obj = doc.addObject("Part::Box", "Cube")
        obj.Length, obj.Width, obj.Height = size if isinstance(size, list) else [size]*3
    elif node.name == 'sphere':
        r = node.args[0] if node.args else 1
        obj = doc.addObject("Part::Sphere", "Sphere")
        obj.Radius = r
    elif node.name == 'multmatrix':
        matrix_vals = node.args[0] if node.args else None
        for c in node.children:
            example_handle_brep_fc(c)
            child_obj = FreeCAD.ActiveDocument.ActiveObject
            if matrix_vals and len(matrix_vals) == 16:
                m = FreeCAD.Matrix(*matrix_vals)
                child_obj.Placement = FreeCAD.Placement(m)
    doc.recompute()

def example_handle_openscad_fc(node):
    FCprint(f"OpenSCAD fallback for {node.name}")
    FCprint(node.to_scad())

# ----------------------------------------------------
# IMPORT FUNCTION
# ----------------------------------------------------
# Save the real Python open first
_builtin_open = open  # <- built-in open

def FCprint(msg):
    FreeCAD.Console.PrintError(f"{msg}\n")

def debug_print_ast(node, indent=0):
    pad = "  " * indent
    if isinstance(node, OpNode):
        FCprint(f"{pad}OpNode: {node.name}, args={node.args}")
        for c in node.children:
            debug_print_ast(c, indent + 1)
    elif isinstance(node, RawStmt):
        FCprint(f"{pad}RawStmt: {node.text}")
    else:
        FCprint(f"{pad}Unknown node: {node}")

def open(path):
    FCprint(f"Open CSG file {path}\n")
    with _builtin_open(path, 'r') as f:  # use the real open
        text = f.read()
    ast_root = parser.parse(text)
    if ast_root is None:
        FCprint("Parser returned None — check your CSG file syntax!")
    else:
        FCprint("---- AST Structure ----\n")
        for stmt in ast_root.statements:
           debug_print_ast(stmt)
    if not ast_root:
        FCprint(f"Failed to parse CSG file: {path}")
        return
    walk_csg_ast_fc(ast_root, lambda n: True, example_handle_brep_fc, example_handle_openscad_fc)


