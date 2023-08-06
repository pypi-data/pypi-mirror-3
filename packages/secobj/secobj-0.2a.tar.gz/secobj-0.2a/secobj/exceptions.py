# coding: utf-8

class SecurityError(Exception):
    pass

class AccessDeniedError(SecurityError):
    pass

class NoMatchingRuleError(SecurityError):
    pass

class UnknownActionError(SecurityError):
    pass

class UnknownPrincipalError(SecurityError):
    pass
