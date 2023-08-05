# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, request, redirect, tmpl_context
from tg import url as tgurl
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort

from repoze.what import predicates

from acr.lib.base import BaseController, get_page_from_urllist, url
from acr.model import DBSession, Page
from acr import model

from libacr.controllers.cms import AcrRootController
from libacr.controllers.rdisk import RDiskController
from acr.controllers.error import ErrorController

from turbomail import Message


__all__ = ['RootController']

class RootController(BaseController):
    acr = AcrRootController()
    rdisk = RDiskController()
    error = ErrorController()

    @expose('libacr.templates.page')
    def index(self, *args, **kw):
        return self.acr.default(*args, **kw)

    @expose()
    def _lookup(self, *args, **kw):
        return self.acr, args

    @expose('acr.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page=None, login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(tgurl('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
