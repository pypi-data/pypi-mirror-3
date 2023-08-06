# coding: utf-8
import secobj
import gettext
import os.path

DOMAIN      = "secobj"
LOCALEDIR   = os.path.join(os.path.dirname(secobj.__file__), "languages")
TRANSLATION = gettext.translation(DOMAIN, LOCALEDIR, fallback=True)
_           = TRANSLATION.ugettext
