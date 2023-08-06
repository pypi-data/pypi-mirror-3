# coding: utf-8
import os.path
import re
import secobj

from ConfigParser        import SafeConfigParser
from secobj.localization import _

LIST_PATTERN = re.compile(r'\s*("[^"]*"|.*?)\s*,')
CFG          = None

class ConfigParser(SafeConfigParser):
    def getlist(self, section, option):
        value = self.get(section, option)
        # Credits to: Armin Ronacher (http://stackoverflow.com/users/19990/armin-ronacher)
        return [x[1:-1] if x[:1] == x[-1:] == '"' else x
            for x in LIST_PATTERN.findall(value.rstrip(',') + ',')]

# If config is not initialized, then there ist no logger too.
def getconfig():
    if CFG is None:
        raise ValueError, _("Configuration is not inizialized")
    return CFG

# Bootstrap phase, no logging possible
def initconfig(configfile, *defaultfiles):
    global CFG
    if CFG is None:
        files = [configfile]
        files.extend(defaultfiles)
        files.reverse()
        if not os.path.isfile(configfile):
            raise ValueError, _("Configuration file doesn't exist or is not a file: {name}")\
                              .format(name=configfile)
        CFG = ConfigParser()
        CFG.read(files)

