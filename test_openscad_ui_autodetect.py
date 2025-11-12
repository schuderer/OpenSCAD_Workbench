# -*- coding: utf-8 -*-
"""
FreeCAD OpenSCAD_Workbench UI Diagnostic Tool (auto-detect .ui files)
Scans Resources/ui folder and tests each .ui file.
"""

import sys, os, traceback
from PySide2 import QtUiTools, QtWidgets
import FreeCAD, FreeCADGui

# -----------------------------
# Configuration
# -----------------------------
WORKBENCH_UI_DIR = os.path.expanduser(
    "~/Workbenches/OpenSCAD_Workbench/freecad/OpenSCAD/Resources/ui"
)

# -----------------------------
# Helper: find all .ui files recursively
# -----------------------------
def find_ui_files(folder):
    ui_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith(".ui"):
                ui_files.append(os.path.join(root, f))
    return ui_files

# -----------------------------
# Test 1: Load UI file safely
# -----------------------------
def test_ui_load(ui_path):
    print(f"\n🔍 Testing load of: {ui_path}")
    if not os.path.exists(ui_path):
        print("❌ File not found:", ui_path)
        return False

    loader = QtUiTools.QUiLoader()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    try:
        with open(ui_path, "r", encoding="utf-8") as f:
            ui = loader.load(ui_path)
        if not ui:
            print("❌ QUiLoader returned None.")
            return False
        print(f"✅ Loaded OK — top widget: {ui.objectName() or '(unnamed)'}")
        print(f"  Child widgets: {len(ui.children())}")
        return True
    except Exception:
        print("💥 Exception during load:")
        traceback.print_exc()
        return False

# -----------------------------
# Test 2: Check FreeCAD custom widgets
# -----------------------------
def test_freecad_widgets():
    print("\n🔎 Checking FreeCAD preference widgets:")
    loader = QtUiTools.QUiLoader()
    pref_widgets = [
        "Gui::PrefCheckBox",
        "Gui::PrefComboBox",
        "Gui::PrefFileChooser",
        "Gui::PrefSpinBox",
        "Gui::PrefRadioButton",
        "Gui::PrefColorButton",
        "Gui::PrefLineEdit",
    ]
    for name in pref_widgets:
        try:
            loader.createWidget(name, None, name)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ⚠️  {name} failed:", e)

# -----------------------------
# Test 3: Show UI in FreeCAD dialog
# -----------------------------
def test_show_in_freecad(ui_path):
    print("\n🪟 Testing FreeCAD dialog display:")
    loader = QtUiTools.QUiLoader()
    mw = FreeCADGui.getMainWindow()
    try:
        with open(ui_path, "r", encoding="utf-8") as f:
            page = loader.load(f, mw)
        if not page:
            print("❌ Failed to load into FreeCAD main window.")
            return False
        FreeCADGui.Control.showDialog(page)
        print("✅ Shown successfully — check your screen.")
        return True
    except Exception:
        print("💥 Exception while showing dialog:")
        traceback.print_exc()
        return False

# -----------------------------
# Main runner
# -----------------------------
def main():
    print("=" * 70)
    print("🔧 FreeCAD OpenSCAD_Workbench UI Diagnostic Tool")
    print("=" * 70)

    ui_files = find_ui_files(WORKBENCH_UI_DIR)
    if not ui_files:
        print("❌ No .ui files found in:", WORKBENCH_UI_DIR)
        return

    print(f"Found {len(ui_files)} .ui file(s) in {WORKBENCH_UI_DIR}:")
    for f in ui_files:
        print("  ", f)

    # Step 2: check widgets once
    test_freecad_widgets()

    # Step 1 & 3 for each UI
    for ui_path in ui_files:
        ok = test_ui_load(ui_path)
        if ok:
            test_show_in_freecad(ui_path)
        else:
            print("❌ Skipping dialog display due to load failure.")

if __name__ == "__main__":
    main()

