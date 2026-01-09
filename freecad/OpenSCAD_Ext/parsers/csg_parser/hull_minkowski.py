import Part

from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
from freecad.OpenSCAD_Ext.core.OpenSCADUtils import process_ObjectsViaOpenSCADShape

# -----------------------------
# try_hull
# -----------------------------

import freecad.OpenSCAD_Ext.core.brepHull

def try_hull(stack):
    """
    Try to handle a hull operation on the top objects in the stack.
    Return Part.Shape if successful, else None
    """
    if not stack:
        write_log("Hull", "try_hull: stack empty")
        return None
    if len(stack) < 2:
        return None
    shape1 = stack.pop()
    shape2 = stack.pop()
    write_log("Hull",f"Shapae 1 {shape1.node_type} {shape2.node_type}")
    node_types = [getattr(n, "node_type", str(type(n))) for n in stack]
    write_log("Hull", f"try_hull: nodes in stack: {node_types}")
    return None

    # Example: convex hull of last two objects
    shape1 = stack.pop()
    shape2 = stack.pop()
    try:
        # For simplicity, create hull of vertices
        pts = shape1.Vertexes + shape2.Vertexes
        pts_vectors = [v.Point for v in pts]
        hull = Part.makePolygon(pts_vectors)
        hull_solid = hull.makeSolid()
        return hull_solid
    except Exception:
        # Cannot handle — return None
        return None


    # For now, do nothing and return None
    return None

# -----------------------------
# process_hull
# -----------------------------
def process_hull(doc, node):
    """
    Called by process_AST_node when node_type is 'hull'.
    """
    write_log("Hull", "process_hull ENTERED")

    # Call try_hull on children
    shape = try_hull(node.children)
    if shape:
        write_log("Info", "Hull converted to BRep")
        return shape

    # Fallback to OpenSCAD processing (will just log for now)
    write_log("HULL","Hull not handled")
    write_log("HULL","WILL NEED TO SEND TO OPENSCAD for now just Retun")
    return
    return process_ObjectsViaOpenSCADShape(doc, [node], "Hull")



def try_minkowski(stack):
    """
    Try to handle a minkowski operation.
    Return Part.Shape if successful, else None
    """
    if len(stack) < 2:
        return None
    shape1 = stack.pop()
    shape2 = stack.pop()
    try:
        # Placeholder: real Minkowski would be more complex
        # For now return None to fallback
        return None
    except Exception:
        return None

