variable "email" {
  description = "The email address of teh user."
  type        = string
}

variable "username" {
  description = "Name of the user. Same az email without dots, and camel cased."
  type        = string
}

variable "user_group_prefix" {
  description = "Prefix for grouping users in naming standards."
  type        = string
}

variable "dbx_admin_group_name" {
  description = "The name of the Databricks administrator group."
  type        = string
}

variable "admin_flag" {
  description = "Boolean flag indicating if the environment is being created for a DBX admin."
  type        = bool
}

variable "user_group_suffix" {
  description = "Suffix for grouping users in naming standards."
  type        = string
}

variable "azure-subscription-id" {
  description = "The Azure subscription where the resources are created."
  type        = string
  sensitive   = true
}

variable "dbx-account-id" {
  description = "ID of the Databricks Account."
  type        = string
  sensitive   = true
}

variable "dbx-metastore-id" {
  description = "Metastore ID for the central internal development Unity Catalog."
  type        = string
}

variable "create-azure-resource-group" {
  description = "Boolean flag indicating if Azure resource group need to be created and managed."
  type        = bool
  default     = true
}

# Valid values are available at https://github.com/claranet/terraform-azurerm-regions/blob/master/REGIONS.md
variable "azure-region" {
  description = "The Azure region where resources are created."
  type        = string
}

variable "dbx-sku" {
  description = "SKU type of Databricks Workspace - ['standard', 'premium', 'trial']."
  type        = string
  default     = "premium"
}

variable "azure_storage_account_replication_type" {
  description = "The replication type of Azure storage. - 'LRS', 'ZRS', 'GRS', 'RA-GRS', 'GZRS', 'RA-GZRS'"
  type        = string
  default     = "LRS"
}
