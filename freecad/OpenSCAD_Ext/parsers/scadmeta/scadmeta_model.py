from dataclasses import dataclass, field

@dataclass
class ScadMeta:
    """
    File-level OpenSCAD metadata
    """
    variables: dict = field(default_factory=dict)   # name -> expression (str)
    modules: dict = field(default_factory=dict)     # name -> [params]
    includes: list = field(default_factory=list)    # list[str]
    uses: dict = field(default_factory=dict)        # lib -> [modules]

