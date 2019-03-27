import platform
import sys

from pkg_resources import VersionConflict

from .about import (__author__, __author_email__, __description__, __name__,
                    __url__, __version__)

if sys.version_info <= (3, 0):
    raise VersionConflict("ORES requires Python '>=3' but your Python version is " + platform.python_version())


__all__ = [__name__, __version__, __author__, __author_email__,
           __description__, __url__]
