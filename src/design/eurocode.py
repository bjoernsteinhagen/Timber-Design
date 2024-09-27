from math import pi, sqrt
from .design_code import DesignCode
from .designer import DesignResults
from src.design.logger import CalculationLog

class Eurocode(DesignCode):
    def __init__(self, design_parameters):
        super().__init__(code='EN 1995-1-1:2004+A1:2008 (E)', design_parameters=design_parameters)

    def design_column(self, column: 'Column') -> DesignResults:

        super().design_column(column) # NOTE: Every column design should receive a blank instance of the logger

        self.calculation_log['Geometric Parameters'].append(CalculationLog('b', column.cross_section.width, 'm'))
        self.calculation_log['Geometric Parameters'].append(CalculationLog('h', column.cross_section.depth, 'm'))
        self.calculation_log['Geometric Parameters'].append(CalculationLog('l', column.length, 'm'))

        buckling_length = column.length * 1.0 # NOTE: Currently assuming pin-pin columns
        characteristic_comp_strength = column.material.strength.compression_parallel_to_grain
        modulus_of_elasticity_fifth_percentile = column.material.stiffness.fifth_percentile_moe_parallel_to_grain
        self.calculation_log[f'Material Parameters ({column.speckle_object.property.material.name})'].append(
            CalculationLog('f_c,0,k', characteristic_comp_strength, 'N/m²'))
        self.calculation_log[f'Material Parameters ({column.speckle_object.property.material.name})'].append(
            CalculationLog('E_0.05', modulus_of_elasticity_fifth_percentile, 'N/m²'))

        results = {}

        for axis in ['y', 'z']:

            radius_of_gyration = getattr(column.cross_section, f'radius_of_gyration_{axis}')
            slenderness_ratio = self.slenderness_ratio(axis, buckling_length, radius_of_gyration)
            relative_slenderness = self.relative_slenderness(axis, slenderness_ratio, characteristic_comp_strength,
                                                             modulus_of_elasticity_fifth_percentile)
            factor_for_member_within_straightness_limits = self.member_within_straightness_limits(
                column.material.description)
            buckling_factor = self.buckling_factor(axis, factor_for_member_within_straightness_limits,
                                                   relative_slenderness)
            buckling_reduction_factor = self.buckling_reduction_factor(axis, buckling_factor, relative_slenderness)

            results[axis] = buckling_reduction_factor

        governing_buckling_reduction_factor = min(results.values())
        strength_modification_factor = self.strength_modification_factor()
        design_resistance = ((governing_buckling_reduction_factor * strength_modification_factor)
                             / self.material_safety_factor(column)) * characteristic_comp_strength
        design_action = abs(column.internal_forces.dataframe['axial_force'].min()) / column.cross_section.area
        utilisation = round(design_action / design_resistance, 3)

        self.calculation_log['Stability'].append(
            CalculationLog('k_c,min', governing_buckling_reduction_factor, note='Governing buckling reduction factor'))
        self.calculation_log['Proof'].append(CalculationLog('R_d', design_resistance, 'N/m²', 'EN 1995-1-1:2004+A1:2008 (E), Cl. 2.4.3'))
        self.calculation_log['Proof'].append(CalculationLog('E_d', design_action, 'N/m²'))
        self.calculation_log['Proof'].append(
            CalculationLog('eta', utilisation, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 6.23 and 6.24', note='Utilisation under axial stresses only'))

        return DesignResults(self.calculation_log, utilisation)

    def strength_modification_factor(self):
        """Strength modification factor (kmod)"""
        result = None
        if self.design_parameters['load_duration_class'] == 'Permanent':
            result = 0.6
        elif self.design_parameters['load_duration_class'] == 'Long term':
            result = 0.7
        elif self.design_parameters['load_duration_class'] == 'Medium term':
            result = 0.8
        elif self.design_parameters['load_duration_class'] == 'Short term':
            result = 0.9
        elif self.design_parameters['load_duration_class'] == 'Instantaneous':
            result = 1.1
        else:
            return ValueError(f'Load duration class {self.design_parameters['load_duration_class']} not recognised')
        self.calculation_log['Stability'].append(CalculationLog('k_mod', result, code='EN 1995-1-1:2004+A1:2008 (E), Table 3.1'))
        return result

    def material_safety_factor(self, structural_element: 'StructuralElement') -> float:
        """Material safety factor (EN 1995-1-1:2004, Table 2.3)"""
        if structural_element.material.description == 'Solid':
            result = 1.3
        elif structural_element.material.description == 'Glulam':
            result = 1.25
        elif structural_element.material.description == 'LVL':
            result = 1.2
        else:
            raise ValueError(f'Material of description {structural_element.material.note} not recognised')
        self.calculation_log['Proof'].append(CalculationLog('gamma_M', result, code='EN 1995-1-1:2004+A1:2008 (E), Table 2.3'))
        return result

    def system_modification_factor(self, material_property: str):
        """Multiple of relevant member and system modification factors"""
        if material_property == 'bending_parallel_to_grain' or material_property == 'tension_parallel_to_grain':
            height = self.structural_element.cross_section.height if material_property == 'bending_parallel_to_grain' else max(
                self.structural_element.cross_section.height, self.structural_element.cross_section.breadth)
            if self.structural_element.material.description == 'Solid':
                if self.structural_element.material.density.minimum <= 700 and height < 150:
                    result = min(pow(150/height, 0.2), 1.3)
                    self.calculation_log['Modification Factors'].append(CalculationLog('k_h', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 3.1'))
            elif self.structural_element.material.description == 'Glulam':
                result = min(pow(600/height, 0.1), 1.1)
                self.calculation_log['Modification Factors'].append(CalculationLog('k_h', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 3.2'))
            elif self.structural_element.material.description == 'LVL':
                raise NotImplementedError('Size effect parameter required form manufacturer')
            else:
                raise ValueError(f'Material of description {material_property} not recognised')
            return result
        return None

    def slenderness_ratio(self, axis: str, buckling_length: float, radius_of_gyration: float):
        """Geometric slenderness ratio"""
        result = buckling_length/radius_of_gyration
        self.calculation_log['Stability'].append(
            CalculationLog(f'lambda_{axis}', result, note=f'Slenderness ratio about the {axis}-axis'))
        return result

    def relative_slenderness(self,
                                axis: str,
                                slenderness: float,
                                characteristic_comp_strength: float,
                                modulus_of_elasticity_fifth_percentile: float):
        """Relative slenderness (EN 1995-1-1:2004, Eq. 6.21 and 6.22)"""
        result = (slenderness/pi)*sqrt(
            characteristic_comp_strength/modulus_of_elasticity_fifth_percentile)
        self.calculation_log['Stability'].append(
            CalculationLog(f'lambda_rel,{axis}', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 6.21 and 6.22',
                           note=f'Relative slenderness about the {axis}-axis'))
        return result

    def member_within_straightness_limits(self, timber_type: str) -> float:
        """Factor for members within the straightness limits (EN 1995-1-1:2004+A1:2008 (E), Eq. 6.29)"""
        if timber_type == 'Solid':
            result = 0.2
        elif timber_type == 'Glulam':
            result = 0.1
        else:
            raise ValueError(f'Timber type {timber_type} not recognised')
        self.calculation_log['Stability'].append(
            CalculationLog('beta_c', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 6.29'))
        return result

    def buckling_factor(self,
                        axis: str,
                        beta_c: float,
                        lambda_rel: float):
        """Buckling factor (EN 1995-1-1:2004, Eq. 6.27 and 6.28)"""
        result = 0.5*(1 + beta_c*(lambda_rel-0.3)+lambda_rel**2)
        self.calculation_log['Stability'].append(
            CalculationLog(f'k_{axis}', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 6.27 and 6.28',
                           note=f'Buckling factor about the {axis}-axis'))
        return result

    def buckling_reduction_factor(self,
                                    axis: str,
                                    buckling_factor: float,
                                    relative_slenderness: float):
        """Buckling reduction factor (EN 1995-1-1:2004, Eq. 6.25 and 6.26)"""
        result = 1/(buckling_factor+sqrt(buckling_factor**2-relative_slenderness**2))
        self.calculation_log['Stability'].append(
            CalculationLog(f'k_c,{axis}', result, code='EN 1995-1-1:2004+A1:2008 (E), Eq. 6.25 and 6.26',
                           note=f'Buckling reduction factor about the {axis}-axis'))
        return result
