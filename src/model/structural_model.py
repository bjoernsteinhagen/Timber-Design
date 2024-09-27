from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from specklepy.objects.geometry import Base
from src.core.structural_elements import Column
from src.design.designer import ColumnDesigner
from src.design.logger import AutomationIDLogger
from src.visualizer.visualizer import ColumnVisualizer, DisplayMeshes

@dataclass
class ModelUnits:
    """Gets the units used by the uploaded model and ensures correct unit conversions"""
    length_unit: str # NOTE: 'mm', 'm', 'cm' etc.
    force_unit: str # NOTE: 'N', 'kN' etc.

class StructuralModel(ABC):
    """StructuralModel base class"""

    def __init__(self, received_object, design_code: 'DesignCode', automate_context: 'AutomateContext'):
        self.received_object = received_object
        self.automate_context = automate_context
        self.automate_results: AutomationIDLogger = AutomationIDLogger()
        self.model: 'Model' = None
        self.units: ModelUnits = None
        self.columns: List['Column'] = []
        self.column_designer = ColumnDesigner(design_code)
        self.columns_commit = Base()

    @abstractmethod
    def setup_model(self) -> None:
        """Convenience method to load, validate, and set units in one call"""

    def load(self, model_attribute: str) -> None:
        """Load the model object from a given commit (i.e. received_object)"""
        model = getattr(self.received_object, model_attribute, None)
        if not model:
            raise ValueError(f'"{model_attribute}" not found in commit')
        self.model = model

    def validate(self, attributes: List[str]) -> None:
        """Ensure model object contains required attributes for downstream applications"""
        if not attributes:
            pass
        for attribute in attributes:
            if not hasattr(self.model, attribute):
                raise ValueError(f'"{attribute}" not found in commit')


    def get_units(self, length_unit: str, force_unit: str) -> None:
        """Get units for appropriate conversions to SI units"""
        self.units = ModelUnits(length_unit, force_unit)

    def create_column_objects(self):
        """Template method for getting columns and parsing attributes"""
        is_designable = True
        length, cross_section, material, internal_forces = None, None, None, None
        for column in self.filter_columns():
            length = self.parse_length(column)
            try:
                cross_section = self.parse_cross_section(column)
            except Exception:
                is_designable = False
                self.automate_results.elements_selected_cross_section_nonconformity.append(column.id)
            try:
                material = self.parse_material(column)
            except Exception:
                is_designable = False
                self.automate_results.elements_selected_material_nonconformity.append(column.id)
            try:
                internal_forces = self.parse_internal_forces(column)
            except Exception:
                is_designable = False
                self.automate_results.elements_selected_forces_nonconformity.append(column.id)
            if is_designable:
                self.automate_results.elements_selected_conformity.append(column.id)
            self.columns.append(Column(column, length, cross_section, material, internal_forces, is_designable))

    @abstractmethod
    def filter_columns(self) -> List['Element1D']:
        """Implementation to extract column objects from the model object"""

    @abstractmethod
    def parse_length(self, element_1d) -> float:
        """Parse length attribute to ensure correctness and unit conversion"""

    @abstractmethod
    def parse_cross_section(self, element_1d) -> 'CrossSection':
        """Parse cross-section attribute to ensure correctness and unit conversion"""

    @abstractmethod
    def parse_material(self, element_1d) -> 'Material':
        """Parse material attribute to ensure correctness and unit conversion"""

    @abstractmethod
    def parse_internal_forces(self, element_1d) -> 'InternalForces':
        """Parse internal forces attribute to ensure correctness and unit conversion"""

    def design_columns(self, generate_meshes: bool = False) -> None:
        """Design of all column objects in the model"""
        self.columns_commit['@Columns'] = []
        for column in self.columns:
            try:
                self.column_designer.design(column)
                utilisation = getattr(column.design_results, 'utilisation', None)
                if isinstance(utilisation, (int, float)):
                    if utilisation <= 1.0:
                        self.automate_results.elements_selected_passed.append(column.speckle_object.id)
                    elif utilisation > 1.0:
                        self.automate_results.elements_selected_failed.append(column.speckle_object.id)
                if generate_meshes and column.design_results is not None:
                    visualizer = ColumnVisualizer(column, self.units)
                    reference_mesh, utilisation_mesh = visualizer.visualize()
                    column.display_meshes = DisplayMeshes(reference_mesh, utilisation_mesh)
                    self.columns_commit['@Columns'].append(
                        visualizer.prepare_commit(
                            {'code':self.column_designer.design_code.code,
                             'serviceClass': self.column_designer.design_code.design_parameters['service_class'],
                             'loadDurationClass': self.column_designer.design_code.design_parameters['load_duration_class']}))
            except ValueError as e:
                print(f'Error designing column {column}: {e}')
