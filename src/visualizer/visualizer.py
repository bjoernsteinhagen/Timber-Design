from dataclasses import dataclass
import trimesh
import numpy as np
from specklepy.objects.geometry import Base
from src.utils.colors import Color
from src.utils.units import Convert
from src.utils.mesh import trimesh_to_speckle_mesh

@dataclass
class DisplayMeshes:
    reference : 'Mesh'
    utilisation : 'Mesh'

class ColumnVisualizer:
    def __init__(self, column: 'Column', units: 'ModelUnits'):
        self.column = column
        self.start_point = np.array([
            Convert.length(column.speckle_object.baseLine.start.x, input_unit=units.length_unit),
            Convert.length(column.speckle_object.baseLine.start.y, input_unit=units.length_unit),
            Convert.length(column.speckle_object.baseLine.start.z, input_unit=units.length_unit)
        ])
        self.end_point = np.array([
            Convert.length(column.speckle_object.baseLine.end.x, input_unit=units.length_unit),
            Convert.length(column.speckle_object.baseLine.end.y, input_unit=units.length_unit),
            Convert.length(column.speckle_object.baseLine.end.z, input_unit=units.length_unit)
        ])
        self.width = Convert.length(column.speckle_object.property.profile.width, input_unit=units.length_unit)
        self.depth = Convert.length(column.speckle_object.property.profile.depth, input_unit=units.length_unit)
        self.utilisation = column.design_results.utilisation

    def sort_line_orientation(self):
        if self.start_point[2] > self.end_point[2]:
            self.start_point, self.end_point = self.end_point, self.start_point

    def create_column_mesh(self):
        self.sort_line_orientation()
        direction = self.end_point - self.start_point
        length = np.linalg.norm(direction)

        # Create a box centered at the origin
        box = trimesh.creation.box((self.width, self.depth, length))

        # Calculate the midpoint of the column
        midpoint = (self.start_point + self.end_point) / 2

        # Calculate the rotation to align the box with the column direction
        rotation_matrix = trimesh.geometry.align_vectors([0, 0, 1], direction)

        # Apply rotation and translation to place the box at the correct position
        box.apply_transform(rotation_matrix)
        box.apply_translation(midpoint)

        return box

    def create_utilisation_mesh(self):
        self.sort_line_orientation()
        direction = self.end_point - self.start_point
        length = np.linalg.norm(direction)

        utilisation = min(self.utilisation, 1.0)  # Cap utilisation at 1.0
        util_length = utilisation * length

        # Create a box for utilisation
        util_box = trimesh.creation.box((self.width, self.depth, util_length))

        # Move the box so that its base is at the origin
        util_box.apply_translation([0, 0, util_length / 2])

        # Calculate the rotation to align the box with the column direction
        rotation_matrix = trimesh.geometry.align_vectors([0, 0, 1], direction)

        # Apply rotation
        util_box.apply_transform(rotation_matrix)

        # Translate the box to the start point of the column
        util_box.apply_translation(self.start_point)

        return util_box

    def visualize(self):
        column_mesh = trimesh_to_speckle_mesh(self.create_column_mesh(), 0.1, Color.Highlight)
        utilisation_mesh = trimesh_to_speckle_mesh(self.create_utilisation_mesh(), 1, Color.Success if self.utilisation < 1.0 else Color.Danger)
        return column_mesh, utilisation_mesh

    def prepare_commit(self, attributes: dict):
        self.column.speckle_object.displayValue = self.column.display_meshes.reference
        designResults = Base()
        for key, value in attributes.items():
            designResults[key] = value
        for section, calculations_steps in self.column.design_results.calculation_log.items():
            designResults[section] = {}
            for step in calculations_steps:
                if step.unit != '':
                    designResults[section][f'{step.symbol} ({step.unit})'] = round(step.value, 2)
                else:
                    designResults[section][step.symbol] = round(step.value, 2)
        designResults.displayValue = self.column.display_meshes.utilisation
        self.column.speckle_object['designResults'] = designResults
        for to_remove in ['baseLine', 'end1Node', 'end2Node', 'end1Offset', 'end2Offset', 'StiffnessModifiers', 'end1Releases', 'end2Releases']:
            delattr(self.column.speckle_object, to_remove)
        return self.column.speckle_object