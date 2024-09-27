from dataclasses import dataclass

@dataclass
class CalculationLog:
    symbol: str
    value: float
    unit: str = ''
    code: str = ''
    note: str = ''