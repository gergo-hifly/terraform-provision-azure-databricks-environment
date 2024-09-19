""" This file contains constant values used in the code.

Note: It might not be intuitive to use Enum for storing Tags, Prompts, and Messages, however, it provides the desired functionality:
   * Enum values cannot be changed at runtime, so it makes them truly constant.
   * Object of an Enum class cannot be instantiated, therefor it behaves like a singleton.

Since I don't see any drawbacks, I am using them for this purpose.
"""

from enum import Enum


class TemplateTag(Enum):
    """Tags to be replaced by the script in the template file."""

    EMAIL = "<EMAIL>"
    USERNAME = "<USERNAME>"
    PREFIX = "<PREFIX>"
    SUFFIX = "<SUFFIX>"
    AZ_REGION = "<AZ_REGION>"
    DBX_ADMIN_GROUP_NAME = "<DBX_ADMIN_GROUP_NAME>"
    ADMIN_FLAG = "<ADMIN_FLAG>"
    AZ_SUBSCRIPTION_ID = "<AZ_SUBSCRIPTION_ID>"
    DBX_ACCOUNT_ID = "<DBX_ACCOUNT_ID>"
    DBX_METASTORE_ID = "<DBX_METASTORE_ID>"


class Prompt(Enum):
    """Prompts used by the script."""

    ENTER_EMAIL = "Please enter the email address: "
    ACCEPT_PROPOSED_VALUE = "Proposed {variable}: '{proposal}'. Do you accept? [Y|N] "
    ACCEPT_DEFAULT_VALUE = "Do you want to use the default: '{proposal}' {variable}? [Y|N] "
    ENTER_DESIRED_VALUE = "Please enter the desired {variable}: "
    ACCEPT_PROPOSED_CONFIG = "\nDo you accept the configuration? [Y|N]: "
    ACCEPT_USER_CONFIG_VALUES = (
        "\nThe following configuration will be used:"
        "\n\t{config}"
        "\nResource group will be named: '{resource_group}'"
        "\nAll resources will be in region: '{az_region}'"
    )


class Message(Enum):
    """Messages output by the script."""

    INVALID_EMAIL = "Invalid email address provided. Quiting.."
    TERRAFORM_COMMAND = "\nTo create the environment run the following terraform command:"
    TRY_AGAIN = "Try again!"
    FOLDER_ALREADY_EXISTS = "\n'{folder}/' folder already exists. Overwriting is prohibited!"
    SUCCESS = "\n'{tfvars_file}' file saved.\nSUCCESS!"
