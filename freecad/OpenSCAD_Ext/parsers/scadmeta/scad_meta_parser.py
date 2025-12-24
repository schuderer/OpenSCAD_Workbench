# scad_meta_parser.py

from dataclasses import dataclass, field

@dataclass
class ScadMeta:
    variables: dict = field(default_factory=dict)
    modules: dict = field(default_factory=dict)
    includes: list = field(default_factory=list)
    uses: dict = field(default_factory=dict)

