from dataclasses import dataclass, field

@dataclass
class CalculationLog:
    symbol: str
    value: float
    unit: str = ''
    code: str = ''
    note: str = ''

@dataclass
class AutomationIDLogger:
    elements_not_selected: list = field(default_factory=list)
    elements_selected_material_nonconformity: list = field(default_factory=list)
    elements_selected_length_nonconformity: list = field(default_factory=list)
    elements_selected_cross_section_nonconformity: list = field(default_factory=list)
    elements_selected_forces_nonconformity: list = field(default_factory=list)
    elements_selected_conformity: list = field(default_factory=list)
    elements_selected_passed: list = field(default_factory=list)
    elements_selected_failed: list = field(default_factory=list)
