from python_code.constants import TemplateTag

DEFAULT_VARIABLE_VALUES = {
    TemplateTag.PREFIX: "INT-DP-DEV-",
    TemplateTag.SUFFIX: "-Personal",
    TemplateTag.AZ_REGION: "westeurope",
    TemplateTag.DBX_ADMIN_GROUP_NAME: "dbx-metastore-admins",
    TemplateTag.ADMIN_FLAG: "false"
}

TERRAFORM_TFVARS_TEMPLATE_FILE = './terraform_code/terraform.tfvars.template'
TERRAFORM_TFVARS_FILE = "./terraform_states/{az_subscription}/{environment}/terraform.tfvars"

ADMIN_CONFIG_FILE = './config/admin_config.json'
COMMANDS_FILENAME = "./terraform_states/{az_subscription}/{environment}/terraform_commands.txt"

EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
USERNAME_SPLIT_SEPARATOR = '.'
ACCEPT_STRINGS = ["Y", "y", "Yes", "yes", ""]

APPLY_COMMAND_TEMPLATE = ('terraform -chdir="./terraform_code" apply '
                          '-var-file="../terraform_states/{az_subscription}/{environment}/terraform.tfvars" '
                          '-state="../terraform_states/{az_subscription}/{environment}/terraform.tfstate"')

DESTROY_COMMAND_TEMPLATE = ('terraform -chdir="./terraform_code" destroy '
                            '-var-file="../terraform_states/{az_subscription}/{environment}/terraform.tfvars" '
                            '-state="../terraform_states/{az_subscription}/{environment}/terraform.tfstate"')
