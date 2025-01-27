terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
    databricks = {
      source = "databricks/databricks"
    }
    external = {
      source = "hashicorp/external"
    }
    random = {
      source = "hashicorp/random"
    }
  }
}
