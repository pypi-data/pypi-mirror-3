# coding: utf-8
from secobj.provider.base    import SecurityProvider
from secobj.provider.default import DefaultSecurityProvider
from secobj.provider.unix    import UnixSecurityProvider

def getprovider():
    from secobj.storage import getstorage
    return getstorage().getprovider()

