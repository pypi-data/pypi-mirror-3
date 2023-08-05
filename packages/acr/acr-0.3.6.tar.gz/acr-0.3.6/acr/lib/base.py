# -*- coding: utf-8 -*-

"""The base Controller API."""

import tg
from tg import TGController, tmpl_context
from tg.render import render
from tg import request
from pylons.i18n import _, ungettext, N_
from tw.jquery import jquery_js

from libacr.lib import *

__all__ = ['Controller', 'BaseController']

class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity

        #Work-Around for IE9 passing only specific mime type for Accept Header
        #causing crash in TG2.0
        accept_header = request.headers.get('Accept')
        if accept_header and '*/*' not in accept_header:
            request.headers['Accept'] += ',*/*;q=0.1'
            
        jquery_js.inject()
        full_acr_js.inject()
        acr_css.inject()
        return TGController.__call__(self, environ, start_response)
