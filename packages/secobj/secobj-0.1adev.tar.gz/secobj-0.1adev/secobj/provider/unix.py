# coding: utf-8
import grp
import os
import pwd
import weakref

from secobj.exceptions   import UnknownPrincipalError
from secobj.localization import _
from secobj.memoizer     import memoize
from secobj.principal    import USER_NAME, GROUP_NAME
from secobj.principal    import Group, GroupList, Subject, User
from secobj.provider     import SecurityProvider
from secobj.utils        import error

_cached_subjects = weakref.WeakValueDictionary()

class UnixSecurityProvider(SecurityProvider):
    def __init__(self):
        # Must be set before the constructor of the super class is called, because 'getcurrentuser'
        # is called via 'checkaccess' in the super class.
        self._currentuser = User.get(pwd.getpwuid(os.getuid()).pw_name)
        super(UnixSecurityProvider, self).__init__()

    def getcurrentuser(self):
        return self._currentuser

    def _setcurrentuser(self, user):
        assert isinstance(user, User)
        self._currentuser = user

    @memoize(cache=_cached_subjects, method=True)
    def _getsubject(self, name):
        if USER_NAME.match(name) is not None:
            try:
                return User.get(pwd.getpwnam(name).pw_name)
            except KeyError:
                pass
        elif GROUP_NAME.match(name) is not None:
            try:
                return Group.get(grp.getgrnam(name[1:]).gr_name)
            except KeyError:
                pass
        return super(UnixSecurityProvider, self)._getsubject(name)

    def is_subject_in_group(self, subject, group):

        def test(group):
            try:
                for name in grp.getgrnam(group.plainname).gr_mem:
                    if name == subject.name:
                        return True
            except KeyError:
                pass
            return False

        if test(group):
            return True
        if isinstance(group, GroupList):
            for member in group:
                if test(member):
                    return True
        return False
