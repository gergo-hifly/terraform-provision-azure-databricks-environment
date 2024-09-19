data "azurerm_client_config" "current" {}

data "external" "me" {
  program = ["az", "account", "show", "--query", "user"]
}

data "azuread_user" "az_user" {
  user_principal_name = var.email
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_metastore" "internal_dev" {
  metastore_id = var.dbx-metastore-id
  provider = databricks.account
}

data "databricks_user" "account_user" {
  provider      = databricks.account
  user_name     = var.email
}

data "databricks_group" "metastore-admins" {
  provider      = databricks.account
  display_name  = var.dbx_admin_group_name
}

locals {
  common_tags = {
    owner        = var.username
    department   = trimsuffix(var.user_group_prefix, "-")
    environment  = trimprefix(var.user_group_suffix, "-")
    client       = "Hifly"
    review_date  = formatdate("YYYY-MM-DD", timeadd(timestamp(), "4320h")) # About 6 months
  }
}
