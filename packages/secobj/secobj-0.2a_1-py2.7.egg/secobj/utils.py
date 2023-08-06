# coding: utf-8
from secobj.logger import getlogger

def error(ex, log, msg, *args, **kwargs):
    msg = msg.format(*args, **kwargs)
    try:
        if isinstance(log, basestring):
            log = getlogger(log)
        if log is not None:
            log.error(msg)
    except ValueError:
        pass
    return ex(msg)

