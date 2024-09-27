from enum import Enum
from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function, ObjectResultLevel,
)
from src.model.factory import model_loader
from src.design.loader import code_loader
from src.project.project import Project

class AvailableDesignModes(Enum):
    """
    AvailableDesignModes: What elements can be designed?
    """
    Columns = 'Column'

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
                               'load_duration_class': function_inputs.chosen_load_duration_class.value}
                              )

    structural_model = model_loader(source_application, automate_context.receive_version(), design_code, automate_context)
    structural_model.setup_model()

    if function_inputs.chosen_design_mode.value == 'Column':
        structural_model.create_column_objects()
        structural_model.design_columns(generate_meshes=True)
    if structural_model.automate_results.elements_not_selected:
        automate_context.attach_info_to_objects(
            category=f"Elements not defined as {str(function_inputs.chosen_design_mode.value).lower()}",
            object_ids=structural_model.automate_results.elements_not_selected,
            message="The Design Mode targets a specific structural element. These elements were filtered out according to their type. Check element definition and assignment in the source application."
        )
    if structural_model.automate_results.elements_selected_material_nonconformity:
        automate_context.attach_info_to_objects(
            category=f"Failing to parse material as timber",
            object_ids=structural_model.automate_results.elements_selected_material_nonconformity,
            message="These elements were found according to the given Design Mode, however, no match was found in the selected region for the defined material. This indicates either that the element(s) are not timber elements, or that the name of the material needs to be updated to match the database."
        )
    if structural_model.automate_results.elements_selected_length_nonconformity:
        automate_context.attach_info_to_objects(
            category=f"Failing to parse length of element",
            object_ids=structural_model.automate_results.elements_selected_length_nonconformity,
            message="The length of these elements could not be parsed and converted to SI units. Check validity of object.baseLine.length."
        )
    if structural_model.automate_results.elements_selected_cross_section_nonconformity:
        automate_context.attach_info_to_objects(
            category=f"Failing to parse element cross-section",
            object_ids=structural_model.automate_results.elements_selected_cross_section_nonconformity,
            message="The defined cross-section of the element could not be parsed. Check validity of object.property.profile. This is currently restricted to 'Rectangular' cross-sections."
        )
    if structural_model.automate_results.elements_selected_forces_nonconformity:
        automate_context.attach_info_to_objects(
            category=f"Failing to parse internal forces",
            object_ids=structural_model.automate_results.elements_selected_forces_nonconformity,
            message="The forces could not be parsed. Check that the analysis results have been sent with the model."
        )
    if not structural_model.automate_results.elements_selected_conformity:
        automate_context.mark_run_failed(
            status_message=f"Failing to find and parse elements. No elements to design")
    if structural_model.automate_results.elements_selected_conformity:
        automate_context.mark_run_success(f"Design of {function_inputs.chosen_design_mode.value} conducted. See results model for more information.")
        if structural_model.automate_results.elements_selected_passed:
            automate_context.attach_info_to_objects(
                category=f"Elements passing design check according to {design_code.code}",
                object_ids=structural_model.automate_results.elements_selected_passed,
                message="The elements passed the design check with a utilisation < 1.0. See results model for more information.")
        if structural_model.automate_results.elements_selected_failed:
            automate_context.attach_warning_to_objects(
                category=f"Elements not passing design check according to {design_code.code}",
                object_ids=structural_model.automate_results.elements_selected_failed,
                message="The elements did not pass the design check with a utilisation > 1.0. See results model for more information.")

    speckle_results_model = Project(automate_context.speckle_client,
                                    automate_context.automation_run_data.project_id,
                                    function_inputs.results_model)
    speckle_results_model.get_results_model()
    speckle_results_model.send_results_model(structural_model.columns_commit)

if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)

