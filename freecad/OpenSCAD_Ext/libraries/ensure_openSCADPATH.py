import os
import sys

def ensure_openSCADPATH():
    """
    Ensure OPENSCADPATH is set to a valid default if missing.
    Returns the path.
    """
    if "OPENSCADPATH" in os.environ:
        path = os.environ["OPENSCADPATH"]
    else:
        home = os.path.expanduser("~")
        if sys.platform.startswith("win"):
            path = os.path.join(home, "Documents", "OpenSCAD", "libraries")
        elif sys.platform.startswith("darwin"):
            path = os.path.join(home, "Documents", "OpenSCAD", "libraries")
        else:  # Linux / Unix
            path = os.path.join(home, ".local", "share", "OpenSCAD", "libraries")
        os.environ["OPENSCADPATH"] = path

    return path

