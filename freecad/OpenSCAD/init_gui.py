import FreeCAD as App
import FreeCADGui as Gui

class OpenSCADWorkbench_Ext(Gui.Workbench):
    """External OpenSCAD Workbench"""
    MenuText = "OpenSCAD_Ext"
    ToolTip = "External replacement for legacy OpenSCAD tools"
    Icon = ""  # optional, leave empty for now

    def Initialize(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench_Ext.Initialize()\n")

    def Activated(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench_Ext.Activated()\n")

    def Deactivated(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench_Ext.Deactivated()\n")

# Register the workbench
Gui.addWorkbench(OpenSCADWorkbench_Ext())
App.Console.PrintMessage("✅ OpenSCADWorkbench_Ext registered\n")

