# commands/varsSCAD.py
import FreeCAD
import FreeCADGui
import os

from freecad.OpenSCAD_Ext.logger.Workbench_logger import write_log
from freecad.OpenSCAD_Ext.core.OpenSCADObjects import SCADfileBase

# Absolute FreeCAD-style imports
from freecad.OpenSCAD_Ext.parsers.scadmeta.scadmeta_parser import parse_scadmeta
from freecad.OpenSCAD_Ext.core.varset_utils import (
    add_scad_vars_to_varset,
    mirror_varset_to_spreadsheet,
)

