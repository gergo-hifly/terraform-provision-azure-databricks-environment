# Every user has access to their own Catalog under the central internal development Metastore.
# The DBX workspace needs to be assigned to the central Metastore

resource "databricks_metastore_assignment" "this" {
  metastore_id  = data.databricks_metastore.internal_dev.metastore_id
  workspace_id  = azurerm_databricks_workspace.personal.workspace_id
}
