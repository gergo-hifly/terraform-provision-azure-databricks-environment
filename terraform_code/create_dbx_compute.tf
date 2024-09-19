############################
# CREATE SINGLE USER CLUSTER
############################

resource "databricks_cluster" "single_user" {
  depends_on              = [azurerm_databricks_workspace.personal]
  provider                = databricks.workspace
  count                   = 1
  cluster_name            = "(Default) Single Node Cluster"
  single_user_name        = var.email
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 60
  data_security_mode      = "SINGLE_USER"

  spark_conf = {
    "spark.databricks.cluster.profile"  : "singleNode"
    "spark.master"                      : "local[*]"
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }
}

resource "databricks_permissions" "cluster_usage" {
  depends_on  = [databricks_cluster.single_user]
  count = var.admin_flag ? 0 : 1
  provider    = databricks.workspace
  cluster_id  = databricks_cluster.single_user[0].id

  access_control {
    user_name         = data.databricks_user.account_user.user_name
    permission_level  = "CAN_MANAGE"
  }
}


###############################
# Create Serverless Warehouse #
###############################

resource "databricks_sql_endpoint" "personal" {
  depends_on                = [databricks_cluster.single_user]
  provider                  = databricks.workspace
  name                      = "Serverless Warehouse (2X-Small)"
  cluster_size              = "2X-Small"
  max_num_clusters          = 1
  enable_serverless_compute = true
  auto_stop_mins            = 5

  tags {
    custom_tags {
      key   = "owner"
      value = data.databricks_user.account_user.user_name
    }
  }
}

resource "databricks_permissions" "sql_endpoint" {
  depends_on      = [databricks_sql_endpoint.personal]
  count = var.admin_flag ? 0 : 1
  provider        = databricks.workspace
  sql_endpoint_id = databricks_sql_endpoint.personal.id

  access_control {
    user_name         = data.databricks_user.account_user.user_name
    permission_level  = "CAN_MANAGE"
  }
}
