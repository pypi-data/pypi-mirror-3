"""
Some useful transforms for L{filecache.FileCache}.  It's useful to have them
in one place to prevent duplicated entries in FileCache's content cache.
"""

import sys
from hashlib import md5

_postImportVars = vars().keys()


def md5hexdigest(s):
	return md5(s).hexdigest()


try: from refbinder.api import bindRecursive
except ImportError: pass
else: bindRecursive(sys.modules[__name__], _postImportVars)
