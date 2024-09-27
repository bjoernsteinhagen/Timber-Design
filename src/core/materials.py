from enum import Enum, EnumMeta
from dataclasses import dataclass
from abc import ABC, ABCMeta
from ..utils.units import Convert

class ABCEnumMeta(ABCMeta, EnumMeta):
    pass

class MaterialFactory:
    """Factory class to create a TimberMaterial based on region and material name."""

    @staticmethod
    def get_material(region: str, material_name: str) -> 'TimberMaterial':
        """Returns the TimberMaterial object based on the region and material_name."""
        # Dictionary mapping region names to their corresponding strength class enums
        region_classes = {
            "Britain": BritishStandards,
            # Add other regions here as needed
        }

        # Get the strength class enum for the region
        strength_class_enum = region_classes.get(region)

        if not strength_class_enum:
            raise ValueError(f"Unsupported region: {region}")

        # Get the material properties based on the material_name
        try:
            strength_class = strength_class_enum[material_name]
        except KeyError as exc:
            # Re-raise the KeyError with a ValueError using `from` to preserve context
            raise ValueError(f"Material '{material_name}' not found in region '{region}'") from exc

        # Return a TimberMaterial object
        return TimberMaterial(strength_class)

@dataclass(frozen=True)
class StrengthProperties:
    """Strength properties in Pascals (N/m²)"""
    bending_parallel_to_grain: float
    tension_parallel_to_grain: float
    tension_perpendicular_to_grain: float
    compression_parallel_to_grain: float
    compression_perpendicular_to_grain: float
    shear_parallel_to_grain: float

@dataclass(frozen=True)
class StiffnessProperties:
    """Stiffness properties in Pascals (N/m²)"""
    mean_moe_parallel_to_grain: float
    fifth_percentile_moe_parallel_to_grain: float
    mean_moe_perpendicular_to_grain: float
    mean_shear_modulus: float

@dataclass(frozen=True)
class DensityProperties:
    """Density properties in kg/m²"""
    mean: float
    minimum: float

@dataclass(frozen=True)
class TimberProperties:
    """Strength, stiffness and density properties for a given strength class"""
    description: str
    strength: StrengthProperties
    stiffness: StiffnessProperties
    density: DensityProperties

class StrengthClass(ABC):
    """Base class for regional enumerations"""

    def __init__(self, properties):
        self._properties = properties

    @property
    def properties(self) -> TimberProperties:
        return self._properties

class BritishStandards(StrengthClass, Enum, metaclass = ABCEnumMeta):
    """Common strength classes as defined in the BS EN 338 and 1994"""
    # Characteristic properties of solid softwood (from BS EN 338)
    C16 = TimberProperties(
        description='Solid',
        strength=StrengthProperties(*Convert.pressure(16, 10, 0.5, 17, 2.2, 1.8)),
        stiffness=StiffnessProperties(*Convert.pressure(8000, 5400, 270, 500)),
        density=DensityProperties(370, 310)
    )
    C24 = TimberProperties(
        description='Solid',
        strength=StrengthProperties(*Convert.pressure(24, 14, 0.5, 21, 2.5, 2.5)),
        stiffness=StiffnessProperties(*Convert.pressure(11000, 7400, 370, 690)),
        density=DensityProperties(420, 350)
    )
    C27 = TimberProperties(
        description='Solid',
        strength=StrengthProperties(*Convert.pressure(27, 16, 0.6, 22, 2.6, 2.8)),
        stiffness=StiffnessProperties(*Convert.pressure(11500, 7700, 380, 720)),
        density=DensityProperties(450, 370)
    )
    # Characteristic properties of softwood glulam (from BS EN 1994)
    GL24c = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(24, 14, 0.35, 21, 2.4, 2.2)),
        stiffness=StiffnessProperties(*Convert.pressure(11600, 9400, 320, 590)),
        density=DensityProperties(395, 350)
    )
    GL28c = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(28, 16.5, 0.4, 24, 2.7, 2.7)),
        stiffness=StiffnessProperties(*Convert.pressure(12600, 10200, 390, 720)),
        density=DensityProperties(430, 380)
    )
    GL32c = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(32, 19.5, 0.45, 26.5, 3.0, 3.2)),
        stiffness=StiffnessProperties(*Convert.pressure(13700, 11100, 420, 780)),
        density=DensityProperties(460, 410)
    )
    GL24h = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(24, 16.5, 0.4, 24, 2.7, 2.7)),
        stiffness=StiffnessProperties(*Convert.pressure(11600, 9400, 390, 720)),
        density=DensityProperties(420, 380)
    )
    GL28h = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(28, 19.5, 0.45, 26.5, 3.0, 3.2)),
        stiffness=StiffnessProperties(*Convert.pressure(12600, 10200, 420, 780)),
        density=DensityProperties(450, 410)
    )
    GL32h = TimberProperties(
        description='Glulam',
        strength=StrengthProperties(*Convert.pressure(32, 22.5, 0.5, 29, 3.3, 3.8)),
        stiffness=StiffnessProperties(*Convert.pressure(13700, 11100, 460, 850)),
        density=DensityProperties(475, 430)
    )

class TimberMaterial:
    """Timber material object"""
    def __init__(self, strength_class: StrengthClass):
        self.strength_class = strength_class

    @property
    def description(self) -> str:
        """A basic description of the material (Solid / Glulam)"""
        return self.strength_class.properties.description

    @property
    def strength(self) -> StrengthProperties:
        """Strength properties for bending, tension, compression and shear"""
        return self.strength_class.properties.strength

    @property
    def stiffness(self) -> StiffnessProperties:
        """Young's and shear modulus"""
        return self.strength_class.properties.stiffness

    @property
    def density(self) -> DensityProperties:
        """"Density properties"""
        return self.strength_class.properties.density
