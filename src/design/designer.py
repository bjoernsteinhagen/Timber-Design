from dataclasses import dataclass
from typing import List
from collections import defaultdict

class ColumnDesigner:
    def __init__(self, design_code: 'DesignCode'):
        self.design_code = design_code

    def design(self, column: 'Column'):
        if column.is_designable:
            results = self.design_code.design_column(column)
            column.set_design_results(results)

@dataclass()
class DesignResults:
    calculation_log: defaultdict[str, List['CalculationLog']]
    utilisation: float
