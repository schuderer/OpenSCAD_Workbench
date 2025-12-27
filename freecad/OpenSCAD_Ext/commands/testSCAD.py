# -------------------------------
# FreeCAD SCAD variables -> Spreadsheets (working)
# -------------------------------

from freecad.OpenSCAD_Ext.parsers.scadmeta.scadmeta_parser import parse_scad_meta
import FreeCAD

def varsSCAD_working(obj):
    """
    Parses SCAD file from obj.sourceFile and populates FreeCAD spreadsheets.
    """
    doc = FreeCAD.ActiveDocument
    if doc is None:
        doc = FreeCAD.newDocument("SCAD_Vars_Doc")

    scad_file = obj.sourceFile
    meta = parse_scad_meta(scad_file)

    # -------------------------------
    # Print variables for verification
    # -------------------------------
    if "__global__" in meta:
        print("Global variables:")
        print("  vars:", meta["__global__"]["vars"])
        print("  sets:", meta["__global__"]["sets"])

    for module_name, data in meta.items():
        if module_name == "__global__":
            continue
        print(f"Module: {module_name}")
        print("  vars:", data["vars"])
        print("  sets:", data["sets"])

    # -------------------------------
    # Create or update spreadsheets
    # -------------------------------
    for module_name, data in meta.items():
        sheet_name = f"Vars_{module_name}"
        sheet = doc.getObject(sheet_name)
        if sheet is None:
            sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)
        else:
            sheet.clearSpreadsheet()

        # Header
        sheet.set("A1", "Name")
        sheet.set("B1", "Value")
        sheet.set("C1", "Type")

        # Variables
        row = 2
        for var in data.get("vars", []):
            sheet.set(f"A{row}", var)
            sheet.set(f"B{row}", "")          # placeholder for value
            sheet.set(f"C{row}", "Variable")  # type label
            row += 1

        # Sets
        for s in data.get("sets", []):
            sheet.set(f"A{row}", s)
            sheet.set(f"B{row}", "")
            sheet.set(f"C{row}", "Set")
            row += 1

    # Recompute document to refresh GUI
    doc.recompute()
    print("✅ Spreadsheets created/updated for all modules and globals.")

