# coding: utf-8
import collections
import inspect
import re

from abc                 import ABCMeta, abstractmethod
from secobj.localization import _

PREDICATE_NAME  = re.compile(r'^&[a-zA-Z0-9][a-zA-Z0-9_\.]*$')
USER_NAME       = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\.]*$')
GROUP_NAME      = re.compile(r'^@[a-zA-Z0-9][a-zA-Z0-9_\.]*$')
SUBJECT_NAME    = re.compile(r'^[@]?[a-zA-Z0-9][a-zA-Z0-9_\.]*$')
PRINCIPAL_NAME  = re.compile(r'^[@&]?[a-zA-Z0-9][a-zA-Z0-9_\.]*$')

# Class hierachy
#
#   Principal
#       Subject
#           Group
#               GroupList
#           User
#               Anonymous
#               System
#       Predicate
#           Authenticated
#           Everyone
#           Owner

class PrincipalMeta(ABCMeta):
    def __call__(cls, *args, **kwargs):
        raise NotImplementedError, 'Principals may only be instantiated through get()'

class Principal(object):
    __metaclass__ = PrincipalMeta
    _principals   = dict()

    def __init__(self, name):
        if PRINCIPAL_NAME.match(name) is None:
            raise ValueError, _("Invalid principal name: {name}").format(name=name)
        self._name = name

    @classmethod
    def get(cls, name, *args, **kwargs):
        if 'instanceclass' in kwargs:
            instanceclass = kwargs['instanceclass']
            if not issubclass(instanceclass, Principal):
                raise TypeError, _("Must be a subclass of Principal")
            del kwargs['instanceclass']
        else:
            instanceclass = Principal
        try:
            principal = cls._principals[name]
            if not issubclass(instanceclass, principal.__class__):
                return principal
        except KeyError:
            pass
        instance = instanceclass.__new__(instanceclass, *args, **kwargs)
        instance.__init__(name, *args, **kwargs)
        cls._principals[name] = instance
        return instance

    @property
    def name(self):
        return self._name

    @property
    def provider(self):
        from secobj.provider import getprovider
        return getprovider()

    @abstractmethod
    def match(self, other, resource=None, args=None, kwargs=None):
        return False

    def __str__(self):
        return self._name

    def __repr__(self):
        classname = self.__class__.__module__+"."+self.__class__.__name__
        return "<{classname}: {name}>".format(classname=classname, name=self._name)

    def __eq__(self, other):
        if isinstance(other, Principal):
            return repr(self) == repr(other)
        else:
            raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, Principal):
            return repr(self) != repr(other)
        else:
            raise NotImplementedError

class Subject(Principal):
    def __init__(self, name):
        if SUBJECT_NAME.match(name) is None:
            raise ValueError, _("Invalid subject name: {name}").format(name=name)
        super(Subject, self).__init__(name)

    @property
    def plainname(self):
        return self._getplainname()

    @abstractmethod
    def _getplainname(self):
        return None

class Group(Subject):
    def __init__(self, name, alias=None):
        assert isinstance(alias, basestring) or alias is None
        if GROUP_NAME.match(name) is None:
            raise ValueError, _("Invalid group name: {name}").format(name=name)
        self._alias = alias if alias is not None else name[1:]
        super(Group, self).__init__(name)

    @classmethod
    def get(cls, name, *args, **kwargs):
        if 'instanceclass' in kwargs:
            if not issubclass(kwargs['instanceclass'], Group):
                raise TypeError, _("Must be a subclass of Group")
        else:
            kwargs['instanceclass'] = Group
        return Principal.get(name, *args, **kwargs)

    @property
    def alias(self):
        return self._alias

    def _getplainname(self):
        return self._alias

    def match(self, other, resource=None, args=None, kwargs=None):
        if isinstance(other, Group):
            return self.name == other.name
        elif isinstance(other, User):
            return self.provider.is_subject_in_group(other, self)
        return False

class GroupList(Group, collections.MutableSequence):
    def __init__(self, name, alias=None, members=None):
        super(GroupList, self).__init__(name, alias=alias)
        self._members = list()
        self.extend(members)

    @classmethod
    def get(cls, name, *args, **kwargs):
        if 'instanceclass' in kwargs:
            if not issubclass(kwargs['instanceclass'], GroupList):
                raise TypeError, _("Must be a subclass of GroupList")
        else:
            kwargs['instanceclass'] = GroupList
        return Principal.get(name, *args, **kwargs)

    def _cast(self, value):
        if isinstance(value, basestring):
            return Group.get(value)
        elif not isinstance(value, Group):
            raise TypeError, _("Members must be of class Group")
        return value

    def __contains__(self, item):
        return item in self._members

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        return self._members.__iter__()

    def __getitem__(self, index):
        return self._members[index]

    def __setitem__(self, index, value):
        self._members[index] = self._cast(value)

    def __delitem__(self, index):
        del self._members[index]

    def insert(self, index, value):
        self._members.insert(index, self._cast(value))

    def match(self, other, resource=None, args=None, kwargs=None):

        def domatch(members):
            for member in members:
                if self.provider.is_subject_in_group(other, member):
                    return True
                if isinstance(member, GroupList):
                    if domatch(member):
                        return True
            return False

        if super(GroupList, self).match(other, resource, args, kwargs):
            return True
        elif isinstance(other, User):
            return domatch(self._members)
        return False

class User(Subject):
    def __init__(self, name, login=None):
        assert isinstance(login, basestring) or login is None
        if USER_NAME.match(name) is None:
            raise ValueError, _("Invalid user name: {name}").format(name=name)
        self._login = login if login is not None else name
        super(User, self).__init__(name)

    @classmethod
    def get(cls, name, *args, **kwargs):
        if 'instanceclass' in kwargs:
            if not issubclass(kwargs['instanceclass'], User):
                raise TypeError, _("Must be a subclass of User")
        else:
            kwargs['instanceclass'] = User
        return Principal.get(name, *args, **kwargs)

    @property
    def login(self):
        return self._login

    @property
    def isauthenticated(self):
        return self._isauthenticated()

    def _getplainname(self):
        return self._login

    def _isauthenticated(self):
        return True

    def match(self, other, resource=None, args=None, kwargs=None):
        if isinstance(other, User):
            return self.name == other.name
        elif isinstance(other, Group):
            return self.provider.is_subject_in_group(self, other)
        return False

class Anonymous(User):
    def _isauthenticated(self):
        return False

class Predicate(Principal):
    def __init__(self, name):
        if PREDICATE_NAME.match(name) is None:
            raise ValueError, _("Invalid predicate name: {name}").format(name=name)
        super(Predicate, self).__init__(name)

class Authenticated(Predicate):
    def match(self, other, resource=None, args=None, kwargs=None):
        if isinstance(other, User):
            return other.isauthenticated
        return False

class Everyone(Predicate):
    def match(self, other, resource=None, args=None, kwargs=None):
        if isinstance(other, Subject):
            return True
        return False

class Owner(Predicate):
    def match(self, other, resource=None, args=None, kwargs=None):
        if resource:
            # is method and args are given then get owner of self (args[0])
            if inspect.isfunction(resource) and hasattr(resource, '__acl_class__') and args:
                return self.provider._getowner(args[0]).match(other)
            return self.provider._getowner(resource).match(other)
        return False

ANONYMOUS     = User.get('Anonymous', instanceclass=Anonymous)
SYSTEM        = User.get('System')
AUTHENTICATED = Principal.get('&Authenticated', instanceclass=Authenticated)
EVERYONE      = Principal.get('&Everyone', instanceclass=Everyone)
OWNER         = Principal.get('&Owner', instanceclass=Owner)

