# -*- coding: utf-8 -*-
"""
FreeCAD OpenSCAD_Workbench UI Diagnostic Tool
Tests for malformed .ui files and missing PrefWidgets.

Usage inside FreeCAD Python console:
    exec(open("/path/to/test_openscad_ui.py").read())
"""

import sys, os, traceback
from PySide2 import QtUiTools, QtWidgets
import FreeCAD, FreeCADGui


# ---------------------------------------------------------
# 🔧 Configuration — adjust this if your UI file name changes
# ---------------------------------------------------------
UI_DIR = os.path.expanduser(
    "~/Mod/OpenSCAD_Workbench/freecad/OpenSCAD/Resources/ui"
)
UI_FILE = "preferences.ui"
UI_PATH = os.path.join(UI_DIR, UI_FILE)


# ---------------------------------------------------------
# 🧩 Step 1 — Test if Qt can load the UI file
# ---------------------------------------------------------
def test_ui_load(ui_path):
    print(f"🔍 Testing load of: {ui_path}")
    if not os.path.exists(ui_path):
        print("❌ File not found:", ui_path)
        return False

    loader = QtUiTools.QUiLoader()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    try:
        with open(ui_path, "r") as f:
            ui = loader.load(f)
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


# ---------------------------------------------------------
# 🧩 Step 2 — Check if all FreeCAD Pref widgets exist
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 🧩 Step 3 — Try displaying the UI in a FreeCAD dialog
# ---------------------------------------------------------
def test_show_in_freecad(ui_path):
    print("\n🪟 Testing FreeCAD dialog display:")
    loader = QtUiTools.QUiLoader()
    mw = FreeCADGui.getMainWindow()
    try:
        with open(ui_path, "r") as f:
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


# ---------------------------------------------------------
# 🧩 Run all tests
# ---------------------------------------------------------
def main():
    print("=" * 70)
    print("🔧 FreeCAD OpenSCAD_Workbench UI Diagnostic Tool")
    print("=" * 70)

    ok1 = test_ui_load(UI_PATH)
    test_freecad_widgets()
    if ok1:
        test_show_in_freecad(UI_PATH)
    else:
        print("❌ Skipping dialog test because UI did not load.")


if __name__ == "__main__":
    main()

