# scad_parser.py
# Requires: pip install ply

import ply.lex as lex
import ply.yacc as yacc
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Any

# -------------------------
# Lexer
# -------------------------
tokens = (
    'IDENT', 'NUMBER', 'STRING',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'COMMA', 'SEMI', 'EQUALS'
)

t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COMMA   = r','
t_SEMI    = r';'
t_EQUALS  = r'='

t_ignore = ' \t\r'

reserved = {
    'module': 'MODULE',
    'translate': 'IDENT',
    'rotate': 'IDENT',
    'union': 'IDENT',
    'difference': 'IDENT',
    'intersection': 'IDENT',
    'hull': 'IDENT',
    'minkowski': 'IDENT',
    'color': 'IDENT',
    'scale': 'IDENT',
    # Add more OpenSCAD builtins as needed
}

def t_IDENT(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

def t_NUMBER(t):
    r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
    try:
        t.value = float(t.value)
    except:
        t.value = float(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_comment(t):
    r'//.*'
    pass

def t_multiline_comment(t):
    r'/\*([^*]|\*+[^*/])*\*+/'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)


# -------------------------
# AST Nodes
# -------------------------
@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    statements: List[Node] = field(default_factory=list)

@dataclass
class OpNode(Node):
    name: str
    args: List[Any] = field(default_factory=list)
    children: List[Node] = field(default_factory=list)
    lineno: int = 0
    col: Optional[int] = None
    parent: Optional[Node] = None
    # mark whether this op is a top-level compound (hull/minkowski)
    top_level_compound: bool = False

    def to_scad(self, indent=0):
        """Serialize subtree back to OpenSCAD-like text for passing to OpenSCAD."""
        pad = '  ' * indent
        args_s = ', '.join(map(self._arg_to_scad, self.args))
        if self.children:
            children_s = '\n'.join(child.to_scad(indent+1) if isinstance(child, OpNode) else str(child)
                                   for child in self.children)
            return f"{pad}{self.name}({args_s}) {{\n{children_s}\n{pad}}}"
        else:
            return f"{pad}{self.name}({args_s});"

    def _arg_to_scad(self, a):
        if isinstance(a, str):
            return f"\"{a}\""
        else:
            return str(a)

@dataclass
class RawStmt(Node):
    """For primitives or raw statements we don't need to break further."""
    text: str
    lineno: int = 0
    parent: Optional[Node] = None

    def to_scad(self, indent=0):
        pad = '  ' * indent
        return f"{pad}{self.text}"


# -------------------------
# Parser grammar
# -------------------------
def p_program(p):
    "program : stmt_list"
    p[0] = Program(statements=p[1])
    # set parent pointers
    for s in p[0].statements:
        if isinstance(s, (OpNode, RawStmt)):
            s.parent = p[0]

def p_stmt_list(p):
    """stmt_list : stmt_list stmt
                 | stmt
                 | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = []

def p_stmt(p):
    """stmt : operation
            | raw_stmt SEMI
            | operation block
    """
    # operation covers both operation; operation block handled in operation rule
    if isinstance(p[1], RawStmt):
        p[0] = p[1]
    else:
        p[0] = p[1]

def p_raw_stmt(p):
    "raw_stmt : IDENT LPAREN maybe_arglist RPAREN"
    # e.g., sphere(r=5); or custom primitive - keep text for passes
    args = p[3] or []
    name = p[1]
    # construct a simple OpNode (no block)
    p[0] = OpNode(name=name, args=args, children=[], lineno=p.lineno(1))

def p_operation(p):
    """operation : IDENT LPAREN maybe_arglist RPAREN block
                 | IDENT LPAREN maybe_arglist RPAREN"""
    name = p[1]
    args = p[3] or []
    if len(p) == 6:
        # has block
        block = p[5]
        node = OpNode(name=name, args=args, children=block, lineno=p.lineno(1))
        # attach parent pointers to children
        for c in node.children:
            if isinstance(c, (OpNode, RawStmt)):
                c.parent = node
        p[0] = node
    else:
        node = OpNode(name=name, args=args, children=[], lineno=p.lineno(1))
        p[0] = node

def p_block(p):
    "block : LBRACE stmt_list RBRACE"
    p[0] = p[2]

def p_maybe_arglist(p):
    """maybe_arglist : arglist
                     | empty"""
    p[0] = p[1]

def p_arglist(p):
    """arglist : arglist COMMA arg
               | arg"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_arg(p):
    """arg : NUMBER
           | STRING
           | IDENT EQUALS NUMBER
           | IDENT EQUALS STRING
           | IDENT"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        # key=value; store as "key=value" or tuple if you prefer
        p[0] = (p[1], p[3])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Parse error at token {p.type!r}, value {p.value!r}, line {p.lineno}")
    else:
        print("Parse error at EOF")

# -------------------------
# Build lexer and parser
# -------------------------
lexer = lex.lex()
parser = yacc.yacc(start='program', debug=False)

# -------------------------
# Post-processing helpers
# -------------------------
COMPOUND_SET = {'hull', 'minkowski'}

def mark_top_level_compounds(ast: Program):
    """
    Mark OpNode.top_level_compound True if the node is named hull/minkowski
    and its parent is Program (i.e., highest-level).
    """
    for stmt in ast.statements:
        if isinstance(stmt, OpNode):
            if stmt.name in COMPOUND_SET:
                stmt.top_level_compound = True
            # recursively set parent pointers already done during parse

def flatten_for_freecad(ast: Program):
    """
    Produce two lists:
    - compounds: list of OpNode which are top-level hull/minkowski (pass to OpenSCAD as whole)
    - brep_ops: list of OpNode / RawStmt representing individual operations for BREP processing
    """
    compounds = []
    brep_ops = []

    for stmt in ast.statements:
        if isinstance(stmt, OpNode) and stmt.top_level_compound:
            compounds.append(stmt)
        else:
            # For non-compound top-level statements: convert to individual ops.
            if isinstance(stmt, OpNode):
                # break down nested children into individual ops for BREP
                collect_brep_ops(stmt, brep_ops)
            elif isinstance(stmt, RawStmt):
                brep_ops.append(stmt)
    return compounds, brep_ops

def collect_brep_ops(node: OpNode, out_list: List):
    """
    Traverse node and collect nodes that should be processed individually for BREP conversion.
    Strategy:
    - If node itself is a primitive (sphere, cube, cylinder, etc) or an operation with no children,
      keep node as individual op.
    - If node has children, traverse children and keep the operation nodes that represent BREP candidates.
    You can tune this to your importer needs.
    """
    primitives = {'sphere', 'cube', 'cylinder', 'polyhedron', 'import'}  # expand as needed
    if node.name in primitives and not node.children:
        out_list.append(node)
    else:
        # operation may be BREP-convertible (like translate/rotate/color around primitives)
        # If node wraps primitives directly, it can be converted with transform applied.
        # For now we output the node itself (importer can interpret transform + children).
        out_list.append(node)
        # and also recurse into children if you want individual child ops separately:
        for c in node.children:
            if isinstance(c, OpNode):
                collect_brep_ops(c, out_list)
            else:
                out_list.append(c)

# -------------------------
# Example usage
# -------------------------
if __name__ == '__main__':
    sample = """
    // Example SCAD
    hull() {
      translate([0,0,0]) sphere(r=5);
      translate([10,0,0]) sphere(r=5);
    }

    union() {
      translate([0,0,0]) cube([5,5,5]);
      rotate([0,0,45]) cylinder(h=10, r=2);
    }

    minkowski() {
      cube([2,2,2]);
      sphere(r=1);
    }

    translate([1,2,3]) {
      sphere(r=2);
    }
    """

    ast = parser.parse(sample, lexer=lexer)
    mark_top_level_compounds(ast)
    compounds, brep_ops = flatten_for_freecad(ast)

    print("Compound (pass whole subtree to OpenSCAD):")
    for c in compounds:
        print("---- Compound:", c.name, "lineno", c.lineno)
        print(c.to_scad())
        print("-----")

    print("\nBREP / individual ops for importer:")
    for b in brep_ops:
        if isinstance(b, OpNode):
            print(f"Op: {b.name} args={b.args} children={len(b.children)}")
            print(b.to_scad())
        elif isinstance(b, RawStmt):
            print("Raw:", b.text)

