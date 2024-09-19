import json
import re
import sys
import os
from python_code.constants import TemplateTag, Prompt, Message
import python_code.config as conf


def validate_email(email: str) -> bool:
    """Validate value against email pattern specified in 'config.email_pattern'."""

    return re.match(conf.EMAIL_PATTERN, email) is not None


def get_email() -> str:
    """Prompt for user input to get the email address of the user. Validate if the input is an email address.
    Quit if not valid."""

    email = input(Prompt.ENTER_EMAIL.value)

    if not validate_email(email):
        print(Message.INVALID_EMAIL.value)
        sys.exit()

    return email


def get_proposed_username(email: str) -> str:
    """Propose a username by taking the local part of the email address, splitting it up on
    'config.username_split_separator', capitalizing every split, and joining bac together.
    I.e.: for 'john.doe.jr@foo.bar', it will propose 'JohnDoeJr'."""

    email = email.replace('-', '.')     # In some special case '-' is also a separator.
    username_splits = email.split('@')[0].split(conf.USERNAME_SPLIT_SEPARATOR)

    capitalized_splits = [chunk.title() for chunk in username_splits]

    return ''.join(capitalized_splits)


def get_variable_value_based_on_suggestion(proposed_value: str, accept_prompt: str, input_prompt: str) -> str:
    """Prompts the user to either accept or reject a proposed value.
    If the user rejects, then it prompts for an input value."""

    proposed_value_accepted = input(accept_prompt)

    if proposed_value_accepted in conf.ACCEPT_STRINGS:
        value = proposed_value
    else:
        value = input(input_prompt)

    return value


def accept_user_config(config: dict[str, str]):
    """Prints the final configuration values that would be used for creating the tfvars file.
    The user can either:
        * accept - in which case the configuration gets created
        * or reject - in which case a 'try again' message is printed and the script exits."""

    print(Prompt.ACCEPT_USER_CONFIG_VALUES.value.format(
        config=config,
        resource_group=config[TemplateTag.PREFIX.value] +
                       config[TemplateTag.USERNAME.value] +
                       config[TemplateTag.SUFFIX.value],
        az_region=config[TemplateTag.AZ_REGION.value]))
    proposed_config = input(Prompt.ACCEPT_PROPOSED_CONFIG.value)

    if proposed_config not in conf.ACCEPT_STRINGS:
        print(Message.TRY_AGAIN.value)
        sys.exit()


def get_user_config_values(email: str = None) -> dict[str, str]:

    config = {}

    if not email:
        email = get_email()

    config[TemplateTag.EMAIL.value] = email

    # Need to set separately because the proposed value is calculated.
    proposed_username = get_proposed_username(config[TemplateTag.EMAIL.value])
    config[TemplateTag.USERNAME.value] = get_variable_value_based_on_suggestion(
        proposed_value=proposed_username,
        accept_prompt=Prompt.ACCEPT_PROPOSED_VALUE.value.format(
            variable=TemplateTag.USERNAME.value, proposal=proposed_username
        ),
        input_prompt=Prompt.ENTER_DESIRED_VALUE.value.format(variable=TemplateTag.USERNAME.value)
    )

    # Loop through and the required user config values that have defaults.
    for tag in [TemplateTag.PREFIX, TemplateTag.SUFFIX, TemplateTag.AZ_REGION, TemplateTag.DBX_ADMIN_GROUP_NAME,
                TemplateTag.ADMIN_FLAG]:

        config[tag.value] = get_variable_value_based_on_suggestion(
            proposed_value=conf.DEFAULT_VARIABLE_VALUES[tag],
            accept_prompt=Prompt.ACCEPT_PROPOSED_VALUE.value.format(
                variable=tag.value, proposal=conf.DEFAULT_VARIABLE_VALUES[tag]
            ),
            input_prompt=Prompt.ENTER_DESIRED_VALUE.value.format(variable=tag.value)
        )

    accept_user_config(config)

    return config


def read_tfvars_template(terraform_tfvars_template_file: str) -> str:

    with open(terraform_tfvars_template_file, 'r') as file:
        template = file.read()

    return template


def get_admin_config(admin_config_file: str) -> dict[str, str]:

    with open(admin_config_file, 'r') as file:
        config_file = file.read()

    return json.loads(config_file)


def replace_values_in_template(tfvars_template: str, config: dict[str, str]) -> str:

    for tag in TemplateTag:
        tfvars_template = tfvars_template.replace(tag.value, config[tag.value])

    return tfvars_template


def save_tfvars(tfvars_content: str, tfvars_file: str) -> None:

    try:
        os.makedirs(os.path.dirname(tfvars_file), exist_ok=False)
    except FileExistsError:
        print(Message.FOLDER_ALREADY_EXISTS.value.format(folder=os.path.dirname(tfvars_file)))
        sys.exit()

    with open(tfvars_file, "w") as f:
        f.write(tfvars_content)


def print_and_save_terraform_commands(file: str, az_subscription: str, environment: str):

    apply_command = conf.APPLY_COMMAND_TEMPLATE.format(
        az_subscription=az_subscription, environment=environment
    )
    destroy_command = conf.DESTROY_COMMAND_TEMPLATE.format(
        az_subscription=az_subscription, environment=environment
    )

    print(Message.TERRAFORM_COMMAND.value + "\n" + apply_command)

    with open(file, "w") as f:
        f.write(f"{apply_command}\n{destroy_command}")


if __name__ == "__main__":

    config = get_user_config_values() | get_admin_config(conf.ADMIN_CONFIG_FILE)
    env_name = config[TemplateTag.PREFIX.value] + config[TemplateTag.USERNAME.value] + config[TemplateTag.SUFFIX.value]
    az_subscription = config[TemplateTag.AZ_SUBSCRIPTION_ID.value]

    tfvars_template = read_tfvars_template(conf.TERRAFORM_TFVARS_TEMPLATE_FILE)
    tfvars_content = replace_values_in_template(tfvars_template, config)
    tfvars_file = conf.TERRAFORM_TFVARS_FILE.format(
        az_subscription=az_subscription, environment=env_name
    )

    commands_file = conf.COMMANDS_FILENAME.format(
        az_subscription=az_subscription, environment=env_name
    )

    save_tfvars(tfvars_content, tfvars_file)

    print(Message.SUCCESS.value.format(tfvars_file=tfvars_file))

    print_and_save_terraform_commands(commands_file, az_subscription, env_name)
