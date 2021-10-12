import uuid
from typing import List, Union

from azure.cosmos import CosmosClient
from pydantic import parse_obj_as

from core import config
from db.errors import DuplicateEntity, EntityDoesNotExist, EntityVersionExist
from db.repositories.base import BaseRepository
from models.domain.resource import ResourceType
from models.domain.resource_template import ResourceTemplate
from models.domain.user_resource_template import UserResourceTemplate
from models.schemas.resource_template import ResourceTemplateInCreate, ResourceTemplateInformation
from services.schema_service import enrich_workspace_template, enrich_workspace_service_template, enrich_user_resource_template


class ResourceTemplateRepository(BaseRepository):
    def __init__(self, client: CosmosClient):
        super().__init__(client, config.STATE_STORE_RESOURCE_TEMPLATES_CONTAINER)

    @staticmethod
    def _template_by_name_query(name: str, resource_type: ResourceType) -> str:
        return f'SELECT * FROM c WHERE c.resourceType = "{resource_type}" AND c.name = "{name}"'

    @staticmethod
    def enrich_template(template: ResourceTemplate) -> dict:
        if template.resourceType == ResourceType.Workspace:
            return enrich_workspace_template(template)
        elif template.resourceType == ResourceType.WorkspaceService:
            return enrich_workspace_service_template(template)
        else:
            return enrich_user_resource_template(template)

    def get_templates_information(self, resource_type: ResourceType, parent_service_name: str = "") -> List[ResourceTemplateInformation]:
        """
        Returns name/description for all current resource_type templates
        """
        query = f'SELECT c.name, c.title, c.description FROM c WHERE c.resourceType = "{resource_type}" AND c.current = true'
        if resource_type == ResourceType.UserResource:
            query += f' AND c.parentWorkspaceService = "{parent_service_name}"'
        template_infos = self.query(query=query)
        return [parse_obj_as(ResourceTemplateInformation, info) for info in template_infos]

    def get_current_template(self, template_name: str, resource_type: ResourceType, parent_service_name: str = "") -> Union[ResourceTemplate, UserResourceTemplate]:
        """
        Returns full template for the current version of the 'template_name' template
        """
        query = self._template_by_name_query(template_name, resource_type) + ' AND c.current = true'
        if resource_type == ResourceType.UserResource:
            query += f' AND c.parentWorkspaceService = "{parent_service_name}"'
        templates = self.query(query=query)
        if len(templates) == 0:
            raise EntityDoesNotExist
        if len(templates) > 1:
            raise DuplicateEntity
        if resource_type == ResourceType.UserResource:
            return parse_obj_as(UserResourceTemplate, templates[0])
        else:
            return parse_obj_as(ResourceTemplate, templates[0])

    def get_template_by_name_and_version(self, name: str, version: str, resource_type: ResourceType, parent_service_name: str = "") -> Union[ResourceTemplate, UserResourceTemplate]:
        """
        Returns full template for the 'resource_type' template defined by 'template_name' and 'version'
        """
        query = self._template_by_name_query(name, resource_type) + f' AND c.version = "{version}"'
        if resource_type == ResourceType.UserResource:
            query += f' AND c.parentWorkspaceService = "{parent_service_name}"'
        templates = self.query(query=query)
        if len(templates) != 1:
            raise EntityDoesNotExist
        if resource_type == ResourceType.UserResource:
            return parse_obj_as(UserResourceTemplate, templates[0])
        else:
            return parse_obj_as(ResourceTemplate, templates[0])

    def create_template(self, template_input: ResourceTemplateInCreate, resource_type: ResourceType, parent_service_name: str = "") -> Union[ResourceTemplate, UserResourceTemplate]:
        """
        creates a template based on the input (workspace and workspace-services template)
        """
        template = {
            "id": str(uuid.uuid4()),
            "name": template_input.name,
            "title": template_input.json_schema["title"],
            "description": template_input.json_schema["description"],
            "version": template_input.version,
            "resourceType": resource_type,
            "current": template_input.current,
            "required": template_input.json_schema["required"],
            "properties": template_input.json_schema["properties"],
        }

        if resource_type == ResourceType.UserResource:
            template["parentWorkspaceService"] = parent_service_name
            template = parse_obj_as(UserResourceTemplate, template)
        else:
            template = parse_obj_as(ResourceTemplate, template)

        self.save_item(template)
        return template

    def create_and_validate_template(self, template_input: ResourceTemplateInCreate, resource_type: ResourceType, workspace_service_template_name: str = "") -> dict:
        """
        Validates that we don't have a version conflict
        Updates the current version for the template
        Saves to the database and returns the enriched template
        """
        try:
            template = self.get_template_by_name_and_version(template_input.name, template_input.version, resource_type, workspace_service_template_name)
            if template:
                raise EntityVersionExist
        except EntityDoesNotExist:
            try:
                template = self.get_current_template(template_input.name, resource_type, workspace_service_template_name)
                if template_input.current:
                    template.current = False
                    self.update_item(template)
            except EntityDoesNotExist:
                # first registration
                template_input.current = True  # For first time registration, template is always marked current
            created_template = self.create_template(template_input, resource_type, workspace_service_template_name)
            return self.enrich_template(created_template)
