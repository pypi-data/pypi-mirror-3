# coding: utf-8
import logging
import logging.config

from secobj.localization import _

LOG      = None
LOG_BASE = None

# If logging is not initialized, then logging is impossible
def getlogger(*args):
    if LOG is None:
        raise ValueError, _("Logger is not initialized")
    if len(args) > 0:
        names = [LOG_BASE]
        names.extend(args)
        return logging.getLogger(".".join(names))
    return LOG

# Bootstrap phase, no logging possible
def initlogger(base, configfile=None):
    global LOG, LOG_BASE
    if LOG is None:
        if not isinstance(base, basestring):
            raise ValueError, _("Invalid logger base, must be a string")
        if configfile is not None:
            logging.config.fileConfig(configfile)
        LOG_BASE = base
        LOG      = logging.getLogger(LOG_BASE)
        if len(LOG.handlers) == 0:
            LOG.addHandler(logging.NullHandler())

