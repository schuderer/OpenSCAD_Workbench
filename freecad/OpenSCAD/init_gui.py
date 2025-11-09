import FreeCAD as App
import FreeCADGui as Gui

class OpenSCADWorkbench(Gui.Workbench):
    """External OpenSCAD Workbench"""
    MenuText = "OpenSCAD"
    ToolTip = "External replacement for legacy OpenSCAD tools"
    Icon = ""

    def Initialize(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench.Initialize()\n")

    def Activated(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench.Activated()\n")

    def Deactivated(self):
        App.Console.PrintMessage("✅ OpenSCADWorkbench.Deactivated()\n")

Gui.addWorkbench(OpenSCADWorkbench())
App.Console.PrintMessage("✅ OpenSCADWorkbench registered\n")

