from typing import Dict, Any, List, Optional

from pydantic import Field

from models.domain.azuretremodel import AzureTREModel
from models.domain.resource import ResourceType


class Property(AzureTREModel):
    type: str = Field(title="Property type")
    title: str = Field("", title="Property description")
    description: str = Field("", title="Property description")
    default: Any = Field(None, title="Default value for the property")
    enum: Optional[List[str]] = Field(None, title="Enum values")
    const: Optional[Any] = Field(None, title="Constant value")
    multipleOf: Optional[float] = Field(None, title="Multiple of")
    maximum: Optional[float] = Field(None, title="Maximum value")
    exclusiveMaximum: Optional[float] = Field(None, title="Exclusive maximum value")
    minimum: Optional[float] = Field(None, title="Minimum value")
    exclusiveMinimum: Optional[float] = Field(None, title="Exclusive minimum value")
    maxLength: Optional[int] = Field(None, title="Maximum length")
    minLength: Optional[int] = Field(None, title="Minimum length")
    pattern: Optional[str] = Field(None, title="Pattern")


class ResourceTemplate(AzureTREModel):
    id: str
    name: str = Field(title="Unique template name")
    description: str = Field(title="Template description")
    version: str = Field(title="Template version")
    resourceType: ResourceType = Field(title="Type of resource this template is for (workspace/service)")
    current: bool = Field(title="Is this the current version of this template")
    type: str = "object"
    required: List[str] = Field(title="List of properties which must be provided")
    properties: Dict[str, Property] = Field(title="Template properties")
