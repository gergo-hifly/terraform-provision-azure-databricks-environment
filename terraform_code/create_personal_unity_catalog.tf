###
# It's time to set up the personal Catalog with personal space in the central internal development Metastore.
###

# In order to create external location in DBX we need to create a storage credential.

resource "databricks_storage_credential" "personal_unity" {
  name    = "${azurerm_resource_group.dbx_environment.name}-access-connector"
  comment = "Managed identity credential managed by TF"
  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.personal_unity.id
  }
}

# Creating the external location in DBX to enable the creation of the Catalog there.

resource "databricks_external_location" "personal_unity_ext" {
  depends_on      = [databricks_metastore_assignment.this]
  name            = "${azurerm_resource_group.dbx_environment.name}-ext-location"
  credential_name = databricks_storage_credential.personal_unity.id
  url             = format("abfss://%s@%s.dfs.core.windows.net",
                            azurerm_storage_container.personal_unity.name,
                            azurerm_storage_account.personal.name)
}

# Now everything is ready for the Catalog creation.
# It is an isolated catalog, other workspaces should not have access to it.

resource "databricks_catalog" "personal_catalog" {
  depends_on      = [databricks_external_location.personal_unity_ext]
  name            = replace(lower(azurerm_resource_group.dbx_environment.name), "-", "_")
  comment         = "This catalog is managed by Terraform"
  storage_root    = format("abfss://%s@%s.dfs.core.windows.net/",
                            azurerm_storage_container.personal_unity.name,
                            azurerm_storage_account.personal.name)
  isolation_mode  = "ISOLATED"
  properties = {
    purpose = "personal development"
  }
}

# Since the isolation is turned on, we need to bind the workspace to the catalog.

resource "databricks_workspace_binding" "this" {
  depends_on = [databricks_catalog.personal_catalog, azurerm_databricks_workspace.personal]
  securable_name = databricks_catalog.personal_catalog.name
  workspace_id   = azurerm_databricks_workspace.personal.workspace_id
}

# Need to grant privileges in order to be able to create the default schema

resource "databricks_grants" "personal_catalog_grants" {
  depends_on = [databricks_catalog.personal_catalog]
  catalog = databricks_catalog.personal_catalog.name
  grant {
    principal  = data.databricks_user.account_user.user_name
    privileges = ["ALL_PRIVILEGES"]
  }
  grant {
    principal  = data.external.me.result.name
    privileges = ["ALL_PRIVILEGES"]
  }
  grant {
    principal  = data.databricks_group.metastore-admins.display_name
    privileges = ["ALL_PRIVILEGES"]
  }
}

# Creating the default schema.

resource "databricks_schema" "default" {
  depends_on    = [databricks_grants.personal_catalog_grants]
  catalog_name  = databricks_catalog.personal_catalog.id
  name          = "Default"
  comment       = "This schema is managed by terraform"
  properties = {
    kind = "development"
  }
}


resource "databricks_grants" "default_schema_grants" {
  depends_on  = [databricks_schema.default]
  schema      = databricks_schema.default.id

  grant {
    principal  = data.databricks_user.account_user.user_name
    privileges = ["ALL_PRIVILEGES"]
  }
  grant {
    principal  = data.external.me.result.name
    privileges = ["ALL_PRIVILEGES"]
  }
  grant {
    principal  = data.databricks_group.metastore-admins.display_name
    privileges = ["ALL_PRIVILEGES"]
  }
}
