# Every user have their own personal DBX workspace

resource "azurerm_databricks_workspace" "personal" {
  depends_on                  = [azurerm_resource_group.dbx_environment]
  name                        = azurerm_resource_group.dbx_environment.name
  resource_group_name         = azurerm_resource_group.dbx_environment.name
  location                    = var.azure-region
  sku                         = var.dbx-sku
  managed_resource_group_name = "${azurerm_resource_group.dbx_environment.name}-DBX"
  tags                        = local.common_tags
}

# Assigning the user to the DBX workspace

resource "databricks_mws_permission_assignment" "add_user" {
  depends_on    = [azurerm_databricks_workspace.personal]
  workspace_id  = azurerm_databricks_workspace.personal.workspace_id
  principal_id  = data.databricks_user.account_user.id
  permissions   = ["USER"]
  provider      = databricks.account
}

