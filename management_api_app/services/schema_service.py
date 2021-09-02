import json
from pathlib import Path
from typing import List, Dict


def get_system_properties():
    return {
        "tre_id": {
            "type": "string"
        },
        "workspace_id": {
            "type": "string"
        },
        "azure_location": {
            "type": "string"
        }
    }


def merge_required(all_required):
    required_lists = [prop_list for prop_list in all_required]
    flattened_required = [prop for prop_list in required_lists for prop in prop_list]
    return list(set(flattened_required))


def merge_properties(all_properties: List[Dict]) -> Dict:
    properties = {}
    for prop in all_properties:
        properties.update(prop)
    return properties


def read_schema(schema_file: str) -> (List[str], Dict):
    workspace_schema_def = Path(__file__).parent / ".." / "schemas" / schema_file
    with open(workspace_schema_def) as schema_f:
        schema = json.load(schema_f)
        return schema["required"], schema["properties"]


def enrich_template(original_template, extra_properties) -> dict:
    template = original_template.dict(exclude_none=True)

    all_required = [template["required"]] + [definition[0] for definition in extra_properties]
    all_properties = [template["properties"]] + [definition[1] for definition in extra_properties]

    template["required"] = merge_required(all_required)
    template["properties"] = merge_properties(all_properties)
    template["system_properties"] = get_system_properties()
    return template


def enrich_workspace_template(template) -> dict:
    """Adds to the provided template all UI and system properties
    Args:
        template: [Template to which UI and system properties are added].
    Returns:
        [Dict]: [Enriched template with all required and system properties added]
    """
    workspace_default_properties = read_schema('workspace.json')
    azure_ad_properties = read_schema('azuread.json')
    return enrich_template(template, [workspace_default_properties, azure_ad_properties])


def enrich_workspace_service_template(template) -> dict:
    """Adds to the provided template all UI and system properties
    Args:
        template: [Template to which UI and system properties are added].
    Returns:
        [Dict]: [Enriched template with all required and system properties added]
    """
    workspace_service_default_properties = read_schema('workspace_service.json')
    return enrich_template(template, [workspace_service_default_properties])


def enrich_user_resource_template(template):
    """Adds to the provided template all UI and system properties
    Args:
        template: [Template to which UI and system properties are added].
    Returns:
        [Dict]: [Enriched template with all required and system properties added]
    """
    user_resource_default_properties = read_schema('user_resource.json')
    return enrich_template(template, [user_resource_default_properties])
