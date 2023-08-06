import httplib
import web
from djblets.siteconfig.models import SiteConfiguration

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1


__all__ = [
    "auth",
    "get_user_info_by_username",
    "db_auth_account_field_name",
    "db_auth_email_field_name",
]


web.config.debug = True

siteconfig = SiteConfiguration.objects.get_current()

db_auth_database_engine_name = siteconfig.get("db_auth_database_engine_name", "sqlite")
db_auth_database_name = siteconfig.get("db_auth_database_name")
db_auth_username = siteconfig.get("db_auth_username")
db_auth_password = siteconfig.get("db_auth_password")

db_auth_table_name = siteconfig.get("db_auth_table_name")
db_auth_account_field_name = siteconfig.get("db_auth_account_field_name")
db_auth_passwd_field_name = siteconfig.get("db_auth_passwd_field_name")
db_auth_email_field_name = siteconfig.get("db_auth_email_field_name")


_settings = {
    "dbn" : db_auth_database_engine_name,
    "db" : db_auth_database_name,
}

if db_auth_database_engine_name in ("mysql", "postgres"):
    addition_attrs = {
        "user" : db_auth_username,
        "pw" : db_auth_password,
    }
    _settings.update(addition_attrs)
    

g_db = web.database(**_settings)


def auth(username, passwd,
         account_field_name = db_auth_account_field_name,
         passwd_field_name = db_auth_passwd_field_name):

    # NOTICE: You should change following to confirms to your protocol
    passwd_got = sha1(passwd).hexdigest()

    vars = {
        account_field_name : username,
    }
    where = web.db.sqlwhere(vars)

    what = "%s, %s" % (account_field_name, passwd_field_name)

    records = g_db.select(db_auth_table_name, vars = vars, where = where, what = what)

    for record in records:
        passwd_expect = record[passwd_field_name]
        if passwd_expect != passwd_got:
            return httplib.FORBIDDEN

        return httplib.OK

    return httplib.NOT_FOUND


def get_user_info_by_username(username,
                              account_field_name = db_auth_account_field_name,
                              db_auth_email_field_name = db_auth_email_field_name):
    where = "%s = $username" % account_field_name
    what = "%s, %s" % (account_field_name, db_auth_email_field_name)
    records = g_db.select(db_auth_table_name, vars = locals(), where = where, what = what)

    data = {}
    for record in records:
        data = dict(username = record[account_field_name],
                    email = record[db_auth_email_field_name])
    return data
