from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
import FreeCAD
import re

# ============================================================
# Spreadsheet helper
# ============================================================

def safe_set(sheet, row, col, value):
    try:
        col_letter = ""
        c = col
        while c > 0:
            c, remainder = divmod(c - 1, 26)
            col_letter = chr(65 + remainder) + col_letter
        sheet.set(f"{col_letter}{row}", str(value))
    except Exception as e:
        write_log("ERROR", f"Failed to set spreadsheet cell {row},{col}: {e}")

# ============================================================
# SCAD parser
# ============================================================

def parse_scad_meta(file_path):
    """
    Parse a SCAD file and return:
      - globals
      - modules
      - module parameter defaults
      - module body expressions
    """
    with open(file_path, "r") as f:
        text = f.read()

    module_re = re.compile(r'^\s*module\s+(\w+)\s*\((.*?)\)\s*{',
                           re.MULTILINE | re.DOTALL)
    assign_re = re.compile(r'^\s*(\w+)\s*=\s*([^;]+);', re.MULTILINE)
    set_re = re.compile(r'^\s*(\w+)\s*=\s*\[.*?\];', re.MULTILINE)

    modules = {}
    last_end = 0

    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------
    for m in module_re.finditer(text):
        name = m.group(1)

        # ---- parameters with defaults
        params_with_expr = {}
        for p in m.group(2).split(','):
            p = p.strip()
            if not p:
                continue
            if '=' in p:
                pname, expr = p.split('=', 1)
                params_with_expr[pname.strip()] = expr.strip()
            else:
                params_with_expr[p] = ""

        # ---- extract module body
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        body = text[start:i - 1]

        # ---- body expressions
        body_exprs = {}
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if "=" in line and ";" in line:
                v, e = line.split("=", 1)
                body_exprs[v.strip()] = e.strip().rstrip(";")

        modules[name] = {
            "params": list(params_with_expr.keys()),
            "param_defaults": params_with_expr,
            "body_exprs": body_exprs,
            "body": body
        }

        last_end = i

    # --------------------------------------------------------
    # Globals
    # --------------------------------------------------------
    global_text = text[:last_end]
    global_vars = assign_re.findall(global_text)
    global_sets = set_re.findall(global_text)

    meta = {
        "__global__": {
            "vars": [v for v, _ in global_vars],
            "exprs": {v: e for v, e in global_vars},
            "sets": global_sets
        }
    }

    # --------------------------------------------------------
    # Module vars
    # --------------------------------------------------------
    for name, data in modules.items():
        vars_found = set(data["params"]) | set(data["body_exprs"].keys())
        meta[name] = {
            "vars": list(vars_found),
            "param_defaults": data["param_defaults"],
            "body_exprs": data["body_exprs"],
            "sets": []
        }

    return meta

# ============================================================
# varsSCAD (called by command)
# ============================================================

def varsSCAD(obj):
    """
    Create spreadsheets:
      Name | Value Expression | Value Evaluated | Type
    """
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("SCAD_Vars")

    meta = parse_scad_meta(obj.sourceFile)

    def eval_expr(expr, scope):
        try:
            return str(eval(expr, {}, scope))
        except Exception:
            return ""

    def safe_clear_sheet(sheet):
        # Clear spreadsheet (FreeCAD version safe)
        try:
           sheet.clearAll()
        except Exception:
           try:
               sheet.clear()
           except Exception:
               # fallback: recreate sheet
               doc.removeObject(sheet.Name)
               sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)


    for module_name, mod in meta.items():
        sheet_name = f"Vars_{module_name}"
        sheet = doc.getObject(sheet_name) or doc.addObject(
            "Spreadsheet::Sheet", sheet_name
        )
        safe_clear_sheet(sheet)
        sheet.ViewObject.Visibility = True

        # Header
        safe_set(sheet, 1, 1, "Name")
        safe_set(sheet, 1, 2, "Value Expression")
        safe_set(sheet, 1, 3, "Value Evaluated")
        safe_set(sheet, 1, 4, "Type")

        row = 2
        scope = {}

        # Globals
        if module_name == "__global__":
            expr_map = mod.get("exprs", {})
        else:
            expr_map = {}

        for var in mod.get("vars", []):
            expr = (
                mod.get("body_exprs", {}).get(var)
                or mod.get("param_defaults", {}).get(var)
                or expr_map.get(var, "")
            )

            value = eval_expr(expr, scope)
            if value:
                try:
                    scope[var] = float(value)
                except Exception:
                    pass

            safe_set(sheet, row, 1, var)
            safe_set(sheet, row, 2, expr)
            safe_set(sheet, row, 3, value)
            safe_set(sheet, row, 4, "Variable")
            row += 1

    doc.recompute()
    if FreeCAD.GuiUp:
        FreeCAD.Gui.updateGui()

    write_log("INFO", f"SCAD variables extracted for {obj.Name}")

