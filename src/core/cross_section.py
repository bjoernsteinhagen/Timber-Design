import math
from abc import ABC

class CrossSection(ABC):
    """Cross-section base class"""

    def __init__(self,
                 area: float,
                 moment_of_intertia_about_y: float,
                 moment_of_intertia_about_z: float) -> None:

        self.area = area
        self.moment_of_intertia_about_y = moment_of_intertia_about_y
        self.moment_of_intertia_about_z = moment_of_intertia_about_z

class RectangularSection(CrossSection):
    """A rectangular (or square) cross-section"""

    def __init__(self,
                 width: float,
                 depth: float,
                 area: float,
                 moment_of_intertia_about_y: float,
                 moment_of_intertia_about_z: float) -> None:

        self.shape = 'Rectangular'
        self.width = width
        self.depth = depth
        super().__init__(area, moment_of_intertia_about_y, moment_of_intertia_about_z)

    @property
    def radius_of_gyration_y(self) -> float:
        """Radius of gyration along y-axis"""

        return self.depth / math.sqrt(12)

    @property
    def radius_of_gyration_z(self) -> float:
        """Radius of gyration along z-axis"""

        return self.width / math.sqrt(12)
