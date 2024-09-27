from typing import Dict
from .eurocode import Eurocode

def code_loader(design_code: str, design_parameters: Dict) -> 'DesignCode':
    if design_code == 'Eurocode':
        return Eurocode(design_parameters)
    else:
        raise NotImplementedError(f"Code {design_code} not implemented")
