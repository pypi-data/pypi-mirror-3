"""
TiddlySpace
A discoursive social model for TiddlyWiki

website: http://tiddlyspace.com
repository: http://github.com/TiddlySpace/tiddlyspace
"""

import tiddlywebplugins.tiddlyspace.fixups
from tiddlywebplugins.tiddlyspace.plugin import init_plugin


__version__ = '1.0.63'


def init(config):
    """
    Establish required plugins and HTTP routes.
    """
    config['tiddlyspace.version'] = __version__
    init_plugin(config)
