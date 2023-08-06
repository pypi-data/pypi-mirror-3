# coding: utf-8
from abc                 import ABCMeta, abstractmethod
from secobj.exceptions   import UnknownActionError
from secobj.localization import _

class Action(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def allowed(self, subject, resource, *permissions):
        raise NotImplementedError

    def denied(self, subject, resource, *permissions):
        return not self.allowed(subject, resource, *permissions)

class Allow(Action):
    def allowed(self, subject, resource, *permissions):
        return True

    def __str__(self):
        return "allow"

    def __repr__(self):
        return "<secobj.action.Allow>"

    def __eq__(self, other):
        if isinstance(other, Allow):
            return True
        elif isinstance(other, Action):
            return False
        else:
            raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, Allow):
            return False
        elif isinstance(other, Action):
            return True
        else:
            raise NotImplementedError

ALLOW = Allow()

class Deny(Action):
    def allowed(self, subject, resource, *permissions):
        return False

    def __str__(self):
        return "deny"

    def __repr__(self):
        return "<secobj.action.Deny>"

    def __eq__(self, other):
        if isinstance(other, Deny):
            return True
        elif isinstance(other, Action):
            return False
        else:
            raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, Deny):
            return False
        elif isinstance(other, Action):
            return True
        else:
            raise NotImplementedError

DENY = Deny()

def getaction(name):
    if name.upper() == 'ALLOW':
        return ALLOW
    if name.upper() == 'DENY':
        return DENY
    raise UnknownActionError, _("Invalid action name: {name}").format(name)

