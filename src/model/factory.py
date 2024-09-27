from src.model.structural_model import StructuralModel
from src.model.etabs import EtabsModel

def model_loader(source_application: str, received_object, design_code = 'DesignCode') -> StructuralModel:
    if source_application == 'ETABS':
        return EtabsModel(received_object, design_code)
    else:
        raise NotImplementedError('The proof of concept is currently limited to ETABS')
