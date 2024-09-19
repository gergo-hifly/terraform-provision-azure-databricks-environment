import unittest
import os
import json
import shutil, tempfile
from unittest.mock import patch
from io import StringIO

import python_code.create_configuration_for_user as code
import python_code.constants as enums
import python_code.config as conf


class ValidateEmail(unittest.TestCase):

    def test_valid(self):
        self.assertTrue(code.validate_email("a@b.c"))

    def test_invalid(self):
        self.assertFalse(code.validate_email("ab.c"))


class GetEmail(unittest.TestCase):

    @patch('builtins.input', side_effect=["email@email.email"])
    def test_accept_config(self, mock_input):
        """The input 'email@email.email' should be accepted, no exception raised, no error message printed."""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            code.get_email()
        self.assertEqual(fake_out.getvalue(), "")

    @patch('builtins.input', side_effect=["email"])
    def test_reject_config(self, mock_input):
        """The input 'email' should be rejected, exception should be raised and error message should be printed."""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit):
                code.get_email()
        self.assertEqual(fake_out.getvalue(), "Invalid email address provided. Quiting..\n")


class GetProposedUsername(unittest.TestCase):
    def test_function(self):
        """The local-part of the email address should be split on '.' character and all parts capitalized."""
        self.assertEqual(code.get_proposed_username("dp.test.01@hiflylabs.com"), "DpTest01")


class GetVariableValueBasedOnSuggestion(unittest.TestCase):

    @patch('builtins.input', side_effect=["Y", "value_entered"])
    def test_accept_proposal(self, mock_input):
        """When the user answers 'Y', the 'value_proposed' should be returned."""

        result = code.get_variable_value_based_on_suggestion("value_proposed", "", "")
        self.assertEqual(result, "value_proposed")

    @patch('builtins.input', side_effect=["N", "value_entered"])
    def test_reject_proposal(self, mock_input):
        """When the user answers 'N', the 'value_entered' should be returned."""

        result = code.get_variable_value_based_on_suggestion("value_proposed", "", "")
        self.assertEqual(result, "value_entered")


class AcceptUserConfig(unittest.TestCase):

    def setUp(self):
        self.config = {
            '<EMAIL>': 'email@email.email',
            '<USERNAME>': 'Email',
            '<PREFIX>': 'prefix_value',
            '<SUFFIX>': 'suffix_value',
            '<AZ_REGION>': 'az_region_value',
            '<AZ_SUBSCRIPTION_ID>': 'az_subscription_id_value',
            '<DBX_ACCOUNT_ID>': 'dbx_account_id_value',
            '<DBX_METASTORE_ID>': 'dbx_metastore_id_value'
        }

        self.expected_config_stdout = (
            "\nThe following configuration will be used:\n"
            "\t{'<EMAIL>': 'email@email.email', '<USERNAME>': 'Email', '<PREFIX>': 'prefix_value', "
            "'<SUFFIX>': 'suffix_value', '<AZ_REGION>': 'az_region_value', "
            "'<AZ_SUBSCRIPTION_ID>': 'az_subscription_id_value', '<DBX_ACCOUNT_ID>': 'dbx_account_id_value', "
            "'<DBX_METASTORE_ID>': 'dbx_metastore_id_value'}\n"
            "Resource group will be named: 'prefix_valueEmailsuffix_value'\n"
            "All resources will be in region: 'az_region_value'\n"
        )

    @patch('builtins.input', side_effect=["Y"])
    def test_accept_config(self, mock_input):
        """The configuration values need to be printed. When the user enters 'Y', no exception should be raised."""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            code.accept_user_config(self.config)
        self.assertEqual(fake_out.getvalue(), self.expected_config_stdout)

    @patch('builtins.input', side_effect=["N"])
    def test_reject_config(self, mock_input):
        """The configuration values need to be printed. When the user enters 'N', exception should be raised."""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit):
                code.accept_user_config(self.config)
        self.assertEqual(fake_out.getvalue(), self.expected_config_stdout + "Try again!\n")


class GetUserConfigValues(unittest.TestCase):

    @patch('builtins.input', side_effect=["Y", "Y", "Y", "Y", "Y", "Y", "Y"])
    def test_accept_all_proposals(self, mock_input):
        """Testing the case when the user accepts all proposed values.
        Configuration values need to be printed, and the proposed config values returned in a dict."""

        expected_result = {
            '<EMAIL>': 'email@email.email',
            '<USERNAME>': 'Email',
            '<PREFIX>': conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.PREFIX],
            '<SUFFIX>': conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.SUFFIX],
            '<AZ_REGION>': conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.AZ_REGION],
            '<DBX_ADMIN_GROUP_NAME>': conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.DBX_ADMIN_GROUP_NAME],
            '<ADMIN_FLAG>': conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.ADMIN_FLAG]
        }

        expected_config_stdout = (
            "\nThe following configuration will be used:\n\t{{'<EMAIL>': 'email@email.email', '<USERNAME>': 'Email', "
            "'<PREFIX>': '{prefix_value}', '<SUFFIX>': '{suffix_value}', '<AZ_REGION>': 'westeurope', "
            "'<DBX_ADMIN_GROUP_NAME>': 'dbx-metastore-admins', '<ADMIN_FLAG>': 'false'}}\n"
            "Resource group will be named: '{rg_value}'\n"
            "All resources will be in region: 'westeurope'\n"
        ).format(
            prefix_value=conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.PREFIX],
            suffix_value=conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.SUFFIX],
            rg_value=conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.PREFIX] + 'Email' + conf.DEFAULT_VARIABLE_VALUES[enums.TemplateTag.SUFFIX]
        )

        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = code.get_user_config_values("email@email.email")
            self.assertEqual(result, expected_result)
        self.assertEqual(fake_out.getvalue(), expected_config_stdout)


    @patch('builtins.input',
           side_effect=["email@email.email", "N", "username", "N", "prefix", "N", "suffix", "N", "az_region", "N", "dbx_admin_group_name", "N", "admin_flag", "Y"])
    def test_reject_all_proposals(self, mock_input):
        """Testing the case when the user rejects all proposed values and enters custom values.
        Configuration values need to be printed, and the entered config values returned in a dict."""

        expected_result = {
            '<EMAIL>': 'email@email.email',
            '<USERNAME>': 'username',
            '<PREFIX>': 'prefix',
            '<SUFFIX>': 'suffix',
            '<AZ_REGION>': 'az_region',
            '<DBX_ADMIN_GROUP_NAME>': 'dbx_admin_group_name',
            '<ADMIN_FLAG>': 'admin_flag'
        }

        expected_config_stdout = (
            "\nThe following configuration will be used:\n\t{'<EMAIL>': 'email@email.email', "
            "'<USERNAME>': 'username', '<PREFIX>': 'prefix', '<SUFFIX>': 'suffix', '<AZ_REGION>': 'az_region', "
            "'<DBX_ADMIN_GROUP_NAME>': 'dbx_admin_group_name', '<ADMIN_FLAG>': 'admin_flag'}\n"
            "Resource group will be named: 'prefixusernamesuffix'\n"
            "All resources will be in region: 'az_region'\n"
        )

        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = code.get_user_config_values()
            self.assertEqual(result, expected_result)
        self.assertEqual(fake_out.getvalue(), expected_config_stdout)


class FileManipulationTaskTests(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        self.terraform_tfvars_template_file_name = "terraform.tfvars.template"
        self.terraform_tfvars_template_file = os.path.join(self.test_dir, self.terraform_tfvars_template_file_name)
        self.terraform_tfvars_template_text = (
            'email                   = "<EMAIL>"\n'
            'username                = "<USERNAME>"\n'
            'user_group_prefix       = "<PREFIX>"\n'
            'user_group_suffix       = "<SUFFIX>"\n'
            'azure-region            = "<AZ_REGION>"\n'
            'dbx_admin_group_name    = "<DBX_ADMIN_GROUP_NAME>"\n'
            'admin_flag              = "<ADMIN_FLAG>"\n'
            '\n\n'
            'azure-subscription-id   = "<AZ_SUBSCRIPTION_ID>"\n'
            'dbx-account-id          = "<DBX_ACCOUNT_ID>"\n'
            'dbx-metastore-id        = "<DBX_METASTORE_ID>"'
        )
        with open(self.terraform_tfvars_template_file, 'w') as template:
            template.write(self.terraform_tfvars_template_text)

        self.admin_config_file_name = "admin_config.json"
        self.admin_config_file = os.path.join(self.test_dir, self.admin_config_file_name)
        self.admin_config_values = {
            '<AZ_SUBSCRIPTION_ID>': 'az_subscription_id',
            '<DBX_ACCOUNT_ID>': 'dbx_account_id',
            '<DBX_METASTORE_ID>': 'dbx_metastore_id'
        }
        self.admin_config_text = json.dumps(self.admin_config_values)
        with open(self.admin_config_file, 'w') as config:
            config.write(self.admin_config_text)

        self.user_config_values = {
            '<EMAIL>': 'email@email.email',
            '<USERNAME>': 'username',
            '<PREFIX>': 'prefix',
            '<SUFFIX>': 'suffix',
            '<AZ_REGION>': 'az_region',
            '<DBX_ADMIN_GROUP_NAME>': 'dbx-metastore-admins',
            '<ADMIN_FLAG>': 'false'
        }

        self.terraform_tfvars_created_text = (
            'email                   = "email@email.email"\n'
            'username                = "username"\n'
            'user_group_prefix       = "prefix"\n'
            'user_group_suffix       = "suffix"\n'
            'azure-region            = "az_region"\n'
            'dbx_admin_group_name    = "dbx-metastore-admins"\n'
            'admin_flag              = "false"\n'
            '\n\n'
            'azure-subscription-id   = "az_subscription_id"\n'
            'dbx-account-id          = "dbx_account_id"\n'
            'dbx-metastore-id        = "dbx_metastore_id"'
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_tfvars_template(self):
        """Testing the read of the template file."""

        result = code.read_tfvars_template(self.terraform_tfvars_template_file)
        self.assertEqual(result, self.terraform_tfvars_template_text)

    def test_get_admin_config(self):
        """Testing the read of the admin config file."""

        result = code.get_admin_config(self.admin_config_file)
        self.assertEqual(result, json.loads(self.admin_config_text))

    def test_replace_values_in_template(self):
        """Testing the replacement of tags in the config file."""

        result = code.replace_values_in_template(
            self.terraform_tfvars_template_text,
            self.user_config_values | self.admin_config_values
        )
        self.assertEqual(result, self.terraform_tfvars_created_text)

    def test_print_and_save_terraform_commands(self):
        """Testing if the correct command is in the output and in the commands file."""

        test_file = os.path.join(self.test_dir, "test_file.txt")

        expected_stdout = ('\nTo create the environment run the following terraform command:\n'
                          'terraform -chdir="./terraform_code" apply '
                          '-var-file="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfvars" '
                          '-state="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfstate"\n')

        with patch('sys.stdout', new=StringIO()) as fake_out:
            code.print_and_save_terraform_commands(test_file, az_subscription="SUBSCRIPTION", environment="EMAIL")
        self.assertEqual(fake_out.getvalue(), expected_stdout)

        expected_result_file_content = ('terraform -chdir="./terraform_code" apply '
                                        '-var-file="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfvars" '
                                        '-state="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfstate"\n'
                                        'terraform -chdir="./terraform_code" destroy '
                                        '-var-file="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfvars" '
                                        '-state="../terraform_states/SUBSCRIPTION/EMAIL/terraform.tfstate"')

        with open(test_file, 'r') as file:
            result_file_content = file.read()

        self.assertEqual(result_file_content, expected_result_file_content)


class SaveTfvars(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_name = "test_file.txt"

        self.content_to_save = "NEW CONTENT TO SAVE"
        self.existing_content = "SHOULD NOT BE OVERWRITTEN"

        self.non_existing_dir_name = "non_existing_dir"
        self.existing_dir_name = "existing_dir"

        self.non_existing_file = os.path.join(self.test_dir, self.non_existing_dir_name, self.file_name)
        self.existing_file = os.path.join(self.test_dir, self.existing_dir_name, self.file_name)

        os.makedirs(os.path.dirname(self.existing_file))
        with open(self.existing_file, 'w') as file:
            file.write(self.existing_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_tfvars_non_existing(self):
        """Non-existing configuration should be created."""

        code.save_tfvars(self.content_to_save, self.non_existing_file)

        with open(self.non_existing_file, 'r') as file:
            result_content = file.read()

        self.assertEqual(result_content, self.content_to_save)

    def test_save_tfvars_existing(self):
        """Existing configuration should be untouched."""

        expected_stdout = (f"\n'{os.path.join(self.test_dir, self.existing_dir_name)}/' folder already exists. "
                           f"Overwriting is prohibited!\n")

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit):
                code.save_tfvars(self.content_to_save, self.existing_file)
        self.assertEqual(fake_out.getvalue(), expected_stdout)

        with open(self.existing_file, 'r') as file:
            result_content = file.read()

        self.assertEqual(result_content, self.existing_content)


if __name__ == '__main__':
    unittest.main()
