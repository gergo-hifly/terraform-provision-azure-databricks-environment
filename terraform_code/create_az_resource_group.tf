# Need a main resource group for all the resources of an environment.
# This way it can be easily managed, monitored, or dropped
#
# Note:
# Databricks creates its own managed resource group (with a "-DBX" ending in it's name).
# When the Databricks instance is deleted, it automatically deletes the managed resource group.

resource "azurerm_resource_group" "dbx_environment" {
  name        = "${var.user_group_prefix}${var.username}${var.user_group_suffix}"
  location    = var.azure-region
  tags        = local.common_tags
}

resource "azurerm_role_assignment" "owner" {
  depends_on = [azurerm_resource_group.dbx_environment, data.azuread_user.az_user]
  scope                = azurerm_resource_group.dbx_environment.id
  role_definition_name = "Owner"
  principal_id         =  data.azuread_user.az_user.id
}
