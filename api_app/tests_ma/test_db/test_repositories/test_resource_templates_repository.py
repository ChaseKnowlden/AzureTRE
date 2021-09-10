import pytest
from mock import patch

from db.repositories.resource_templates import ResourceTemplateRepository
from db.errors import DuplicateEntity, EntityDoesNotExist
from models.domain.resource import ResourceType
from models.domain.resource_template import ResourceTemplate
from models.domain.user_resource_template import UserResourceTemplate


@pytest.fixture
def resource_template_repo():
    with patch('azure.cosmos.CosmosClient') as cosmos_client_mock:
        yield ResourceTemplateRepository(cosmos_client_mock)


def sample_resource_template(name: str, version: str = "1.0", resource_type: ResourceType = ResourceType.Workspace) -> ResourceTemplate:
    return ResourceTemplate(
        id="a7a7a7bd-7f4e-4a4e-b970-dc86a6b31dfb",
        name=name,
        description="test",
        version=version,
        resourceType=resource_type,
        current=False,
        properties={},
        required=[],
    )


def sample_resource_template_as_dict(name: str, version: str = "1.0", resource_type: ResourceType = ResourceType.Workspace) -> dict:
    return sample_resource_template(name, version, resource_type).dict()


def sample_user_resource_template_as_dict(name: str, version: str = "1.0") -> dict:
    template = UserResourceTemplate(id="123", name=name, description="", version=version, current=True, required=[], properties={}, parentWorkspaceService="parent_service")
    return template.dict()


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_by_name_and_version_queries_db(query_mock, resource_template_repo):
    expected_query = 'SELECT * FROM c WHERE c.resourceType = "workspace" AND c.name = "test" AND c.version = "1.0"'
    query_mock.return_value = [sample_resource_template_as_dict(name="test", version="1.0")]

    resource_template_repo.get_template_by_name_and_version(name="test", version="1.0", resource_type=ResourceType.Workspace)

    query_mock.assert_called_once_with(query=expected_query)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_user_resource_template_by_name_and_version_queries_db(query_mock, resource_template_repo):
    expected_query = 'SELECT * FROM c WHERE c.resourceType = "user-resource" AND c.name = "test" AND c.version = "1.0" AND c.parentWorkspaceService = "parent_service"'
    query_mock.return_value = [sample_user_resource_template_as_dict(name="test", version="1.0")]

    resource_template_repo.get_template_by_name_and_version(name="test", version="1.0", resource_type=ResourceType.UserResource, parent_service_name="parent_service")

    query_mock.assert_called_once_with(query=expected_query)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_by_name_and_version_returns_matching_template(query_mock, resource_template_repo):
    template_name = "test"
    template_version = "1.0"
    workspace_templates_in_db = [sample_resource_template_as_dict(name=template_name, version=template_version)]
    query_mock.return_value = workspace_templates_in_db

    template = resource_template_repo.get_template_by_name_and_version(name=template_name, version=template_version, resource_type=ResourceType.Workspace)

    assert template.name == template_name


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_by_name_and_version_raises_entity_does_not_exist_if_no_template_found(query_mock, resource_template_repo):
    template_name = "test"
    template_version = "1.0"
    query_mock.return_value = []

    with pytest.raises(EntityDoesNotExist):
        resource_template_repo.get_template_by_name_and_version(name=template_name, version=template_version, resource_type=ResourceType.Workspace)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_by_name_queries_db(query_mock, resource_template_repo):
    template_name = "template1"
    expected_query = 'SELECT * FROM c WHERE c.resourceType = "workspace" AND c.name = "template1" AND c.current = true'
    query_mock.return_value = [sample_resource_template_as_dict(name="test")]

    resource_template_repo.get_current_template(template_name=template_name, resource_type=ResourceType.Workspace)

    query_mock.assert_called_once_with(query=expected_query)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_by_name_returns_matching_template(query_mock, resource_template_repo):
    template_name = "template1"
    query_mock.return_value = [sample_resource_template_as_dict(name=template_name)]

    template = resource_template_repo.get_current_template(template_name=template_name, resource_type=ResourceType.Workspace)

    assert template.name == template_name


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_by_name_raises_entity_does_not_exist_if_no_template_found(query_mock, resource_template_repo):
    query_mock.return_value = []

    with pytest.raises(EntityDoesNotExist):
        resource_template_repo.get_current_template(template_name="template1", resource_type=ResourceType.Workspace)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_user_resource_template_queries_db(query_mock, resource_template_repo):
    template_name = "template1"
    parent_template_name = "parent_template1"
    expected_query = 'SELECT * FROM c WHERE c.resourceType = "user-resource" AND c.name = "template1" AND c.current = true AND c.parentWorkspaceService = "parent_template1"'
    query_mock.return_value = [sample_resource_template_as_dict(name=template_name)]

    resource_template_repo.get_current_template(template_name, ResourceType.UserResource, parent_template_name)

    query_mock.assert_called_once_with(query=expected_query)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_user_resource_template_returns_matching_template(query_mock, resource_template_repo):
    template_name = "template1"
    parent_template_name = "parent_template1"
    query_mock.return_value = [sample_resource_template_as_dict(name=template_name)]

    template = resource_template_repo.get_current_template(template_name, ResourceType.UserResource, parent_template_name)

    assert template.name == template_name


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_user_resource_template_raises_entity_does_not_exist_if_no_template_found(query_mock, resource_template_repo):
    query_mock.return_value = []

    with pytest.raises(EntityDoesNotExist):
        resource_template_repo.get_current_template("template1", ResourceType.UserResource, "parent_template1")


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_current_user_resource_template_raises_duplicate_entity_if_multiple_current_found(query_mock, resource_template_repo):
    template_name = "template1"
    parent_template_name = "parent_template1"
    query_mock.return_value = [sample_resource_template_as_dict(name=template_name), sample_resource_template_as_dict(name=template_name)]

    with pytest.raises(DuplicateEntity):
        resource_template_repo.get_current_template(template_name, ResourceType.UserResource, parent_template_name)


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_templates_information_returns_unique_template_names(query_mock, resource_template_repo):
    query_mock.return_value = [
        {"name": "template1", "description": "description1"},
        {"name": "template2", "description": "description2"}
    ]

    result = resource_template_repo.get_templates_information(ResourceType.Workspace)

    assert len(result) == 2
    assert result[0].name == "template1"
    assert result[1].name == "template2"


@patch('db.repositories.resource_templates.ResourceTemplateRepository.save_item')
@patch('uuid.uuid4')
def test_create_workspace_template_item_calls_create_item_with_the_correct_parameters(uuid_mock, save_item_mock, resource_template_repo, input_workspace_template):
    uuid_mock.return_value = "1234"

    returned_template = resource_template_repo.create_template(input_workspace_template, ResourceType.Workspace)

    expected_resource_template = ResourceTemplate(
        id="1234",
        name=input_workspace_template.name,
        description=input_workspace_template.json_schema["description"],
        version=input_workspace_template.version,
        resourceType=ResourceType.Workspace,
        properties=input_workspace_template.json_schema["properties"],
        required=input_workspace_template.json_schema["required"],
        current=input_workspace_template.current
    )
    save_item_mock.assert_called_once_with(expected_resource_template)
    assert expected_resource_template == returned_template


@patch('db.repositories.resource_templates.ResourceTemplateRepository.save_item')
@patch('uuid.uuid4')
def test_create_user_resource_template_item_calls_create_item_with_the_correct_parameters(uuid_mock, save_item_mock, resource_template_repo, input_user_resource_template):
    uuid_mock.return_value = "1234"

    returned_template = resource_template_repo.create_template(input_user_resource_template, ResourceType.UserResource, "parent_service_template_name")

    expected_resource_template = UserResourceTemplate(
        id="1234",
        name=input_user_resource_template.name,
        description=input_user_resource_template.json_schema["description"],
        version=input_user_resource_template.version,
        resourceType=ResourceType.UserResource,
        properties=input_user_resource_template.json_schema["properties"],
        required=input_user_resource_template.json_schema["required"],
        current=input_user_resource_template.current,
        parentWorkspaceService="parent_service_template_name"
    )
    save_item_mock.assert_called_once_with(expected_resource_template)
    assert expected_resource_template == returned_template


@patch('db.repositories.resource_templates.ResourceTemplateRepository.save_item')
@patch('uuid.uuid4')
def test_create_item_created_with_the_expected_type(uuid_mock, save_item_mock, resource_template_repo, input_workspace_template):
    uuid_mock.return_value = "1234"
    expected_type = ResourceType.WorkspaceService
    returned_template = resource_template_repo.create_template(input_workspace_template, expected_type)
    expected_resource_template = ResourceTemplate(
        id="1234",
        name=input_workspace_template.name,
        description=input_workspace_template.json_schema["description"],
        version=input_workspace_template.version,
        resourceType=expected_type,
        properties=input_workspace_template.json_schema["properties"],
        required=input_workspace_template.json_schema["required"],
        current=input_workspace_template.current
    )
    save_item_mock.assert_called_once_with(expected_resource_template)
    assert expected_resource_template == returned_template


@patch('db.repositories.resource_templates.ResourceTemplateRepository.query')
def test_get_template_infos_for_user_resources_queries_db(query_mock, resource_template_repo):
    expected_query = 'SELECT c.name, c.description FROM c WHERE c.resourceType = "user-resource" AND c.current = true AND c.parentWorkspaceService = "parent_service"'
    query_mock.return_value = [sample_resource_template_as_dict(name="test", version="1.0", resource_type=ResourceType.UserResource)]

    resource_template_repo.get_templates_information(ResourceType.UserResource, parent_service_name="parent_service")

    query_mock.assert_called_once_with(query=expected_query)
