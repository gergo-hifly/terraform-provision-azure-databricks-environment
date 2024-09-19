# Every user have their personal storage account

resource "random_string" "storage_account" {
  length  = 24
  lower   = true
  upper   = false
  special = false
  numeric = false
}

resource "azurerm_storage_account" "personal" {
  name                      = lower(random_string.storage_account.id)
  resource_group_name       = azurerm_resource_group.dbx_environment.name
  location                  = azurerm_resource_group.dbx_environment.location
  account_tier              = "Standard"
  account_replication_type  = var.azure_storage_account_replication_type
  account_kind              = "StorageV2"
  is_hns_enabled            = true
  tags                      = local.common_tags
}


# The personal Catalog has it's own storage container within the personal storage account.

resource "azurerm_storage_container" "personal_unity" {
  name                  = "personalunitycatalogcontainer"
  storage_account_name  = azurerm_storage_account.personal.name
  container_access_type = "private"
}


# Using Databricks Access Connector to give access for DBX to the personal storage
# Note: one access connector for every user.

resource "azurerm_databricks_access_connector" "personal_unity" {
  name                = "${azurerm_resource_group.dbx_environment.name}-ac-${random_string.storage_account.id}"
  resource_group_name = azurerm_resource_group.dbx_environment.name
  location            = azurerm_resource_group.dbx_environment.location
  tags                = local.common_tags
  identity {
    type = "SystemAssigned"
  }
}


# DBX needs to have Storage Blob Data Contributor role on the storage. Assigning it.

resource "azurerm_role_assignment" "databricks_connector_role_assignment" {
  scope                = azurerm_storage_account.personal.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.personal_unity.identity[0].principal_id
}
