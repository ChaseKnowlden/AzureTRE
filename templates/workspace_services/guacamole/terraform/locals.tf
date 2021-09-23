locals {
  short_service_id             = substr(var.tre_resource_id, -4, -1)
  short_workspace_id           = substr(var.workspace_id, -4, -1)
  service_resource_name_suffix = "${var.tre_id}-ws-${local.short_workspace_id}-svc-${local.short_service_id}"
  webapp_name                  = "guacamole-${local.service_resource_name_suffix}"
  core_vnet                    = "vnet-${var.tre_id}"
  core_resource_group_name     = "rg-${var.tre_id}"
  aad_tenant_id                = data.azurerm_app_service.api_core.app_settings["AAD_TENANT_ID"]
  issuer                       = "https://login.microsoftonline.com/${local.aad_tenant_id}/v2.0"
  kv_url                       = "https://kv-${var.tre_id}-${local.short_workspace_id}-${local.short_service_id}.vault.azure.net"
  api_url                      = "https://api-${var.tre_id}.azurewebsites.net"
}
