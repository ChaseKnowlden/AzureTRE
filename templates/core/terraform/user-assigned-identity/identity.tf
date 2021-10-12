resource "azurerm_user_assigned_identity" "id" {
  resource_group_name = var.resource_group_name
  location            = var.location

  name = "id-api-${var.tre_id}"

  lifecycle { ignore_changes = [tags] }
}

resource "azurerm_role_assignment" "acrpull_role" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.id.principal_id
}

resource "azurerm_role_assignment" "servicebus_sender" {
  scope                = var.servicebus_namespace.id
  role_definition_name = "Azure Service Bus Data Sender"
  principal_id         = azurerm_user_assigned_identity.id.principal_id
}

resource "azurerm_role_assignment" "servicebus_receiver" {
  scope                = var.servicebus_namespace.id
  role_definition_name = "Azure Service Bus Data Receiver"
  principal_id         = azurerm_user_assigned_identity.id.principal_id
}

resource "azurerm_role_assignment" "cosmos_contributor" {
  scope                = var.cosmos_id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.id.principal_id
}
