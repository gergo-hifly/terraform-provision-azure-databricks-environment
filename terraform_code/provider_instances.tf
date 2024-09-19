provider "azurerm" {
  features {}
  subscription_id = var.azure-subscription-id
}


provider "databricks" {
  alias      = "account"
  host       = "https://accounts.azuredatabricks.net"
  account_id = var.dbx-account-id
}

provider "databricks" {
  alias = "workspace"
  host  = azurerm_databricks_workspace.personal.workspace_url
}
