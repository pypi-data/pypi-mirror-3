# coding: utf-8
import inspect
import json
import re
import weakref

from abc                 import ABCMeta, abstractmethod
from secobj.action       import ALLOW
from secobj.config       import getconfig
from secobj.exceptions   import AccessDeniedError, NoMatchingRuleError, SecurityError
from secobj.exceptions   import UnknownPrincipalError
from secobj.localization import _
from secobj.logger       import getlogger
from secobj.memoizer     import memoize
from secobj.permission   import ALL
from secobj.permission   import getpermission, Permission
from secobj.principal    import EVERYONE, SYSTEM
from secobj.principal    import Principal, Subject, User
from secobj.utils        import error

NAMEDRULES = re.compile(r'^(?P<section>[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*)'+\
                        r'#(?P<option>[a-zA-Z0-9_]+)$')

_cached_acls        = weakref.WeakKeyDictionary()
_cached_namedacls   = dict()
_cached_owners      = weakref.WeakKeyDictionary()
_cached_permissions = weakref.WeakKeyDictionary()

class SecurityProviderMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        from secobj.rule import Rule

        attrs['__acl__']                = (Rule(ALLOW, EVERYONE, 'secobj'),)
        attrs['__acl_owner__']          = SYSTEM
        attrs['__acl_inherit__']        = True
        attrs['__acl_permission__']     = getpermission('secobj')
        attrs['__acl_decorated_init__'] = None
        return ABCMeta.__new__(cls, name, bases, attrs)

class SecurityProvider(object):
    __metaclass__ = SecurityProviderMeta

    def __init__(self):
        self._config = getconfig()
        self._log    = getlogger('provider')
        self.checkaccess(self, permission=self.__acl_permission__)

    @property
    def config(self):
        return self._config

    @property
    def log(self):
        return self._log

    @property
    def policy(self):
        from secobj import POLICY_RULES
        return POLICY_RULES

    @memoize(cache=_cached_acls, method=True)
    def _getacl(self, resource):
        if not self.hasaccess(resource):
            raise error(SecurityError, self.log,
                        _("Can't get acl on resource, which is not security controlled"))
        rules = list()
        name  = ""
        if inspect.ismethod(resource):
            name = "{modulename}.{classname}.{methodname}"\
                .format(modulename=resource.im_class.__module__,
                        classname=resource.im_class.__name__,
                        methodname=resource.__name__)
            rules.extend(resource.__acl__)
            rules.extend(resource.__acl_class__.__acl__)
        elif inspect.isfunction(resource):
            rules.extend(resource.__acl__)
            if hasattr(resource, '__acl_class__'):
                name = "{modulename}.{classname}.{methodname}"\
                    .format(modulename=resource.__acl_class__.__module__,
                            classname=resource.__acl_class__.__name__,
                            methodname=resource.__name__)
                rules.extend(resource.__acl_class__.__acl__)
            else:
                name = "{modulename}.{methodname}"\
                    .format(modulename=resource.__module__, methodname=resource.__name__)
        elif inspect.isclass(resource):
            name = "{modulename}.{classname}"\
                .format(modulename=resource.__module__, classname=resource.__name__)
            rules.extend(resource.__acl__)
        elif hasattr(resource, '__class__'):
            name = "{modulename}.{classname}"\
                .format(modulename=resource.__class__.__module__,
                        classname=resource.__class__.__name__)
            rules.extend(resource.__class__.__acl__)
        if len(rules) > 0:
            rules.extend(self.policy)
            rules = tuple(rules)
            return name, rules
        return name, self.policy

    @memoize(cache=_cached_namedacls, method=True)
    def _getnamedacl(self, name):
        from secobj.rule import Rule

        m = NAMEDRULES.match(name)
        if m is None:
            raise error(ValueError, self.log, _("Invalid name for named rule: {name}"\
                                                .format(name=name)))
        section = "rules:"+m.group('section')
        option  = m.group('option')
        if not self.config.has_option(section, option):
            self.log.warning(_("Named rule '{option}' doesn't exist in section '{section}'")\
                               .format(section=section, option=option))
            return tuple()
        text = self.config.get(section, option)
        if not text:
            self.log.warning(_("Named rule '{option}' in section '{section}' has no value")\
                               .format(section=section, option=option))
            return tuple()
        return tuple(map(lambda x: Rule(*x), json.loads(text)))

    @abstractmethod
    def _setcurrentuser(self, user):
        pass

    def _isowner(self, resource, principal):
        return self._getowner(resource).match(principal, resource)

    @memoize(cache=_cached_owners, method=True)
    def _getowner(self, resource):
        if not self.hasaccess(resource):
            raise error(SecurityError, self.log,
                        _("Can't get owner on resource, which is not security controlled"))
        if inspect.ismethod(resource):
            if hasattr(resource.im_self, '__acl_owner__'):
                return resource.im_self.__acl_owner__
            return resource.__acl_class__.__acl_owner__
        elif inspect.isfunction(resource):
            if hasattr(resource, '__acl_class__'):
                raise error(SecurityError, self.log,
                            _("Can't get owner on unbound method function. Use method instead"))
            return resource.__acl_owner__
        elif inspect.isclass(resource):
            return resource.__acl_owner__
        elif hasattr(resource, '__class__'):
            if hasattr(resource, '__acl_owner__'):
                return resource.__acl_owner__
            return resource.__class__.__acl_owner__
        return SYSTEM

    def _setowner(self, resource, principal=SYSTEM):
        assert isinstance(principal, Principal)
        if not self.hasaccess(resource):
            raise error(SecurityError, self.log,
                        _("Can't set owner on resource, which is not security controlled"))
        if inspect.ismethod(resource):
            raise error(SecurityError, self.log, _("Can't set owner on method"))
        elif inspect.isfunction(resource):
            if hasattr(resource, '__acl_class__'):
                raise error(SecurityError, self.log, _("Can't set owner on method function"))
            resource.__acl_owner__ = user
        else:
            resource.__acl_owner__ = principal
        key = (resource,)
        if key in _cached_owners:
            _cached_owners[key] = principal

    @memoize(cache=_cached_permissions, method=True, createkey=lambda args,kwargs: args)
    def _getpermission(self, resource, default=None):
        if not self.hasaccess(resource):
            raise error(SecurityError, self.log,
                        _("Can't set permission on resource, which is not security controlled"))
        if inspect.ismethod(resource) or inspect.isfunction(resource) or inspect.isclass(resource):
            permission = resource.__acl_permission__
            if permission is None and hasattr(resource, '__acl_class__'):
                permission = resource.__acl_class__.__acl_permission__
        else:
            permission = resource.__class__.__acl_permission__
        return permission if permission else default

    def _getsubject(self, name):
        try:
            subject = Principal.get(name)
            if not isinstance(subject, Subject):
                raise KeyError
            return subject
        except KeyError:
            raise error(UnknownPrincipalError, self.log, _("Unknown subject: {name}")\
                                                           .format(name=name))

    def _getprincipal(self, name):
        try:
            return Principal.get(name)
        except KeyError:
            raise error(UnknownPrincipalError, self.log, _("Unknown principal: {name}")\
                                                           .format(name=name))

    def _runas(self, func, user, *args, **kwargs):
        assert isinstance(user, User)
        olduser = self.getcurrentuser()
        if olduser != user:
            try:
                self.log.info(_("Starting run as for {newuser} by {olduser}")\
                                .format(newuser=user.name, olduser=olduser.name))
                self._setcurrentuser(user)
                return func(*args, **kwargs)
            finally:
                self._setcurrentuser(olduser)
                self.log.info(_("Finished run as for {newuser} by {olduser}")\
                                .format(newuser=user.name, olduser=olduser.name))
        return func(*args, **kwargs)

    def _check_getacl(self, resource):
        pass

    def _check_getnamedacl(self, name):
        pass

    def _check_getowner(self, resource):
        self.checkaccess(resource, permission='secobj.getowner',
                                   namedacl  ='secobj.provider#getowner')

    def _check_setowner(self, resource, principal):
        self.checkaccess(resource, permission='secobj.setowner',
                                   namedacl  ='secobj.provider#setowner')

    def _check_getpermission(self, resource):
        pass

    def _check_getprincipal(self, name):
        pass

    def _check_setcurrentuser(self, user):
        self.checkaccess(self, permission='secobj.runas',
                               namedacl  ='secobj.provider#runas')

    def _check_runas(self, func, user):
        self._check_setcurrentuser(user)
        self.checkaccess(self, permission='secobj.runas',
                               namedacl  ='secobj.provider#runas')

    def _checkrules(self, rules, resourcename, resource, args=None, kwargs=None):
        user = self.getcurrentuser()
        for rule in rules:
            if not rule.match(user, resource, args, kwargs):
                continue
            self.log.debug(_("Applied rule for {user} on {resource}: {rule}")\
                               .format(user=user.name, resource=resourcename, rule=str(rule)))
            if rule.denied(user, resource):
                raise error(AccessDeniedError, self.log,
                            _("Access denied for {user} on {resource}")\
                                .format(user=user.name, resource=resourcename))
            elif rule.allowed(user, resource):
                return rule.getpermissions_for(resource)
            else:
                msg = _("Rule neither allowed nor denied access for {user} on {resource}")\
                          .format(user=user.name, resource=resourcename)
                self.log.critical(msg)
                self.log.critical(_("Failed rule: {rule}").format(rule=str(rule)))
                raise SecurityError, msg
        raise error(NoMatchingRuleError, self.log,
                    _("No rule matched for {name} on {resource}")\
                        .format(name=user.name, resource=resourcename))

    @abstractmethod
    def getcurrentuser(self):
        return None

    def setcurrentuser(self, user):
        self._check_setcurrentuser(user)
        self._setcurrentuser(user)

    @abstractmethod
    def is_subject_in_group(self, subject, group):
        raise NotImplementedError

    def runas(self, func, user, *args, **kwargs):
        self._check_runas(func, user)
        return self._runas(func, user, *args, **kwargs)

    def hasaccess(self, resource):
        if hasattr(resource, '__acl__'):
            return True
        if hasattr(resource, '__class__'):
            return hasattr(resource.__class__, '__acl__')
        return False

    def checkaccess(self, resource, permission=None, namedacl=None, args=None, kwargs=None):
        if permission is None:
            permission = self._getpermission(resource, ALL)
        else:
            permission = getpermission(permission)
        assert isinstance(permission, Permission)
        name, rules = self._getacl(resource)
        if namedacl is not None:
            rules = self._getnamedacl(namedacl) + self.policy
        permissions = self._checkrules(rules, name, resource)
        if permission not in permissions:
            raise error(AccessDeniedError, self.log,
                        _("Access denied for {user} on {resource}, required: '{permission}', granted: {permissions}")\
                          .format(user=self.getcurrentuser().name,
                                  resource=name,
                                  permission=permission.name,
                                  permissions=map(str, permissions)))
        else:
            self.log.info(_("Access allowed for {user} on {resource} with '{permission}'")\
                            .format(user=self.getcurrentuser().name,
                                    resource=name,
                                    permission=permission.name,
                                    permissions=map(str, permissions)))


    def getsubject(self, name):
        self._check_getprincipal(name)
        return self._getsubject(name)

    def getprincipal(self, name):
        self._check_getprincipal(name)
        return self._getprincipal(name)

    def getacl(self, resource):
        self._check_getacl(resource)
        name, rules = self._getacl(resource)
        self.log.debug(_("Getting ACL on {name} for {user}")\
                           .format(name=name, user=self.getcurrentuser().name))
        return rules

    def getnamedacl(self, name):
        self._check_getnamedacl(name)
        return self._getnamedacl(name)

    def isowner(self, resource, principal):
        self._check_getowner(resource)
        return self._isowner(resource, principal)

    def getowner(self, resource):
        self._check_getowner(resource)
        return self._getowner(resource)

    def setowner(self, resource, principal=SYSTEM):
        self._check_setowner(resource, principal)
        self._setowner(resource, principal)

    def getpermission(self, resource):
        self._check_getpermission(resource)
        return self._getpermission(resource)

