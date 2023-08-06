#!/usr/bin/python
# -*- coding: utf-8 -*-

################
# LDAP
################

# Baseline Configuration

AUTH_LDAP_SERVER_URI = "${AUTH_LDAP_SERVER_URI}"
AUTH_LDAP_START_TLS = "${AUTH_LDAP_START_TLS}"
AUTH_LDAP_BIND_DN = "${AUTH_LDAP_BIND_DN}"
AUTH_LDAP_BIND_PASSWORD = "${AUTH_LDAP_BIND_PASSWORD}"
#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=pwet,dc=pwet,dc=pwet,dc=org",
#		ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "${AUTH_LDAP_USER_ATTR_MAP-first_name}",
        "last_name": "${AUTH_LDAP_USER_ATTR_MAP-last_name}",
        "email": "${AUTH_LDAP_USER_ATTR_MAP-email}"
        }

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "${AUTH_LDAP_USER_FLAGS_BY_GROUP-is_active}",
        "is_staff": "${AUTH_LDAP_USER_FLAGS_BY_GROUP-is_staff}",
        "is_superuser": "${AUTH_LDAP_USER_FLAGS_BY_GROUP-is_superuser}"
        }

AUTH_LDAP_SERVER = '${AUTH_LDAP_SERVER}'
AUTH_LDAP_BASE_USER = "${AUTH_LDAP_BASE_USER}"
AUTH_LDAP_BASE_PASS = "${AUTH_LDAP_BASE_PASS}"
AUTH_LDAP_BASE = "${AUTH_LDAP_BASE}"
AUTH_LDAP_SCOPE = "${AUTH_LDAP_SCOPE}"

