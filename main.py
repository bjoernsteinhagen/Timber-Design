from enum import Enum
from specklepy.api.client import SpeckleClient
from specklepy.api import operations
from specklepy.transports.server import ServerTransport
from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from src.model.factory import model_loader
from src.design.loader import code_loader
from src.project.project import Project

class AvailableDesignModes(Enum):
    """
    AvailableDesignModes: What elements can be designed?
    """
    Columns = 'Columns'

class LoadDurationClasses(Enum):
    """
    LoadDurationClasses: Global parameter for designs.
    """
    Permanent = 'Permanent'
    LongTerm = 'Long term'
    MediumTerm = 'Medium term'
    ShortTerm = 'Short term'
    Instantaneous = 'Instantaneous'

class AvailableDesignCodes(Enum):
    """
    AvailableDesignCodes: Abstractions of DesignCode
    """
    Eurocode = 'Eurocode'

class AvailableMaterialRegions(Enum):
    """
    AvailableMaterialRegions: Abstractions of StrengthClass
    """
    Britain = 'Britain'

def create_one_of_enum(enum_cls):
    """
    Helper function to create a JSON schema from an Enum class.
    This is used for generating user input forms in the UI.
    """
    return [{"const": item.value, "title": item.name} for item in enum_cls]

class FunctionInputs(AutomateBase):

    results_model: str = Field(
        default="Timber Design",
        title="Model for Writing Results",
        description="The model name within the project where the automation results will be written. If the model corresponding to the given name does not exist, it will be created.",
    )

    chosen_design_mode: AvailableDesignModes = Field(
        default=AvailableDesignModes.Columns,
        title='Elements to Design',
        description='The chosen elements will be designed according to the selected design standard. These can be extended, help by contributing.',
        json_schema_extra={
            "oneOf": create_one_of_enum(AvailableDesignModes)
        },
    )

    chosen_design_code: AvailableDesignCodes = Field(
        default=AvailableDesignCodes.Eurocode,
        title='Design Code',
        description='Design code used for the design of timber elements. These can be extended, help by contributing.',
        json_schema_extra={
            "oneOf": create_one_of_enum(AvailableDesignCodes)
        },
    )

    chosen_region: AvailableMaterialRegions = Field(
        default=AvailableMaterialRegions.Britain,
        title='Region',
        description='Regional strength classifications are used when creating materials. These can be extended, help by contributing.',
        json_schema_extra={
            "oneOf": create_one_of_enum(AvailableMaterialRegions)
        },
    )

    chosen_load_duration_class: LoadDurationClasses = Field(
        default=LoadDurationClasses.Permanent,
        title='Load Duration Class',
        description='Load duration classes need to be explicitly stated as there is currently no logic to abstract this from the load combination naming.',
        json_schema_extra={
            "oneOf": create_one_of_enum(LoadDurationClasses)
        },
    )

def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:

    version_id = automate_context.automation_run_data.triggers[0].payload.version_id
    commit = automate_context.speckle_client.commit.get(
        automate_context.automation_run_data.project_id, version_id
    )
    if not commit.sourceApplication:
        raise ValueError("The commit has no sourceApplication, cannot distinguish which model to load.")
    source_application = commit.sourceApplication

    design_code = code_loader(design_code=function_inputs.chosen_design_code.value,
                              design_parameters=
                              {'service_class': 1,
                               'load_duration_class': function_inputs.loaded_duration_class}
                              )

    structural_model = model_loader(source_application, automate_context.receive_version(), design_code)
    structural_model.setup_model()

    if function_inputs.chosen_design_mode.value == 'Columns':
        structural_model.create_column_objects()
        structural_model.design_columns(generate_meshes=True)

    speckle_results_model = Project(automate_context.speckle_client,
                                    automate_context.automation_run_data.project_id,
                                    function_inputs.results_model)
    speckle_results_model.get_results_model()
    speckle_results_model.send_results_model(structural_model.columns_commit)

if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)

