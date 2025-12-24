from dataclasses import dataclass, field

@dataclass
class CsgMeta:
    """
    Structural CSG metadata
    """
    top_level_hulls: list = field(default_factory=list)
    top_level_minkowski: list = field(default_factory=list)

