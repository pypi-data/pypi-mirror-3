# coding: utf-8
#
# Copyright 2012, Marc Göldner <info@cramren.de>
#

"""
The package :py:mod:`secobj` provides an interface wich allows a fine grained access control on
functions, methods and classes. Access control is declared via the decorator
:py:func:`secobj.decorator.access`.
"""

__version__ = '0.1a'

from secobj.action     import ALLOW, DENY
from secobj.decorator  import access
from secobj.permission import ALL
from secobj.principal  import ANONYMOUS, AUTHENTICATED, EVERYONE, OWNER, SYSTEM

ALLOW_ALL    = (ALLOW, EVERYONE, ALL)
DENY_ALL     = (DENY,  EVERYONE, ALL)
POLICY_RULES = None

def getprovider():
    from secobj.provider import getprovider
    return getprovider()

def getacl(resource):
    from secobj.provider import getprovider
    return getprovider().getacl(resource)

def getnamedacl(name):
    from secobj.provider import getprovider
    return getprovider().getnamedacl(name)

def getsubject(name):
    from secobj.provider import getprovider
    return getprovider().getsubject(name)

def getprincipal(name):
    from secobj.provider import getprovider
    return getprovider().getprincipal(name)

def isowner(resource, principal):
    from secobj.provider import getprovider
    return getprovider().isowner(resource, principal)

def getowner(resource):
    from secobj.provider import getprovider
    return getprovider().getowner(resource)

def setowner(resource, principal=SYSTEM):
    from secobj.provider import getprovider
    return getprovider().setowner(resource, principal)

def getcurrentuser():
    from secobj.provider import getprovider
    return getprovider().getcurrentuser()

def runas(func, user, *args, **kwargs):
    from secobj.provider import getprovider
    return getprovider().runas(func, user, *args, **kwargs)

def initsecurity(configfile=None, logconfigfile=None, policyrules=None):
    """
    Initialize the package. This function must be called before an access controlled class is
    instanciated or an access controlled function is called or a named acl is used.

    :param configfile: Name and path of the main configuration file. This parameter can be omitted.
    :type configfile: string

    :param logconfigfile: Name and path of the configuration file for logging. This parameter can be
        omitted. Either the logging facility is configuered elsewhere or a null logger ist used.
    :type logconfigfile: string

    :param policyrules: Additional policy rules may be defined here. The tuples will be passed as
        arguments to the constructor of :py:class:`secobj.rule.Rule`.
    :type policyrules: list of tuples

    :raises: :py:exc:`secobj.exceptions.SecurityError`
    """
    import json
    import os.path
    import secobj

    from secobj.exceptions   import SecurityError
    from secobj.config       import initconfig, getconfig
    from secobj.localization import _
    from secobj.logger       import getlogger, initlogger
    from secobj.rule         import Rule

    global DEFAULT_OWNER, POLICY_RULES

    if POLICY_RULES is not None:
        return
    try:
        initconfig(configfile, os.path.join(os.path.dirname(secobj.__file__), 'default.conf'))
        initlogger("secobj", configfile=logconfigfile)
        config = getconfig()
        acl    = list()
        log    = getlogger('init')
        # set the policy rules
        if policyrules is not None:
            for rule in policyrules:
                acl.append(Rule(*rule))
        # append policy rules defined in the configuration file
        if config.has_option('secobj', 'policy_rules'):
            text = config.get('secobj', 'policy_rules')
            if text:
                acl.extend((map(lambda x: Rule(*x), json.loads(text))))
            else:
                log.warning(_("Policy rules have no value"))
        # append an allow or deny all rule to the policy
        policyname = config.get('secobj', 'policy').upper()
        if policyname == 'DENY':
            acl.append(Rule(*DENY_ALL))
        elif policyname == 'ALLOW':
            acl.append(Rule(*ALLOW_ALL))
        else:
            raise error(ValueError, log, _("Unknown policy: {name}").format(name=policyname))
        POLICY_RULES = tuple(acl)
    except Exception, e:
        raise SecurityError, _("Initialization of package 'secobj' failed: {msg}").format(msg=str(e))

