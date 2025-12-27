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
    Parse a SCAD file and return a dictionary describing:
      - global variables and sets
      - module variables, parameter defaults, body expressions, and sets

    Return format:
    {
        "__global__": {
            "vars": [...],
            "sets": [...],
            "body_exprs": { var: expr }
        },
        "moduleName": {
            "vars": [...],
            "sets": [...],
            "param_defaults": { param: default_expr },
            "body_exprs": { var: expr }
        }
    }
    """
    import re

    meta_dict = {}

    with open(file_path, "r") as f:
        text = f.read()

    # -------------------------------------------------
    # Regex helpers
    # -------------------------------------------------
    module_re = re.compile(
        r'^\s*module\s+(\w+)\s*\((.*?)\)\s*{',
        re.MULTILINE | re.DOTALL
    )

    assign_re = re.compile(r'^\s*(\w+)\s*=\s*(.+?);', re.MULTILINE)
    set_re = re.compile(r'^\s*(\w+)\s*=\s*\[.*?\];', re.MULTILINE)

    modules = {}
    last_end = 0

    # -------------------------------------------------
    # Extract modules + bodies
    # -------------------------------------------------
    for m in module_re.finditer(text):
        name = m.group(1)

        # ---- parameters ----
        params = {}
        for p in m.group(2).split(","):
            p = p.strip()
            if not p:
                continue
            if "=" in p:
                pname, expr = p.split("=", 1)
                params[pname.strip()] = expr.strip()
            else:
                params[p] = ""

        # ---- body text ----
        start = m.end()
        brace_depth = 1
        i = start
        while i < len(text) and brace_depth > 0:
            if text[i] == "{":
                brace_depth += 1
            elif text[i] == "}":
                brace_depth -= 1
            i += 1

        body = text[start:i - 1]

        modules[name] = {
            "param_defaults": params,
            "body": body
        }

        last_end = i

    # -------------------------------------------------
    # GLOBAL (top-level) variables
    # -------------------------------------------------
    global_text = text[:last_end]

    global_exprs = {}
    global_sets = []

    for name, expr in assign_re.findall(global_text):
        if "[" in expr and "]" in expr:
            global_sets.append(name)
        else:
            global_exprs[name] = expr.strip()

    meta_dict["__global__"] = {
        "vars": list(global_exprs.keys()),
        "sets": global_sets,
        "body_exprs": global_exprs
    }

    # -------------------------------------------------
    # MODULE variables
    # -------------------------------------------------
    for name, data in modules.items():
        body_exprs = {}
        body_sets = []

        for v, expr in assign_re.findall(data["body"]):
            if "[" in expr and "]" in expr:
                body_sets.append(v)
            else:
                body_exprs[v] = expr.strip()

        vars_all = set(data["param_defaults"].keys()) | set(body_exprs.keys())

        meta_dict[name] = {
            "vars": list(vars_all),
            "sets": body_sets,
            "param_defaults": data["param_defaults"],
            "body_exprs": body_exprs
        }

    return meta_dict

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

