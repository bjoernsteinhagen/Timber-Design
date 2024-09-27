# NOTE: Be cautious when using Textbooks where they continually round results or where different material properties are used.

import os, sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)

TOLERANCE = 1e-1

from src.core.cross_section import RectangularSection
from src.core.materials import MaterialFactory
from src.core.structural_elements import Column
from src.core.internal_forces import InternalForces
from src.model.etabs import EtabsModel
from src.design.eurocode import Eurocode
from src.model.structural_model import ModelUnits

@pytest.mark.skip(reason="Run without automate_context")
def test_case_1():
    """Wendehorst - Beispiele aus der Baupraxis (6. Auflage) - Kapitel 8, Beispiel 2.6"""

    # Manually assign cross-section, material, forces
    cross_section = RectangularSection(0.16, 0.32, 0.16 * 0.32, (0.16 * 0.32 **3 / 12), (0.32 * 0.16 **3 / 12))
    material = MaterialFactory.get_material('Britain', 'GL28c')
    internal_forces = InternalForces(data=[{'result_case' : 'Dummy', 'station' : 1, 'axial_force' : 180e3}])

    # Create a column instance
    column = Column(None, 5.0, cross_section, material, internal_forces, True)

    # Create a dummy model instance
    design_parameters = {'service_class': 1, 'load_duration_class': 'Permanent'}
    design_code = Eurocode(design_parameters)
    model = EtabsModel(None, design_code)
    model.columns.append(column)
    model.units = ModelUnits('m', 'N')
    model.design_columns()


    results = model.columns[0].design_results.calculation_log

    for section, result in results.items():
        for log in result:
            if log.symbol == 'f_c,0,k':
                assert abs(log.value - 24e6) < TOLERANCE
            elif log.symbol == 'lambda_y':
                assert abs(log.value - 54.1266) < TOLERANCE
            elif log.symbol == 'lambda_rel,y': # NOTE: Adjusted for different EOM 0.05
                assert abs(log.value - 0.82766) < TOLERANCE
            elif log.symbol == 'beta_c':
                assert abs(log.value - 0.1) < TOLERANCE
            elif log.symbol == 'k_y':
                assert abs(log.value - 0.8688898) < TOLERANCE
            elif log.symbol == 'k_c,y':
                assert abs(log.value - 0.882326) < TOLERANCE
            elif log.symbol == 'lambda_z':
                assert abs(log.value - 108.253) < TOLERANCE
            elif log.symbol == 'lambda_rel,z':
                assert abs(log.value - 1.6514) < TOLERANCE
            elif log.symbol == 'beta_c':
                assert abs(log.value - 0.1) < TOLERANCE
            elif log.symbol == 'k_z':
                assert abs(log.value - 1.93111) < TOLERANCE
            elif log.symbol == 'k_c,z':
                assert abs(log.value - 0.341) < TOLERANCE
            elif log.symbol == 'k_mod':
                assert abs(log.value - 0.6) < TOLERANCE
            elif log.symbol == 'gamma_M':
                assert abs(log.value - 1.3) <TOLERANCE
            elif log.symbol == 'eta':
                assert abs(log.value - 0.93) < TOLERANCE

@pytest.mark.skip(reason="Run without automate_context")
def test_case_2():
    """Schneider Bautabellen (20. Auflage) - Beispiel auf Seite 9.29"""

    # Manually assign cross-section, material, forces
    cross_section = RectangularSection(0.14, 0.14, 0.14 * 0.14, (0.14 * 0.14 **3 / 12), (0.14 * 0.14 **3 / 12))
    material = MaterialFactory.get_material('Britain', 'C24')
    internal_forces = InternalForces(data=[{'result_case' : 'Dummy', 'station' : 1, 'axial_force' : 65.2e3}])

    # Create a column instance
    column = Column(None, 2.85, cross_section, material, internal_forces, True)

    # Create a dummy model instance
    design_parameters = {'service_class': 1, 'load_duration_class': 'Short term'}
    design_code = Eurocode(design_parameters)
    model = EtabsModel(None, design_code, None)
    model.columns.append(column)
    model.units = ModelUnits('m', 'N')
    model.design_columns()

    results = model.columns[0].design_results.calculation_log

    for section, result in results.items():
        for log in result:
            if log.symbol == 'k_c,y':
                assert abs(log.value - 0.542) < TOLERANCE
            elif log.symbol == 'eta':
                assert abs(log.value - 0.42) < TOLERANCE
