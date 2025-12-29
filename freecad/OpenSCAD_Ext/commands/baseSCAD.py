import FreeCAD
import FreeCADGui
import os

from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log

class BaseParams:
    def __init__(self):
        params = FreeCAD.ParamGet(\
            "User parameter:BaseApp/Preferences/Mod/OpenSCAD")
        self.editorPathName = params.GetString('externalEditor')  
        write_log("Info", f"Path to external editor {self.editorPathName}")
        if not self.isValidFilePath(self.editorPathName):
            FreeCAD.Console.PrintError(
                "External editor path is not set or invalid\n"
            )
        self.scadSourcePath = params.GetString('defaultSourceDirectory')
        write_log("Info", f"Path to scad Source {self.scadSourcePath}")
        if not self.isValidDirectory(self.scadSourcePath):
            FreeCAD.Console.PrintError(
                "Default Source path {self.scadSourcePath} is not set or invalid\n"
            )


    def isValidFilePath(self, path):
        import os
        if not path:
           return False
    
        if not isinstance(path, str):
           return False
            
        # Expand ~ and environment variables
        path = os.path.expandvars(os.path.expanduser(path))
        
        # Must exist and be a file
        return os.path.isfile(path)

    def isValidDirectory(self, path):
        import os
        if not path:
            return False
        if not isinstance(path, str):
            return False

        # Expand ~ and environment variables
        path = os.path.expanduser(os.path.expandvars(path))

        return os.path.isdir(path)

    def editSource(self, scadPath):
        import os
        name = os.path.basename(scadPath)[0]
        self.editFile(name, scadPath) 

    def editFile(self, name, scadPath):
        import subprocess, os
        write_log("Info", f"Launching editor for {name}: {scadPath}")
        p1 = subprocess.Popen(
            [self.editorPathName, scadPath],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        write_log("Info", f"Launching editor: {self.editorPathName} {scadPath}")

