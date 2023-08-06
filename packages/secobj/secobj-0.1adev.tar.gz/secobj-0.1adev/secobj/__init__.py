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

def initsecurity(configfile, logconfigfile=None, policyrules=None):
    """
    Initialize the package. This function must be called before an access controlled class is
    instanciated or an access controlled function is called or a named acl is used.

    :param configfile: Name and path of the main configuration file.
    :type configfile: string

    :param logconfigfile: Name and path of the configuration file for logging. This parameter can be
        omitted. Either the logging facility is configuered elsewhere or a null logger ist used.
    :type logconfigfile: string

    :param policyrules: Additional policy rules may be defined here. The tuples will be passed as
        arguments to the constructor of :py:class:`secobj.rule.Rule`.
    :type policyrules: list of tuples

    :raises: :py:exc:`secobj.exceptions.SecurityError`
    """
    import os.path
    import secobj

    from secobj.exceptions   import SecurityError
    from secobj.config       import initconfig, getconfig
    from secobj.localization import _
    from secobj.logger       import initlogger
    from secobj.rule         import Rule

    global DEFAULT_OWNER, POLICY_RULES
    try:
        initconfig(configfile, os.path.join(os.path.dirname(secobj.__file__), 'default.conf'))
        initlogger("secobj", configfile=logconfigfile)
        # set the policy rules
        if policyrules is not None:
            acl = list()
            for rule in policyrules:
                acl.append(Rule(*rule))
            POLICY_RULES = tuple(acl)
        # append an allow or deny all rule to the policy
        policyname  = getconfig().get('secobj', 'policy').upper()
        if policyname == 'DENY':
            POLICY_RULES = (Rule(*DENY_ALL),)
        elif policyname == 'ALLOW':
            POLICY_RULES = (Rule(*ALLOW_ALL),)
        else:
            raise ValueError, _("Unknown policy: {name}").format(name=policyname)
    except Exception, e:
        raise SecurityError, _("Initialization of package 'secobj'' failed: {msg}").format(msg=str(e))

