from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
from freecad.OpenSCAD_Ext.commands.baseSCAD import BaseParams
from freecad.OpenSCAD_Ext.objects.SCADObject import SCADfileBase, ViewSCADProvider
#
# Called with 
# Wrap in SCADModuleObject
# SCADModuleObject(obj, self.meta, self.selected_module_meta, args=args_values)  
#
# self.meta : SCADMeta
# self.selected_module_meta : SCADModule: 
#
# --- Data Classes ---
#class SCADArgument:
#    def __init__(self, name, default=None, description=None):
#        self.name = name
#        self.default = default
#        self.description = description
#
#class SCADModule:
#    def __init__(self, name):
#        self.name = name
#        self.description = ""
#        self.usage = []
#        self.includes = []
#        self.arguments = []
#
#class SCADMeta:
#    def __init__(self, sourceFile):
#        self.sourceFile = sourceFile
#        self.baseName = os.path.basename(sourceFile)
#        self.includes = []          # Includes in the file
#        self.comment_includes = []  # Includes found in file header comments
#        self.modules = []           # List of SCADModule objects
  
import os

class SCADModuleObject(SCADfileBase):
    def __init__(self, obj, name, sourceFile, meta, module, args):
        # SCADfileBase(self, obj, scadName, sourceFile, mode='Mesh', fnmax=16, timeout=30, keep=False):
        super().__init__(
            obj,
            name,
            sourceFile
        )
        self.Object = obj
        #self.sourceFile = meta.sourceFile
        #self.scadName = meta.baseName
        self.meta = meta
        self.module = module
        self.args = args
        obj.Proxy = self

        write_log("INFO",f"library scad file {meta.sourceFile}")
        write_log("INFO",f"includes {meta.includes}")
        write_log("INFO",f"modules {module.name}")
        write_log("INFO",f"args {args}")
        
        self._init_properties(obj, meta, module)
        # defaults set when creating properties
        # self._set_defaults(obj, module)
        # Need to do properties before build_scad_source
        # refresh_scad_source ??
        self._build_scad_source(obj) # obj ?
        self.add_args_as_properties(obj)
        self.renderFunction(obj)
    
    def _init_properties(self, obj, meta, module):
        # --- Parameters group ---
        obj.addProperty(
            "App::PropertyString",
            "ModuleName",
            "Parameters",
            "OpenSCAD module name"
        ).ModuleName = self.module.name

        obj.addProperty(
            "App::PropertyString",
            "Description",
            "Parameters",
            "Module description"
        ).Description = module.description

        obj.setEditorMode("Description", 1)
        '''
        obj.addProperty(
            "App::PropertyString",
            "Usage",
            "Parameters",
            "Usage examples"
        ).Usage = "\n".join(module.usage, [])

        obj.setEditorMode("Usage", 1)

        # Collect argument documentation
        arg_info = []
        for arg in module.get("arguments", []):
            line = arg["name"]
            if arg.get("description"):
                line += " – " + arg["description"]
            arg_info.append(line)

        obj.addProperty(
            "App::PropertyString",
            "ArgumentsInfo",
            "Parameters",
            "Argument documentation"
        ).ArgumentsInfo = "\n".join(arg_info)

        obj.setEditorMode("ArgumentsInfo", 1)
        '''

    def add_args_as_properties(self, obj):
        # --- Add to SCAD group ---
        #obj.addProperty(
        #    "App::PropertyStringList",
        #    "Includes",
        #    "SCAD",
        #    "Required include files"
        #).Includes = meta.get("includes", [])

        #obj.addProperty(
        #    "App::PropertyString",
        #    "Source",
        #    "SCAD",
        #    "Generated OpenSCAD source"
        #)

        #obj.setEditorMode("Source", 1)

        # --- Add module parameters dynamically ---
        for arg in self.module.arguments:
            name = arg.name
            default = arg.default
            description = arg.description

            prop = obj.addProperty(

                "App::PropertyString",
                name,
                "Module Parameters",
                description

            )
        
            if default is not None:
                setattr(obj, name, str(default))


    #def _set_defaults(self, obj, module):
    #    obj.ModuleName = module["name"]

    def execute(self, obj):
        # src = self._build_scad_source(obj)
        # obj.Source = src

        # Hook to existing OpenSCAD execution
        # run_openscad(obj, src)
        pass

    def _build_scad_source(self, obj):
        import os

        # Log the current source file
        write_log("Source File", obj.sourceFile)

        # Get the SCAD source directory from BaseParams (static method)
        scad_dir = BaseParams.getScadSourcePath()

        # Build the full SCAD file path
        obj.Proxy.sourceFile = os.path.join(scad_dir, obj.Name + ".scad")

        # Make sure the directory exists
        os.makedirs(scad_dir, exist_ok=True)

        # Open the file for reading/writing (append + read)
        with open(obj.Proxy.sourceFile, "a+", encoding="utf-8") as fp:
            # These are the includes found in the library
            # may or may not be required by this module
            # For now include in case needed
            for inc in self.meta.comment_includes:
                print(f"include <{inc}>;", file=fp)

            for inc in self.meta.includes:
                print(f"include <{inc}>;", file=fp)

            #print(f"Arguments {self.module.arguments})")
            argsLst = [arg.name for arg in self.module.arguments]
            argsLst = ", ".join(argsLst)
            print(f"Args List {argsLst}")
            # First add the Module definition
            # Could be just name or name=value ?
            print(f"module {self.module.name} ({argsLst})", file=fp)
            print(f"{self.module.name} ({argsLst});", file=fp)
            fp.close()

    '''

        args = []
        for prop in obj.PropertiesList:
            if obj.getGroupOfProperty(prop) != "Parameters":
                continue
            if prop in (
                "ModuleName",
                "Description",
                "ArgumentsInfo",
                "Usage",
            ):
                continue

            val = getattr(obj, prop)
            if val != "":
                args.append(f"    {prop} = {val}")

        lines.append(",\n".join(args))
        lines.append(");")

        return "\n".join(lines)
    '''

    def _module_source_from_library(self, lines):
        # maybe find and save original source as property
        # Need to deal with case if library changes
        # SCADModuleObject maybe no edit
        # So maybe SCADfileBase, SCADObject and SCADModuleObject
        #lines.append("#ToDo Add from library defintion")
        # defintion is in library so should not add
        pass

def _add_argument_property(self, obj, arg):
    name = arg.name
    default = arg.default
    desc = arg.description
    subsection = "SCAD Parameters"

    # Boolean
    if default in ("true", "false"):
        prop = obj.addProperty(
            "App::PropertyBool",
            name,
            subsection,
            desc
        )
        setattr(obj, name, default == "true")
        return

    # Integer
    try:
        if default is not None and "." not in str(default):
            ival = int(default)
            prop = obj.addProperty(
                "App::PropertyInteger",
                name,
                subsection,
                desc
            )
            setattr(obj, name, ival)
            return
    except Exception:
        pass

    # Float
    try:
        fval = float(default)
        prop = obj.addProperty(
            "App::PropertyFloat",
            name,
            subsection,
            desc
        )
        setattr(obj, name, fval)
        return
    except Exception:
        pass

    # String fallback
    prop = obj.addProperty(
        "App::PropertyString",
        name,
        subsection,
        desc
    )
    if default:
        setattr(obj, name, str(default).strip('"'))

