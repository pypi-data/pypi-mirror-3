from django import forms
from django.utils.translation import ugettext as _

from djblets.siteconfig.forms import SiteSettingsForm
#from djblets.siteconfig.models import SiteConfiguration


#siteconfig = SiteConfiguration.objects.get_current()
#
#db_auth_database_engine_name = siteconfig.get("db_auth_database_engine_name", "sqlite")
#db_auth_database_name = siteconfig.get("db_auth_database_name")
#db_auth_username = siteconfig.get("db_auth_username")
#db_auth_password = siteconfig.get("db_auth_password")
#
#db_auth_account_field_name = siteconfig.get("db_auth_account_field_name")
#db_auth_passwd_field_name = siteconfig.get("db_auth_passwd_field_name")
#db_auth_email_field_name = siteconfig.get("db_auth_email_field_name")
#db_auth_table_name = siteconfig.get("db_auth_table_name")


class DatabaseAuthBackendSettingsForm(SiteSettingsForm):
    db_auth_database_engine_name = forms.CharField(
        label = _("Database engine name"),
        help_text = _("e.g. 'sqlite', 'postgres'"),
        required = True)

    db_auth_database_name = forms.CharField(
        label = _("Database name or database data file full path(SQLite)"),
        help_text = _("e.g. 'users', '/data/data.sqlite'"),
        required = True)

    db_auth_username = forms.CharField(
        label = _("Username"),
        help_text = _("use when connecting to server"),
        required = False)

    db_auth_password = forms.CharField(
        label = _("Password"),
        help_text = _("use when connecting to server"),
        required = False)


    db_auth_table_name = forms.CharField(
        label = _("Table name"),
        help_text = _("the 'xxx' in `SELECT password, email FROM xxx WHERE username = 'some_one'`"),
        required = True)

    db_auth_account_field_name = forms.CharField(
        label = _("Username/Account field name"),
        help_text = _("the 'xxx' in `SELECT password, email FROM users WHERE xxx = 'some_one'`"),
        required = True)

    db_auth_passwd_field_name = forms.CharField(
        label = _("Password field name"),
        help_text = _("the 'xxx' in `SELECT 'xxx', email FROM users WHERE username = 'some_one'`"),
        required = True)

    db_auth_email_field_name = forms.CharField(
        label = _("Email field name"),
        help_text = _("the 'xxx' in `SELECT password, xxx FROM users WHERE username = 'some_one'`."
                    "You should set this field if you want to usee E-Mail notification in ReviewBoard."),
        required = False)


    class Meta:
        title = _("Database Authorization Backend Settings")