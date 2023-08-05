# -*- coding: utf-8 -*-

"""The application's Globals object"""

__all__ = ['Globals']
from libacr.views.manager import ViewsManager
from libacr.plugins.manager import PluginsManager

import tg
if tg.version == '2.1':
    print 'TG2.1 found, helpers work-around in place'
    import tg.render, pylons
    def patched_pylons_globals():
        x = tg.render.my_pylons_globals()
        if x['h'] == {}:
            conf = pylons.config._current_obj()
            x['h'] = conf['package'].lib.helpers
        return x
    pylons.templating.pylons_globals = patched_pylons_globals

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        self.acr_viewmanager = ViewsManager()
        self.plugins = PluginsManager()
        """Do nothing, by default."""
        from turbomail.adapters import tm_pylons
        tm_pylons.start_extension()
