# coding: utf-8
from secobj.principal import ANONYMOUS
from secobj.provider  import SecurityProvider

class DefaultSecurityProvider(SecurityProvider):
    def getcurrentuser(self):
        return ANONYMOUS

    def is_subject_in_group(self, subject, group):
        return False

