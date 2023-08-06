# coding: utf-8
from secobj.action       import Action, getaction
from secobj.localization import _
from secobj.permission   import ALL
from secobj.permission   import getpermission, Permission
from secobj.principal    import Principal, Subject
from secobj.principal    import PRINCIPAL_NAME
from secobj.utils        import error

class Rule(object):
    def __init__(self, action, principal, *permissions):
        # Initialize action
        if isinstance(action, Action):
            self._action = action
        else:
            self._action = getaction(action)
        # Initialize principal
        if isinstance(principal, Principal):
            self._principalname  = principal.name
            self._principal      = principal
        elif Principal.has(principal):
            self._principalname  = principal
            self._principal      = Principal.get(principal)
        elif PRINCIPAL_NAME.match(principal) is not None:
            self._principalname  = principal
            self._principal      = None
        else:
            raise error(ValueError, "rule", _("Invalid principal name: {name}")\
                                              .format(name=principal))
        # Initialize premissions
        self._permissions = list()
        for permission in permissions:
            if not isinstance(permission, Permission):
                permission = getpermission(permission)
            if permission.name == ALL.name:
                self._permissions = [ALL]
                break
            self._permissions.append(permission)
        if len(self._permissions) > 0:
            self._permissions = tuple(self._permissions)
        else:
            self._permissions = None

    def __str__(self):
        return "({action}, {principal}, {permissions})".format(action=self._action,
               principal=self._principalname, permissions=map(str, self.permissions))

    def __repr__(self):
        return "<secobj.rule.Rule: {rule}>".format(rule=self)

    @property
    def action(self):
        return self._action

    @property
    def principal(self):
        from secobj.provider import getprovider

        if self._principal is None:
            from secobj.provider import getprovider
            self._principal = getprovider().getprincipal(self._principalname)
        return self._principal

    @property
    def permissions(self):
        return self._permissions if self._permissions else tuple()
    @permissions.setter
    def permissions(self, permissions):

        def convert(permission):
            if not isinstance(permission, Permission):
                permission = getpermission(permission)
            return permission

        if self._permissions is not None:
            raise error(ValueError, "rule", _("Permissions are already set"))
        self._permissions = tuple(map(convert, permissions))

    @property
    def haspermissions(self):
        return self._permissions is not None

    def getpermissions_for(self, resource):
        from secobj.provider import getprovider

        if not self._permissions:
            return (getprovider()._getpermission(resource, ALL),)
        return self.permissions

    def match(self, subject, resource=None, args=None, kwargs=None):
        assert isinstance(subject, Subject)
        return self.principal.match(subject, resource, args, kwargs)

    def allowed(self, subject, resource):
        return self.action.allowed(subject, resource, *self.getpermissions_for(resource))

    def denied(self, subject, resource):
        return self.action.denied(subject, resource, *self.getpermissions_for(resource))

