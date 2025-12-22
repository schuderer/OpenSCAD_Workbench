import FreeCAD
import FreeCADGui

from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
from freecad.OpenSCAD_Ext.core.OpenSCADObjects import SCADBase

class RenderSCADFileObject_Class:
    """Execute SCAD file Object """
    def GetResources(self):
        return {
            'MenuText': 'Render SCAD File Object to Shape',
            'ToolTip': 'Render SCAD file Object to Shape',
            'Pixmap': ':/icons/renderScadFileObj.svg'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Render SCAD File Object executed\n")
        #FreeCAD.Console.PrintError("Render SCAD File Object executed\n")

        write_log("Info", "Render SCAD File Object to Shape")
        doc = FreeCAD.ActiveDocument
        write_log("Info",f"Document {doc.Label}")
        # if not doc:
        #    return

        sel = FreeCADGui.Selection.getSelection()
        write_log("Info",f"selection {sel}")
        # if not sel:
        #    FreeCAD.Console.PrintErrorMessage("No objects selected\n")
        # return

        for obj in sel:
            write_log("Info",f"obj {obj.Label} TypeId {obj.TypeId}")
            if obj.TypeId != "Part::FeaturePython":
               continue
            write_log("INFO","Feature Python")

            if not hasattr(obj, "Proxy"):
                continue
            # print(dir(obj.Proxy))
            write_log("INFO",f"Has Proxy {obj.Proxy.renderFunction}")
            if not hasattr(obj.Proxy, "renderFunction"):
                continue
            write_log("INFO","Has renderFunction")

            try:
               write_log("Render",f"obj.sourceFile {obj.sourceFile}")
               obj.Proxy.renderFunction(obj)

            except Exception as e:
               FreeCAD.Console.PrintError(
                f"Failed to Render SCAD file for {obj.Label}: {e}\n"
               )

    def IsActive(self):
        return True

FreeCADGui.addCommand("RenderSCADFileObject_CMD", RenderSCADFileObject_Class())

