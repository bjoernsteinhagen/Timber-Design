from typing import Optional
from dataclasses import dataclass
from abc import ABC

@dataclass
class StructuralElement1D(ABC):
    """A typical 1D bar object. Try to maintain as much of Speckle object as possible"""

    speckle_object: Optional['Element1D']
    length: Optional[float]
    cross_section: Optional['CrossSection']
    material: Optional['TimberMaterial']
    internal_forces: Optional['InternalForces']
    is_designable: bool = False
    _design: Optional['DesignResults'] = None
    display_meshes: 'DisplayMeshes' = None

    def set_design_results(self, results: 'DesignResults') -> None:
        if self.is_designable:
            self._design = results

    @property
    def design_results(self):
        return self._design

@dataclass
class Column(StructuralElement1D):
    """A typical column object"""
