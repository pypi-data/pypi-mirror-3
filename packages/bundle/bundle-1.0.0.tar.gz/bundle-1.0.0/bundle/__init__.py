"""Create and manage bundle packages."""
from __future__ import absolute_import

VERSION = (1, 0, 0)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Ask Solem"
__contact__ = "ask@celeryproject.org"
__homepage__ = "http://github.com/ask/bundle/"
__docformat__ = "restructuredtext en"

# -eof meta-

from .bundle import Bundle
