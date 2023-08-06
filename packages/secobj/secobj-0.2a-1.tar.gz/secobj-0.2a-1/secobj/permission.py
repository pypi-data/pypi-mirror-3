# coding: utf-8
import re

from secobj.localization import _

NAME = re.compile(r'^[a-zA-Z0-9_][a-zA-Z0-9_\.]*$')

def getpermission(value):
    if isinstance(value, basestring):
        return Permission.get(value)
    if isinstance(value, Permission):
        return value
    raise ValueError, _("Invalid permission")

class PermissionMeta(type):
    def __call__(cls, *args, **kwargs):
        raise NotImplementedError, 'Permissions may only be instantiated through get()'

class Permission(object):
    __metaclass__ = PermissionMeta
    _permissions  = dict()

    def __new__(cls, *args, **kwargs):
        return super(Permission, cls).__new__(cls, *args, **kwargs)

    def __init__(self, name):
        assert isinstance(name, basestring)
        if NAME.match(name) is None:
            raise ValueError, _("Invalid permission name: {name}").format(name=name)
        self._name = name

    @classmethod
    def get(cls, name, *args, **kwargs):
        try:
            return cls._permissions[name]
        except KeyError:
            if 'instanceclass' in kwargs:
                instanceclass = kwargs['instanceclass']
                if not issubclass(instanceclass, Permission):
                    raise TypeError, _("Must be a subclass of Permission")
                del kwargs['instanceclass']
            else:
                instanceclass = Permission
            instance = instanceclass.__new__(instanceclass, *args, **kwargs)
            instance.__init__(name, *args, **kwargs)
            cls._permissions[name] = instance
            return instance

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<secobj.permission.Permission: {name}>".format(name=self._name)

    def __eq__(self, other):
        if isinstance(other, basestring):
            other = getpermission(other)
        if isinstance(other, AllPermission):
            return True
        elif isinstance(other, Permission):
            return self._name == other._name
        else:
            raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, basestring):
            other = getpermission(other)
        if isinstance(other, AllPermission):
            return False
        elif isinstance(other, Permission):
            return self._name != other.__name
        else:
            raise NotImplementedError

class AllPermission(Permission):
    def __repr__(self):
        return "<secobj.permission.AllPermission>"

    def __eq__(self, other):
        if isinstance(other, basestring):
            other = getpermission(other)
        if isinstance(other, Permission):
            return True
        else:
            raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, basestring):
            other = getpermission(other)
        if isinstance(other, Permission):
            return False
        else:
            raise NotImplementedError

ALL = Permission.get('all', instanceclass=AllPermission)

