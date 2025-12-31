import FreeCAD
import FreeCADGui
import os

from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log

class BaseParams:

    PARAM_PATH = "User parameter:BaseApp/Preferences/Mod/OpenSCAD"

    @staticmethod
    def _params():
        return FreeCAD.ParamGet(BaseParams.PARAM_PATH)

    @staticmethod
    def editorPathName():
        params = BaseParams._params()
        path = params.GetString('externalEditor')

        write_log("Info", f"Path to external editor {path}")

        if not BaseParams.isValidFilePath(path):
            FreeCAD.Console.PrintError(
                "External editor path is not set or invalid\n"
            )
        return path

    @staticmethod
    def scadSourcePath():
        params = BaseParams._params()
        path = params.GetString('defaultSourceDirectory')

        write_log("Info", f"Path to scad Source {path}")

        if not BaseParams.isValidDirectory(path):
            FreeCAD.Console.PrintError(
                f"Default Source path {path} is not set or invalid\n"
            )
        return path

    # ---- validation helpers ----

    @staticmethod
    def isValidFilePath(path):
        return bool(path) and os.path.isfile(path)

    @staticmethod
    def isValidDirectory(path):
        return bool(path) and os.path.isdir(path)


    def editSource(self, scadPath):
        import os

        name = os.path.basename(scadPath)[0]
        self.editFile(name, scadPath)

    def editFile(self, name, scadPath):
        import subprocess

        editor = BaseParams.editorPathName()   # ✅ CALL IT
        if not editor:
            FreeCAD.Console.PrintError("No external editor configured\n")
            return

        write_log("Info", f"Launching editor for {name}: {scadPath}")
        write_log("Info", f"Launching editor: {editor} {scadPath}")

        subprocess.Popen(
            [editor, scadPath],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
