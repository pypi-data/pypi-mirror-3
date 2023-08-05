"""Helpers to run multiple ACR sites inside the same WSGIDaemon and Process"""

from zope.interface import implements
from repoze.who.interfaces import IAuthenticator, IMetadataProvider
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import sqlalchemy.pool

from sqlalchemy import engine_from_config
from tg import config, request
import threading

class AcrMultiSiteEngine(object):
    def __init__(self):
        self.engines = {}
        self.configs = {}
        self.tl = threading.local()

    @property
    def forced_script(self):
        try:
            return self.tl.forced_script
        except:
            return None

    def force_thread_env(self, environ):
        if environ:
            try:
                script_name = environ['SCRIPT_FILENAME']
            except:
                script_name = environ['HTTP_HOST']
        else:
            script_name = None
        self.tl.forced_script = script_name

    def __getattr__(self, name):
        if name in ('engines', 'forced_script', 'force_script', 'configs', 'tl'):
            return object.__getattribute__(self, name)

        config_key = None
        try:
            try:
                config_key = request.environ['SCRIPT_FILENAME']
            except:
                config_key = request.environ['HTTP_HOST']
        except:
            pass

        if not self.forced_script and config_key and not self.configs.has_key(config_key):
            self.configs[config_key] = config['sqlalchemy.url']

        try:
            used_db = self.configs[config_key]
        except KeyError:
            used_db = config['sqlalchemy.url']

        if self.forced_script:
            try:
                used_db = self.configs[self.forced_script]
            except KeyError:
                pass

        if not self.forced_script and not config_key:
            raise Exception('Outside of a request and no script forced')

        if not self.engines.has_key(used_db):
            if 'acrmultisite.poolclass' in config:
                config['sqlalchemy.poolclass'] = getattr(sqlalchemy.pool, config['acrmultisite.poolclass'])
            self.engines[used_db] = engine_from_config(config, 'sqlalchemy.')

        return getattr(self.engines[used_db], name)

class AcrAuthenticatorPlugin(object):
    implements(IAuthenticator, IMetadataProvider)

    def __init__(self, user_class, dbsession):
        self.user_class = user_class
        self.dbsession = dbsession

    def get_user(self, environ, username):
        from acr import model
        username_attr = getattr(self.user_class, 'user_name')

        query = self.dbsession.query(self.user_class)
        query = query.filter(username_attr==username)

        try:
            model.multisite_engine.force_thread_env(environ)
            r = query.one()
            model.multisite_engine.force_thread_env(None)
            return r
        except:
            # As recommended in the docs for repoze.who, it's important to
            # verify that there's only _one_ matching userid.
            return None

    def get_groups(self, environ, user):
        from acr import model
        groups = []
        model.multisite_engine.force_thread_env(environ)
        if user:
            groups = [g.group_name.encode('utf-8') for g in user.groups]
        model.multisite_engine.force_thread_env(None)
        return groups

    # IAuthenticator
    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None

        user = self.get_user(environ, identity['login'])
        if user:
            validator = getattr(user, 'validate_password')
            if validator(identity['password']):
                return identity['login']

    # IMetadataProdiver
    def add_metadata(self, environ, identity):
        identity['user'] = self.get_user(environ, identity['repoze.who.userid'])
        identity['groups'] = self.get_groups(environ, identity['user'])

        environ['repoze.what.credentials'] = {}
        environ['repoze.what.credentials']['groups'] = identity['groups']
